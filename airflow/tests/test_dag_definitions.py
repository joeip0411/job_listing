import os

import pytest
from include.constants import DAG_EXPECTED_TASKS, DAG_TASKS_EXPECTED_DEPENDENCIES, DAGS_TO_IGNORE

from airflow.models import DagBag

DAG_BAG = DagBag(include_examples=False)


def get_dags():
    """
    Generate a tuple of dag_id, <DAG objects> in the DagBag
    """

    def strip_path_prefix(path):
        return os.path.relpath(path, os.environ.get("AIRFLOW_HOME"))
    return [(k,v, strip_path_prefix(v.fileloc)) for k,v in DAG_BAG.dags.items() if v.dag_id not in DAGS_TO_IGNORE]


def get_dags_expected_tasks():

    dags = get_dags()
    
    return [(d[0], d[1], d[2], set(d[1].tasks), DAG_EXPECTED_TASKS[d[0]]) for d in dags]


@pytest.mark.parametrize(
    "dag_id,dag,fileloc", get_dags(), ids=[x[2] for x in get_dags()],
)
def test_dag_has_required_attribute(dag_id, dag, fileloc):
    """
    test if a DAG is tagged and if those TAGs are in the approved list
    """
    assert dag.tags, f"{dag_id} in {fileloc} has no tags"
    assert dag.owner, f"{dag_id} in {fileloc} has no owner"
    assert dag.on_success_callback, f"{dag_id} in {fileloc} has no success callback"
    assert dag.on_failure_callback, f"{dag_id} in {fileloc} has no failure callback"
    assert not dag.catchup, f"{dag_id} in {fileloc} has catchup set to True"

@pytest.mark.parametrize(
    "dag_id,dag,fileloc,tasks,expected_tasks", get_dags_expected_tasks(), ids=[x[2] for x in get_dags()],
)
def test_dag_tasks_trigger_rule(dag_id,dag,fileloc,tasks,expected_tasks):
    """
    test if all tasks use the trigger_rule all_success
    """

    for task in tasks:
        t_rule = task.trigger_rule
        assert (
            t_rule == "all_success"
        ), f"{task.task_id} in {dag_id} has the trigger rule {t_rule}"

@pytest.mark.parametrize(
    "dag_id,dag,fileloc,tasks,expected_tasks", get_dags_expected_tasks(), ids=[x[2] for x in get_dags()],
)
def test_dag_tasks_matched_expected(dag_id, dag, fileloc, tasks, expected_tasks):
    ids_from_tasks = {t.task_id for t in tasks}
    assert ids_from_tasks == expected_tasks, f"{dag_id} in {fileloc} does not have the required tasks"

@pytest.mark.parametrize(
    "dag_id,dag,fileloc,tasks,expected_tasks", get_dags_expected_tasks(), ids=[x[2] for x in get_dags()],
)
def test_dag_tasks_correct_dependencies(dag_id, dag, fileloc, tasks, expected_tasks):
    for task in tasks:
        downstream_task_ids = set({t.task_id for t in task.downstream_list})
        expected_downstream_dependencies = DAG_TASKS_EXPECTED_DEPENDENCIES[dag_id][task.task_id]['downstream']
        assert downstream_task_ids == expected_downstream_dependencies,\
            f"{task.task_id} in {dag_id} in {fileloc} should have {', '.join(expected_downstream_dependencies)} as downstream dependencies"

        upstream_task_ids = set({t.task_id for t in task.upstream_list})
        expected_upstream_dependencies = DAG_TASKS_EXPECTED_DEPENDENCIES[dag_id][task.task_id]['upstream']
        assert upstream_task_ids == DAG_TASKS_EXPECTED_DEPENDENCIES[dag_id][task.task_id]['upstream'], \
            f"{task.task_id} in {dag_id} in {fileloc} should have {', '.join(expected_upstream_dependencies)} as upstream dependencies"