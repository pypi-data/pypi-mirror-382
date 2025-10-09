from datetime import datetime, timedelta
from acceldata_airflow_sdk.dag import DAG
from airflow.operators.python_operator import PythonOperator
import os
from acceldata_airflow_sdk.operators.torch_initialiser_operator import TorchInitializer
from acceldata_sdk.models.job import CreateJob, JobMetadata, Node
from acceldata_sdk.models.pipeline import PipelineMetadata
from acceldata_airflow_sdk.decorators.job import job

job_metadata = JobMetadata('sangeeta@acceldata.io', 'DR', ' Data Pipeline')
pipeline_uid = "job_deco_success_dag_2_retries_with_dag"
pipeline_name = "job_deco_success_dag_2_retries_with_dag"

os.environ["no_proxy"] = "*"


@job(job_uid='get_config',
     inputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CALL_CENTER")],
     outputs=[Node(job_uid="process_data"),
              Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER")],
     metadata=job_metadata,
     span_uid='get_config.span')
def get_config(**kwargs):
    config = {
        'param1': 'value1',
        'param2': 'value2'
    }
    return config


@job(job_uid='process_data',
     inputs=[Node(job_uid="get_config")],
     outputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.REASON")],
     metadata=job_metadata,
     span_uid='process_data.span')
def process_data(**kwargs):
    """
    Process data based on configuration.
    """
    """
    Your task logic goes here.
    """
    # Example: Simulating a task failure
    try_number = kwargs['ti'].try_number
    if try_number <= 2:
        raise ValueError("Simulated error occurred!")
    print("I am successful in the last try")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Number of retries
    'retry_delay': timedelta(minutes=1)  # Retry delay
}

with (DAG(
        'job_deco_success_dag_2_retries_with_dag',
        default_args=default_args,
        description='A DAG example with retry and configuration-driven approach',
        schedule_interval='@once',
        start_date=datetime(2024, 3, 25),
        catchup=False
) as dag):
    # Define a task to fetch configuration
    # Define your task with PythonOperator
    # Initialize ADOC
    torch_initializer_task = TorchInitializer(
        task_id='torch_pipeline_initializer',
        pipeline_uid=pipeline_uid,
        pipeline_name=pipeline_name,
        # Torch connection id goes here
        connection_id='acceldata-poc',
        # optional root span: span_name=pipeline_uid + '_' + 'root_span',
        meta=PipelineMetadata(owner='Demo', team='demo_team', codeLocation='...')
    )

    config_task = PythonOperator(
        task_id='config_task',
        python_callable=get_config,
        provide_context=True
    )
    process_data_task = PythonOperator(
        task_id='process_data_task',
        provide_context=True,
        python_callable=process_data
    )
    torch_initializer_task >> config_task >> process_data_task
