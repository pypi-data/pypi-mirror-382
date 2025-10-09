from __future__ import annotations
from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance
from airflow.utils.state import TaskInstanceState

import logging
from listener.utils import create_pipeline_for_dag_run, \
    get_torch_client, end_pipeline_for_dag_run, create_pipeline_for_older_versions, create_job_and_span, \
    end_job_and_span, end_pipeline_for_older_versions, observe_dag_env_variables_detected, \
    ignore_dag_env_variables_detected, should_observe_dag, should_ignore_dag, validate_and_auto_instrument_dag
from listener.constants import INVALID_ENV_SELECTION_MESSAGE

from acceldata_sdk.models.pipeline import PipelineRunResult, PipelineRunStatus

log = logging.getLogger(__name__)


@hookimpl
def on_dag_run_running(dag_run: DagRun, msg: str):
    log.info("Listener Event ==> on_dag_run_running")
    try:
        dag_id = dag_run.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            create_pipeline_for_dag_run(dag_run, get_torch_client(), msg)
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_dag_run_running event : %s", e)


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    log.info("Listener Event ==> on_dag_run_failed")
    try:
        dag_id = dag_run.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            end_pipeline_for_dag_run(dag_run, get_torch_client(), PipelineRunResult.FAILURE, PipelineRunStatus.FAILED,
                                     msg)
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_dag_run_failed event : %s", e)


@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    log.info("Listener Event ==> on_dag_run_success")
    try:
        dag_id = dag_run.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            end_pipeline_for_dag_run(dag_run, get_torch_client(), PipelineRunResult.SUCCESS,
                                     PipelineRunStatus.COMPLETED, msg)
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_dag_run_success event: %s", e)


@hookimpl
def on_task_instance_running(previous_state: TaskInstanceState, task_instance: TaskInstance, session):
    log.info("Listener Event ==> on_task_instance_running")
    log.info("Task instance state: %s", task_instance.state)
    try:
        dag_id = task_instance.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            create_pipeline_for_older_versions(task_instance, session)
            create_job_and_span(task_instance, get_torch_client())
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_task_instance_running event: %s", e)


@hookimpl
def on_task_instance_success(previous_state: TaskInstanceState, task_instance: TaskInstance, session):
    log.info("Listener Event ==> on_task_instance_success")
    log.info("Task instance state: %s", task_instance.state)
    try:
        dag_id = task_instance.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            end_job_and_span(task_instance, get_torch_client())
            log.info("Pushed span to Torch Server for success task")
            # Versions prior to 2.5.0 should end pipeline for task with zero downstream events
            end_pipeline_for_older_versions(task_instance, PipelineRunResult.SUCCESS, PipelineRunStatus.COMPLETED,
                                            session)
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_task_instance_success event: %s", e)


@hookimpl
def on_task_instance_failed(previous_state: TaskInstanceState, task_instance: TaskInstance, session):
    log.info("Listener Event ==> on_task_instance_failed")
    log.info("Task instance state: %s", task_instance.state)
    try:
        dag_id = task_instance.dag_id
        if observe_dag_env_variables_detected() and ignore_dag_env_variables_detected():
            log.error(INVALID_ENV_SELECTION_MESSAGE)
            return

        if validate_and_auto_instrument_dag(dag_id):
            log.info("Observing the DAG with dag_id  %s ", dag_id)
            end_job_and_span(task_instance, get_torch_client())
            log.info("Pushed span to Torch Server for failed task")
            # Versions prior to 2.5.0 should end pipeline for events with zero downstream events or upon failure
            end_pipeline_for_older_versions(task_instance, PipelineRunResult.FAILURE, PipelineRunStatus.FAILED, session)
        else:
            log.info("Instrumentation not enabled for the dag with dag_id %s ", dag_id)
    except Exception as e:
        log.error("Error in on_task_instance_failed event: %s", e)
