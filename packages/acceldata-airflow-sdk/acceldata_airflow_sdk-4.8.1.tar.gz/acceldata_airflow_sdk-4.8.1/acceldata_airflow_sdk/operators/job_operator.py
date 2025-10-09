from datetime import datetime
from airflow.models.baseoperator import BaseOperator
from acceldata_airflow_sdk.utils.airflow_job_utils import create_job_span, log_job_details, get_task_instance, \
    generate_job_uid, handle_span_success, create_context_job, is_span_not_found, create_new_span, \
    handle_span_failure, create_context_job, generate_job_operator_uid, log_tries
import logging

LOGGER = logging.getLogger("airflow.task")


class JobOperator(BaseOperator):
    """
    Description:
        Used to create Job and send span start and end event for any std airflow operator. Just wrap your operator with
        Job operator. Make sure you do not add your task in dag(dag parameter should not be specified in the
        operator being wrapped by job operator). If you wrap it using Job operator, will take care of that task
         operator.

    You need to add extra parameter mentioned below. Other parameters will be same as std airflow base operator's
     parameters

    :param operator: std task operator defined
    :param job_uid: optional job uid of the pipeline. If not provided default job_id will bre created using dagname,
        task_id of the base operator and operator name of base operator being wrapped
    :param inputs: input arrays of the task
    :param outputs: output array of the job
    :param metadata: metadata of the job
    :param span_uid: span uid for the task. If not passed job_uid will get used as span_uid
    :param xcom_to_event_mapper_ids: list of xcom keys. Used to send xcom variables in span event job
    :param bounded_by_span: optional True if you want to create a span for the current task
    """

    def __init__(self, *, operator: BaseOperator, inputs=[], outputs=[], job_uid: str = None, metadata=None,
                 span_uid: str = None,
                 xcom_to_event_mapper_ids=None, bounded_by_span=True, **kwargs):
        """
        You need to add extra parameter mentioned below. Other parameters will be same as std airflow base operator's parameters
        :param operator: std task operator defined
        :param job_uid: optional job uid of the pipeline. If not provided default job_id will bre created using dagname,
            task_id of the base operator and operator name of base operator being wrapped
        :param inputs: input arrays of the task
        :param outputs: output array of the job
        :param metadata: optional metadata of the job
        :param span_uid: optional span uid for the task. If not passed job_uid will get used as span_uid
        :param xcom_to_event_mapper_ids: list of xcom keys. Used to send xcom variables in span event
        :param bounded_by_span: optional True if you want to create a span for the current task
        Example :

        --> Defined std operator.

        postgres_operator = PostgresOperator(
            task_id="task_name",
            postgres_conn_id='example_db',
            sql="select * from information_schema.attributes",
        )


        --> To create Job and wrap operator with span. Assign this to your dag (not your std operator)

        job_operator = JobOperator(
            task_id='task_name',
            job_uid='customer.order.join.job',
            inputs=[Node('POSTGRES_LOCAL_DS.pipeline.pipeline.orders'), Node('POSTGRES_LOCAL_DS.pipeline.pipeline.customers')] ,
            outputs=[Node('POSTGRES_LOCAL_DS.pipeline.pipeline.customer_orders')],
            metadata=JobMetadata('name', 'team', 'code_location'),
            span_uid='span.uid',
            operator=postgres_operator,
            dag=dag,
            bounded_by_span=True
        )

        """
        if kwargs.get("provide_context"):
            kwargs.pop('provide_context', None)
        super().__init__(**kwargs)
        self.operator = operator
        self.pipeline_uid = None
        self.job_uid = job_uid
        self.span_uid = span_uid
        self.inputs = inputs
        self.outputs = outputs
        self.metadata = metadata
        self.xcom_to_event_mapper_ids = xcom_to_event_mapper_ids
        self.parent_span_ctxt = None
        self.span_context = None
        self.bounded_by_span = bounded_by_span

    def execute(self, context):
        xcom_context_data = None
        context_job = create_context_job("operator", self.job_uid, "operator", str(self.operator))
        task_instance = context['ti']
        if self.job_uid is None:
            self.job_uid = generate_job_operator_uid(type(self.operator).__name__, self.operator.task_id)
        self.span_uid, context, xcom_context_data = create_job_span(
            task_instance=task_instance,
            job_uid=self.job_uid,
            inputs=self.inputs,
            outputs=self.outputs,
            metadata=self.metadata,
            context_job=context_job,
            bounded_by_span=self.bounded_by_span,
            xcom_to_event_mapper_ids=self.xcom_to_event_mapper_ids,
            span_uid=self.span_uid,
            kwargs=context
        )
        self.span_context = context.get('span_context_parent', None)
        try_number = task_instance.try_number
        max_retries = task_instance.task.retries
        log_tries(try_number, max_retries)
        try:
            try:
                self.operator.prepare_for_execution().execute(context)
            except Exception as e1:
                if type(e1) == AttributeError:
                    try:
                        self.operator.execute(context)
                    except Exception as e2:
                        LOGGER.error(e2)
                        raise e2
                else:
                    LOGGER.error(e1)
                    raise e1
        except Exception as e:
            LOGGER.error("Send span end failure event")
            exception = e.__dict__
            LOGGER.error(exception)
            if self.span_context is not None:
                handle_span_failure(e, self.span_context, self.span_uid, try_number, xcom_context_data, max_retries)
        else:
            handle_span_success(self.span_context, self.span_uid, try_number, xcom_context_data)

    def set_downstream(self, task_or_task_list) -> None:
        super().set_downstream(task_or_task_list)

    def set_upstream(self, task_or_task_list) -> None:
        super().set_upstream(task_or_task_list)
