import pytest
from automation.history import record_run,summarize

def test_empty_history(tmp_path):
    s=summarize(tmp_path/'runs.sqlite3')
    assert s['total']==s['passed']==s['failed']==s['skipped']==0

def test_history_statistics(tmp_path):
    db=tmp_path/'runs.sqlite3'
    record_run(db,'form_submission','passed',100)
    record_run(db,'timeout_recovery','failed',300,'Timed out')
    assert summarize(db)=={'total':2,'passed':1,'failed':1,'skipped':0,'success_rate':50.0,'average_duration_ms':200.0}

@pytest.mark.parametrize('status,duration,error',[('unknown',10,None),('passed',-1,None),('passed',10,'unexpected')])
def test_reject_invalid_runs(tmp_path,status,duration,error):
    with pytest.raises(ValueError): record_run(tmp_path/'runs.sqlite3','demo',status,duration,error)

def test_skipped_excluded_from_success_rate(tmp_path):
    db=tmp_path/'runs.sqlite3'
    record_run(db,'a','passed',10)
    record_run(db,'b','skipped',0)
    s=summarize(db)
    assert (s['total'],s['passed'],s['skipped'],s['success_rate'])==(2,1,1,100.0)

def test_same_test_is_upserted(tmp_path):
    db=tmp_path/'runs.sqlite3'
    record_run(db,'a','passed',10)
    record_run(db,'a','failed',20,'teardown failed')
    s=summarize(db)
    assert (s['total'],s['passed'],s['failed'])==(1,0,1)
