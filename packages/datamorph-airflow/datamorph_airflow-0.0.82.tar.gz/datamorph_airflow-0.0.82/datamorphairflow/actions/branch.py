from airflow.operators.python import BranchPythonOperator


class DMBranchOnReturnValueOperator(BranchPythonOperator):
    """
    Extension to branching operator to fork based on given conditional expression.
    """

    def __init__(
            self,
            branches,
            *args,
            **kwargs
    ):
        super().__init__(python_callable=branch_onret_val,
                         op_kwargs={'branches': branches},
                         provide_context=True, *args, **kwargs)


# todo multiple dependson ..now only with one
def branch_onret_val_using_variable(ti, **kwargs):
    branches = kwargs["branches"]
    dependsOn = kwargs["parenttask"][0]
    returnBranchList = []
    for node in branches:
        if "variable" in node:
            variable = node["variable"]
        else:
            variable = "return_value"
        match = node["match"]
        branch = node["branch"]
        returnValue = ti.xcom_pull(key=variable, task_ids=[dependsOn])[0]
        if returnValue.lower() == match.lower():
            returnBranchList.append(branch)
    return returnBranchList

def branch_onret_val(ti, **kwargs):
    branches = kwargs["branches"]
    returnBranchList = []
    for node in branches:
        properties = node["properties"]
        #logging.info(properties)
        match_expr = properties["match_expression"]
        #logging.info(match_expr)
        match = eval(match_expr)
        branch = properties["branch"]
        if match == True:
            returnBranchList.extend(branch)
    #logging.debug(returnBranchList)
    return returnBranchList