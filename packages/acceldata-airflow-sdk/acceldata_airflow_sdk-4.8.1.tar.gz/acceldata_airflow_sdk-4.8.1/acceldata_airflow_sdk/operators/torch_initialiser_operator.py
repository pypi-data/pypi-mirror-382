from datetime import datetime
from airflow.models.baseoperator import BaseOperator
from urllib import parse
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_sdk.models.pipeline import CreatePipeline, PipelineMetadata, PipelineSourceType
from acceldata_sdk.torch_client import TorchClient
from acceldata_sdk.api_version_utils import APIVersionUtils
from acceldata_airflow_sdk.initialiser import torch_credentials
from acceldata_airflow_sdk.utils.torch_client import TorchDAGClient
from acceldata_airflow_sdk.utils.airflow_job_utils import PIPELINE_UID_XCOM, is_pipeline_run_ended, CONNECTION_ID
from semantic_version import Version, SimpleSpec
import logging


LOGGER = logging.getLogger("airflow.task")

def check_if_pipeline_exists(pipeline_uid: str, client):
    try:
        pipeline = client.get_pipeline(pipeline_uid=pipeline_uid)
        LOGGER.info('check_if_pipeline_exists:: pipeline:  %s ', pipeline)
        return True
    except Exception as e:
        LOGGER.warn('check_if_pipeline_exists:: pipeline: False -> ERROR : %s ', str(e))
        return False


class TorchInitializer(BaseOperator):
    template_fields = ['continuation_id']
    """
    You need to add task with given operator at the root of your dag. It will create new pipeline run for your dag run.
    You need to add it as a root of the dag.

    You need to add 6 additional parameters pipeline_uid, pipeline_name, create_pipeline, span_name, continuation_id, meta.
    Other parameters will be same as std airflow base operator's parameters

    """

    def __init__(self, *, pipeline_uid, pipeline_name=None, create_pipeline=True, span_name=None, continuation_id=None,
                 meta: PipelineMetadata = None, connection_id=None, **kwargs):
        """
        You need to add 6 additional parameters pipeline_uid, pipeline_name, create_pipeline, span_name, continuation_id, meta.
        Other parameters will be same as std airflow base operator's parameters

        :param pipeline_uid: (String) uid of the pipeline given in torch
        :param pipeline_name: (String) name of the pipeline given in torch
        :param create_pipeline: (bool) optional False If pipeline, pipeline_run and root span has already been created
            before running Airflow DAG
        :param continuation_id continuation_id of the pipeline run
        :param span_name: (String) optional Custom root span name. If nothing is passed pipeline_uid.span is used as name
        :param meta: (PipelineMetadata) meta data of the pipeline
        :param connection_id connection_id of the connection from where credentials need to be used. If this is None credential will be used from environment variable
        """
        super().__init__(**kwargs)
        self.pipeline_name = pipeline_name
        self.pipeline_uid = pipeline_uid
        self.continuation_id = continuation_id
        self.create_pipeline = create_pipeline
        self.span_name = span_name
        self.connection_id = connection_id
        self.meta = meta
        if self.meta is None:
            self.meta = PipelineMetadata(owner='sdk/pipeline-user', team='TORCH', codeLocation='...')

    def execute(self, context):
        task_instance = context['ti']
        # Make the key unique by appending UUID
        task_instance.xcom_push(key=PIPELINE_UID_XCOM, value=self.pipeline_uid)
        task_instance.xcom_push(key=CONNECTION_ID, value=self.connection_id)

        if self.create_pipeline:
            pipeline_name_ = self.pipeline_uid
            if self.pipeline_name is not None:
                pipeline_name_ = self.pipeline_name
            LOGGER.info('Creating new pipeline with passed uid :: %s',self.pipeline_uid)
            torch_client = TorchClient(**torch_credentials(self.connection_id))
            pipeline = CreatePipeline(
                    uid=self.pipeline_uid,
                    name=pipeline_name_,
                    description=f'The pipeline {pipeline_name_} has been created from acceldata-airflow-sdk',
                    meta=self.meta,
                    context={'pipeline_uid': self.pipeline_uid, 'pipeline_name': pipeline_name_},
                    sourceType=PipelineSourceType.AIRFLOW
            )
            pipeline_res = torch_client.create_pipeline(pipeline=pipeline)
            LOGGER.info('pipeline id :: %s', pipeline_res.id)
            if self.continuation_id is not None:
                LOGGER.info(f'Creating new pipeline run with passed continuation_id :: %s {self.continuation_id}.')
                pipeline_run = pipeline_res.create_pipeline_run(continuation_id=self.continuation_id)
            else:
                pipeline_run = pipeline_res.create_pipeline_run()
            task_instance.xcom_push(key=f'{task_instance.dag_id}_pipeline_run_id', value=pipeline_run.id)
            if self.span_name:
                span_name_ = self.span_name
            else:
                span_name_ = f'{self.pipeline_uid}.span'
            parent_span_context = pipeline_run.create_span(uid=span_name_)
        else:
            client = TorchDAGClient(self.connection_id)
            if self.continuation_id is not None:
                LOGGER.info('Using precreated pipeline with continuation_id :: %s ', self.continuation_id)
                pipeline = client.get_pipeline(self.pipeline_uid)
                pipeline_run = client.get_pipeline_run(continuation_id=self.continuation_id, pipeline_id=pipeline.id)
                if is_pipeline_run_ended(pipeline_run):
                    raise Exception("Please provide continuation_id of active pipeline run")
            else:
                LOGGER.info('Using latest pipeline run.')
                pipeline_run = client.get_latest_pipeline_run(self.pipeline_uid)
                if is_pipeline_run_ended(pipeline_run):
                    raise Exception("Latest pipeline run is in terminal state. Please make sure latest pipeline run is not completed")
            parent_span_context = client.get_root_span(pipeline_uid=self.pipeline_uid,
                                                       pipeline_run_id=pipeline_run.id)
            task_instance.xcom_push(key=f'{task_instance.dag_id}_pipeline_run_id', value=pipeline_run.id)
            LOGGER.info('Using precreated pipeline with pipeline uid :: %s ', self.pipeline_uid)
        try:
            log_url = list({context.get('task_instance').log_url})
            list_ = list(log_url)
            url = list_[0]
            parsed = parse.urlsplit(url)
            query = parse.parse_qs(parse.urlsplit(url).query)
            dag_id = query['dag_id'][0]
            execution_date = query['execution_date'][0]
            encoded_time = parse.quote(execution_date)
            dagrun_url = parsed.scheme + '://' + parsed.netloc + '/graph?root=&dag_id=' + dag_id + '&execution_date=' + encoded_time + '&arrang=LR'
            parent_span_context.send_event(GenericEvent(
                context_data={
                    'dag_id': dag_id,
                    'time': str(datetime.now()),
                    'url': dagrun_url,
                    'execution_time': execution_date
                },
                event_uid='AIRFLOW.DETAILS')
            )
        except:
            pass

