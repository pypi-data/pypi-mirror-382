# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
import os
import time

import digitalhub as dh


def _is_finished(state: str):
    return state == "COMPLETED" or state == "ERROR" or state == "STOPPED"


os.environ["DHCORE_ENDPOINT"] = "http://localhost:8080/"
os.environ["DHCORE_WORKFLOW_IMAGE"] = "localhost:5000/dhcoreworkflow9:latest"
os.environ["KFP_ENDPOINT"] = "http://localhost:8888/"

# Get or create project
project = dh.get_or_create_project("project-kfp2")

url = "https://gist.githubusercontent.com/kevin336/acbb2271e66c10a5b73aacf82ca82784/raw/e38afe62e088394d61ed30884dd50a6826eee0a8/employees.csv"

di = project.new_dataitem(name="employees", kind="table", path=url)

function = project.get_function(entity_name="test-kfp")
if function is None:
    function = project.new_function(
        name="test-kfp",
        kind="kfp",
        source={"source": "test/testkfp_pipeline.py"},
        handler="myhandler",
    )


run = function.run("pipeline", parameters={"ref": di.key}, local_execution=True)
while not _is_finished(run.status.state):
    time.sleep(5)
    run = run.refresh()

print(str(run.status.to_dict()))
