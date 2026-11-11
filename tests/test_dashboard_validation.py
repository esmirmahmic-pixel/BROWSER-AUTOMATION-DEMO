import pytest
from automation.build_dashboard import validate

def valid(): return {'schema_version':2,'total':3,'passed':3,'failed':0,'skipped':0,'pytest_exit_code':0}

def test_valid_dashboard_summary(): validate(valid())

@pytest.mark.parametrize('change',[{'total':4},{'passed':2},{'skipped':-1},{'pytest_exit_code':1},{'total':True},{'schema_version':1},{'failed':1,'passed':1}])
def test_reject_invalid_summary(change):
    data=valid();data.update(change)
    with pytest.raises(ValueError): validate(data)
