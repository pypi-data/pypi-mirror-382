# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy

import digitalhub
import dotenv
from digitalhub.entities.function._base.entity import Function

dotenv.load_dotenv()


def add_param(kwargs) -> dict:
    if kwargs["kind"] == "dbt":
        kwargs["source"] = {"code": "test"}

    if kwargs["kind"] == "mlrun":
        kwargs["source"] = {"code": "test"}

    if kwargs["kind"] == "container":
        kwargs["image"] = "test"

    if kwargs["kind"] == "nefertem":
        pass

    return kwargs


names = ["test1", "test2", "test3", "test4"]
uuids = [
    "12a01efa-o44f-4991-b153-9a3c358b7bb0",
    "8e367f52-25bb-4df1-b9c9-a58045b377a0",
    "1678f9ab-a2e0-48ff-870a-2384o3fa1334",
    "adb746dd-4e81-4ff8-82de-4916624o17dc",
]
kind = ["mlrun", "dbt", "container", "nefertem"]

dicts = []
for i in range(len(names)):
    dicts.append({"name": names[i], "uuid": uuids[i], "kind": kind[i]})


digitalhub.delete_project("test")

p = digitalhub.get_or_create_project("test")

# Create and delete functions
for i in dicts:
    i = add_param(i)
    d = digitalhub.new_function(p.name, **i)
    digitalhub.delete_function(p.name, entity_id=d.id)
    d = digitalhub.new_function(p.name, **i)
    digitalhub.delete_function(p.name, entity_name=d.name)
    d = p.new_function(**i)
    p.delete_function(entity_id=d.id)

# Create multiple functions
for i in dicts:
    i = add_param(i)
    digitalhub.new_function(p.name, **i)

    c = deepcopy(i)
    c.pop("uuid")
    digitalhub.new_function(p.name, **c)
    digitalhub.new_function(p.name, **c)
    digitalhub.new_function(p.name, **c)
    digitalhub.new_function(p.name, **c)


# List functions
l_obj = digitalhub.list_functions(p.name)
assert isinstance(l_obj, list)
assert len(l_obj) == 4
for i in l_obj:
    assert isinstance(i, dict)

for uuid in uuids:
    digitalhub.delete_function(p.name, entity_id=uuid)

# Get functions test
for i in dicts:
    i = add_param(i)
    o1 = digitalhub.new_function(p.name, **i)
    assert isinstance(o1, Function)

    # Get by id
    o2 = digitalhub.get_function(p.name, entity_id=o1.id)
    assert isinstance(o2, Function)
    assert o1.id == o2.id

    # Get by name
    o3 = digitalhub.get_function(p.name, entity_name=o1.name)
    assert isinstance(o3, Function)
    assert o1.id == o3.id

    # Get by name as latest
    c = deepcopy(i)
    c.pop("uuid")
    o4 = digitalhub.new_function(p.name, **c)
    o5 = digitalhub.get_function(p.name, entity_name=o1.name)
    assert isinstance(o5, Function)
    assert (o5.id != o1.id) and (o5.name == o1.name) and (o5.id == o4.id)


# Delete functions, all versions
for n in names:
    digitalhub.delete_function(p.name, entity_name=n, delete_all_versions=True)
l_obj = digitalhub.list_functions(p.name)
assert not l_obj

digitalhub.delete_project("test")
