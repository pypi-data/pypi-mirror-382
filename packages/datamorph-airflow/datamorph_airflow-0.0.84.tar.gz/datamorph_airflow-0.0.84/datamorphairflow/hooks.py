import ast
import json
from typing import Dict, Any
from airflow.models import Variable


class WorkflowParameters:
    """
    Requires context to extract DataMorph workflow parameters
    """

    def __init__(
            self, context: Dict
    ) -> None:
        self.context = context
        self.dag_name = context["dag"].dag_id
        varname = "datamorph_" + self.dag_name
        self.var_name = varname

    def get_json_params(self) -> str:
        """
        Return all the parameters as a string object for workflow provided
        through the context
        :return:
        """
        # creating a dict
        param_as_json = Variable.get(self.var_name, default_var=None, deserialize_json=False)
        return param_as_json

    def get_params(self) -> dict:
        """
        Return all the parameters as a dictionary object for workflow provided
        through the context
        :return:
        """
        # creating a dict
        taskvar = Variable.get(self.var_name, default_var=None, deserialize_json=False)
        param_dict = ast.literal_eval(taskvar)
        return param_dict

    def items(self):
        """
        Set like object providing view on the parameter items
        :return:
        """
        return self.get_params().items()

    def get(self, key: str):
        """
        Retrieve value of the given parameter key
        :param key:
        :return:
        """
        return self.get_params().get(key)

    def pop(self, key: str):
        """
        Remove specified key and return the value
        :param key:
        :return:
        """
        return self.get_params().pop(key)

    def update(self, key: str = None, value: Any = None, params_dict: dict = None):
        """
        Update parameters with given key-value or dict
        :param params_dict:
        :param key:
        :param value:
        :return:
        """
        param2: dict = self.get_params()
        assert bool(params_dict) ^ (bool(key) & bool(value)), \
            "Either `params_dict` or 'key and value' should be provided"

        if params_dict:
            param2.update(params_dict)
            param_json2 = json.dumps(param2)
            Variable.update(self.var_name, param_json2, serialize_json=False)

        if key:
            param2.update({key: value})
            param_json2 = json.dumps(param2)
            Variable.update(self.var_name, param_json2, serialize_json=False)

    def set(self, key: str = None, value: Any = None, params_dict: dict = None):
        """
        Set parameters with given key-value or dict
        :param params_dict:
        :param key:
        :param value:
        :return:
        """
        param2: dict = self.get_params()
        assert bool(params_dict) ^ (bool(key) & bool(value)), \
            "Either `params_dict` or 'key and value' should be provided"

        if params_dict:
            param2.update(params_dict)
            param_json2 = json.dumps(param2)
            Variable.update(self.var_name, param_json2, serialize_json=False)

        if key:
            param2.update({key: value})
            param_json2 = json.dumps(param2)
            Variable.update(self.var_name, param_json2, serialize_json=False)
