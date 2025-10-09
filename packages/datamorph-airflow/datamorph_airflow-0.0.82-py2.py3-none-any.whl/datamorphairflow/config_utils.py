import json
import re
from typing import Optional

import boto3
from airflow.models import Variable

from datamorphairflow.datamorph_constants import DATAMORPH_PROPERTY_WORKFLOW, DATAMORPH_PROPERTY_DATAMORPHCONF, \
    DATAMORPH_PROPERTIES, DATAMORPH_PROPERTY_SUBSTITUTIONS, DATAMORPH_PROPERTY_PARAMETERS, DATAMORPH_PREFIX, \
    DATAMORPH_PROPERTY_NAME

from datamorphairflow import utils


def load_json_config_file(config_file_path: Optional[str] = None, s3bucket: Optional[str] = None,
                          s3key: Optional[str] = None, s3region: Optional[str] = None):
    """
    load json config file, example with workflow and variables attribute.
    substitute ${VAR} with its value from the variables key value pair.
    variables may or may not be provided.
    {
        "datamorphConf":{
            "variables":{
               "ENV1":"value1",
               "ENV2":"value2"
                }
        }
        "workflow": [
        "properties": {
            "parm1": 8000,
            "parm2": "${ENV1}",
            "parm3": "${ENV2}"
        }
        ]
    }
    :param config_file_path:
    :return:
    """

    def _substitute_params_in_dict(d, params, var_name):
        for key in d.keys():
            v = d.get(key)
            if isinstance(v, str):
                d[key] = re.sub('\$([a-zA-z0-9_-]+)', lambda m: "{{var.json." + var_name + "['" + m.group(1) + "']}}", v)
            elif isinstance(v, list):
                for each in v:
                    if not isinstance(each, str):
                        _substitute_params_in_dict(each, params, var_name)
            elif isinstance(v, dict):
                _substitute_params(v, params, var_name)

    def _substitute_params(d, params, var_name):
        if isinstance(d, list):
            for each in d:
                _substitute_params_in_dict(each, params, var_name)
        else:
            _substitute_params_in_dict(d, params, var_name)

    def _substitute_in_dict(d, variables):
        for key in d.keys():
            v = d.get(key)
            if isinstance(v, str):
                d[key] = re.sub('\${([a-zA-z0-9_-]+)}', lambda m: variables.get(m.group(1)), v)
            elif isinstance(v, list):
                for each in v:
                    if not isinstance(each, str):
                        _substitute_in_dict(each, variables)
            elif isinstance(v, dict):
                _substitute_vars(v, variables)

    def _substitute_vars(d, variables):
        if isinstance(d, list):
            for each in d:
                _substitute_in_dict(each, variables)
        else:
            _substitute_in_dict(d, variables)

    def _retrive_config(app_config):
        workflow = app_config[DATAMORPH_PROPERTY_WORKFLOW]
        datamorphConf = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTIES]
        # Substitute variables
        if utils.check_dict_key(datamorphConf, DATAMORPH_PROPERTY_SUBSTITUTIONS):
            variables = datamorphConf[DATAMORPH_PROPERTY_SUBSTITUTIONS]
            _substitute_vars(app_config, variables)
        # Add parameters to airflow variables
        if utils.check_dict_key(datamorphConf, DATAMORPH_PROPERTY_PARAMETERS):
            dag_name = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTY_NAME]
            var_name = DATAMORPH_PREFIX + dag_name
            parameters = app_config[DATAMORPH_PROPERTY_DATAMORPHCONF][DATAMORPH_PROPERTIES][DATAMORPH_PROPERTY_PARAMETERS]
            obj = Variable.get(var_name, default_var=None, deserialize_json=False)
            if obj is None:
                Variable.set(var_name, json.dumps(parameters), serialize_json=False)
            # check for any parameter substitutions in the workflow
            _substitute_params(workflow, parameters, var_name)

        return app_config

    if config_file_path:
        with open(config_file_path, 'r') as f:
            app_config = json.load(f)
            updated_config = _retrive_config(app_config)
            return updated_config

    elif s3key and s3bucket:
        s3res = boto3.resource('s3',
                               region_name=s3region)
        content_object = s3res.Object(s3bucket, s3key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        app_config = json.loads(file_content)
        updated_config = _retrive_config(app_config)
        return updated_config

    else:
        raise Exception('Configuration file not found: '.format(config_file_path))


