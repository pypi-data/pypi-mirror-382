from datetime import datetime, timedelta
# from airflow import DAG
import datetime
from airflow.operators.bash import BashOperator
from acceldata_sdk.models.job import CreateJob, JobMetadata, Node
from acceldata_sdk.models.pipeline import PipelineMetadata
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_airflow_sdk.dag import DAG
from airflow.operators.python import PythonOperator
from acceldata_airflow_sdk.decorators.job import job
from acceldata_airflow_sdk.operators.torch_initialiser_operator import TorchInitializer
import os
from acceldata_airflow_sdk.operators.job_operator import JobOperator

os.environ["no_proxy"] = "*"

job_metadata = JobMetadata('sangeeta@acceldata.io', 'DR', ' Data Pipeline')
pipeline_uid = "job_operator_success_dag_2_retries"
pipeline_name = "job_operator_success_dag_2_retries"

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def get_bash_command():
    return """
    ATTEMPT_FILE="/tmp/airflow_bash_operator_attempt_count.txt"
    if [ ! -f "$ATTEMPT_FILE" ]; then
      echo 0 > "$ATTEMPT_FILE"
    fi
    ATTEMPT_COUNT=$(cat "$ATTEMPT_FILE")
    ATTEMPT_COUNT=$((ATTEMPT_COUNT + 1))
    echo $ATTEMPT_COUNT > "$ATTEMPT_FILE"
    if [ "$ATTEMPT_COUNT" -eq 2 ]; then
      echo "Success on attempt $ATTEMPT_COUNT"
      rm "$ATTEMPT_FILE"  # Cleanup the attempt file after success
      exit 0
    else
      echo "Failing attempt $ATTEMPT_COUNT"
      exit 1
    fi
    """


default_args = {
    "owner": "Sangeeta Airflow", 'retries': 2, "retry_delay": timedelta(minutes=2), "depends_on_past": False,
    "email": ["sangeeta@accceldata.io"], "email_on_failure": False, "email_on_retry": False
}

dag = DAG(
    dag_id="job_operator_success_dag_2_retries", catchup=False, default_args=default_args,
    schedule=None, description="job_operator_success_dag_2_retries",
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

bash_task = BashOperator(
    task_id="bash_task",
    bash_command='echo "Here is the message: \'{{ dag_run.conf["message"] if dag_run.conf else "" }}\'"',
)

# Define a function to generate the Bash command


# Define the BashOperator using the generated command
bash_operator_retry = BashOperator(
    task_id='bash_operator_retry',
    bash_command=get_bash_command()
)

bash_operator_1 = JobOperator(
    task_id='bash_task_1',
    job_uid='bash_task_1',
    span_uid='bash_task_1.span',
    inputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CALL_CENTER")],
    outputs=[Node(job_uid="bash_task_2"),
             Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.CUSTOMER")],
    metadata=JobMetadata('name', 'team', 'code_location'),
    operator=bash_task,
    dag=dag,
    xcom_to_event_mapper_ids=['run_id', 'event_id'],
    bounded_by_span=True
)

bash_operator_2 = JobOperator(
    task_id='bash_task_2',
    job_uid='bash_task_2',
    inputs=[Node(job_uid="bash_task_1")],
    outputs=[Node(asset_uid="Snowflake_stg.SNOWFLAKE_SAMPLE_DATA.TPCDS_SF100TCL.REASON")],
    metadata=JobMetadata('name', 'team', 'code_location'),
    operator=bash_operator_retry,
    dag=dag
)

torch_initializer_task >> bash_operator_1 >> bash_operator_2
