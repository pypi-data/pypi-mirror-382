import json

from opentea.tools.schema2md import schema2md


def test_schema2md(datadir):
    schema_f = datadir.join("sample_schema.json")
    out_ref = datadir.join("out.md")
    with open(schema_f, "r") as fin:
        schema = json.load(fin)

    with open(out_ref, "r") as fin:
        out = fin.read()

    assert out == schema2md(schema)
