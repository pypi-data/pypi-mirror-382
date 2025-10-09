from airflow.operators.dummy import DummyOperator


class DMEmptyOperator(DummyOperator):
    """
    Extension of Dummy Operator
    """

    def __init__(
            self, *args, **kwargs
    ):
        super().__init__(do_xcom_push=True, **kwargs)

    def execute(self, context):
        super(DMEmptyOperator, self).execute(context)
