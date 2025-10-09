from airflow.models.baseoperator import BaseOperator
from acceldata_sdk.torch_client import TorchClient
from acceldata_airflow_sdk.initialiser import torch_credentials
from acceldata_sdk.constants import FailureStrategy
from acceldata_airflow_sdk.utils.airflow_job_utils import CONNECTION_ID, get_dag_run_pipeline_run_id
from acceldata_sdk.models.common_types import PolicyExecutionRequest

import logging
LOGGER = logging.getLogger("tasks")


class ExecutePolicyOperator(BaseOperator):
    """
    Description:
        ExecutePolicyOperator is used to execute a policy by passing policy_type and policy_id.
        It will return only after the execution ends if sync is set to True.

        :param policy_type: (String) Type of policy to be executed
        :param policy_id: (String) id of the policy to be executed
        :param incremental: (bool) optional Set it to True if full execution has to be done
        :param sync: (bool) optional Set it to True to execute policy in synchronous mode
        :param failure_strategy: (enum) optional Set it to decide if it should fail at error,
            fail at warning or never fail
    """

    def __init__(self, *, policy_type, policy_id, sync, incremental=False,
                 failure_strategy: FailureStrategy = FailureStrategy.DoNotFail,
                 policy_execution_request: PolicyExecutionRequest = None, **kwargs):
        """
        :param policy_type: (PolicyType) Type of policy to be executed
        :param policy_id: (String) id of the policy to be executed
        :param incremental: (bool) optional Set it to True if full execution has to be done
        :param sync: (bool) optional Set it to True to execute policy in synchronous mode
        :param failure_strategy: (enum) optional Set it to decide if it should fail at error,
            fail at warning or never fail
        :param policy_execution_request: (PolicyExecutionRequest) An optional parameter that allows you to provide
        additional options for executing the policy. It is an instance of the PolicyExecutionRequest modules class,
        which contains various properties that can be used to customize the policy execution, such as `executionType`,
        `markerConfigs`, `ruleItemSelections`, and more.

        Example:
        from acceldata_sdk.constants import RuleExecutionStatus, FailureStrategy, PolicyType
        from acceldata_sdk.common import Executor
        operator_task = ExecutePolicyOperator(
            task_id='torch_pipeline_operator_test',
            policy_type=PolicyType.DATA_QUALITY,
            policy_id=46,
            sync=True,
            failure_strategy=FailureStrategy.FailOnError,
            policy_execution_request=policy_execution_request
            dag=dag
        )

        In case you need to query the status in another task you need to pull the execution id from xcom by passing
        the policy name in the {policy_name}_execution_id. In this example the policy name of policy_id 46 is 'policy_with_email'

        After getting the execution_id you need to create object of Executor by passing policy_type and
        torch_client object and call get_result using the execution_id.

        def operator_result(**context):
            xcom_key = {policy_type.name}_{policy_id}_execution_id'
            task_instance = context['ti']
            # get the policy_name and execution id - then pull from xcom
            execution_id = task_instance.xcom_pull(key=xcom_key)
            if execution_id is not None:
                torch_client = TorchClient(**torch_credentials)
                result = torch_client.get_policy_execution_result(policy_type=PolicyType.DATA_QUALITY, execution_id=execution_id)
        """
        super().__init__(**kwargs)
        self.policy_type = policy_type
        self.policy_id = policy_id
        self.incremental = incremental
        self.failure_strategy = failure_strategy
        self.sync = sync
        self.policy_execution_request = policy_execution_request

    def execute(self, context):
        task_instance = context['ti']
        conn_id = task_instance.xcom_pull(key=CONNECTION_ID)
        torch_client = TorchClient(**torch_credentials(conn_id))
        pipeline_run_id = get_dag_run_pipeline_run_id(task_instance)
        execution_return = torch_client.execute_policy(
            policy_type=self.policy_type,
            policy_id=self.policy_id,
            sync=self.sync,
            incremental=self.incremental,
            failure_strategy=self.failure_strategy,
            pipeline_run_id=pipeline_run_id,
            policy_execution_request=self.policy_execution_request
        )
        if execution_return.id is not None:
            xcom_key = f'{self.policy_type.name}_{self.policy_id}_execution_id'
            task_instance = context['ti']
            # get the policy_name and execution id - then push them in xcom
            task_instance.xcom_push(key=xcom_key, value=execution_return.id)

