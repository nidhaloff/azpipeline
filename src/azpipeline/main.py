#!/usr/bin/env python3

__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""

import os
import sys
from dataclasses import dataclass
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Optional, Tuple, Union

from azpipeline.config import Config
from azpipeline.libs.utils import write_json
from azpipeline.log import logger
from azpipeline.models import PipelineSummary

try:
    from azure.devops.connection import Connection
    from azure.devops.released.build import BuildClient
    from azure.devops.v7_1.build.models import Build, Timeline, TimelineRecord
    from msrest import Serializer
    from msrest.authentication import BasicAuthentication
except ImportError:
    print("Make sure azure-devops is installed")


@dataclass
class AzurePipeline(Connection):
    build_id: str
    token: str = os.getenv("AZURE_PIPELINES_TOKEN", None)
    organization_url: str = ""
    project: str = ""
    save_logs: bool = False
    logs_dir: Path = Config.ADO_LOGS_DIR

    def __post_init__(self):
        if not self.build_id:
            logger.error(
                f"Something wrong with the BuildId: {self.build_id}. Please provide an existent one."
            )
            sys.exit(1)

        if not self.token:
            logger.error(
                """
            Azure Pipeline token not found. Please set the AZURE_PIPELINES_TOKEN environment variable.
            If you are running this locally, you need to create a pipeline token on AzureDevops, make sure your token has the right permissions
            and then set the value to AZURE_PIPELINES_TOKEN.
            export AZURE_PIPELINES_TOKEN=<your_access_token>
            """
            )
            sys.exit(1)

        credentials = BasicAuthentication("", self.token)
        super().__init__(base_url=self.organization_url, creds=credentials)

        # Client object to interface with azure devops builds
        self._build_client: BuildClient = self.clients.get_build_client()

        # Get the current pipeline build
        self._build_pipeline: Build = self._build_client.get_build(
            build_id=self.build_id, project=self.project
        )

        # Serializer object (used for object to dict/json conversion)
        self._serializer: Serializer = self._build_client._serialize

    @property
    def build_url(self):
        """Get the url of the current pipeline."""
        try:
            return self._build_pipeline._links.additional_properties["web"]["href"]
        except KeyError as err:
            logger.error(f"Build url not found!\nERROR: {err}")
            sys.exit(1)

    @property
    def branch_name(self):
        return self._build_pipeline.source_branch

    @property
    def commit_id(self):
        return self._build_pipeline.source_version

    @property
    def build_triggered_by(self):
        return self._build_pipeline.requested_by.display_name

    @property
    def name(self):
        return self._build_pipeline.definition.name

    @property
    def result(self):
        return self._build_pipeline.result

    @property
    def status(self):
        return self._build_pipeline.status

    @property
    def summary(self) -> PipelineSummary:
        """Get an overview of important/useful infos about the pipeline."""
        return PipelineSummary(
            name=self.name,
            build_id=self.build_id,
            result=self.result,
            status=self.status,
            url=self.build_url,
            branch=self.branch_name,
            commit_id=self.commit_id,
            triggered_by=self.build_triggered_by,
        )

    def _serialize(self, obj):
        """Serialize custom object/instance into dict/json"""
        return self._serializer.serialize_object(obj)

    def get_timeline(self, build_id: Optional[str] = None) -> Timeline:
        """Get timeline of an azure devops pipeline

        Args:
            build_id (Optional[str], optional): build_id of an azure pipeline. If None, current build_id will be used

        Returns:
            Timeline: Timeline of the azure pipeline
        """

        # Use build_id for the current pipeline if not custom one is provided
        if not build_id:
            build_id = self.build_id

        logger.info(f"Getting timeline for pipeline with Build id = {build_id}")
        timeline: Timeline = self._build_client.get_build_timeline(
            build_id=build_id, project=self.project
        )
        if not timeline:
            logger.error("Timeline not found")
            sys.exit(1)

        if self.save_logs:
            write_json(
                output_path=Path(self.logs_dir, "timeline.json"),
                obj=self._serialize(timeline),
            )

        return timeline

    def get_failed_tasks(self, timeline: Timeline) -> List[TimelineRecord]:
        """Get failed tasks from the whole pipeline timeline

        Args:
            timeline (Timeline): Timeline of the azure pipeline

        Returns:
            List[TimelineRecord]: List of failed/errored pipeline tasks
        """

        logger.debug("Getting all failed tasks for ado pipeline...")
        failed_tasks = []
        for record in timeline.records:
            if record.result == "failed" and record.type == "Task":
                failed_tasks.append(record)

        if self.save_logs:
            write_json(
                output_path=Path(self.logs_dir, "failed_tasks.json"),
                obj=self._serialize(failed_tasks),
            )

        logger.debug(
            f"Failed tasks have been extracted successfully -> length={len(failed_tasks)}"
        )
        return failed_tasks

    def get_failed_tasks_logs(self, timeline: Timeline) -> Tuple[dict, dict]:
        """Get logs for failed tasks (that failed during the pipeline execution)

        Args:
            failed_tasks (List[TimelineRecord]): List of failed/errored pipeline tasks

        Returns:
            Tuple[dict, dict]: dict task_name to log, dict task_name to metadata
        """

        logger.debug("Getting all logs for failed tasks in ado pipeline...")
        failed_tasks: List[TimelineRecord] = self.get_failed_tasks(timeline=timeline)
        logs = {}
        metadata = {}

        for task in failed_tasks:
            task_metadata = {}
            log_id = task.log.id

            # Get logs of the failed pipeline task
            task_log = self._build_client.get_build_log_lines(
                project=self.project, build_id=self.build_id, log_id=log_id
            )
            logs[task.name] = task_log

            # Extract the issue messages of a task, if exist.
            task_metadata["issues"] = [d.message for d in task.issues]
            logger.info(
                f"searching parent for: {task.name} with parent_id: {task.parent_id}"
            )

            for record in timeline.records:
                if record.type == "Job" and record.id == task.parent_id:
                    task_metadata["parent"] = record.name
            metadata[task.name] = task_metadata

        if self.save_logs:
            write_json(output_path=Path(self.logs_dir, "tasks_logs.json"), obj=logs)
            write_json(
                output_path=Path(self.logs_dir, "tasks_metadata.json"), obj=metadata
            )

        logger.debug(f"Logs have been extracted successfully -> length={len(logs)}")
        return logs, metadata

    def get_previous_builds(self):
        """Return a list of previous builds

        Returns:
            _type_: _description_
        """

        builds = self._build_client.get_builds(
            self.project,
            definitions=[self._build_pipeline.definition.id],
            branch_name=self._build_pipeline.source_branch,
            query_order="startTimeDescending",
        )

        list_builds = []
        if builds.value:
            for past_build in builds.value:
                list_builds.append(past_build.id)

        logger.info(f"List of builds {list_builds}")
        if len(list_builds) > 1:
            build_index = list_builds.index(self._build_pipeline.id)
            if build_index + 1 < len(list_builds):
                return list_builds[build_index + 1]
            else:
                return None
        return None

    def failed_jobs(self, build_id: Optional[str] = None) -> Union[list, dict]:
        """Get list of failed jobs during the pipeline execution.
        This returns a dict with the failed job names as values.
        It is meant more for debugging purposes

        Args:
            build_id (Optional[str], optional): build_id of an azure pipeline. If None, current build_id will be used

        Returns:
            Union[list, dict]: list of error jobs/stages names during the pipeline execution
        """

        # Use current build_id if not custom id was provided
        if not build_id:
            build_id = self.build_id

        timeline = self.get_timeline(build_id)
        failed_job_records = {}
        list_errors = []

        for record in timeline.records:
            if record.result == "failed" and record.type == "Job":
                if record.type not in failed_job_records:
                    failed_job_records[record.type] = []

                failed_job_records[record.type].append(record)
                logger.info(f"failed_job_records: {failed_job_records}")

        # Create a section for each error
        if "Job" in failed_job_records:
            for record in failed_job_records["Job"]:
                error = {
                    "stage": "JobStageErrors",
                    "job": record.name,
                }
                if error not in list_errors:
                    list_errors.append(error)

        if len(list_errors) > 0:
            # Display data grouped by stage
            group_list = {}
            for key, value in groupby(list_errors, key=itemgetter("stage")):
                jobs = []
                group_list[key] = {}
                for k in value:
                    if k["job"] not in jobs:
                        jobs.append(k["job"])
                group_list[key]["jobs"] = sorted(jobs)
            return group_list
        else:
            return list_errors

    def compare_with_prev_build(
        self, prev_build, curr_build: Optional[str] = None
    ) -> str:
        """Compare two builds. Generally the current build with the previous one

        Args:
            prev_build (_type_): previous build_id
            curr_build (Optional[str], optional): current build_id. If None, the current will be used

        Returns:
            str: feedback message that shows comparison of current build with the previous one
        """
        # Set curr_build to the current build_id if no custom one is provided
        if not curr_build:
            curr_build = self.build_id

        logger.info(
            f"Compare previous build: {prev_build} to current build: {curr_build}"
        )

        curr_error = self.get_list_of_errors(curr_build)
        logger.info(f"Current  builds errors: {curr_error}")
        # previous error sometimes is empty
        if prev_build:
            prev_error = self.get_list_of_errors(prev_build)
        else:
            prev_error = {}
        logger.info(f"Previous builds errors: {prev_error}")

        logger.info(f"Current error ={len(curr_error)}")
        logger.info(f"Previous error ={len(prev_error)}")

        message = None

        if len(curr_error) == 0 and len(prev_error) > 0:
            message = "back to normal"

        if len(curr_error) > 0 and len(prev_error) > 0:
            if curr_error == prev_error:
                message = "repeated failure"
            else:
                message = "new failure!"

        if len(curr_error) > 0 and len(prev_error) == 0:
            message = "new failure!"

        logger.info(f"Out message ={message}")
        return message
