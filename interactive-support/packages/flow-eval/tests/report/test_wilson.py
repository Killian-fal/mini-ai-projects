from interactive_support_flow_eval.report.wilson import wilson


def test_wilson_interval():
    low, high = wilson(45, 50)
    assert (round(low, 3), round(high, 3)) == (0.786, 0.957)
    assert wilson(0, 10)[0] == 0.0
    assert wilson(10, 10)[1] == 1.0
