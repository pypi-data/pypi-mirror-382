# pylint: disable=missing-docstring

import os
import copy
import yaml
from opentea.noob.noob import nob_pprint, nob_set, nob_del

from opentea.noob.inferdefault import nob_complete


def test_nob_complete(datadir):
    """Test nob complete"""
    schema_f = datadir.join("schema_validate.yaml")
    setup_f = datadir.join("setup_test.yaml")
    with open(schema_f, "r") as fin:
        schema = yaml.load(fin, Loader=yaml.FullLoader)
    with open(setup_f, "r") as fin:
        setup = yaml.load(fin, Loader=yaml.FullLoader)

    # without initial data
    out = nob_complete(schema)
    assert out == setup

    # without initial data
    partial = copy.deepcopy(setup)
    partial = nob_del(partial, "multiple_object")
    partial = nob_del(partial, "leafs")
    nob_set(partial, "replaced", "leaf_opta")
    setup_changed = copy.deepcopy(setup)
    nob_set(setup_changed, "replaced", "leaf_opta")
    out_partial = nob_complete(schema, update_data=partial)
    print(nob_pprint(partial))
    assert out_partial == setup_changed


if __name__ == "__main__":
    test_nob_complete()
