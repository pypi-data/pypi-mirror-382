from alidaparse.input import InParamFactory


def test_inparam():
    param = InParamFactory.from_cli(
        name="param_name", param_type=int, required=True, argv=["--param_name", "42"]
    )
    assert param.param_name == "param_name"
    assert param.param_value == 42


def test_bool_conversion_false():
    param = InParamFactory.from_cli(
        name="param_name",
        param_type=bool,
        required=True,
        argv=["--param_name", "False"],
    )
    assert param.param_name == "param_name"
    assert param.param_value == False


def test_bool_conversion_true():
    param = InParamFactory.from_cli(
        name="param_name", param_type=bool, required=True, argv=["--param_name", "True"]
    )
    assert param.param_name == "param_name"
    assert param.param_value == True
