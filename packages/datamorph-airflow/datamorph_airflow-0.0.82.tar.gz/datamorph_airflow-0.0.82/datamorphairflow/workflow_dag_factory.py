import ast
import logging
import os

from typing import Any, Dict, Optional, List

from airflow import DAG

from datamorphairflow import utils,config_utils
from datamorphairflow.datamorph_constants import DATAMORPH_UI_PROPERTY, DATAMORPH_PROPERTY_OUTPUTTO, \
    DATAMORPH_UI_PROPERTY_ID, DATAMORPH_PROPERTY_DEPENDSON, DATAMORPH_PROPERTY_WORKFLOW, DATAMORPH_PROPERTIES, \
    DATAMORPH_PROPERTY_DESCRIPTION, DATAMORPH_PROPERTY_NAME, DATAMORPH_PROPERTY_NODETYPE, DATAMORPH_PROPERTY_TYPE, \
    DATAMORPH_PROPERTY_DATAMORPHCONF, AIRFLOW_PROPERTY_DAG_ID, AIRFLOW_PROPERTY_DESC, DATAMORPH_PROPERTY_JOBPARAMS, \
    DATAMORPH_JOBPARAMS_STICKYPARAMS, DATAMORPH_JOBPARAMS_WORKFLOWRUNTINE, DATAMORPH_PROPERTY_PIPELINE_ID, \
    DATAMORPH_PROPERTY_TYPE_OVERRIDE, DEFAULT_AWS_REGION, DATAMORPH_JOBPARAMS_PROFILEID, DATAMORPH_UI_PROPERTIES
from datamorphairflow.helper_classes import WorkflowDAGNode, WorkflowDAG
from datamorphairflow.workflow_dag_builder import WorkflowDagBuilder

#Global Variables
WORKFLOW_REGION = DEFAULT_AWS_REGION

