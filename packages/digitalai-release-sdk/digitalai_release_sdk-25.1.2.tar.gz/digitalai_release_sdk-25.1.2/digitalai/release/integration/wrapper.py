from __future__ import annotations

import ast
import base64
import importlib
import json
import os
import signal
import sys
import time

import requests
import urllib3

from digitalai.release.integration import k8s, watcher
from .base_task import BaseTask
from .input_context import InputContext
from .job_data_encryptor import AESJobDataEncryptor, NoOpJobDataEncryptor
from .logger import dai_logger
from .masked_io import MaskedIO
from .output_context import OutputContext

# Mask the standard output and error streams by replacing them with MaskedIO objects.
masked_std_out: MaskedIO = MaskedIO(sys.stdout)
masked_std_err: MaskedIO = MaskedIO(sys.stderr)
sys.stdout = masked_std_out
sys.stderr = masked_std_err

# input and output context file location
input_context_file: str = os.getenv('INPUT_LOCATION', '')
output_context_file: str = os.getenv('OUTPUT_LOCATION', '')
base64_session_key: str = os.getenv('SESSION_KEY', '')
release_server_url: str = os.getenv('RELEASE_URL', '')
callback_url: str = os.getenv('CALLBACK_URL', '')
input_context_secret: str = os.getenv('INPUT_CONTEXT_SECRET', '')
result_secret_key: str = os.getenv('RESULT_SECRET_NAME', '')
runner_namespace: str = os.getenv('RUNNER_NAMESPACE', '')
execution_mode: str = os.getenv('EXECUTOR_EXECUTION_MODE', '')

input_context: InputContext = None

size_of_1Mb = 1024 * 1024

# Create the encryptor
def get_encryptor():
    if base64_session_key:
        encryptor = AESJobDataEncryptor(base64_session_key)
    else:
        encryptor = NoOpJobDataEncryptor()
    return encryptor


# Initialize the global task object
dai_task_object: BaseTask = None


def abort_handler(signum, frame):
    """
    This function handles the abort request by calling the abort method on the global task object, if it exists.
    If the task object does not exist, it logs a message and exits with a status code of 1.
    """
    dai_logger.info("Received SIGTERM to gracefully stop the process")
    global dai_task_object

    if dai_task_object:
        dai_task_object.abort()
    else:
        dai_logger.info("Abort requested")
        sys.exit(1)


# Register abort handler
signal.signal(signal.SIGTERM, abort_handler)


def get_task_details():
    """
    Get the task details by reading the input context file or fetching from secret, decrypting the contents using the encryptor,
    and parsing the JSON data into an InputContext object. Then, set the secrets for the masked standard output
    and error streams, build the task properties from the InputContext object.
    """
    dai_logger.info("Preparing for task properties")
    if input_context_file:
        dai_logger.info("Reading input context from file")
        with open(input_context_file) as data_input:
            input_content = data_input.read()
        #dai_logger.info("Successfully loaded input context from file")
    else:
        k8s_client = k8s.get_client()
        dai_logger.info("Reading input context from secret")
        secret =k8s_client.read_namespaced_secret(input_context_secret, runner_namespace)
        #dai_logger.info("Successfully loaded input context from secret")
        global base64_session_key, callback_url
        base64_session_key = base64.b64decode(secret.data["session-key"])
        callback_url = base64.b64decode(secret.data["url"])

        input_content = secret.data["input"]
        if not input_content or len(input_content) == 0:
            fetch_url_base64 = secret.data["fetchUrl"]
            if not fetch_url_base64 or len(fetch_url_base64) == 0:
                raise ValueError("Cannot find fetch URL for task")

            fetch_url_bytes = base64.b64decode(fetch_url_base64)
            fetch_url = base64.b64decode(fetch_url_bytes).decode("UTF-8")
            try:
                response = requests.get(fetch_url)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                dai_logger.error("Failed to fetch data.", exc_info=True)
                raise e

            if response.status_code != 200:
                raise ValueError(f"Failed to fetch data, server returned status: {response.status_code}")

            input_content = response.content
        else:
            input_content = base64.b64decode(input_content)

    decrypted_json = get_encryptor().decrypt(input_content)
    #dai_logger.info("Successfully decrypted input context")
    global input_context
    input_context = InputContext.from_dict(json.loads(decrypted_json))

    secrets = input_context.task.secrets()
    if input_context.release and input_context.release.automated_task_as_user and input_context.release.automated_task_as_user.password:
        secrets.append(input_context.release.automated_task_as_user.password)
    masked_std_out.secrets = secrets
    masked_std_err.secrets = secrets
    task_properties = input_context.task.build_locals()
    return task_properties, input_context.task.type


