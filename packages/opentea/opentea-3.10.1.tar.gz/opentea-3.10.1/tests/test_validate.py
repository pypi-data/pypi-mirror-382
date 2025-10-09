# pylint: disable=missing-docstring

import yaml
import pytest
import copy

from opentea.noob.validate_light import validate_light, ValidationErrorShort
from opentea.noob.noob import nob_set


def test_validate_light(datadir):
    """Test nvalidate light"""
    schema_f = datadir.join("schema_validate.yaml")
    setup_f = datadir.join("setup_test.yaml")
    with open(schema_f, "r") as fin:
        schema = yaml.load(fin, Loader=yaml.FullLoader)
    with open(setup_f, "r") as fin:
        setup = yaml.load(fin, Loader=yaml.FullLoader)

    # Positive
    assert validate_light(setup, schema) is None

    # negatives
    tmp = copy.deepcopy(setup)
    nob_set(tmp, "aaa", "leaf_number")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, 1.0, "leaf_integer")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, 1.0, "leaf_string")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, "true", "leaf_boolean")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, [0.1, 0.1, "aaa"], "multiple_leaf")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp["multiple_object"][0], "foobar", "leaf_int1")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, {"option_c": {"leaf_opta": "setup_a"}}, "xor_object")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)

    tmp = copy.deepcopy(setup)
    nob_set(tmp, {"option_a": {"leaf_opta": 42}}, "xor_object")
    with pytest.raises(ValidationErrorShort):
        validate_light(tmp, schema)
