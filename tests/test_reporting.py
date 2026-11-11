import json
from automation.history import record_run,summarize

def test_summary_can_be_exported_as_json(tmp_path):
    db=tmp_path/'results.sqlite3'
    record_run(db,'test_login','passed',120)
    record_run(db,'test_timeout','failed',80,'Timeout')
    target=tmp_path/'summary.json'
    target.write_text(json.dumps({'schema_version':2,**summarize(db)}),encoding='utf-8')
    data=json.loads(target.read_text(encoding='utf-8'))
    assert data['total']==2 and data['success_rate']==50.0 and data['failed']==1
