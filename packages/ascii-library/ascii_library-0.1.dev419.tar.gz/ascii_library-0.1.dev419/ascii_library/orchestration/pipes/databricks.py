import os
import sys
import time
from typing import Any, Dict, List, Mapping, Optional

from dagster import (
    OpExecutionContext,
    PipesContextInjector,
    PipesMessageReader,
    ResourceParam,
    get_dagster_logger,
    open_pipes_session,
)
from dagster._core.pipes.client import PipesClientCompletedInvocation  # type: ignore
from dagster_databricks import (
    PipesDbfsContextInjector,
    PipesDbfsLogReader,
    PipesDbfsMessageReader,
)
from dagster_pipes import PipesExtras
from dagster_shared.check.functions import bool_param, opt_inst_param
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from mypy_boto3_resourcegroupstaggingapi import ResourceGroupsTaggingAPIClient
from pydantic import Field

from ascii_library.orchestration.pipes.cloud_client import _PipesBaseCloudClient
from ascii_library.orchestration.pipes.exceptions import CustomPipesException


class _PipesDatabricksClient(_PipesBaseCloudClient):
    """Pipes client for databricks.

    Args:
        client (WorkspaceClient): A databricks `WorkspaceClient` object.
        env (Optional[Mapping[str,str]]: An optional dict of environment variables to pass to the
            databricks job.
        context_injector (Optional[PipesContextInjector]): A context injector to use to inject
            context into the k8s container process. Defaults to :py:class:`PipesDbfsContextInjector`.
        message_reader (Optional[PipesMessageReader]): A message reader to use to read messages
            from the databricks job. Defaults to :py:class:`PipesDbfsMessageReader`.
        poll_interval_seconds (float): How long to sleep between checking the status of the job run.
            Defaults to 5.
        forward_termination (bool): Whether to cancel the Databricks job if the orchestration process
            is interrupted or canceled. Defaults to True.
    """

    env: Optional[Mapping[str, str]] = Field(
        default=None,
        description="An optional dict of environment variables to pass to the subprocess.",
    )

    def __init__(
        self,
        client: WorkspaceClient,
        tagging_client: ResourceGroupsTaggingAPIClient,
        context_injector: Optional[PipesContextInjector] = None,
        message_reader: Optional[PipesMessageReader] = None,
        forward_termination: bool = True,
    ):
        super().__init__(
            main_client=client,
            context_injector=context_injector,
            message_reader=message_reader,
            tagging_client=tagging_client,
        )
        self.client = client
        self.context_injector = opt_inst_param(
            context_injector,
            "context_injector",
            PipesContextInjector,
        ) or PipesDbfsContextInjector(client=self.client)
        self.message_reader = opt_inst_param(
            message_reader,
            "message_reader",
            PipesMessageReader,
        )
        self.forward_termination = bool_param(
            forward_termination, "forward_termination"
        )

    @classmethod
    def _is_dagster_maintained(cls) -> bool:
        return False

    def get_default_message_reader(
        self, task: jobs.SubmitTask
    ) -> "PipesDbfsMessageReader":
        # include log readers if the user is writing their logs to DBFS
        if (
            task.as_dict()
            .get("new_cluster", {})
            .get("cluster_log_conf", {})
            .get("dbfs", None)
        ):
            log_readers = [
                PipesDbfsLogReader(
                    client=self.client,
                    remote_log_name="stdout",
                    target_stream=sys.stdout,
                ),
                PipesDbfsLogReader(
                    client=self.client,
                    remote_log_name="stderr",
                    target_stream=sys.stderr,
                ),
            ]
        else:
            log_readers = None
        return PipesDbfsMessageReader(
            client=self.client,
            log_readers=log_readers,
        )

    def _prepare_environment(
        self,
        local_file_path: str,
        dbfs_path: str,
        libraries_to_build_and_upload: Optional[List[str]],
    ) -> None:
        """Prepare the environment by uploading files and ensuring libraries are available."""
        self._upload_file_to_cloud(
            local_file_path=local_file_path, cloud_path=dbfs_path
        )
        self.filesystem = "s3"
        self._ensure_library_on_cloud(
            libraries_to_build_and_upload=libraries_to_build_and_upload
        )

    def _process_submit_args(
        self, submit_args: Optional[Mapping[str, Any]]
    ) -> Dict[str, Any]:
        """Process submit_args to ensure they are of the allowed types."""
        if not submit_args:
            return {}

        allowed_types = (
            list,
            jobs.JobEmailNotifications,
            jobs.GitSource,
            jobs.JobsHealthRules,
            jobs.JobNotificationSettings,
            jobs.QueueSettings,
            int,
            jobs.WebhookNotifications,
        )
        submit_kwargs = {}
        for key, value in submit_args.items():
            if isinstance(value, allowed_types):
                submit_kwargs[key] = value
            else:
                raise TypeError(f"Unexpected type for submit_arg {key}: {type(value)}")
        return submit_kwargs

    def run(  # type: ignore
        self,
        *,
        env: Optional[Mapping[str, str]] = None,
        context: OpExecutionContext,
        extras: Optional[PipesExtras] = None,
        task: jobs.SubmitTask,
        submit_args: Optional[Mapping[str, str]] = None,
        local_file_path: str,
        dbfs_path: str,
        libraries_to_build_and_upload: Optional[List[str]] = None,
    ) -> PipesClientCompletedInvocation:
        """Synchronously execute a Databricks job with the pipes protocol.

        Args:
            task (databricks.sdk.service.jobs.SubmitTask): Specification of the databricks
                task to run. Environment variables used by dagster-pipes will be set under the
                `spark_env_vars` key of the `new_cluster` field (if there is an existing dictionary
                here, the EXT environment variables will be merged in). Everything else will be
                passed unaltered under the `tasks` arg to `WorkspaceClient.jobs.submit`.
            context (OpExecutionContext): The context from the executing op or asset.
            extras (Optional[PipesExtras]): An optional dict of extra parameters to pass to the
                subprocess.
            submit_args (Optional[Mapping[str, str]]): Additional keyword arguments that will be
                forwarded as-is to `WorkspaceClient.jobs.submit`.

        Returns:
            PipesClientCompletedInvocation: Wrapper containing results reported by the external
                process.
        """
        self._prepare_environment(
            local_file_path, dbfs_path, libraries_to_build_and_upload
        )
        submit_kwargs = self._process_submit_args(submit_args)

        message_reader = self.message_reader or self.get_default_message_reader(task)
        with open_pipes_session(
            context=context,
            extras=extras,
            context_injector=self.context_injector,
            message_reader=message_reader,
        ) as pipes_session:
            submit_task_dict = task.as_dict()
            ascii_wandb_value = {"ASCII_WANDB": os.environ.get("ASCII_WANDB", "")}
            if not ascii_wandb_value:
                get_dagster_logger().warning(
                    "Environment variable 'ASCII_WANDB' is not set; defaulting to empty value."
                )
            submit_task_dict["new_cluster"]["spark_env_vars"] = {
                **submit_task_dict["new_cluster"].get("spark_env_vars", {}),
                **(env or {}),
                **pipes_session.get_bootstrap_env_vars(),
                **ascii_wandb_value,
            }
            task = jobs.SubmitTask.from_dict(submit_task_dict)
            run_id = self.client.jobs.submit(
                run_name=extras.get("job_name"),  # type: ignore
                tasks=[task],
                **(submit_kwargs or {}),
            ).bind()["run_id"]
            context.log.info(
                f"Databricks url: {self.client.jobs.get_run(run_id).run_page_url}"
            )
            try:
                self._poll_till_success(
                    run_id=run_id, extras=extras, tagging_client=self._tagging_client
                )
            except CustomPipesException:
                if self.forward_termination:
                    context.log.info(
                        "[pipes] execution interrupted, canceling Databricks job."
                    )
                    self.client.jobs.cancel_run(run_id)
                    self._poll_til_terminating(run_id)
                raise
        return PipesClientCompletedInvocation(pipes_session)

    def _poll_til_terminating(self, run_id: str) -> None:
        # Wait to see the job enters a state that indicates the underlying task is no longer executing
        # TERMINATING: "The task of this run has completed, and the cluster and execution context are being cleaned up."
        run_id_int = int(run_id)
        while True:
            run = self.client.jobs.get_run(run_id_int)
            if (
                run
                and run.state
                and run.state.life_cycle_state
                in (
                    jobs.RunLifeCycleState.TERMINATING,
                    jobs.RunLifeCycleState.TERMINATED,
                    jobs.RunLifeCycleState.SKIPPED,
                    jobs.RunLifeCycleState.INTERNAL_ERROR,
                )
            ):
                return

            time.sleep(self.poll_interval_seconds)


PipesDatabricksEnhancedClient = ResourceParam[_PipesDatabricksClient]
