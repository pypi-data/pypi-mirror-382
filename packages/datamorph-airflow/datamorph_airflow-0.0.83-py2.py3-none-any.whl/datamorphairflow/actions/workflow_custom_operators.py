import json
import logging
import os
from typing import Union, List, Optional, Iterable, Dict, Any

from airflow.models import BaseOperator
from airflow.operators.python import BranchPythonOperator
from airflow.providers.databricks.hooks.databricks import DatabricksHook
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.operators.bash import BashOperator

from datamorphairflow.file_util import S3FileSystem

from datamorphairflow import utils

from datamorphairflow.hooks import WorkflowParameters


class DMStartDatabricksClusterOperator(BaseOperator):
    """
    Custom databricks operator to start a cluster with the provided cluster id.
    """

    def __init__(
            self, cluster_id: str, databricks_conn_id: str = "databricks_default", **kwargs
    ):
        super().__init__(**kwargs)
        self.databricks_conn_id = databricks_conn_id
        self.cluster_id = cluster_id

    def execute(self, context):
        databricks_hook = DatabricksHook(databricks_conn_id=self.databricks_conn_id)
        responds = databricks_hook._do_api_call(
            ("POST", "api/2.0/clusters/start"), {"cluster_id": self.cluster_id}
        )
        return responds


class DMTerminateDatabricksClusterOperator(BaseOperator):
    """
    Custom databricks operator to stop a cluster with the provided cluster id
    """

    def __init__(
            self, cluster_id: str, databricks_conn_id: str = "databricks_default", **kwargs
    ):
        super().__init__(**kwargs)
        self.databricks_conn_id = databricks_conn_id
        self.cluster_id = cluster_id

    def execute(self, context):
        databricks_hook = DatabricksHook(databricks_conn_id=self.databricks_conn_id)
        responds = databricks_hook._do_api_call(
            ("POST", "api/2.0/clusters/terminate"), {"cluster_id": self.cluster_id}
        )
        return responds

















