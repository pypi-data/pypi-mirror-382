import os
import threading

from kubernetes import watch
from .logger import dai_logger
from digitalai.release.integration import k8s


def start_input_context_watcher(on_input_context_update_func):
    dai_logger.info("Input context watcher started")

    stop = threading.Event()

    try:
        start_input_secret_watcher(on_input_context_update_func, stop)
    except Exception:
        dai_logger.error("Unexpected error occurred.", exc_info=True)
        return

    # Wait until the watcher is stopped
    stop.wait()


def start_input_secret_watcher(on_input_context_update_func, stop):
    dai_logger.info("Input secret watcher started")

    kubernetes_client = k8s.get_client()
    field_selector = "metadata.name=" + os.getenv("INPUT_CONTEXT_SECRET")
    namespace = os.getenv("RUNNER_NAMESPACE")
    old_session_key = None

    w = watch.Watch()
    for event in w.stream(kubernetes_client.list_namespaced_secret, namespace, field_selector=field_selector):
        secret = event['object']
        new_session_key = secret.data.get("session-key")

        # Checking if 'session-key' field has changed
        if old_session_key and old_session_key != new_session_key:
            dai_logger.info("Detected input context value change")
            on_input_context_update_func()

        # Set old session-key value
        old_session_key = new_session_key

        # Check if the watcher should be stopped
        if stop.is_set():
            break
