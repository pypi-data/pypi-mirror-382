from datetime import datetime, timedelta
# from airflow import DAG
import datetime
from acceldata_sdk.models.job import CreateJob, JobMetadata, Node
from acceldata_sdk.models.pipeline import PipelineMetadata
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_airflow_sdk.dag import DAG
from airflow.operators.python import PythonOperator
from acceldata_airflow_sdk.decorators.job import job
from acceldata_airflow_sdk.decorators.span import span
from acceldata_airflow_sdk.operators.torch_initialiser_operator import TorchInitializer
import os

os.environ["no_proxy"] = "*"

job_metadata = JobMetadata('sangeeta@acceldata.io', 'DR', ' Data Pipeline')
pipeline_uid = "span_deco_success_dag_0_retries"
pipeline_name = "span_deco_success_dag_0_retries"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


@job(job_uid='get_config',
     inputs=[],
     outputs=[Node(job_uid="process_data")],
     metadata=job_metadata,
     span_uid='get_config.span')
def get_config(**context):
    config = {
        'param1': 'value1',
        'param2': 'value2'
    }
    return config


@span(span_uid='process_data.span',
      associated_job_uids=['process_data'], xcom_to_event_mapper_ids=['run_id', 'event_id'])
def process_data(**context):
    processed_data = {
        'param1': 'processed_value1',
        'param2': 'processed_value2'
    }
    return processed_data


default_args = {
    "owner": "Sangeeta Airflow", 'retries': 0, "retry_delay": timedelta(minutes=2), "depends_on_past": False,
    "email": ["sangeeta@accceldata.io"], "email_on_failure": False, "email_on_retry": False
}

dag = DAG(
    dag_id="span_deco_success_dag_0_retries", catchup=False, default_args=default_args,
    schedule=None, description="Reviews Data Pipeline",
    max_active_runs=2, start_date=datetime.datetime(2024, 4, 24), tags=["ad-pipeline-example"]
)

# Initialize ADOC
torch_initializer_task = TorchInitializer(
    task_id='torch_pipeline_initializer',
    pipeline_uid=pipeline_uid,
    pipeline_name=pipeline_name,
    dag=dag,
    # Torch connection id goes here
    connection_id='acceldata-poc',
    # optional root span: span_name=pipeline_uid + '_' + 'root_span',
    meta=PipelineMetadata(owner='Demo', team='demo_team', codeLocation='...')
)

config_task = PythonOperator(
    task_id='config_task',
    provide_context=True,
    python_callable=get_config,
    dag=dag)

process_data_task = PythonOperator(
    task_id='process_data_task',
    provide_context=True,
    python_callable=process_data,
    dag=dag
)

torch_initializer_task >> config_task >> process_data_task
