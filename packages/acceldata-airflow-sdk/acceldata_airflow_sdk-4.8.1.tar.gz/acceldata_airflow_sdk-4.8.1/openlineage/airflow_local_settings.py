from airflow.models import BaseOperator

import logging

log = logging.getLogger(__name__)

from policy.config_helper import _mutate_data_proc_create_batch_operator


# Mutating task level policy
def task_policy(task: BaseOperator):
    try:
        log.info("OPEN_LINEAGE_POLICY task_policy invoked")
        task_obj_type = type(task)
        task_obj_class_name = task_obj_type.__name__
        log.info("OPEN_LINEAGE_POLICY task object class name %s, proceeding with further checks", task_obj_class_name)
        from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator

        # apply policy only for DataprocCreateBatchOperator
        if isinstance(task, DataprocCreateBatchOperator):
            log.info("OPEN_LINEAGE_POLICY task is instance of DataprocCreateBatchOperator. Proceeding with mutations")
            _mutate_data_proc_create_batch_operator(task)

    except Exception as e:
        log.error("OPEN_LINEAGE_POLICY Error when calling task_policy")
        log.error("OPEN_LINEAGE_POLICY %s", e)
