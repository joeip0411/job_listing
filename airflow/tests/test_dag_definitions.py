import os

import pytest

from airflow.models import DagBag

DAG_BAG = DagBag(include_examples=False)

def get_dags():
    """
    Generate a tuple of dag_id, <DAG objects> in the DagBag
    """

    def strip_path_prefix(path):
        return os.path.relpath(path, os.environ.get("AIRFLOW_HOME"))

    return [(k, v, strip_path_prefix(v.fileloc)) for k, v in DAG_BAG.dags.items()]


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

class TestIcebergOptmize:

    dag_id = "iceberg_optimize"
    dag = DAG_BAG.get_dag(dag_id)
    tasks = dag.tasks

    def test_task_count(self):
        assert len(self.tasks) == 1

    def test_contain_task(self):
        task_ids = {t.task_id for t in self.tasks}
        assert task_ids == {'optimize_iceberg_table'}


class TestIcebergVacuum:

    dag_id = "iceberg_vacuum"
    dag = DAG_BAG.get_dag(dag_id)
    tasks = dag.tasks

    def test_task_count(self):
        assert len(self.tasks) == 1

    def test_contain_task(self):
        task_ids = {t.task_id for t in self.tasks}
        assert task_ids == {'expire_iceberg_snapshots'}

class TestJobListing:
    dag_id = "job_listing"
    dag = DAG_BAG.get_dag(dag_id)
    tasks = dag.tasks

    def test_task_count(self):
        assert len(self.tasks) == 24

    # def test_contain_task(self):
    #     task_ids = {t.task_id for t in self.tasks}
    #     assert task_ids == {'expire_iceberg_snapshots'}