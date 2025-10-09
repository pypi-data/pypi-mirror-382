# Copyright 2018-2022 contributors to the OpenLineage project
# SPDX-License-Identifier: Apache-2.0
import traceback
from typing import List, Optional

from openlineage.airflow.extractors.base import BaseExtractor, TaskMetadata
from openlineage.client.run import Dataset
from openlineage.airflow.utils import get_job_name, try_import_from_string

import logging

_BIGQUERY_NAMESPACE = 'bigquery'

log = logging.getLogger(__name__)


class GCSToBigQueryExtractor(BaseExtractor):
    def __init__(self, operator):
        super().__init__(operator)

    @classmethod
    def get_operator_classnames(cls) -> List[str]:
        return ['GCSToBigQueryOperator']

    def _get_client(self):
        # lazy-load the bigquery Client due to its slow import
        from google.cloud.bigquery import Client
        # Get client using Airflow hook - this way we use the same credentials as Airflow
        log.debug("Get client using Airflow hook - this way we use the same credentials as Airflow")
        if hasattr(self.operator, 'hook') and self.operator.hook:
            log.debug("Airflow Hook found")
            hook = self.operator.hook
            return hook.get_client(
                project_id=hook.project_id,
                location=hook.location
            )
        BigQueryHook = try_import_from_string(
            'airflow.providers.google.cloud.operators.bigquery.BigQueryHook'
        )

        if BigQueryHook is not None:
            log.debug("Biqquery Hook found")
            params = {}
            if hasattr(self.operator, "location"):
                location = self.operator.location
                params["location"] = location
            if hasattr(self.operator, "gcp_conn_id"):
                gcp_conn_id = self.operator.gcp_conn_id
                params["gcp_conn_id"] = gcp_conn_id
            if hasattr(self.operator, "use_legacy_sql"):
                use_legacy_sql = self.operator.use_legacy_sql
                params["use_legacy_sql"] = use_legacy_sql
            if hasattr(self.operator, "impersonation_chain"):
                impersonation_chain = self.operator.impersonation_chain
                params["impersonation_chain"] = impersonation_chain
            if hasattr(self.operator, "delegate_to"):
                params["delegate_to"] = self.operator.delegate_to

            log.debug("params")
            log.debug(params)
            hook = BigQueryHook(**params)
            log.debug("BigQueryHook")
            log.debug(hook)
            return hook.get_client(
                project_id=hook.project_id,
                location=hook.location
            )
        return Client()

    def _get_xcom_bigquery_job_id(self, task_instance):
        bigquery_job_id = task_instance.xcom_pull(
            task_ids=task_instance.task_id, key='job_id')

        self.log.debug(f"bigquery_job_id: {bigquery_job_id}")
        return bigquery_job_id

    def extract(self) -> Optional[TaskMetadata]:
        return None

    def extract_on_complete(self, task_instance) -> Optional[TaskMetadata]:
        from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
        from openlineage.common.provider.bigquery import BigQueryDatasetsProvider, BigQueryErrorRunFacet

        self.log.debug(f"extract_on_complete({task_instance})")
        self.log.debug(f"extract (GCSToBigQueryOperator)")
        self.log.debug(f"Operator: {self.operator}")

        job_id = None

        try:
            bigquery_job_id = self._get_xcom_bigquery_job_id(task_instance)
            job_id = bigquery_job_id
            if bigquery_job_id is None:
                raise Exception(
                    "Xcom could not resolve BigQuery job id. Job may have failed."
                )
        except Exception as e:
            self.log.error(
                f"Cannot retrieve job details from BigQuery.Client. {e}", exc_info=True
            )
            return TaskMetadata(
                name=f"{self.operator.dag_id}.{self.operator.task_id}",
                run_facets={
                    "bigQuery_error": BigQueryErrorRunFacet(
                        clientError=f"{e}: {traceback.format_exc()}",
                    )
                }
            )

        inputs = []
        outputs = []

        if self.operator.source_objects:
            inputs = [Dataset(
                namespace=f"gs://{self.operator.bucket}",
                name=f"{source_object}",
                facets={},
            ) for source_object in self.operator.source_objects]

        client = self._get_client()

        if job_id is not None:
            job = client.get_job(job_id=job_id)  # type: ignore
            props = job._properties
            log.debug("Job Props")
            log.debug(props)

            if "configuration" in props:
                configuration = props["configuration"]
                if "load" in configuration:
                    load = props["configuration"]["load"]
                    if "destinationTable" in load:
                        destinationTable = load["destinationTable"]
                        if "projectId" in destinationTable:
                            projectId = destinationTable["projectId"]
                            bigquery_destination_project_dataset_table = self.operator.destination_project_dataset_table
                            self.log.debug(
                                f"bigquery destination project dataset table: {bigquery_destination_project_dataset_table}")

                            if bigquery_destination_project_dataset_table:
                                outputs = [Dataset(
                                    namespace=_BIGQUERY_NAMESPACE,
                                    name=f"{projectId}.{bigquery_destination_project_dataset_table}",
                                    facets={},
                                )]

                            taskmetaData = TaskMetadata(
                                name=f"{self.operator.dag_id}.{self.operator.task_id}",
                                inputs=inputs,
                                outputs=outputs
                            )

                            self.log.debug(f"Task Meta Data: {taskmetaData}")
                            return taskmetaData