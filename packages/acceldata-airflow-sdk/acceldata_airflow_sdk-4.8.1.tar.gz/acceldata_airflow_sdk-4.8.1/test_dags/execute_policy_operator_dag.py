from datetime import datetime, timedelta
# from airflow import DAG
import datetime
from airflow.operators.bash import BashOperator
from acceldata_sdk.models.job import CreateJob, JobMetadata, Node
from acceldata_sdk.models.pipeline import PipelineMetadata
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_airflow_sdk.dag import DAG
from acceldata_airflow_sdk.operators.torch_initialiser_operator import TorchInitializer
from acceldata_airflow_sdk.operators.span_operator import SpanOperator
from acceldata_airflow_sdk.operators.job_operator import JobOperator
from acceldata_airflow_sdk.operators.execute_policy_operator import ExecutePolicyOperator
from acceldata_sdk.constants import FailureStrategy, PolicyType

import os

os.environ["no_proxy"] = "*"

job_metadata = JobMetadata('sangeeta@acceldata.io', 'DR', ' Data Pipeline')
pipeline_uid = "execute_policy_operator_dag"
pipeline_name = "execute_policy_operator_dag"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

default_args = {
    "owner": "Sangeeta Airflow", 'retries': 0, "depends_on_past": False,
    "email": ["sangeeta@accceldata.io"], "email_on_failure": False, "email_on_retry": False
}

dag = DAG(
    dag_id="execute_policy_operator_dag", catchup=False, default_args=default_args,
    schedule=None, description="execute_policy_operator_dag", start_date=datetime.datetime(2024, 4, 24),
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

execute_policy_task = ExecutePolicyOperator(
    task_id='execute_policy_operator',
    policy_type=PolicyType.RECONCILIATION,
    policy_id=269722,
    sync=False,
    failure_strategy=FailureStrategy.DoNotFail
)

execute_policy_operator = JobOperator(
    task_id='execute_policy_operator_task',
    job_uid='execute_policy_operator',
    inputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CALL_CENTER")],
    outputs=[Node(job_uid="bash_task_2"),
             Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER")],
    metadata=JobMetadata('name', 'team', 'code_location'),
    operator=execute_policy_task,
    dag=dag,
    xcom_to_event_mapper_ids=['run_id', 'event_id']
)

torch_initializer_task >> execute_policy_operator
