"""Scheduler for automatic PyTorchJob discovery and tuning in Kubernetes."""

import concurrent.futures
import logging
import queue
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, Optional

from kubernetes import client, config, watch
from optuna.samplers import BaseSampler

from .annotation_based_tuning import (
    annotation_job_converter,
    annotation_value_extractor,
)
from .pytorchjob import PyTorchJob
from .pytorchjob_tuner import PyTorchJobTuner

logger = logging.getLogger("zenith-tune")


@dataclass
class TuningConfig:
    """Configuration for a tuning job."""

    job_converter: Callable[[any, PyTorchJob], PyTorchJob] = annotation_job_converter
    value_extractor: Callable[[str, PyTorchJob], float] = annotation_value_extractor
    n_trials: Optional[int] = None
    output_dir: str = "outputs"
    sampler: Optional[BaseSampler] = None
    maximize: Optional[bool] = None
    timeout_per_trial: int = 1209600  # 2 weeks
    default_params: Optional[Dict] = None


@dataclass
class JobFilter:
    """Filter criteria for selecting PyTorchJobs to tune."""

    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    name_pattern: Optional[str] = None
    namespace_pattern: Optional[str] = None
    exclude_namespace_pattern: Optional[str] = None


class PyTorchJobTuningScheduler:
    """
    Scheduler that discovers PyTorchJobs and automatically creates tuning jobs.

    This scheduler periodically scans for PyTorchJobs matching specified criteria
    and creates PyTorchJobTuner instances to optimize them.
    """

    def __init__(
        self,
        submit_namespace: str,
        tuning_config: Optional[TuningConfig] = None,
        max_concurrent_tuning: int = 3,
        job_filter: Optional[JobFilter] = None,
    ):
        """
        Initialize the tuning scheduler.

        Args:
            submit_namespace: Namespace to submit tuning jobs (required)
            tuning_config: Configuration for tuning jobs (optional, uses defaults if None)
            max_concurrent_tuning: Maximum number of concurrent tuning jobs (default: 3)
            job_filter: Filter criteria for selecting jobs to tune (includes namespace filtering)
        """
        self.submit_namespace = submit_namespace
        self.tuning_config = tuning_config or TuningConfig()
        self.max_concurrent_tuning = max_concurrent_tuning
        self.job_filter = job_filter or JobFilter()

        # Track active tuning futures
        self._active_futures: Dict[str, concurrent.futures.Future] = {}

        # Queue for jobs to be tuned
        self._job_queue: queue.Queue = queue.Queue()

        # Shutdown event for graceful termination
        self._shutdown_event = threading.Event()

        # Record scheduler startup time (UTC)
        self._startup_time = datetime.now(timezone.utc).timestamp()

        # Setup ThreadPoolExecutor for concurrent tuning
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent_tuning
        )

        # Setup Kubernetes API clients
        self._setup_api_clients()

    def _setup_api_clients(self):
        """Setup Kubernetes API clients."""
        try:
            # Try in-cluster config first (for Pod execution)
            try:
                config.load_incluster_config()
                logger.info("Using in-cluster Kubernetes configuration")
            except config.ConfigException:
                # Fallback to kubeconfig (for local development)
                config.load_kube_config()
                logger.info("Using kubeconfig for Kubernetes configuration")

            self.core_api = client.CoreV1Api()
            self.custom_api = client.CustomObjectsApi()
        except config.ConfigException as e:
            logger.error(f"Failed to load Kubernetes config: {e}")
            raise

    def _tuning_job_producer(self):
        """
        Producer: Watch for PyTorchJobs and add matching ones to the queue.

        This runs in a separate thread and continuously watches for new/modified jobs.
        """
        w = watch.Watch()
        resource_version = None

        logger.info("Starting tuning job producer (PyTorchJob watcher)")

        while not self._shutdown_event.is_set():
            try:
                # Watch for all PyTorchJob events
                for event in w.stream(
                    self.custom_api.list_cluster_custom_object,
                    group="kubeflow.org",
                    version="v1",
                    plural="pytorchjobs",
                    resource_version=resource_version,
                    timeout_seconds=30,  # Shorter timeout for faster shutdown response
                ):
                    if self._shutdown_event.is_set():
                        break

                    event_type = event["type"]
                    job = event["object"]

                    # Update resource version for reconnection
                    metadata = job.get("metadata", {})
                    if "resourceVersion" in metadata:
                        resource_version = metadata["resourceVersion"]

                    # Only process ADDED events (new jobs created)
                    if event_type == "ADDED":
                        # Check if job was created after scheduler startup
                        creation_timestamp = metadata.get("creationTimestamp")

                        if creation_timestamp:
                            # Parse ISO 8601 timestamp from Kubernetes
                            try:
                                # Convert timestamp to epoch time for comparison
                                creation_time = datetime.fromisoformat(
                                    creation_timestamp.replace("Z", "+00:00")
                                ).timestamp()

                                # Only process jobs created after scheduler startup
                                if (
                                    creation_time > self._startup_time
                                    and self._matches_filter(job)
                                ):
                                    job_name = metadata.get("name", "unknown")
                                    logger.info(
                                        f"[Producer] Queueing newly created job {job_name} for tuning"
                                    )
                                    self._job_queue.put(job)
                            except (ValueError, AttributeError) as e:
                                job_name = metadata.get("name", "unknown")
                                logger.warning(
                                    f"Failed to parse creation timestamp for job {job_name}: {e}"
                                )
                        else:
                            job_name = metadata.get("name", "unknown")
                            logger.error(
                                f"PyTorchJob {job_name} is missing creationTimestamp - this should not happen in a normal Kubernetes cluster"
                            )

            except Exception as e:
                if not self._shutdown_event.is_set():
                    error_message = str(e)
                    if "too old resource version" in error_message:
                        logger.warning(
                            f"[Producer] Resource version too old, resetting: {e}"
                        )
                        # Reset only for "too old resource version" errors
                        resource_version = None
                    else:
                        logger.warning(
                            f"[Producer] Watch disconnected: {e}, reconnecting in 5 seconds..."
                        )
                    time.sleep(5)

        logger.info("[Producer] Shutting down")

    def _matches_filter(self, job: Dict) -> bool:
        """
        Check if a PyTorchJob matches the filter criteria.

        Args:
            job: PyTorchJob dictionary

        Returns:
            True if job matches filter criteria, False otherwise
        """
        metadata = job.get("metadata", {})
        name = metadata.get("name", "")
        namespace = metadata.get("namespace", "")
        labels = metadata.get("labels", {})
        annotations = metadata.get("annotations", {})

        # Check if job has required metadata
        if not name or not namespace:
            return False

        # Skip jobs created by tuning system to prevent recursive tuning
        if annotations.get("zenith-tune/created-by") == "PyTorchJobTuner":
            return False

        # Check namespace pattern
        if self.job_filter.namespace_pattern:
            if not re.match(self.job_filter.namespace_pattern, namespace):
                return False

        # Check exclude namespace pattern
        if self.job_filter.exclude_namespace_pattern:
            if re.match(self.job_filter.exclude_namespace_pattern, namespace):
                return False

        # Check name pattern
        if self.job_filter.name_pattern:
            if not re.match(self.job_filter.name_pattern, name):
                return False

        # Check required labels
        if self.job_filter.labels:
            for key, value in self.job_filter.labels.items():
                if labels.get(key) != value:
                    return False

        # Check required annotations
        if self.job_filter.annotations:
            for key, value in self.job_filter.annotations.items():
                if value is None:
                    # Check for key existence only
                    if key not in annotations:
                        return False
                else:
                    # Check for specific value
                    if annotations.get(key) != value:
                        return False

        return True

    def _get_job_key(self, job: Dict) -> str:
        """
        Generate a unique key for a PyTorchJob.

        Args:
            job: PyTorchJob dictionary

        Returns:
            Unique key string
        """
        metadata = job.get("metadata", {})
        namespace = metadata.get("namespace")
        name = metadata.get("name")
        uid = metadata.get("uid", "")

        return f"{namespace}_{name}_{uid}"

    def _start_tuning_job(self, job: Dict) -> bool:
        """
        Start a tuning job for a specific PyTorchJob using ThreadPoolExecutor.

        Args:
            job: PyTorchJob dictionary to tune

        Returns:
            True if tuning started successfully, False otherwise
        """
        job_key = self._get_job_key(job)
        job_name = job.get("metadata", {}).get("name")

        try:
            logger.info(f"Starting tuning for job {job_name}")

            # Create PyTorchJob object to pass to tuning job
            pytorch_job = PyTorchJob(job)

            # Submit tuning job to thread pool
            future = self.executor.submit(self._run_tuning_job, pytorch_job)

            # Mark as active
            self._active_futures[job_key] = future

            return True

        except Exception as e:
            logger.error(f"Error starting tuning for job {job_name}: {e}")
            return False

    def _run_tuning_job(
        self,
        job: PyTorchJob,
    ) -> None:
        """
        Run the actual tuning job in a separate thread.

        Args:
            job: PyTorchJob object to tune
        """
        # Extract namespace and job_name from the PyTorchJob object
        job_name = job.get_name()
        namespace = job._job_dict.get("metadata", {}).get("namespace", "default")
        logger.info(f"Running tuning for job {job_name} in namespace {namespace}")

        # Extract values from annotation if tuning config values are None
        # Only check annotation if job has tuning config
        has_tuning_config = job.has_tuning_config()

        # Handle n_trials
        n_trials = self.tuning_config.n_trials
        if n_trials is None and has_tuning_config:
            annotation_n_trials = job.get_n_trials()
            if annotation_n_trials is not None:
                n_trials = annotation_n_trials
                logger.info(f"Using n_trials from annotation: {n_trials}")

        if n_trials is not None:
            logger.info(f"Using n_trials: {n_trials}")
        else:
            # Use PyTorchJobTuner's default
            n_trials = 10
            logger.info(f"No n_trials specified, using default: {n_trials}")

        # Handle maximize
        maximize = self.tuning_config.maximize
        if maximize is None and has_tuning_config:
            should_maximize = job.should_maximize()
            if should_maximize is not None:
                maximize = should_maximize
                logger.info(f"Using maximize from annotation: {maximize}")

        if maximize is not None:
            logger.info(f"Using maximize: {maximize}")
        else:
            # Default to minimize if not specified anywhere
            maximize = False
            logger.info("No maximize value specified, defaulting to minimize")

        # Generate study name based on namespace and job name
        study_name = f"tune_{namespace}_{job_name}"

        try:
            tuner = PyTorchJobTuner(
                job_name=job_name,
                get_namespace=namespace,
                submit_namespace=self.submit_namespace,
                output_dir=self.tuning_config.output_dir,
                study_name=study_name,
                sampler=self.tuning_config.sampler,
                maximize=maximize,
                timeout_per_trial=self.tuning_config.timeout_per_trial,
            )
            logger.info(f"Created tuner for job {job_name} in namespace {namespace}")
        except Exception as e:
            logger.error(f"Failed to create tuner for job {job_name}: {e}")
            return

        try:
            # Run optimization
            best_value, best_params = tuner.optimize(
                job_converter=self.tuning_config.job_converter,
                value_extractor=self.tuning_config.value_extractor,
                n_trials=n_trials,
                default_params=self.tuning_config.default_params,
            )

            if best_value is not None:
                logger.info(
                    f"Tuning completed for {job_name}: best_value={best_value}, best_params={best_params}"
                )
            else:
                logger.warning(
                    f"Tuning completed for {job_name} but no valid results found"
                )
        except Exception as e:
            logger.error(f"Error during optimization of job {job_name}: {e}")

    def _cleanup_completed_tuners(self) -> None:
        """Clean up completed tuning futures."""
        completed_keys = [
            key for key, future in self._active_futures.items() if future.done()
        ]

        for key in completed_keys:
            future = self._active_futures[key]
            try:
                # Get result to handle any exceptions
                future.result()
            except Exception as e:
                logger.error(f"Tuning job {key} failed with exception: {e}")

            # Remove from active futures
            del self._active_futures[key]

        if completed_keys:
            logger.debug(f"Cleaned up {len(completed_keys)} completed tuners")

    def _tuning_job_consumer(self):
        """
        Consumer: Process jobs from the queue and start tuning when capacity is available.

        This runs in the main thread and manages concurrent tuning jobs.
        """
        logger.info("Starting tuning job consumer")

        while not self._shutdown_event.is_set():
            # Clean up completed tuners first
            self._cleanup_completed_tuners()

            # Check current active tuner count
            current_active = len(self._active_futures)

            if current_active < self.max_concurrent_tuning:
                try:
                    # Wait for a job from the queue (timeout to allow periodic cleanup)
                    job = self._job_queue.get(timeout=5)

                    job_name = job.get("metadata", {}).get("name")
                    logger.info(f"[Consumer] Processing job {job_name} from queue")
                    self._start_tuning_job(job)

                except queue.Empty:
                    # No jobs in queue, just continue to check for completed tuners
                    pass

            else:
                # At capacity, wait a bit before checking again
                time.sleep(5)

            # Log status periodically
            if current_active > 0 or not self._job_queue.empty():
                logger.debug(
                    f"[Consumer] Active: {current_active}/{self.max_concurrent_tuning}, Queue: {self._job_queue.qsize()}"
                )

        logger.info("[Consumer] Shutting down")

    def run(self):
        """
        Run the scheduler continuously.
        """
        logger.info("Starting PyTorchJob tuning scheduler")
        logger.info(f"Submit namespace: {self.submit_namespace}")
        logger.info(f"Max concurrent tuning: {self.max_concurrent_tuning}")
        if self.job_filter.namespace_pattern:
            logger.info(
                f"Namespace pattern filter: {self.job_filter.namespace_pattern}"
            )
        if self.job_filter.exclude_namespace_pattern:
            logger.info(
                f"Exclude namespace pattern: {self.job_filter.exclude_namespace_pattern}"
            )

        # Start the producer thread
        producer_thread = threading.Thread(
            target=self._tuning_job_producer, daemon=True, name="tuning-job-producer"
        )
        producer_thread.start()

        try:
            # Run the consumer in the main thread
            self._tuning_job_consumer()
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            raise
        finally:
            self.shutdown()

    def shutdown(self):
        """
        Gracefully shutdown the scheduler.

        This will:
        1. Signal all threads to stop
        2. Wait for active tuning jobs to complete
        3. Shutdown the executor
        """
        logger.info("Initiating scheduler shutdown...")

        # Signal all threads to shutdown
        self._shutdown_event.set()

        # Wait for active tuning jobs to complete with a timeout
        logger.info(
            f"Waiting for {len(self._active_futures)} active tuning jobs to complete..."
        )

        # Give tuning jobs some time to complete (e.g., 5 minutes)
        max_wait_time = 300  # 5 minutes
        start_time = time.time()

        while self._active_futures and (time.time() - start_time) < max_wait_time:
            self._cleanup_completed_tuners()
            if self._active_futures:
                logger.info(
                    f"Still waiting for {len(self._active_futures)} jobs to complete..."
                )
                time.sleep(10)

        if self._active_futures:
            logger.warning(
                f"Timeout: {len(self._active_futures)} jobs still running, forcing shutdown"
            )

        # Shutdown the executor
        logger.info("Shutting down ThreadPoolExecutor...")
        self.executor.shutdown(wait=True, cancel_futures=True)

        logger.info("Scheduler shutdown complete")
