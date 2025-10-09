# pylint: disable=missing-docstring

import copy
from opentea.noob.noob import (
    nob_get,
    nob_get_only_child,
    nob_set,
    nob_find,
    nob_find_unique,
    nob_node_exist,
    nob_del,
    nob_merge_agressive,
    nob_pprint,
)

NOB_DICT = {
    "b1": {"b11": "chuck norris"},
    "b2": {"b21": [{"b211", "chow yun fat"}, {"b212", "jean claude vandamme"}]},
}


def test_nob_get():
    """Test nob get."""
    assert nob_get(NOB_DICT, "b11") == "chuck norris"
    assert nob_get(NOB_DICT, "b21")[1] == {"b212", "jean claude vandamme"}

    assert nob_get(NOB_DICT, "bullshit", failsafe=True) == None


def test_nob_get_only_child():
    """Test nob get only child."""
    assert nob_get_only_child(NOB_DICT, "b1") == "b11"


def test_nob_set():
    """Test nob set."""
    nob_test = copy.deepcopy(NOB_DICT)
    nob_set(nob_test, "snake plisken", "b21")
    assert nob_get(nob_test, "b21") == "snake plisken"


def test_nob_find():
    """Test multiple match finder."""
    same_keys_dict = {"b1": {"b11": "chuck norris"}, "b2": {"b11": "JCVD"}}

    out_list = [["b1", "b11"], ["b2", "b11"]]
    assert nob_find(same_keys_dict, "b11") == out_list


def test_nob_find_unique():
    """Test multiple match finder."""
    out_list = ["b1", "b11"]
    assert nob_find_unique(NOB_DICT, "b11") == out_list


def test_nob_node_exist():
    """Test multiple match finder."""
    assert nob_node_exist(NOB_DICT, "b11") is True
    assert nob_node_exist(NOB_DICT, "bullshit") is False


def test_nob_del():
    """Test job del, nob_del is not a deletion inplace."""
    nob_test = copy.deepcopy(NOB_DICT)
    nob_out = nob_del(nob_test, "b2", verbose=True)
    assert nob_test == NOB_DICT
    assert nob_out == {"b1": {"b11": "chuck norris"}}


def test_nob_merge_agressive():
    """Test aggressive merge"""
    dict1 = {"b1": {"b11": "chuck norris"}, "b2": {"b21": "JCVD"}}
    dict2 = {"b2": {"b22": "Jet li"}}

    dict_out = {"b1": {"b11": "chuck norris"}, "b2": {"b21": "JCVD", "b22": "Jet li"}}

    assert nob_merge_agressive(dict1, dict2) == dict_out


def test_pprint():
    """Test pprint function with level limitation."""
    out_pp = """b1: (...)\nb2: (...)\n"""
    assert nob_pprint(NOB_DICT, max_lvl=1) == out_pp
