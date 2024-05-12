import glob
import importlib.util
import os

import pytest

from airflow.models import DAG, DagBag
from airflow.utils.dag_cycle_tester import check_cycle

DAG_PATH = os.path.join(
   os.path.dirname(__file__), "..", "dags/*.py",
)
DAG_FILES = glob.glob(DAG_PATH, recursive=True)

DAG_BAG = DagBag(include_examples=False)

@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_dag_cycle(dag_file):
   """Check for cycles in DAGs
   """
   module_name, _ = os.path.splitext(dag_file)
   module_path = os.path.join(DAG_PATH, dag_file)
   mod_spec = importlib.util.spec_from_file_location(module_name, module_path)
   module = importlib.util.module_from_spec(mod_spec)
   mod_spec.loader.exec_module(module)
 
   dag_objects = [var for var in vars(module).values() if isinstance(var, DAG)]
 
   assert dag_objects
 
   for dag in dag_objects:
       check_cycle(dag)


def get_import_errors():
    """
    Generate a tuple for import errors in the dag bag
    """

    def strip_path_prefix(path):
        return os.path.relpath(path, os.environ.get("AIRFLOW_HOME"))

    # prepend "(None,None)" to ensure that a test object is always created even if it's a no op.
    return [(None, None)] + [
        (strip_path_prefix(k), v.strip()) for k, v in DAG_BAG.import_errors.items()
    ]


@pytest.mark.parametrize(
    "rel_path,rv", get_import_errors(), ids=[x[0] for x in get_import_errors()],
)
def test_file_imports(rel_path, rv):
    """Test for import errors on a file"""
    if rel_path and rv:
        raise Exception(f"{rel_path} failed to import with message \n {rv}")
    


