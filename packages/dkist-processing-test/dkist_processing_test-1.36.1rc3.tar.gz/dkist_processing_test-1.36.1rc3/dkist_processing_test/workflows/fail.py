"""
Workflow which is designed to fail
"""

from dkist_processing_core import Workflow

from dkist_processing_test.tasks import FailTask

fail = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="fail",
    workflow_package=__package__,
)
fail.add_node(task=FailTask, upstreams=None)