class WorkflowDagFactory:
    """
    :param config_filepath: the filepath of the DAG factory JSON config file.
        Must be absolute path to file. Cannot be used with `config`.
    :type config_filepath: str
    :param config: DAG factory config dictionary. Cannot be used with `config_filepath`.
    :type config: dict
    """

    def __init__(self, config_filepath: Optional[str] = None, config: Optional[dict] = None,
                 s3bucket: Optional[str] = None, s3key: Optional[str] = None, s3region: Optional[str] = None
                 ) -> None:
        assert bool(config_filepath) ^ bool(config) ^ (bool(s3bucket) & bool(s3key)), \
            "Either `config_filepath` or `config` or 's3key and s3bucket' should be provided"
        if config_filepath:
            WorkflowDagFactory._validate_config_filepath(config_filepath=config_filepath)
            self.config: Dict[str, Any] = WorkflowDagFactory._load_config(
                config_filepath=config_filepath
            )
        if config:
            self.config: Dict[str, Any] = config
        if s3key and s3bucket:
            global WORKFLOW_REGION
            WORKFLOW_REGION = WORKFLOW_REGION if s3region is None else s3region
            self.config: Dict[str, Any] = WorkflowDagFactory._load_s3_config(
                s3key=s3key, s3bucket=s3bucket, s3region=WORKFLOW_REGION
            )

    @staticmethod
    def _validate_config_filepath(config_filepath: str) -> None:
        """
        Validates config file path is absolute
        """
        if not os.path.isabs(config_filepath):
            raise Exception("DAG Factory `config_filepath` must be absolute path")

    @staticmethod
    def _load_config(config_filepath: str) -> Dict[str, Any]:
        """
        Loads JSON config file to dictionary. Substitute variables if any.
        :returns: dict from JSON config file
        """
        # pylint: disable=consider-using-with
        try:
            config: Dict[str, Any] = config_utils.load_json_config_file(config_file_path=config_filepath)
            # logging.debug(f" Config: {config}")

        except Exception as err:
            raise Exception("Invalid Workflow DAG config file:", format(config_filepath)) from err

        return config

    @staticmethod
    def _load_s3_config(s3key: str, s3bucket: str, s3region: str) -> Dict[str, Any]:
        """
        Loads JSON config file to dictionary. Substitute variables if any.
        :returns: dict from JSON config file
        """
        # pylint: disable=consider-using-with
        try:
            config: Dict[str, Any] = config_utils.load_json_config_file(s3key=s3key, s3bucket=s3bucket, s3region=s3region)
            # logging.debug(f" Config: {config}")

        except Exception as err:
            raise Exception("Invalid Workflow DAG config file:", format("s3://" + s3bucket + "/" + s3key)) from err

        return config

    def get_default_config(self) -> Dict[str, Any]:
        """
        Returns all the config elements excluding workflow as workflow contains task specific parameters.
        Typical DAG specific config elements include dag_id, description, schedule_interval etc.

        :returns: dict with default configuration to create dag
        """
        config_elems = self.config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTIES][DATAMORPH_PROPERTY_JOBPARAMS]
        utils.remove_keys(config_elems, [DATAMORPH_JOBPARAMS_STICKYPARAMS, DATAMORPH_JOBPARAMS_WORKFLOWRUNTINE, DATAMORPH_JOBPARAMS_PROFILEID])
        return config_elems

    def remove_datamorph_properties(self, properties: dict):
        # remove DataMorph UI specific properties
        properties = utils.remove_key(properties, DATAMORPH_UI_PROPERTY)
        properties = utils.remove_key(properties, DATAMORPH_PROPERTY_OUTPUTTO)
        properties = utils.remove_key(properties, DATAMORPH_UI_PROPERTY_ID)
        properties = utils.remove_key(properties, DATAMORPH_PROPERTY_DEPENDSON)
        properties = utils.remove_key(properties, DATAMORPH_PROPERTY_PIPELINE_ID)
        properties = utils.remove_key(properties, DATAMORPH_PROPERTY_TYPE_OVERRIDE)
        properties = utils.remove_key(properties, "aws_region")
        utils.remove_keys(properties,DATAMORPH_UI_PROPERTIES)
        return properties

    def get_workflow_nodes(self) -> List[WorkflowDAGNode]:
        nodelist = []
        try:
            workflow = self.config[DATAMORPH_PROPERTY_WORKFLOW]
            for node in ast.literal_eval(str(workflow)):
                properties = node.get(DATAMORPH_PROPERTIES)
                description = node.get(DATAMORPH_PROPERTY_DESCRIPTION)
                name = node.get(DATAMORPH_PROPERTY_NAME)
                type = properties.get(DATAMORPH_PROPERTY_TYPE_OVERRIDE, node.get(DATAMORPH_PROPERTY_TYPE))
                nodetype = node.get(DATAMORPH_PROPERTY_NODETYPE)
                # all nodes may not have depends on
                dependson = properties.get(DATAMORPH_PROPERTY_DEPENDSON, "")
                # remove DataMorph specific properties
                filtered_properties = self.remove_datamorph_properties(properties)
                # only if node type is action or trigger, add to the list of dag nodes.
                # Any new nodetype for dag should be included here
                if nodetype in ["action", "trigger"]:
                    # only for trigger type there will not be any dependsOn as of now
                    eachnode = WorkflowDAGNode(name, description, type, nodetype, dependson,
                                               filtered_properties)
                    nodelist.append(eachnode)

        except Exception as err:
            raise Exception("Invalid Workflow DAG config file") from err

        return nodelist

    def create_dag(self) -> WorkflowDAG:
        """
        Creates DAG using the config file
        :return: DAG
        """
        workflow_node_list = self.get_workflow_nodes()
        dag_name = self.config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTY_NAME]
        dag_desc = self.config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTY_DESCRIPTION]
        default_config = self.get_default_config()
        default_config[AIRFLOW_PROPERTY_DAG_ID] = dag_name
        default_config[AIRFLOW_PROPERTY_DESC] = dag_desc
        workflow_dag_builder: WorkflowDagBuilder = WorkflowDagBuilder(
            dag_name=dag_name,
            dag_config=default_config,
            default_config={},
            workflow_nodes=workflow_node_list)
        try:
            dag_with_name: WorkflowDAG = workflow_dag_builder.build()
        except Exception as err:
            raise Exception(
              f"Failed to generate dag {dag_name}. verify config is correct"
            ) from err
        return dag_with_name

    @staticmethod
    def register_dag(dag_id: str, dag: DAG, globals: Dict[str, Any]) -> None:
        """Adds `dags` to `globals` so Airflow can discover them.
        :param: dags_id: Name of the DAG to be registered.
        :param: dags: DAG to be registered.
        :param globals: The globals() from the file used to generate DAGs. The dag_id
            must be passed into globals() for Airflow to import
        """
        globals[dag_id]: DAG = dag

    def generate_dags(self, globals: Dict[str, Any]) -> None:
        """
        Generates DAGs from JSON config
        :param globals: The globals() from the file used to generate DAGs. The dag_id
            must be passed into globals() for Airflow to import
        """
        dag: WorkflowDAG = self.create_dag()
        self.register_dag(dag.dagid, dag.dag, globals)
