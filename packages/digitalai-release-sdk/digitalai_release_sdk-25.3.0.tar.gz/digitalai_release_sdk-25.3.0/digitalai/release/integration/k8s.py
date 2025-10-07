import threading

from kubernetes import client, config
from kubernetes.client import CoreV1Api
from kubernetes.config.config_exception import ConfigException
from .logger import dai_logger

kubernetes_client: CoreV1Api = None
lock = threading.Lock()


def get_client():
    global kubernetes_client

    if not kubernetes_client:
        with lock:
            if not kubernetes_client:
                try:
                    #dai_logger.info("Attempting to load in-cluster config")
                    config.load_incluster_config()
                    #dai_logger.info("Successfully loaded in-cluster config")
                except ConfigException:
                    #dai_logger.warning("In-cluster config failed, attempting default load_config")
                    try:
                        config.load_config()
                        #dai_logger.info("Successfully loaded config using load_config")
                    except Exception:
                        dai_logger.exception("Failed to load any Kubernetes config")
                        raise RuntimeError("Could not configure Kubernetes client")
                kubernetes_client = client.CoreV1Api()
                #dai_logger.info("Kubernetes client created successfully")

    return kubernetes_client


def split_secret_resource_data(secret_entry: str) -> tuple:
    split = secret_entry.split(":")
    if len(split) != 3:
        return "", "", ""
    return tuple(split)
