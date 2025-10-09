from acceldata_airflow_sdk.utils.torch_client import TorchDAGClient
from acceldata_sdk.models.job import CreateJob, JobMetadata
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_sdk.errors import APIError
import json
from datetime import datetime
import logging

LOGGER = logging.getLogger(__name__)
PIPELINE_UID_XCOM = 'pipeline_uid_ff069534-5069-45b1-b737-aea6229db4bf'
CONNECTION_ID = 'CONNECTION_ID'


def get_dag_run_pipeline_run_id(task_instance):
    return task_instance.xcom_pull(key=f'{task_instance.dag_id}_pipeline_run_id')


def create_job_span(task_instance, job_uid, inputs, outputs, metadata, context_job, bounded_by_span,
                    xcom_to_event_mapper_ids, span_uid, kwargs):
    local_span_context = None
    span_uid_temp = None
    xcom_context_data = None
    try:
        xcom_context_data = {}
        span_uid_temp = span_uid
        conn_id = pull_xcom_data(task_instance, CONNECTION_ID)
        pipeline_uid_ = pull_xcom_data(task_instance, PIPELINE_UID_XCOM)
        client = TorchDAGClient(conn_id)
        pipeline = client.get_pipeline(pipeline_uid_)
        pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
        pipeline_run = pipeline.get_run(pipeline_run_id)
        LOGGER.info("Creating job")
        job = create_job(pipeline, job_uid, inputs, outputs, metadata, context_job, pipeline_run)
    except Exception as e:
        handle_job_creation_failure(e)
    else:
        LOGGER.info("Successfully created job.")
        if bounded_by_span:
            LOGGER.info('Sending Span Start event')
            try:
                xcoms = xcom_to_event_mapper_ids
                parent_span_context = pull_xcom_data(task_instance, "parent_span_context")
                if parent_span_context is None:
                    LOGGER.debug('Sending new request to ADOC Pipeline service to get parent span context')
                    parent_span_context = client.get_root_span(pipeline_uid=pipeline_uid_)
                else:
                    LOGGER.debug('Using xcom to get parent span context to send span event')
                associated_job_uids = [job_uid]
                if span_uid is None:
                    span_uid_temp = job_uid
                try_number = task_instance.try_number
                # 3. Handle the case when the span already exists (retry)
                try:
                    local_span_context = pipeline_run.get_span(span_uid_temp)
                    LOGGER.info("Span already exists with child_span_uid : %s . Not creating the span again.",
                                span_uid_temp)
                    # No need to create a span, emit generic events related to the retry here
                    send_span_start_generic_event(local_span_context, try_number, span_uid, xcoms)
                except APIError as e:
                    LOGGER.warn("APIError : %s", e)
                    if is_span_not_found(e):
                        LOGGER.info("Span does not exist with child_span_uid : %s. Creating new child span. ",
                                    span_uid_temp)
                        local_span_context = create_new_span(parent_span_context, span_uid_temp, xcoms, try_number,
                                                             associated_job_uids)
                if xcoms is None:
                    xcoms = []
                else:
                    xcom_context_data = fetch_xcom_data(xcoms, task_instance)
                    LOGGER.info('Xcom context data :: %s ', xcom_context_data)
                kwargs['span_context_parent'] = local_span_context
            except Exception as ex:
                LOGGER.error(f'Span creation failed with exception: {str(ex)}')
    return span_uid_temp, kwargs, xcom_context_data


def is_pipeline_run_ended(pipeline_run):
    if pipeline_run.status == "COMPLETED" or pipeline_run.status == "FAILED" or pipeline_run.status == "ABORTED":
        return True


def log_job_details(inputs, outputs):
    LOGGER.info(f"Job inputs: {inputs}")
    LOGGER.info(f"Job outputs: {outputs}")


def log_tries(task_try_number, max_retries):
    LOGGER.info("try_number inside task failure/success callback %s", task_try_number)
    LOGGER.info("max_retries %s", max_retries)


def handle_job_creation_failure(e):
    LOGGER.error("Error in creating job")
    exception = e.__dict__
    LOGGER.error(exception)
    raise e


def get_task_instance(kwargs, func):
    if kwargs is None or kwargs.get('ti', None) is None:
        raise Exception(f'Please pass context to function:  {str(func.__name__)}')
    return kwargs['ti']


def generate_job_uid(func, task_instance, job_uid):
    if job_uid is None:
        fname_six = '{:.6}'.format(func.__name__)
        job_uid = f'{task_instance.task_id}_{fname_six}'
    return job_uid


def generate_job_operator_uid(operator_name, task_id):
    opame_six = '{:.6}'.format(operator_name)
    job_uid = f'{task_id}_{opame_six}'
    return job_uid


def generate_span_uid(func, task_instance, span_uid):
    if span_uid is None:
        fname_six = '{:.6}'.format(func.__name__)
        span_uid = f'{task_instance.task_id}_{fname_six}.span'
    return span_uid


def generate_span_operator_uid(operator_name, task_id):
    opame_six = '{:.6}'.format(operator_name)
    span_uid = f'{task_id}_{opame_six}.span'
    return span_uid


