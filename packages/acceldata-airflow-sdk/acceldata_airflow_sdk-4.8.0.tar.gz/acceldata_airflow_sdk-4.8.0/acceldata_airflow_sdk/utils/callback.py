from acceldata_sdk.models.pipeline import PipelineRunResult, PipelineRunStatus
from acceldata_airflow_sdk.utils.torch_client import TorchDAGClient
from datetime import datetime

from airflow.models import TaskInstance

from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_airflow_sdk.utils.airflow_job_utils import get_dag_run_pipeline_run_id, CONNECTION_ID

import logging

LOGGER = logging.getLogger(__name__)


# update pipeline with failed status
def on_dag_failure_callback(context):
    """
    Used to update pipeline run with failure status of the corresponding span and end parent span as well. In case of failure it will send failure event as well.
    """
    LOGGER.info("on_dag_failure_callback")
    task: TaskInstance = context.get('task_instance')
    conn_id = task.xcom_pull(key=CONNECTION_ID)
    pipeline_run_id = get_dag_run_pipeline_run_id(task)
    client = TorchDAGClient(conn_id)
    pipeline_run = client.get_pipeline_run(pipeline_run_id=pipeline_run_id)
    parent_span = pipeline_run.get_root_span()
    LOGGER.info("Sending generic event for pipeline root span failure")
    parent_span.send_event(GenericEvent(context_data={'dag_status': 'FAILED', 'time': str(datetime.now())},
                                        event_uid=f'{parent_span.span.uid}.error.event'))
    LOGGER.info("Marking the pipeline root span as failed")
    parent_span.failed(context_data={'dag_status': 'FAILED', 'time': str(datetime.now())})
    pipeline_run.update_pipeline_run(
        context_data={'status': 'failure', 'dag': 'adoc', 'context': str(context)},
        result=PipelineRunResult.FAILURE,
        status=PipelineRunStatus.FAILED
    )


# update pipeline with success status
def on_dag_success_callback(context):
    """
    Used to update pipeline run with success status of the corresponding span and end span parent span
    """
    LOGGER.info("on_dag_success_callback")
    LOGGER.info("Sending generic event for pipeline root span success")
    task: TaskInstance = context.get('task_instance')
    conn_id = task.xcom_pull(key="CONNECTION_ID")
    pipeline_run_id = get_dag_run_pipeline_run_id(task)
    client = TorchDAGClient(conn_id)
    pipeline_run = client.get_pipeline_run(pipeline_run_id=pipeline_run_id)
    parent_span = pipeline_run.get_root_span()
    LOGGER.info("Marking the pipeline root span as successful")
    parent_span.end(context_data={'dag_status': 'SUCCESS', 'time': str(datetime.now())})
    pipeline_run.update_pipeline_run(
        context_data={'status': 'success', 'dag': 'torch', 'context': str(context)},
        result=PipelineRunResult.SUCCESS,
        status=PipelineRunStatus.COMPLETED
    )
    