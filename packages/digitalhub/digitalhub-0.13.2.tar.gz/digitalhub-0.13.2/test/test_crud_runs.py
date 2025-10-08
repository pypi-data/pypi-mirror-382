# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
import digitalhub
import dotenv
from digitalhub.entities.run._base.entity import Run

dotenv.load_dotenv()


def add_param(kwargs) -> dict:
    if kwargs["kind"] == "mlrun+run":
        kwargs["task"] = t1._get_task_string()

    if kwargs["kind"] == "dbt+run":
        kwargs["task"] = t2._get_task_string()

    if kwargs["kind"] == "container+run":
        kwargs["task"] = t3._get_task_string()

    if kwargs["kind"] == "nefertem+run":
        kwargs["task"] = t4._get_task_string()

    kwargs["local_execution"] = True

    return kwargs


names = ["test1", "test2", "test3", "test4"]
uuids = [
    "12a01efa-o44f-4991-b153-9a3c358b7bb0",
    "8e367f52-25bb-4df1-b9c9-a58045b377a0",
    "1678f9ab-a2e0-48ff-870a-2384o3fa1334",
    "adb746dd-4e81-4ff8-82de-4916624o17dc",
]
kind = ["mlrun+run", "dbt+run", "container+run", "nefertem+run"]

dicts = []
for i in range(len(names)):
    dicts.append({"name": names[i], "uuid": uuids[i], "kind": kind[i]})

digitalhub.delete_project("test")

p = digitalhub.get_or_create_project("test")

f1 = p.new_function(name="t1", kind="mlrun", source={"code": "test"})
t1 = f1.new_task(kind="mlrun+job")
f2 = p.new_function(name="t2", kind="dbt", source={"code": "test"})
t2 = f2.new_task(kind="dbt+transform")
f3 = p.new_function(name="t3", kind="container", image="test")
t3 = f3.new_task(kind="container+job")
f4 = p.new_function(name="t4", kind="nefertem")
t4 = f4.new_task(kind="nefertem+infer", framework="test")


# Create and delete runs
for i in dicts:
    i = add_param(i)
    d = digitalhub.new_run(p.name, **i)
    digitalhub.delete_run(p.name, entity_id=d.id)

# Create multiple runs
for i in dicts:
    i = add_param(i)
    digitalhub.new_run(p.name, **i)

# List runs
l_obj = digitalhub.list_runs(p.name)
assert isinstance(l_obj, list)
assert len(l_obj) == 4
for i in l_obj:
    assert isinstance(i, dict)

for uuid in uuids:
    digitalhub.delete_run(p.name, entity_id=uuid)

# Get runs test
for i in dicts:
    i = add_param(i)
    o1 = digitalhub.new_run(p.name, **i)
    assert isinstance(o1, Run)

    # Get by id
    o2 = digitalhub.get_run(p.name, entity_id=o1.id)
    assert isinstance(o2, Run)
    assert o1.id == o2.id

digitalhub.delete_project("test")
