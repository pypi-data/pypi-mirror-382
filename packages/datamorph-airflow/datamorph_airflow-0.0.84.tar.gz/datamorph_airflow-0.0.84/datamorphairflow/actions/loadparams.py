import logging

from airflow.operators.python import PythonOperator
from datamorphairflow.file_util import S3FileSystem
from datamorphairflow.hooks import WorkflowParameters


class DMLoadParametersFromFileOperator(PythonOperator):
    """
    Load parameters from a JSON file with key value pairs.
    """

    def __init__(
            self,
            filepath,
            *args,
            **kwargs
    ):
        super().__init__(python_callable=load_params_from_file,
                         op_kwargs={'filepath': filepath},
                         provide_context=True, *args, **kwargs)



def load_params_from_file(**context):
    fileloc = context["filepath"]
    
    try:
        s3resource = S3FileSystem(context)
        workflow_params = WorkflowParameters(context)
        params = workflow_params.get_json_params()

        # Call the method with the filepath parameter
        return_params = s3resource.readJsonFromS3(fileloc)
        print(return_params)
        
        if bool(return_params):
            # Merge all JSON files into a single dictionary
            merged_params = {}
            for json_file in return_params:
                # Remove the _source_file metadata before merging
                file_params = {k: v for k, v in json_file.items() if k != '_source_file'}
                merged_params.update(file_params)
            
            workflow_params.update(params_dict=merged_params)
            logging.info(f"Successfully loaded and merged {len(return_params)} JSON files from {fileloc}")
        else:
            logging.info("No parameters to load")
            
    except Exception as e:
        logging.error(f"Failed to load parameters from {fileloc}: {str(e)}")
        raise
