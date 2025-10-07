import threading
import queue
import datetime
import sys
import time

class Logger:
    """
    An asynchronous logger that writes log messages in a separate thread
    to avoid blocking the main application.

    Supports dynamic, on-the-fly enabling/disabling of logging globally or
    per-tag to minimize performance overhead by replacing methods with no-ops.
    """

    def __init__(self, timestamp_format: str = "%Y-%m-%d %H:%M:%S,%f"):
        """
        Initializes the logger.

        Args:
            timestamp_format: The strftime format for the log timestamps.
        """
        self.log_queue = queue.Queue()
        self.timestamp_format = timestamp_format
        self._stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)

        # --- State for enabling/disabling logs ---
        self._is_enabled = True
        self._disabled_tags = set()

        # Store original methods to allow re-enabling them later.
        self._real_log = self._log_to_queue
        self._real_info = self._info_to_queue
        self._real_warning = self._warning_to_queue
        self._real_error = self._error_to_queue

        # This no-op function will replace real log methods when they are disabled.
        self._nop = lambda *args, **kwargs: None

        # The public methods are pointers that can be swapped.
        # Initially, they point to the real implementations.
        self.log = self._real_log
        self.info = self._real_info
        self.warning = self._real_warning
        self.error = self._real_error
        # --- End of state management ---

    def _worker(self):
        """The target function for the worker thread."""
        while not self._stop_event.is_set() or not self.log_queue.empty():
            try:
                message = self.log_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if message is None:
                continue

            tag, content = message
            timestamp = datetime.datetime.now().strftime(self.timestamp_format)
            log_entry = f"[{timestamp}] [{tag}] {content}"
            
            print(log_entry, file=sys.stdout)
            sys.stdout.flush()
            self.log_queue.task_done()

    # --- Real Logging Implementations ---
    def _log_to_queue(self, tag: str, content: str):
        """The actual implementation that puts a log message into the queue."""
        self.log_queue.put((tag, content))

    def _info_to_queue(self, content: str):
        """The actual implementation for an 'INFO' message."""
        self.log("INFO", content)

    def _warning_to_queue(self, content: str):
        """The actual implementation for a 'WARNING' message."""
        self.log("WARNING", content)

    def _error_to_queue(self, content: str):
        """The actual implementation for an 'ERROR' message."""
        self.log("ERROR", content)

    # --- Public Methods for Controlling Logging ---
    def disable(self):
        """
        Disables all logging globally by replacing the main log method with a no-op.
        This has the highest precedence.
        """
        self._is_enabled = False
        self.log = self._nop

    def enable(self):
        """Enables logging globally and reapplies any tag-specific rules."""
        self._is_enabled = True
        self.log = self._real_log
        self._update_tag_based_methods()

    def disable_tag(self, tag: str):
        """Disables logging for a specific tag (e.g., "INFO"). Case-insensitive."""
        self._disabled_tags.add(tag.upper())
        self._update_tag_based_methods()

    def enable_tag(self, tag: str):
        """Enables logging for a specific tag. Case-insensitive."""
        self._disabled_tags.discard(tag.upper())
        self._update_tag_based_methods()
    
    def _update_tag_based_methods(self):
        """
        Internal helper to assign real or no-op methods based on the current
        state of _disabled_tags and the global enabled flag.
        """
        if not self._is_enabled:
            return

        # Update the .info() method
        self.info = self._nop if "INFO" in self._disabled_tags else self._real_info
        # Update the .warning() method
        self.warning = self._nop if "WARNING" in self._disabled_tags else self._real_warning
        # Update the .error() method
        self.error = self._nop if "ERROR" in self._disabled_tags else self._real_error

    # --- Lifecycle Methods ---
    def start(self):
        """Starts the logging worker thread."""
        self.worker_thread.start()

    def shutdown(self):
        """
        Signals the worker thread to stop and waits for it to finish
        processing all messages in the queue.
        """
        self.log_queue.join()
        self._stop_event.set()
        self.worker_thread.join()

    def __enter__(self):
        """Starts the logger when entering a 'with' block."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Shuts down the logger when exiting a 'with' block."""
        self.shutdown()

