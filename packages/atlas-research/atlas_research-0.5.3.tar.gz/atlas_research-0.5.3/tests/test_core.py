from atlas.core import run_analysis

def test_run_analysis_returns_result():
    result = run_analysis("graph neural networks")
    assert result is not None