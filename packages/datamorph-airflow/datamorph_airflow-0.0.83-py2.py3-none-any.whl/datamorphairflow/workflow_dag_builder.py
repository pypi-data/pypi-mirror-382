import datetime
import json
import logging
from copy import deepcopy
from json import JSONDecodeError
from typing import Dict, Any, List, Callable

from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.models import BaseOperator, TaskInstance
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.module_loading import import_string

from datamorphairflow import utils
from datamorphairflow.helper_classes import WorkflowDAG, WorkflowDAGNode


class WorkflowDagBuilder:
    """
    Generates tasks and a DAG from a config.
    :param dag_name: the name of the DAG
    :param dag_config: a dictionary containing configuration for the DAG
    :param default_config: a dictitionary containing defaults for all DAGs
    """

    def __init__(
            self, dag_name: str, dag_config: Dict[str, Any], default_config: Dict[str, Any],
            workflow_nodes: List[WorkflowDAGNode]
    ) -> None:
        self.dag_name: str = dag_name
        self.dag_config: Dict[str, Any] = deepcopy(dag_config)
        self.default_config: Dict[str, Any] = deepcopy(default_config)
        self.workflow_nodes: List[WorkflowDAGNode] = deepcopy(workflow_nodes)

    def get_dag_params(self) -> Dict[str, Any]:
        """
        Check all the default parameters for DAGs and validate the type.
        TBD
        :return:
        """

        dag_params: Dict[str, Any] = {**self.dag_config, **self.default_config}

        # check if the schedule_interval is set to None
        if (
                utils.check_dict_key(dag_params, "schedule_interval")
                and dag_params["schedule_interval"] == "None"
        ):
            dag_params["schedule_interval"] = None

        try:
            dag_params["start_date"]: datetime = utils.get_datetime(
                date_value=dag_params["start_date"],
                timezone=dag_params.get("timezone", "UTC"),
            )
        except KeyError as err:
            raise Exception(f"{self.dag_name} config is missing start_date") from err

        return dag_params

    def pre_execute(context):
        """
        This function will be triggered before each task execution. Checks the status of the upstream tasks
        and if parent node is in "upstream_failed" state, then skips the current task.
        As of Airflow version 2.2.5, if parent task is in "upstream_failed" state and current task trigger_rule
        is "all_failed/one_failed" then the current task still executes. To work around this behavior, this
        method raises an AirflowSkipException if parent status is upstream failed.
        :param context:
        :return:
        """
        # logging.debug("Running pre_execute...")
        task = context['task']
        upstream_ids = task.upstream_task_ids
        logging.debug(f" Upstream task ids: {task.upstream_task_ids}")
        execution_date = context['execution_date']
        dag_instance = context['dag']
        upstream_failed_count = 0
        for each in upstream_ids:
            operator_instance = dag_instance.get_task(each)
            task_status = TaskInstance(operator_instance, execution_date).current_state()
            logging.debug(f" Status for upstream task {each} is {task_status}")
            if task_status == "upstream_failed" or task_status == "skipped":
                upstream_failed_count = upstream_failed_count + 1
        # raise exception if all the upstream nodes failed or skipped
        # the logic to check this can be changed
        if upstream_failed_count >= 1 and upstream_failed_count == len(upstream_ids):
            raise AirflowSkipException

    @staticmethod
    def create_task(node: WorkflowDAGNode, dag: DAG) -> BaseOperator:
        """
        create task using the information from node and returns an instance of the Airflow BaseOperator
        :param dag:
        :return: instance of operator object
        """
        operator = node.type
        task_params = node.taskparams
        task_params["task_id"] = node.name
        task_params["dag"] = dag
        try:
            operator_obj: Callable[..., BaseOperator] = import_string(operator)
        except Exception as err:
            raise Exception(f"Failed to import operator: {operator}") from err
        try:
            # check for PythonOperator and get Python Callable from the
            # function name and python file with the function.
            if operator_obj in [PythonOperator, BranchPythonOperator]:
                if (
                        not task_params.get("python_callable_name")
                        and not task_params.get("python_callable_file")
                ):
                    raise Exception(
                        "Failed to create task. PythonOperator and BranchPythonOperator requires \
                        `python_callable_name` and `python_callable_file` parameters"
                    )
                if not task_params.get("python_callable"):
                    task_params[
                        "python_callable"
                    ]: Callable = utils.get_python_callable(
                        task_params["python_callable_name"],
                        task_params["python_callable_file"],
                    )
                    # remove DataMorph specific parameters
                    del task_params["python_callable_name"]
                    del task_params["python_callable_file"]

                # loading arguments as json for handling positional arguments, arrays and strings
                if task_params.get("op_args"):
                    op_args_string = task_params["op_args"]
                    try:
                        op_args_json = json.loads(op_args_string)
                    except JSONDecodeError:
                        op_args_json = op_args_string
                    if isinstance(op_args_json, dict):
                        # op_kwargs for dict
                        task_params["op_kwargs"] = op_args_json
                        del task_params["op_args"]
                    else:
                        # op_args is for list of positional arguments or strings
                        task_params["op_args"] = op_args_json

            task_params["pre_execute"] = WorkflowDagBuilder.pre_execute

            # create task  from the base operator object with all the task params
            task: BaseOperator = operator_obj(**task_params)
        except Exception as err:
            raise Exception(f"Failed to create {operator_obj} task") from err
        return task

    def build(self) -> WorkflowDAG:
        """
        Generates a DAG from the dag parameters
        step 1: iterate through all the nodes in list of WorkflowDAGNode
        step 2: create task _params for each node
        step 3: set upstream based on the depends on criteria
        step 4: return dag with the dag name as WorkflowDAG object
        :return:
        """

        dag_kwargs = self.get_dag_params()
        dag: DAG = DAG(**dag_kwargs)

        # workflow dictionary to maintain node name and Task as Airflow BaseOpertaor
        workflow_dict = {}

        for node in self.workflow_nodes:
            # logging.debug(f"Node name: {node}")
            dependsOn = node.dependson
            dependsOnList = []
            name = node.name
            workflow_dict[name] = WorkflowDagBuilder.create_task(node, dag)
            if dependsOn is not None:
                baseOperator = workflow_dict[name]
                for eachDependsOn in dependsOn:
                    dependsOnList.append(workflow_dict[utils.remove_node_suffix(eachDependsOn)])
                # logging.debug(f"Depends on list: {dependsOnList}")
                baseOperator.set_upstream(dependsOnList)
        return WorkflowDAG(self.dag_name, dag)
