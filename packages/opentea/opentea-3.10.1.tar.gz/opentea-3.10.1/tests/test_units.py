# pylint: disable=missing-docstring


from opentea.gui_forms.node_widgets import hierachical_call


def test_hierachical_call():

    # no _ hidden (identity)
    in_ = ["aa", "bb", "cc"]
    names = ["Aa", "Bb", "Cc"]
    out = {"aa": "Aa", "bb": "Bb", "cc": "Cc"}
    assert hierachical_call(in_, names) == out

    # two _ hidden
    in_ = ["one_a", "one_b", "three"]
    names = ["First", "Second", "Third"]
    out = {"one_": {"one_a": "First", "one_b": "Second"}, "three": "Third"}
    assert hierachical_call(in_, names) == out

    # one _ hidden and not used
    in_ = ["one_a", "two", "three"]
    names = ["First", "Second", "Third"]
    out = {"one_a": "First", "two": "Second", "three": "Third"}
    assert hierachical_call(in_, names) == out

    # Tavbp ugly booby trap
    in_ = ["one", "one_a", "one_b", "three"]
    names = in_
    out = {"one": "one", "one_": {"one_a": "one_a", "one_b": "one_b"}, "three": "three"}
    assert hierachical_call(in_, names) == out
