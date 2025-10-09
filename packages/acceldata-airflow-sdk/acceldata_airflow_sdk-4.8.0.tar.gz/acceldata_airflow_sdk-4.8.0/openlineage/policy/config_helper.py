import logging

log = logging.getLogger(__name__)

ACCELDATA_LINEAGE_URL = "acceldata_lineage_url"
ACCELDATA_LINEAGE_ENDPOINT = "acceldata_lineage_endpoint"
ACCELDATA_ACCESS_KEY = "acceldata_access_key"
ACCELDATA_SECRET_KEY = "acceldata_secret_key"
ACCELDATA_BEARER_TOKEN = "acceldata_bearer_token"
ACCELDATA_EXPIRES_AT = "acceldata_expires_at"
DATAPROC_CREATE_BATCH_OPERATOR = "DataprocCreateBatchOperator"
RUNTIME_CONFIG = "runtime_config"



def _fetch_open_lineage_spark_properties(parent_run_id, job_name):
    from airflow.models import Variable
    log.info("OPEN_LINEAGE_POLICY Setting up openlineage spark properties")
    acceldata_lineage_url = Variable.get(ACCELDATA_LINEAGE_URL, None)
    acceldata_lineage_endpoint = Variable.get(ACCELDATA_LINEAGE_ENDPOINT, None)
    acceldata_secret_key = Variable.get(ACCELDATA_SECRET_KEY, None)
    acceldata_access_key = Variable.get(ACCELDATA_ACCESS_KEY, None)

    if acceldata_lineage_url is not None and acceldata_lineage_endpoint is not None and acceldata_secret_key is not None and acceldata_access_key is not None:
        properties = {"spark.extraListeners": 'io.openlineage.spark.agent.OpenLineageSparkListener',
                      "spark.openlineage.transport.url": acceldata_lineage_url,
                      "spark.openlineage.parentRunId": parent_run_id,
                      "spark.jars.packages": 'io.openlineage:openlineage-spark:1.1.0',
                      "spark.openlineage.transport.type": 'http',
                      "spark.openlineage.parentJobName": job_name,
                      "spark.openlineage.transport.headers.accessKey": acceldata_access_key,
                      "spark.openlineage.transport.headers.secretKey": acceldata_secret_key,
                      "spark.openlineage.transport.endpoint": acceldata_lineage_endpoint}
        log.info("OPEN_LINEAGE_POLICY Spark Properties: %s ", properties)
        return properties
    else:
        log.error("OPEN_LINEAGE_POLICY Necessary parameters to construct spark properties not available in cache")


# Building batch->runtime_config->properties
def _build_properties(task, parent_run_id, runtime_config):
    spark_properties = _fetch_open_lineage_spark_properties(parent_run_id, task.task_id)
    log.info("OPEN_LINEAGE_POLICY spark_properties: %s", str(spark_properties))
    # If task.batch["runtime_config] contains properties key
    if "properties" in runtime_config:
        existing_properties = runtime_config["properties"]
        # Merge existing and openlineage properties
        merged_properties = {**spark_properties, **existing_properties}
        task.batch["runtime_config"]["properties"] = merged_properties
        log.info("OPEN_LINEAGE_POLICY Properties %s :", merged_properties)
    else:
        #  If task.batch["runtime_config] doesn't have properties key
        task.batch["runtime_config"]["properties"] = spark_properties
        log.info("OPEN_LINEAGE_POLICY Properties %s :", spark_properties)


def _mutate_data_proc_create_batch_operator(task):
    log.info("OPEN_LINEAGE_POLICY mutate_data_proc_create_batch_operator")
    try:
        if hasattr(task, "batch"):
            task_batch = task.batch
            parent_run_id = "{{ macros.OpenLineagePlugin.lineage_run_id(task, task_instance) }}"
            log.debug("OPEN_LINEAGE_POLICY task_batch %s", str(task_batch))
            if RUNTIME_CONFIG in task_batch:
                # Append to run_time config if exists
                runtime_config = task_batch["runtime_config"]
                log.info("OPEN_LINEAGE_POLICY task.batch['runtime_config'] found: %s", str(runtime_config))
                _build_properties(task, parent_run_id, runtime_config)
            else:
                # construct runtime_config here
                task.batch["runtime_config"] = {}
                runtime_config = task.batch["runtime_config"]
                _build_properties(task, parent_run_id, runtime_config)
        log.info("OPEN_LINEAGE_POLICY DataprocCreateBatchOperator mutations completed")
    except Exception as e:
        log.error("OPEN_LINEAGE_POLICY Error when calling task_policy")
        log.error("OPEN_LINEAGE_POLICY %s", e)
