import json
import logging
import os

from airflow.operators.bash import BashOperator
from datamorphairflow.file_util import S3FileSystem

from datamorphairflow import utils

from datamorphairflow.hooks import WorkflowParameters


class DMRunJavaJarOperator(BashOperator):
    """
    Operator to run java jar with given arguments.
    """

    def __init__(
            self,
            jarPath: str,
            className: str,
            arguments: str = None,
            systemparams: str = "",
            jvmoptions: str = None,
            *args,
            **kwargs
    ):


        DEFAULT_CLASSNAME = "ai.datamorph.DataMorphWorkflowHook"
        arguments = "" if not bool(arguments) else " "+ arguments
        jvmoptions = "" if not bool(jvmoptions) else " "+ jvmoptions
        cmd = 'java ' + jvmoptions + ' ' + ' -cp' +  jarPath + ' ' + systemparams + ' ' + DEFAULT_CLASSNAME + ' ' + arguments
        super().__init__(bash_command=cmd, *args, **kwargs)
        self.jarpath = jarPath
        self.classname = DEFAULT_CLASSNAME
        self.arguments = arguments
        self.systemparams = systemparams
        self.bash_command = cmd
        self.classname_extn = className
        self.jvmoptions = jvmoptions

    def execute(self, context):
        DM_CLASSNAME_PROP = "-Ddm.javahook.classname="
        DM_JSONPARAMS_PROP = "-Ddm.javahook.parameters="
        workflow_params = WorkflowParameters(context)
        params = workflow_params.get_json_params()
        print(params)
        print(str(params))
        dag_system_params = DM_CLASSNAME_PROP + self.classname_extn + " " + DM_JSONPARAMS_PROP + "\"" + str(params).replace("\"","\\\"") + "\"" + " " + self.systemparams
        self.systemparams = dag_system_params
        #TODO: Multiple dependency jars
        # step1: check if the jarPath is on S3
        if utils.is_s3_file(self.jarpath):
            # step2: copy jar to a tmp path on local
            s3resource = S3FileSystem(context)
            tempPath = s3resource.copyFromS3ToTempLocal(self.jarpath)
            # step3: create bash command and execute
            cmd = 'java ' + self.jvmoptions + ' -cp ' + ' ' + tempPath + ' ' + dag_system_params + " " + self.classname + " " + self.arguments
            self.bash_command = cmd
            return_value = super(DMRunJavaJarOperator, self).execute(context)
            # step4: remove the tmp file
            if os.path.isfile(tempPath):
                os.remove(tempPath)
            else:
                logging.error("Error: %s file not found" % tempPath)
        else:
            # step3: create bash command and execute
            cmd = 'java ' + self.jvmoptions + ' -cp ' + ' ' + self.jarpath + ' ' + dag_system_params + " " + self.classname + " " + self.arguments
            self.bash_command = cmd
            return_value = super(DMRunJavaJarOperator, self).execute(context)


        # parse return value from string to dict and add to workflow_params
        print(return_value)
        return_params = json.loads(return_value)
        if bool(return_params):
            workflow_params.update(params_dict=return_params)
