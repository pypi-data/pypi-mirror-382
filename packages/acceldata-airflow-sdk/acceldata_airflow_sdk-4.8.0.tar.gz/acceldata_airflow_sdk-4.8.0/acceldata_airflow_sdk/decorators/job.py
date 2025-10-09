import functools
import logging
from acceldata_airflow_sdk.utils.airflow_job_utils import create_job_span, log_job_details, get_task_instance, \
    generate_job_uid, handle_span_success, create_context_job, is_span_not_found, create_new_span, \
    handle_span_failure, log_tries

LOGGER = logging.getLogger("airflow.task")


def job(job_uid=None, span_uid=None, inputs=[], outputs=[], metadata=None, xcom_to_event_mapper_ids=None,
        bounded_by_span=True):
    """
    Description:
    Use this decorator to create functional node (job) in your pipeline and crate span for your function inside your
     pipeline.
    :param job_uid: optional job uid of the pipeline. If not provided default job_id will bre created using dagname,
            task_id  and function name of function being wrapped
    :param span_uid: optional uid of the span. If not passed job_uid will get used as span_uid
    :param inputs: input arrays of the task
    :param outputs: output array of the job
    :param metadata: metadata of the job
    :param xcom_to_event_mapper_ids: xcom pull ids that you want to send with span event
    :param bounded_by_span: optional True by default. Set True if you want span to be created for the job as well


    Example:
    @job(job_uid='customer.order.join.job',
        inputs=[Node(asset_uid='POSTGRES_LOCAL_DS.pipeline.pipeline.orders'), Node(asset_uid='POSTGRES_LOCAL_DS.pipeline.pipeline.customers')] ,
        outputs=[Node(asset_uid='POSTGRES_LOCAL_DS.pipeline.pipeline.customer_orders')],
        metadata=JobMetadata('name', 'team', 'code_location'),
        span_uid='customer.orders.datagen.span',
        bounded_by_span=True)
    def function(**context)

    """

    def decorator_job(func):
        @functools.wraps(func)
        def wrapper_job(*args, **kwargs):
            log_job_details(inputs, outputs)
            task_instance = get_task_instance(kwargs, func)
            temp_job_uid = generate_job_uid(func, task_instance, job_uid)
            context_job = create_context_job("decorator", temp_job_uid, "operator", str(func))
            span_uid_temp, kwargs, xcom_context_data = create_job_span(
                task_instance=task_instance,
                job_uid=temp_job_uid,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                context_job=context_job,
                bounded_by_span=bounded_by_span,
                xcom_to_event_mapper_ids=xcom_to_event_mapper_ids,
                span_uid=span_uid,
                kwargs=kwargs
            )
            span_context = kwargs.get('span_context_parent', None)
            try_number = task_instance.try_number
            max_retries = task_instance.task.retries
            log_tries(try_number, max_retries)
            try:
                func(*args, **kwargs)
            except Exception as e:
                handle_span_failure(e, span_context, span_uid_temp, try_number, xcom_context_data, max_retries)
            else:
                handle_span_success(span_context, span_uid_temp, try_number, xcom_context_data)

        return wrapper_job

    return decorator_job
