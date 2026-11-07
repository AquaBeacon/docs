"""Check the plan's local sources, timing and numerical claims, without rendering slides."""
import csv
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
PLAN = Path(__file__).resolve().parents[1]
A = ROOT / 'aquabeacon-analysis'
checks = []
sources = set()

def check(name, condition, detail=None):
    checks.append(dict(name=name, passed=bool(condition), detail=detail))

def source(path):
    path = Path(path).resolve()
    sources.add(path)
    check('source_exists', path.is_file(), str(path.relative_to(ROOT)))
    return path

def rows(path):
    with source(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def centered_rms(data, columns):
    arrays = [[float(r[c]) for r in data] for c in columns]
    means = [sum(a) / len(a) for a in arrays]
    return math.sqrt(sum(sum((v-m)**2 for v in a) for a,m in zip(arrays,means)) / len(data))

docs = list(PLAN.glob('*.md'))
for doc in docs:
    text = doc.read_text(encoding='utf-8')
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if target.startswith(('http://', 'https://', 'thread://', '#')):
            continue
        path = (doc.parent / unquote(target.split('#')[0].strip('<>'))).resolve()
        check('markdown_link', path.exists(), f'{doc.name}: {target}')

spec = (PLAN / '01_スライド詳細.md').read_text(encoding='utf-8')
slides = re.findall(r'^## (\d{2}) .+?｜(\d+)秒｜(\d+):(\d+)〜(\d+):(\d+)$', spec, re.M)
elapsed = 0
for n, seconds, sm, ss, em, es in slides:
    start, end = int(sm)*60+int(ss), int(em)*60+int(es)
    check('slide_timing', start == elapsed and end-start == int(seconds), n)
    elapsed = end
check('slide_count', [int(s[0]) for s in slides] == list(range(1,22)), len(slides))
check('total_seconds', elapsed == 735, elapsed)

for rel in [
    'docs/presentations/以前の資料/MitouAquaBeacon.pptx',
    'docs/presentations/以前の資料/AquaBeacon.pptx',
    'assets/aquabeacon-cad-tour/preview/parent_exterior_0096.png',
    'assets/aquabeacon-cad-tour/preview/child_interior_0096.png',
    'aquabeacon-analysis/data/raw/ngtHighSchoolExperiment1/IMG_4393.MOV',
    'aquabeacon-analysis/data/raw/nanyo_experiment/Photos-1-001/IMG_8286.MOV',
    'aquabeacon-analysis/data/interim/20261028_ngt_004/synchronized/child/child_video.mp4',
    'aquabeacon-analysis/results/20261028_ngt_004/wall_mapping/rotation_corrected_20261031/blender_Estimated_route_and_wall.png',
    'aquabeacon-analysis/results/20261101_nanyo_003/poster_static/static_float_overhead.png',
    'aquabeacon-analysis/results/20261101_nanyo_003/poster_static/static_float_overhead.svg',
    'aquabeacon-analysis/results/20261101_nanyo_003/poster_static/static_float_overhead.figure.pickle',
    'aquabeacon-analysis/results/20261101_nanyo_003/poster_static/static_float_overhead.plot.json',
    'aquabeacon-analysis/results/20261101_nanyo_001/mapping_selected/scene.json',
    'aquabeacon-analysis/results/20261101_nanyo_001/mapping_selected/textured_map.glb',
    'firmware-experiments/reports/2026-10-10_005_gnss_rtk_ppk/README.md',
    'aquabeacon-sim/docs/reports/20_target_accuracy.md',
    'aquabeacon-analysis/calibration/camera_defaults.json',
]:
    source(ROOT / rel)

pool = rows(A / 'results/20261028_ngt_002/position_evaluation/rotation_corrected_20261031/positions_at_acoustic_events.csv')
pool = [r for r in pool if r['magnetic_position_available'] == 'True']
pool_rms = centered_rms(pool, ['relative_magnetic_east_m','relative_magnetic_north_m','relative_down_m'])
check('pool_rms', len(pool) == 53 and len({r['shot_seq'] for r in pool}) == 53 and abs(pool_rms-0.14776744768705125)<1e-9, pool_rms)
for eid, columns in [
    ('20261028_ngt_003',['parent_video_s','range_formula_available','optical_available','magnetic_position_available']),
    ('20261028_ngt_004',['parent_east_m','parent_north_m','child_east_declination0_m','child_north_declination0_m','approximate_global_available']),
]:
    data=rows(A / f'results/{eid}/position_evaluation/rotation_corrected_20261031/positions_5hz.csv')
    check('pool_plot_columns', all(c in data[0] for c in columns), eid)
source(A / 'results/20261028_ngt_000/coordinate_reassessment/position_comparison.csv')

sea = rows(A / 'results/20261101_nanyo_003/stationary_spectra/day2_101500/matched_positions.csv')
values = {}
for prefix, expected in [('corrected',0.13966445131709956), ('fixed_parent',1.4544686095717585)]:
    value = centered_rms(sea, [f'{prefix}_{c}_m' for c in ['east','north','up']])
    values[prefix]=value
    check('sea_rms_'+prefix, len(sea)==32 and abs(value-expected)<1e-9, value)

review = A / 'results/20261103_field_review_000/research_review'
for name in ['report.md','03_methods.md','04_pool.md','05_nanyo.md','06_simulation.md','07_mapping.md','simulation_comparison.csv','mapping_trials.csv']:
    source(review / name)
stationary = rows(review / 'stationary_summary.csv')
selected = [r for r in stationary if r['condition'].startswith('user_static')]
check('four_user_static_windows', len(selected)==4, [r['window'] for r in selected])

manifest = json.loads((PLAN / 'evidence_manifest.json').read_text(encoding='utf-8'))
for rel, expected in manifest['inputs_sha256'].items():
    path = source(ROOT / rel)
    check('coverage_source_hash', hashlib.sha256(path.read_bytes()).hexdigest()==expected, rel)
coverage = rows(PLAN / 'coverage_summary.csv')
check('coverage_seven_by_five', len(coverage)==35 and len({r['experiment'] for r in coverage})==7)
with (PLAN / 'coverage_samples.csv').open(encoding='utf-8') as f:
    coverage_count=sum(1 for _ in f)-1
check('coverage_sample_count', coverage_count==148820, coverage_count)

cuts=[]
day1_segments=json.loads(source(A/'results/20261031_nanyo_000/segmentation/manifest.json').read_text(encoding='utf-8'))
day1_sync=json.loads(source(A/'results/20261031_nanyo_000/synchronization/manifest.json').read_text(encoding='utf-8'))
for eid, start in [('20261031_nanyo_001',600),('20261031_nanyo_002',150),('20261101_nanyo_001',100),('20261101_nanyo_003',120)]:
    base=A / 'data/processed' / eid / 'videos'
    clocks={}
    for role in ['parent','child']:
        source(base / f'{role}.mp4')
        if eid.startswith('20261101'):
            clocks[role]=json.loads(source(base/f'{role}.clock.json').read_text(encoding='utf-8'))['pieces']
        else:
            segment=next(s for s in day1_segments['segments'] if s['experiment_id']==eid)
            video=next(v for v in segment['videos'] if v['role']==role)
            clocks[role]=[]
            if role=='child':
                key=next(k for k in day1_sync['cameras'] if k.startswith('child_'))
                clock=day1_sync['cameras'][key]
                clocks[role]=[dict(joined_start_s=0,joined_end_s=video['source_end_s']-video['source_start_s'],source_start_s=video['source_start_s'],utc_at_source_zero_s=clock['utc_at_video_zero_s'],time_scale=clock['time_scale'],sync_utc_start_s=video['sync_utc_start_s'],sync_utc_end_s=video['sync_utc_end_s'],validated_source_interval_s=clock['validated_interval_s'])]
            else:
                for part in day1_segments['parent_join_mapping']:
                    lo=max(part['joined_start_s'], video['source_start_s'])
                    hi=min(part['joined_end_s'], video['source_end_s'])
                    if hi<=lo:
                        continue
                    src_lo,src_hi=lo-part['joined_start_s'],hi-part['joined_start_s']
                    clocks[role].append(dict(joined_start_s=lo-video['source_start_s'],joined_end_s=hi-video['source_start_s'],source_start_s=src_lo,utc_at_source_zero_s=part['utc_at_source_zero_s'],time_scale=part['time_scale'],sync_utc_start_s=part['utc_at_source_zero_s']+part['time_scale']*src_lo,sync_utc_end_s=part['utc_at_source_zero_s']+part['time_scale']*src_hi,validated_source_interval_s=day1_sync['cameras'][part['camera_key']]['validated_interval_s']))
    endpoints=[]
    for c in [start, start+5]:
        p=next(p for p in clocks['child'] if p['joined_start_s'] <= c <= p['joined_end_s'])
        src=p['source_start_s']+c-p['joined_start_s']
        utc=p['utc_at_source_zero_s']+p['time_scale']*src
        q=next(p for p in clocks['parent'] if p['sync_utc_start_s'] <= utc <= p['sync_utc_end_s'])
        ps=(utc-q['utc_at_source_zero_s'])/q['time_scale']
        endpoints.append(dict(utc_s=utc,parent_clip_s=q['joined_start_s']+ps-q['source_start_s']))
        for role,piece,s in [('child',p,src),('parent',q,ps)]:
            interval=piece.get('validated_source_interval_s')
            check('video_clock_validated', interval is not None and interval[0]<=s<=interval[1], f'{eid}/{role}@{c}')
    cuts.append(dict(experiment=eid,child_start_s=start,child_end_s=start+5,parent_start_s=endpoints[0]['parent_clip_s'],parent_end_s=endpoints[1]['parent_clip_s'],utc_start_s=endpoints[0]['utc_s'],utc_end_s=endpoints[1]['utc_s']))

with (PLAN/'source_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,['path','exists','size_bytes']); writer.writeheader()
    writer.writerows(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),exists=p.is_file(),size_bytes=p.stat().st_size if p.is_file() else 0) for p in sorted(sources))
result=dict(checked_at=datetime.now(timezone.utc).isoformat(),passed=all(c['passed'] for c in checks),checks=checks,source_count=len(sources),video_cuts=cuts,scope='Plan and source verification only; no PPTX rendering or completed-video playback was performed.')
(PLAN/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=result['passed'],checks=len(checks),sources=len(sources),seconds=elapsed,failed=[c for c in checks if not c['passed']],video_cuts=cuts),ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
