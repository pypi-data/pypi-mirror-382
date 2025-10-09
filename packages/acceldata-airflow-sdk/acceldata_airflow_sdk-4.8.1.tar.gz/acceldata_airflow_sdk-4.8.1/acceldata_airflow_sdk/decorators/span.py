import functools
import logging
from acceldata_airflow_sdk.utils.torch_client import TorchDAGClient
from acceldata_airflow_sdk.utils.airflow_job_utils import PIPELINE_UID_XCOM, get_dag_run_pipeline_run_id, CONNECTION_ID, \
    get_task_instance, pull_xcom_data, is_span_not_found, send_span_start_generic_event, create_new_span, \
    generate_span_uid, handle_span_failure, handle_span_success, fetch_xcom_data, log_tries

from acceldata_sdk.errors import APIError

LOGGER = logging.getLogger("airflow.task")


def span(span_uid=None, associated_job_uids=None, xcom_to_event_mapper_ids=None):
    """
    Description:
        Used to decorate function for which you need span in side your pipeline. Just decorate your function with `span`
    :param xcom_to_event_mapper_ids: xcom pull ids that you want to send with span event
    :param associated_job_uids: list of string
    :param span_uid: uid of the span

    Example:

    @span(span_uid='customer.orders.datagen.span')
    def function(**context)

    """

    def decorator_span(func):
        @functools.wraps(func)
        def wrapper_span(*args, **kwargs):
            span_context, xcom_context_data, try_number, temp_span_uid, max_retries, pipeline_run = None, None, None, None, None, None
            try:
                LOGGER.info("Sending Span Start Event")
                task_instance = get_task_instance(kwargs, func)
                pipeline_uid_ = pull_xcom_data(task_instance, PIPELINE_UID_XCOM)
                conn_id = pull_xcom_data(task_instance, CONNECTION_ID)
                xcoms = xcom_to_event_mapper_ids
                try_number = task_instance.try_number
                max_retries = task_instance.task.retries
                log_tries(try_number, max_retries)
                parent_span_context = pull_xcom_data(task_instance, 'parent_span_context')
                if parent_span_context is None:
                    LOGGER.debug('Sending new request to ADOC Pipeline service to get parent span context')
                    client = TorchDAGClient(conn_id)
                    pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
                    parent_span_context = client.get_root_span(pipeline_uid=pipeline_uid_,
                                                               pipeline_run_id=pipeline_run_id)
                    pipeline = client.get_pipeline(pipeline_uid_)
                    pipeline_run = pipeline.get_run(pipeline_run_id)
                    # task_instance.xcom_push(key="parent_span_context", value=parent_span_context)
                else:
                    LOGGER.debug('using xcom to get parent span context to send span event')
                associated_job_uids_with_span = associated_job_uids
                if span_uid is None:
                    temp_span_uid = generate_span_uid(func, task_instance, span_uid)
                else:
                    temp_span_uid = span_uid
                try:
                    span_context = pipeline_run.get_span(temp_span_uid)
                    LOGGER.info("Span already exists with child_span_uid : %s . Not creating the span again.",
                                temp_span_uid)
                    # No need to create a span, emit generic events related to the retry here
                    send_span_start_generic_event(span_context, try_number, span_uid, xcoms)
                except APIError as e:
                    LOGGER.warning("APIError : %s", e)
                    if is_span_not_found(e):
                        LOGGER.info("Span does not exist with child_span_uid : %s. Creating new child span. ",
                                    temp_span_uid)
                        span_context = create_new_span(parent_span_context, temp_span_uid, xcoms, try_number,
                                                       associated_job_uids_with_span)
                xcom_context_data = {}
                if xcoms is None:
                    xcoms = []
                else:
                    for key in xcoms:
                        value = task_instance.xcom_pull(key=key)
                        if value is not None:
                            xcom_context_data[key] = value
                kwargs['span_context_parent'] = span_context
                LOGGER.info('Xcom context data %s', xcom_context_data)
                func(*args, **kwargs)
            except Exception as e:
                handle_span_failure(e, span_context, span_uid, try_number, xcom_context_data, max_retries)
            else:
                handle_span_success(span_context, span_uid, try_number, xcom_context_data)

        return wrapper_span

    return decorator_span
