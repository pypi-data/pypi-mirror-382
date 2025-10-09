import logging
from datamorphairflow.hooks import WorkflowParameters



"""
Python callable function that can be triggered in Python action node.

:param context: DataMorph workflow native context
:return: Any

DataMorph Parameters defined in the workflow can be accessed by initializing WorkflowParameters as follows:
parameters = WorkflowParameters(context)

Following are the available operations using WorkflowParameters:
--> items(): Returns set like object providing view on the parameters' collection
             items = parameters.items()
             logging.debug(f"List of parameters defined: {items} ")

--> get(key: str): Retrieves value for the given parameter key
                   input = parameters.get("input")

--> pop(key: str): Removes specified key and return the value
                   value = pop("input")

--> set(key: str, value: Any, params_dict: dict): Set parameters with given key-value or dict.
                  If the key is already present,value gets updated.  Setting/updating values
                  in this function modifies the workflow parameter collection globally.
                  parameters.set("error_count", 10)

Note: If the function name is changed, "Python Callable Name"  property should be updated.

todo    : add pip install datamorphairflow for local testing
          check the camel case for WorkflowParameters class
           any custom libraries needs to be installed via requirements.txt on the target airflow environment

"""


def python_callable_function(**context):
    """
    ## Uncomment this part to access parameters
    parameters = WorkflowParameters(context)
    items = parameters.items()
    logging.debug(f"List of parameters defined: {items} ")
    """
    """
    ## Implement custom logic here
    """


