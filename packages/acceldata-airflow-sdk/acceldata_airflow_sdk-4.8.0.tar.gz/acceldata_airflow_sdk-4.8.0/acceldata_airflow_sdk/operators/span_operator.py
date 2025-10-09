from airflow.models.baseoperator import BaseOperator
from acceldata_airflow_sdk.utils.torch_client import TorchDAGClient
from acceldata_airflow_sdk.utils.airflow_job_utils import PIPELINE_UID_XCOM, get_dag_run_pipeline_run_id, CONNECTION_ID, \
    create_job_span, log_job_details, get_task_instance, \
    generate_job_uid, handle_span_success, create_context_job, is_span_not_found, create_new_span, \
    handle_span_failure, fetch_xcom_data, send_span_start_generic_event, log_tries, generate_span_operator_uid, \
    pull_xcom_data
from acceldata_sdk.errors import APIError
import logging

LOGGER = logging.getLogger("airflow.task")


class SpanOperator(BaseOperator):
    """
    Description:
        Used to send span start and end event for any std airflow operator. Just wrap your operator with span operator.
        Make sure you do not add your task in dag(dag parameter should not be specified in the operator being wrapped by
         span operator). If you wrap it using span operator, will take care of that task operator.

    You need to add extra parameter mentioned below. Other parameters will be same as std airflow base operator's parameters

    :param operator: std task operator defined
    :param span_uid: span uid for the task
    :param associated_job_uids: list of job uids
    :param xcom_to_event_mapper_ids: list of xcom keys. Used to send xcom variables in span event job

    """

    def __init__(self, *, operator: BaseOperator, span_uid: str = None, associated_job_uids=None,
                 xcom_to_event_mapper_ids=None, **kwargs):
        """
        You need to add extra parameter mentioned below. Other parameters will be same as std airflow base operator's parameters
        :param operator: std task operator defined
        :param span_uid: span uid for the task
        :param associated_job_uids: list of job uids
        :param xcom_to_event_mapper_ids: list of xcom keys. Used to send xcom variables in span event
        Example :

        --> Defined std operator.

        postgres_operator = PostgresOperator(
            task_id="task_name",
            postgres_conn_id='example_db',
            sql="select * from information_schema.attributes",
        )


        --> To wrap operator with span. Write assign this to your dag (not your std operator)

        span_operator = SpanOperator(
            task_id='task_name',
            span_uid='span.uid',
            operator=postgres_operator,
            dag=dag
        )

        """
        if kwargs.get("provide_context"):
            kwargs.pop('provide_context', None)
        super().__init__(**kwargs)
        self.operator = operator
        self.pipeline_uid = None
        self.span_uid = span_uid
        self.parent_span_ctxt = None
        if associated_job_uids is None:
            self.associated_job_uids = []
        else:
            self.associated_job_uids = associated_job_uids
        self.xcom_to_event_mapper_ids = xcom_to_event_mapper_ids
        self.span_context = None

    def execute(self, context):
        xcom_context_data, pipeline_run, try_number, max_retries, child_span_context = (None, None, None, None, None)
        try:
            LOGGER.info("Send span start event")
            task_instance = context['ti']
            parent_span_context = pull_xcom_data(task_instance, 'parent_span_context')
            conn_id = pull_xcom_data(task_instance, CONNECTION_ID)
            try_number = task_instance.try_number
            max_retries = task_instance.task.retries
            log_tries(try_number, max_retries)
            if parent_span_context is None:
                LOGGER.debug('Sending new request to ADOC pipeline service to get parent span context')
                self.pipeline_uid = pull_xcom_data(task_instance, PIPELINE_UID_XCOM)
                client = TorchDAGClient(conn_id)
                pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
                pipeline = client.get_pipeline(self.pipeline_uid)
                pipeline_run = pipeline.get_run(pipeline_run_id)
                self.parent_span_ctxt = client.get_root_span(pipeline_uid=self.pipeline_uid,
                                                             pipeline_run_id=pipeline_run_id)
                # task_instance.xcom_push(key="parent_span_context", value=self.parent_span_ctxt.__dict__)
            else:
                LOGGER.debug('using xcom to get parent span context to send span event')
                self.parent_span_ctxt = parent_span_context
            if self.span_uid is None:
                LOGGER.debug("Span Uid is None. Generating span uid")
                self.span_uid = generate_span_operator_uid(type(self.operator).__name__, task_instance.task_id)
                LOGGER.debug("Generated Span uid : %s", self.span_uid)

            # Add the logic to check if the span already exists or not and create a new span if span doesn't exist
            try:
                LOGGER.info("Checking if span already exists with the child_span_uid :: %s", self.span_uid)
                child_span_context = pipeline_run.get_span(self.span_uid)
                LOGGER.info("Span already exists with the child_span_uid : %s . Not creating the span again.",
                            self.span_uid)
                # No need to create a span, emit generic events related to the retry here
                send_span_start_generic_event(child_span_context, try_number, self.span_uid)
            except APIError as e:
                if is_span_not_found(e):
                    LOGGER.info("Span does not exist with child_span_uid : %s. Creating new child span. ",
                                self.span_uid)
                    child_span_context = create_new_span(self.parent_span_ctxt, self.span_uid, None, try_number,
                                                         self.associated_job_uids)

            self.span_context = child_span_context
            LOGGER.debug("Span context : %s", self.span_context)
            context['span_context_parent'] = self.span_context
            xcom_context_data = {}
            if self.xcom_to_event_mapper_ids is None:
                self.xcom_to_event_mapper_ids = []
            else:
                for key in self.xcom_to_event_mapper_ids:
                    value = task_instance.xcom_pull(key=key)
                    if value is not None:
                        xcom_context_data[key] = value
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
            LOGGER.error("Exception : %s", e)
            handle_span_failure(e, self.span_context, self.span_uid, try_number, xcom_context_data, max_retries)
        else:
            handle_span_success(self.span_context, self.span_uid, try_number, xcom_context_data)

    def set_downstream(self, task_or_task_list) -> None:
        super().set_downstream(task_or_task_list)

    def set_upstream(self, task_or_task_list) -> None:
        super().set_upstream(task_or_task_list)
