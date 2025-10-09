import logging
import os

from airflow.models import BaseOperator
from airflow.operators.bash import BashOperator

from datamorphairflow.file_util import S3FileSystem


class DMBashOperator(BaseOperator):
    """
    Operator to run custom bash operator.
    """

    def __init__(
            self,
            bash_command: str,
            *args,
            **kwargs
    ):

        super(DMBashOperator, self).__init__(**kwargs)
        self.bash_command = bash_command

    def execute(self, context):
        # step1: check if the bashPath is on S3
        if self.bash_command.endswith(".sh") & self.bash_command.startswith("s3://"):
            # step2: copy jar to a tmp path on local
            s3resource = S3FileSystem(context)
            tempPath = s3resource.copyFromS3ToTempLocal(self.bash_command.lstrip("./"))
            # step3: create bash command and execute
            self.bash_command = "bash " + tempPath
            new_cmd = "bash " +  tempPath
            t1 = BashOperator(
                task_id='test',
                bash_command=new_cmd
            )
            t1.execute(dict())
            #super(DMBashOperator).execute(self,context)
            # step4: remove the tmp file
            #todo: change this to try catch
            if os.path.isfile(tempPath):
                os.remove(tempPath)
            else:
                logging.error("Error: %s file not found" % tempPath)

        else:
            t1 = BashOperator(
                task_id='test',
                bash_command=self.bash_command
            )
            t1.execute(dict())