def update_output_context(output_context: OutputContext):
    """
    Update the output context file or secret by converting the output context object to a dictionary, serializing the
    dictionary to a JSON string, encrypting the string using the encryptor, and writing the encrypted string
    to the output context file or secret and pushing to callback URL.
    """
    output_content = json.dumps(output_context.to_dict())
    encrypted_json = get_encryptor().encrypt(output_content)
    try:
        if output_context_file:
            dai_logger.info("Writing output context to file")
            with open(output_context_file, "w") as data_output:
                data_output.write(encrypted_json)
        if result_secret_key:
            dai_logger.info("Writing output context to secret")
            if len(encrypted_json) >= size_of_1Mb:
                dai_logger.warning("Result size exceeds 1Mb and is too big to store in secret")
            else:
                namespace, name, key = k8s.split_secret_resource_data(result_secret_key)
                secret = k8s.get_client().read_namespaced_secret(name, namespace)
                secret.data[key] = encrypted_json
                k8s.get_client().replace_namespaced_secret(name, namespace, secret)
        if callback_url:
            dai_logger.info("Pushing result using HTTP")
            url = base64.b64decode(callback_url).decode("UTF-8")
            try:
                urllib3.PoolManager().request("POST", url, headers={'Content-Type': 'application/json'},
                                              body=encrypted_json)
            except Exception:
                if should_retry_callback_request(encrypted_json):
                    dai_logger.error("Cannot finish Callback request.", exc_info=True)
                    dai_logger.info("Retry flag was set on Callback request, retrying until successful...")
                    retry_push_result_infinitely(encrypted_json)
                else:
                    raise

    except Exception:
        dai_logger.error("Unexpected error occurred.", exc_info=True)


def retry_push_result_infinitely(encrypted_json):
    """
    Keeps retrying to push encrypted data to the callback URL with exponential backoff, capping at 3 minutes.
    Callback URL is re-fetched from input context secret since it will change when remote-runner restarts.
    """
    retry_delay = 1
    max_backoff = 180
    backoff_factor = 2.0

    while True:
        try:
            # If we can't read the secret, we should fail fast
            secret = k8s.get_client().read_namespaced_secret(input_context_secret, runner_namespace)
        except Exception:
            raise

        try:
            callback_url = base64.b64decode(secret.data["url"])
            url = base64.b64decode(callback_url).decode("UTF-8")
            response = urllib3.PoolManager().request("POST", url, headers={'Content-Type': 'application/json'}, body=encrypted_json)
            return response
        except Exception as e:
            dai_logger.warning(f"Cannot finish retried Callback request: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * backoff_factor, max_backoff)


def should_retry_callback_request(encrypted_data):
    """
    Checks if callback request should be retried on failure.
    It should be retried when result is too big for Secret and Output File handler is not used.
    """
    return len(encrypted_data) >= size_of_1Mb and len(input_context_file) == 0


def execute_task(task_object: BaseTask):
    """
    Execute the given task object by setting it as the global task object and starting its execution.
    If an exception is raised during execution, log the error. Finally, update the output context file
    using the output context of the task object.
    """
    global dai_task_object
    try:
        dai_task_object = task_object
        dai_logger.info("Starting task execution")
        dai_task_object.execute_task()
    except Exception:
        dai_logger.error("Unexpected error occurred.", exc_info=True)
    finally:
        update_output_context(dai_task_object.get_output_context())


def find_class_file(root_dir, class_name):
    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                with open(filepath) as file:
                    node = ast.parse(file.read())
                    classes = [n.name for n in node.body if isinstance(n, ast.ClassDef)]
                    if class_name in classes:
                        return filepath
    return None


def run():
    try:
        # Get task details, parse the script file to get the task class, import the module,
        # create an instance of the task class, and execute the task
        task_props, task_type = get_task_details()
        task_class_name = task_type.split(".")[1]
        class_file_path = find_class_file(os.getcwd(), task_class_name)
        if not class_file_path:
            raise ValueError(f"Could not find the {task_class_name} class")
        module_name = class_file_path.replace(os.getcwd() + os.sep, '')
        module_name = module_name.replace(".py", "").replace(os.sep, ".")
        module = importlib.import_module(module_name)
        task_class = getattr(module, task_class_name)
        task_obj = task_class()
        task_obj.input_properties = task_props
        task_obj.release_server_url = release_server_url.strip('/')
        task_obj.release_context = input_context.release
        task_obj.task_id = input_context.task.id
        execute_task(task_obj)
    except Exception as e:
        # Log the error and update the output context file with exit code 1 if an exception is raised
        dai_logger.error("Unexpected error occurred.", exc_info=True)
        update_output_context(OutputContext(1, str(e), {}, []))
    finally:
        if execution_mode == "daemon":
            watcher.start_input_context_watcher(run)


if __name__ == "__main__":
    run()