def create_context_job(type, job_uid, function_key, func_value):
    return {
        'job': 'adoc_job_' + type,
        'time': str(datetime.now()),
        'uid': job_uid,
        function_key: str(func_value)
    }


def handle_span_failure(e, temp_span_context, span_uid, try_number, xcom_context_data, retries):
    LOGGER.error("Handling task failure event")
    exception = e.__dict__
    LOGGER.error(exception)
    if temp_span_context is not None:
        send_span_failure_generic_event(temp_span_context, try_number, span_uid, e)
        # Only end the span if this is the final try
        if try_number > retries:
            LOGGER.info("Sending Span Failed event for the last attempt")
            temp_span_context.failed(context_data=xcom_context_data)
        raise e
    else:
        LOGGER.warning("SpanContext is unavailable. Not able to send Span failure generic event.")


def handle_span_success(temp_span_context, span_uid_temp, try_number, xcom_context_data):
    LOGGER.info("Sending Span End event with status Success")
    if temp_span_context is not None:
        send_span_success_generic_event(temp_span_context, try_number, span_uid_temp)
        temp_span_context.end(context_data=xcom_context_data)
    else:
        LOGGER.warning("SpanContext is unavailable. Not able to send Span Success generic event.")


def send_span_success_generic_event(temp_span_context, try_number, span_uid_temp):
    event_uid = f'{span_uid_temp}.job.end.try_{try_number}.event'
    job_end_event = GenericEvent(context_data={
        'time': str(datetime.now()),
        'try_number': try_number
    }, event_uid=event_uid)
    LOGGER.info("Sending job end event %s for the child span with span_uid %s", job_end_event, span_uid_temp)
    temp_span_context.send_event(job_end_event)


def send_span_start_generic_event(temp_span_context, try_number, span_uid, xcoms=[]):
    LOGGER.info("Sending Span start generic event")
    event_uid = f'{span_uid}.job.start.try_{try_number}.event'
    job_start_event = GenericEvent(context_data={
        'time': str(datetime.now()),
        'try_number': try_number,
        'xcom_to_event_mapper_ids': xcoms},
        event_uid=event_uid)
    LOGGER.info("Sending job retry start event %s for the child span with span_uid %s", job_start_event,
                span_uid)
    temp_span_context.send_event(job_start_event)
    LOGGER.info("Successfully sent job start retry event for the child span with child_span_uid %s",
                span_uid)


def send_span_failure_generic_event(temp_span_context, try_number, span_uid, e):
    LOGGER.debug("Sending Span failure generic event")
    event_uid = f'{span_uid}.job.failed.try_{try_number}.event'
    job_failed_event = GenericEvent(context_data={
        'status': 'error',
        'error_data': str(e),
        'time': str(datetime.now()),
        'try_number': try_number,
        'exception_type': str(type(e).__name__)
    }, event_uid=event_uid)
    temp_span_context.send_event(job_failed_event)


def fetch_xcom_data(xcoms, task_instance):
    xcom_context_data = {}
    for key in xcoms:
        value = pull_xcom_data(task_instance, key)
        if value is not None:
            xcom_context_data[key] = value
    return xcom_context_data


def pull_xcom_data(task_instance, key):
    return task_instance.xcom_pull(key=key)


def initialize_torch_client(task_instance):
    conn_id = pull_xcom_data(task_instance, CONNECTION_ID)
    return TorchDAGClient(conn_id)


def get_pipeline_and_run(client, task_instance):
    pipeline_uid = pull_xcom_data(task_instance, PIPELINE_UID_XCOM)
    pipeline = client.get_pipeline(pipeline_uid)
    pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
    pipeline_run = pipeline.get_run(pipeline_run_id)
    return pipeline, pipeline_run


def create_job(pipeline, job_uid, inputs, outputs, metadata, context_job, pipeline_run):
    job = CreateJob(
        uid=job_uid,
        name=f'{job_uid} Job',
        pipeline_run_id=pipeline_run.id,
        description=f'{job_uid} created using adoc job decorator',
        inputs=inputs,
        outputs=outputs,
        meta=metadata,
        context=context_job
    )
    return pipeline.create_job(job)


def create_new_span(parent_span_context, span_uid_temp, xcoms, try_number, associated_job_uids):
    LOGGER.info("Creating new span with span_uid %s", span_uid_temp)
    temp_span_context = parent_span_context.create_child_span(
        uid=span_uid_temp,
        context_data={
            'time': str(datetime.now()),
            'xcom_to_event_mapper_ids': xcoms,
            'try_number': try_number
        },
        associatedJobUids=associated_job_uids
    )
    send_span_start_generic_event(temp_span_context, try_number, span_uid_temp, xcoms)
    return temp_span_context


def is_span_not_found(e):
    try:
        error_details = json.loads(e.args[0])
        if error_details.get("errors"):
            for error in error_details["errors"]:
                message = error.get("message", "")
                if "not found" in message.lower() and error.get("status") == 404:
                    return True
        return False
    except:
        return False
