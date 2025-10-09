from datetime import datetime, timedelta
# from airflow import DAG
import datetime
from airflow.operators.bash import BashOperator
from acceldata_sdk.models.job import CreateJob, JobMetadata, Node
from acceldata_sdk.models.pipeline import PipelineMetadata
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_airflow_sdk.dag import DAG
from acceldata_airflow_sdk.operators.torch_initialiser_operator import TorchInitializer
from acceldata_airflow_sdk.operators.job_operator import JobOperator
import os

os.environ["no_proxy"] = "*"

job_metadata = JobMetadata('sangeeta@acceldata.io', 'DR', ' Data Pipeline')
pipeline_uid = "job_operator_success_dag_0_retries"
pipeline_name = "job_operator_success_dag_0_retries"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

default_args = {
    "owner": "Sangeeta Airflow", 'retries': 0, "depends_on_past": False,
    "email": ["sangeeta@accceldata.io"], "email_on_failure": False, "email_on_retry": False
}

dag = DAG(
    dag_id="job_operator_success_dag_0_retries", catchup=False, default_args=default_args,
    schedule=None, description="job_operator_success_dag_0_retries", start_date=datetime.datetime(2024, 4, 24),
    tags=["ad-pipeline-example"]
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

bash_task_1 = BashOperator(
    task_id="bash_task_1",
    bash_command='echo "Here is the message: \'{{ dag_run.conf["message"] if dag_run.conf else "" }}\'"',
)

bash_task_2 = BashOperator(
    task_id="bash_task_2",
    bash_command='echo "Here is the message: \'{{ dag_run.conf["message"] if dag_run.conf else "" }}\'"',
)

bash_operator_1 = JobOperator(
    task_id='bash_task_1',
    job_uid='bash_task_1',
    span_uid='bash_task_1.span',
    inputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CALL_CENTER")],
    outputs=[Node(job_uid="bash_task_2"),
             Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER")],
    metadata=JobMetadata('name', 'team', 'code_location'),
    operator=bash_task_1,
    dag=dag,
    xcom_to_event_mapper_ids=['run_id', 'event_id'],
    bounded_by_span=True
)

bash_operator_2 = JobOperator(
    task_id='bash_task_2',
    job_uid='bash_task_2',
    inputs=[Node(job_uid="bash_task_1")],
    outputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER")],
    metadata=JobMetadata('name', 'team', 'code_location'),
    operator=bash_task_2,
    dag=dag
)

torch_initializer_task >> bash_operator_1 >> bash_operator_2
