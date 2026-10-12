"""Synthetic decision regression only. These results are not OCR accuracy."""
import json
import tempfile
from pathlib import Path
from backend.store import Store


def evaluate():
    cases=json.loads((Path(__file__).parent/'fixtures/decision-cases.json').read_text())
    with tempfile.TemporaryDirectory() as folder:
        store=Store(Path(folder)/'experiment.sqlite3')
        results=[]
        for i,case in enumerate(cases):
            observation={k:case[k] for k in ['plate','confidence','fault']}
            actual=store.scan(dict(request_id=f'fixture-{i}',**observation))['decision']
            results.append(dict(name=case['name'],expected=case['expected'],actual=actual,passed=actual==case['expected']))
            store.clear()
    return dict(kind='synthetic_decision_regression', real_ocr=False,
                total=len(results),passed=sum(r['passed'] for r in results),cases=results)


if __name__=='__main__':
    report=evaluate()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['passed']==report['total'] else 1)
