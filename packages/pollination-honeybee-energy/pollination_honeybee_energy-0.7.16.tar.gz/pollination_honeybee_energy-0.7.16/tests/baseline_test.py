from pollination.honeybee_energy.baseline import ModelToBaseline, \
    AppendixGSummary, LeedV4Summary
from queenbee.plugin.function import Function


def test_model_to_baseline():
    function = ModelToBaseline().queenbee
    assert function.name == 'model-to-baseline'
    assert isinstance(function, Function)


def test_appendix_g_summary():
    function = AppendixGSummary().queenbee
    assert function.name == 'appendix-g-summary'
    assert isinstance(function, Function)


def test_leed_v4_summary():
    function = LeedV4Summary().queenbee
    assert function.name == 'leed-v4-summary'
    assert isinstance(function, Function)
