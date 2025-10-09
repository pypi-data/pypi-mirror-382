"""
DataMorph constants are maintained in this file
"""
DATAMORPH_UI_PROPERTY_ID: str = "id"
DATAMORPH_UI_PROPERTY: str = "ui"
DATAMORPH_UI_PROPERTIES = ['icon','extras','label','dragging','width','style','position','id','selected','height','style.backgroundColor','position.x','position.y']

DATAMORPH_PROPERTY_DEPENDSON: str = "dependsOn"
DATAMORPH_PROPERTY_OUTPUTTO: str = "outputTo"

DATAMORPH_PROPERTY_WORKFLOW: str = "workflow"
DATAMORPH_PROPERTY_DATAMORPHCONF: str = "datamorphConf"
DATAMORPH_PROPERTY_SUBSTITUTIONS: str = "substitutions"
DATAMORPH_PROPERTY_PARAMETERS: str = "parameters"
DATAMORPH_PROPERTY_CONNECTIONS: str = "connections"
DATAMORPH_PROPERTY_JOBPARAMS: str = "job_params"
DATAMORPH_PROPERTIES: str = "properties"

DATAMORPH_PROPERTY_NAME: str = "name"
DATAMORPH_PROPERTY_DESCRIPTION: str = "description"
DATAMORPH_PROPERTY_TYPE: str = "type"
DATAMORPH_PROPERTY_NODETYPE: str = "nodeType"
DATAMORPH_PROPERTY_TYPE_OVERRIDE: str = "type_override"

AIRFLOW_PROPERTY_DAG_ID: str = "dag_id"
AIRFLOW_PROPERTY_DESC: str = "description"

DATAMORPH_PREFIX = "datamorph_"

DATAMORPH_JOBPARAMS_STICKYPARAMS = "sticky_params"
DATAMORPH_JOBPARAMS_WORKFLOWRUNTINE = "workflowRuntime"
DATAMORPH_JOBPARAMS_PROFILEID="profileId"


NODE_SUCCESS: str = "_Success"
NODE_FAILURE: str = "_Failure"

DEFAULT_AWS_REGION: str = "" #"us-east-1"

DATAMORPH_PROPERTY_PIPELINE_ID= "pipeline_id"
