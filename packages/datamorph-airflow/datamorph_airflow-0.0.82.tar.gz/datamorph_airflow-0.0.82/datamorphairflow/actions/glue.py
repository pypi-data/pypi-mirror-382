from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

from datamorphairflow.hooks import WorkflowParameters


class DMAWSGlueRunNowJobOperator(GlueJobOperator):
    """
    Extension of aws glue run operator with custom status push to xcom
    """

    def __init__(self, run_job_kwargs=None, *args, **kwargs):
        super().__init__(run_job_kwargs=run_job_kwargs, **kwargs)
        self.jar_params = None
        if run_job_kwargs is None:
            run_job_kwargs = dict()
        self.run_job_kwargs = run_job_kwargs
        self.args = args
        self.kwargs = kwargs

    def execute(self, context):
        workflow_params = WorkflowParameters(context)
        params = workflow_params.get_params()
        print(params)
        params_key = "--params"
        params_value = ""


        # 1. Check if params is not empty
        # 2. If not empty, construct the required string/list "key1=value,key2=value"
        # 3. Update job run arguments with the constructed string above

        if params:
            for k,v in params.items():
                params_value = params_value + "," + f'{k}={v}'

        if params_key in self.run_job_kwargs:
            self.run_job_kwargs[params_key] += "," + params_value
        else:
            self.run_job_kwargs[params_key] = params_value

        print(self.run_job_kwargs)
        #conn_id = self.kwargs.get("conn_id")
        job_id = self.kwargs.get("job_name")
        task_id = f'{self.kwargs.get("task_id")}_custom'
        run_now = GlueJobOperator(task_id=task_id,job_name=job_id, script_args=self.run_job_kwargs, do_xcom_push=True).execute(context)




