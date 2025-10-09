# pylint: disable=missing-docstring
import os
import yaml
import inspect
from opentea.gui_forms.otinker import main_otinker


def test_guiform(datadir):
    """Test nob complete"""
    schema_f = datadir.join("schema_calculator.yaml")

    with open(schema_f, "r") as fin:
        schema = yaml.load(fin, Loader=yaml.FullLoader)
        base_dir = inspect.getfile(inspect.currentframe())
        base_dir = os.path.dirname(os.path.abspath(base_dir))
        main_otinker(schema, calling_dir=base_dir, start_mainloop=False)
