from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase, config
from marshmallow import fields


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BuildRecord:
    """
     BuildRecord is a data model class which represents the record of a build.
    """
    target_id: str
    build: str
    build_url: str = field(metadata=config(field_name="build_url"))
    project: str
    outcome: str
    start_date: datetime = field(metadata=config(encoder=datetime.isoformat, decoder=datetime.fromisoformat,
                                                 mm_field=fields.DateTime(format='iso')))
    end_date: datetime = field(metadata=config(encoder=datetime.isoformat, decoder=datetime.fromisoformat,
                                               mm_field=fields.DateTime(format='iso')))
    duration: str
    type: str = "udm.BuildRecord"
    id: str = ""
    server_url: Optional[str] = None
    server_user: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlanRecord:
    """
     PlanRecord is a data model class which represents the record of a plan.
    """
    target_id: str
    ticket: str
    ticket_url: str = field(metadata=config(field_name="ticket_url"))
    title: str
    ticket_type: str
    status: str
    updated_date: datetime = field(metadata=config(encoder=datetime.isoformat, decoder=datetime.fromisoformat,
                                                   mm_field=fields.DateTime(format='iso')))
    type: str = "udm.PlanRecord"
    id: str = ""
    updated_by: Optional[str] = None
    server_url: Optional[str] = None
    server_user: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ItsmRecord:
    """
     ItsmRecord is a data model class which represents the record of IT Service Management.
    """
    target_id: str
    record: str
    record_url: str = field(metadata=config(field_name="record_url"))
    title: str
    status: str
    priority: str
    created_by: str
    type: str = "udm.ItsmRecord"
    id: str = ""
    server_url: Optional[str] = None
    server_user: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CodeComplianceRecord:
    """
     CodeComplianceRecord is a data model class which represents the record of a Security and Compliance.
    """
    target_id: str
    project: str
    project_url: str = field(metadata=config(field_name="project_url"))
    analysis_date: datetime = field(metadata=config(encoder=datetime.isoformat, decoder=datetime.fromisoformat,
                                                    mm_field=fields.DateTime(format='iso')))
    outcome: str
    compliance_data: str
    type: str = "udm.CodeComplianceRecord"
    id: str = ""
    server_url: Optional[str] = None
    server_user: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeploymentRecord:
    """
     DeploymentRecord is a data model class which represents the record of a Deployment.
    """
    target_id: str
    deployment_task: str
    deployment_task_url: str = field(metadata=config(field_name="deploymentTask_url"))
    status: str
    version: str
    type: str = "udm.DeploymentRecord"
    id: str = ""
    application_name: Optional[str] = None
    environment_name: Optional[str] = None
    server_url: Optional[str] = None
    server_user: Optional[str] = None
