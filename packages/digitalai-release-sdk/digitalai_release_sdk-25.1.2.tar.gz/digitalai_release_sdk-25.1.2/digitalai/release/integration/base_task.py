import logging
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict

from .input_context import AutomatedTaskAsUserContext
from .output_context import OutputContext
from .exceptions import AbortException
from .logger import dai_logger
from digitalai.release.release_api_client import ReleaseAPIClient


class BaseTask(ABC):
    """
    An abstract base class representing a task that can be executed.
    """

    def __init__(self):
        self.task_id = None
        self.release_context = None
        self.release_server_url = None
        self.input_properties = None
        self.output_context = None

    def execute_task(self) -> None:
        """
        Executes the task by calling the execute method. If an AbortException is raised during execution,
        the task's exit code is set to 1 and the program exits with a status code of 1. If any other exception
        is raised, the task's exit code is also set to 1.
        """
        try:
            self.output_context = OutputContext(0, "", {}, [])
            self.execute()
        except AbortException:
            dai_logger.info("Abort requested")
            self.set_exit_code(1)
            self.set_error_message("Abort requested")
            sys.exit(1)
        except Exception as e:
            dai_logger.error("Unexpected error occurred", exc_info=True)
            self.set_exit_code(1)
            self.set_error_message(str(e))

    @abstractmethod
    def execute(self) -> None:
        """
        This is an abstract method that must be implemented by subclasses of BaseTask. It represents the main
        logic of the task.
        """
        pass

    def abort(self) -> None:
        """
        Sets the task's exit code to 1 and exits the program with a status code of 1.
        """
        self.set_exit_code(1)
        sys.exit(1)

    def get_output_context(self) -> OutputContext:
        """
        Returns the OutputContext object associated with the task.
        """
        return self.output_context

    def get_output_properties(self) -> Dict[str, Any]:
        """
        Returns the output properties dictionary of the task's OutputContext object.
        """
        return self.output_context.output_properties

    def get_input_properties(self) -> Dict[str, Any]:
        """
        Returns the input properties dictionary of the task
        """
        if not self.input_properties:
            raise ValueError(f"Input properties have not been set")
        return self.input_properties

    def set_output_property(self, name: str, value: Any) -> None:
        """
        Sets the name and value of an output property of the task
        """
        if not name:
            raise ValueError("Output property name cannot be empty")

        accepted_data_types = (str, int, list, dict, bool)

        if value and not isinstance(value, accepted_data_types):
            raise ValueError(
                f"Invalid data type for value '{value}' in name '{name}' in set_output_property. Accepted data types "
                f"are: str, int, list, dict, bool")

        self.output_context.output_properties[name] = value

    def set_exit_code(self, value) -> None:
        """
        Sets the exit code of the task's OutputContext object.
        """
        self.output_context.exit_code = value

    def set_error_message(self, value) -> None:
        """
        Sets the error message of the task's OutputContext object.
        """
        self.output_context.job_error_message = value

    def add_comment(self, comment: str) -> None:
        """
        Logs a comment of the task.
        """
        dai_logger.debug(f"##[start: comment]{comment}##[end: comment]")

    def set_status_line(self, status_line: str) -> None:
        """
        Set the status of the task.
        """
        dai_logger.debug(f"##[start: status]{status_line}##[end: status]")

    def add_reporting_record(self, reporting_record: Any) -> None:
        """
        Adds a reporting record to the OutputContext
        """
        self.output_context.reporting_records.append(reporting_record)

    def get_release_server_url(self) -> str:
        """
        Returns the Release server URL of the associated task
        """
        return self.release_server_url

    def get_task_user(self) -> AutomatedTaskAsUserContext:
        """
        Returns the user details that are executing the task.
        """
        return self.release_context.automated_task_as_user

    def get_release_id(self) -> str:
        """
        Returns the Release ID of the task
        """
        return self.release_context.id

    def get_task_id(self) -> str:
        """
        Returns the Task ID of the task
        """
        return self.task_id

    def get_release_api_client(self) -> ReleaseAPIClient:
        """
        Returns a ReleaseAPIClient object with default configuration based on the task.
        """
        self._validate_api_credentials()
        return ReleaseAPIClient(self.get_release_server_url(),
                                self.get_task_user().username,
                                self.get_task_user().password)

    def _validate_api_credentials(self) -> None:
        """
        Validates that the necessary credentials are available for connecting to the Release API.
        """
        if not all([
            self.get_release_server_url(),
            self.get_task_user().username,
            self.get_task_user().password
        ]):
            raise ValueError(
                "Cannot connect to Release API without server URL, username, or password. "
                "Make sure that the 'Run as user' property is set on the release."
            )



