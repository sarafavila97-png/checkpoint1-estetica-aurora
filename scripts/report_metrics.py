"""Aggregate observed evaluations; never substitute judge scores for correctness.

Costs must use one currency and a documented scope/rate date in the source
report. Missing costs remain null; projections are estimates, not invoices.
"""
from collections import Counter
import math

def summarize_runs(rows):
    costs=[]
    errors=Counter()
    for row in rows:
        if type(row.get('correct')) is not bool:
            raise ValueError('Each run needs an independently assessed boolean correct')
        cost=row.get('cost',row.get('provider_cost'))
        if cost is not None:
            if type(cost) not in (int,float) or not math.isfinite(cost) or cost<0:
                raise ValueError('Cost must be finite, nonnegative or null')
            costs.append(cost)
        if not row['correct']:
            errors[str(row.get('error_category') or 'unclassified')]+=1
    n=len(rows)
    total=math.fsum(costs) if n and len(costs)==n else None
    return dict(runs=n,correct=sum(r['correct'] for r in rows),
                precision_pct=100*sum(r['correct'] for r in rows)/n if n else None,
                error_categories=dict(sorted(errors.items())),cost_coverage=len(costs),
                known_cost_subtotal=math.fsum(costs),total_cost=total,
                mean_cost=total/n if total is not None else None,
                projected_cost_1000=total/n*1000 if total is not None else None)

def compare_ab(rows):
    """Require the assignment's five unique matched cases per architecture."""
    groups={a:[r for r in rows if r.get('architecture')==a] for a in ('A','B')}
    if len(rows)!=10 or any(len(g)!=5 for g in groups.values()):
        raise ValueError('Exactly five A and five B runs required')
    cases={a:[r.get('case_id') for r in g] for a,g in groups.items()}
    ids=[r.get('run_id') for r in rows]
    if any(not isinstance(v,str) or not v for v in ids) or len(set(ids))!=10:
        raise ValueError('Ten unique nonempty run IDs required')
    for values in cases.values():
        if any(not isinstance(v,str) or not v for v in values) or len(set(values))!=5:
            raise ValueError('Five unique nonempty case IDs per architecture required')
    if set(cases['A'])!=set(cases['B']):
        raise ValueError('A/B cases must match')
    a,b=(summarize_runs(groups[k]) for k in ('A','B'))
    delta=None if a['projected_cost_1000'] is None or b['projected_cost_1000'] is None else b['projected_cost_1000']-a['projected_cost_1000']
    return {'A':a,'B':b,'precision_delta_points':b['precision_pct']-a['precision_pct'],
            'projected_cost_delta_1000':delta,'projection_basis':'sample mean × 1000; same documented cost scope and currency required'}

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--ab',action='store_true')
    args=parser.parse_args();rows=json.loads(args.input.read_text())
    print(json.dumps(compare_ab(rows) if args.ab else summarize_runs(rows),ensure_ascii=False,indent=2,allow_nan=False))
