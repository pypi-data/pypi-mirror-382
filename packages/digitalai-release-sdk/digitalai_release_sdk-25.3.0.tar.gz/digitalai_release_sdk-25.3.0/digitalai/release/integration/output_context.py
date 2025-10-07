from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class OutputContext:
    """
    A context for the output of the task execution.

    Attributes:
        exit_code (int): The exit code of the command.
        job_error_message (str): The job error message.
        output_properties (Dict[str, Any]): A dictionary of output properties.
        reporting_records (List[Dict[str, Any]]): A list of reporting records.
    """
    exit_code: int
    job_error_message: str
    output_properties: Dict[str, Any]
    reporting_records: List[Dict[str, Any]]

