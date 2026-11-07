"""Prepare descriptive evidence for the presentation plan; preserve all inputs."""
import csv
import hashlib
import json
import math
from bisect import bisect_left
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
IDS = ['20261031_nanyo_001','20261031_nanyo_002', *[f'20261101_nanyo_{i:03}' for i in range(1,6)]]
sources = {}
def read(path):
    sources[str(path.relative_to(ROOT)).replace('\\','/')] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def write(name, rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,list(dict.fromkeys(k for r in rows for k in r))); w.writeheader(); w.writerows(rows)
records=[]; summary=[]
for eid in IDS:
    base=ROOT/'aquabeacon-analysis/results'/eid
    acoustic=read(base/'evaluation/acoustic_depth.csv')
    optical=read(base/'mapping_light_tracking/camera_relative_candidates.csv')
    observations=read(base/'mapping_navigation/child_observations.csv')
    nav=read(base/'mapping_navigation/child_navigation.csv')
    t0=min(float(r['sync_utc_s']) for r in acoustic)
    depth=sorted((float(r['sync_utc_s']),float(r['pressure_depth_m'])) for r in acoustic if math.isfinite(float(r['pressure_depth_m'])))
    dt=[t for t,d in depth]
    def depth_at(t):
        i=bisect_left(dt,t); j=min([j for j in (i-1,i) if 0<=j<len(dt)],key=lambda j:abs(dt[j]-t))
        return depth[j][1] if abs(dt[j]-t)<=.75 else None
    stages=[('acoustic_candidate',acoustic,'sync_utc_s',lambda r:r['acoustic_candidate']=='True'),
            ('optical_direction',optical,'utc_s',lambda r:r['optical_candidate']=='True'),
            ('joint_range_ray_depth',observations,'utc_s',lambda r:r['method']=='ray_range_depth' and r['filter_used_horizontal']=='True'),
            ('ray_depth_fallback',observations,'utc_s',lambda r:r['method']=='ray_depth' and r['filter_used_horizontal']=='True'),
            ('navigation_available',nav,'utc_s',lambda r:r['position_available']=='True')]
    for stage,data,key,valid in stages:
        accepted=[]
        for row in data:
            t=float(row[key]); good=valid(row); d=depth_at(t)
            records.append(dict(experiment=eid,stage=stage,utc_s=t,elapsed_s=t-t0,valid=good,pressure_depth_proxy_m=d))
            if good and d is not None: accepted.append(d)
        summary.append(dict(experiment=eid,stage=stage,samples=len(data),valid_samples=sum(valid(r) for r in data),
             valid_fraction=sum(valid(r) for r in data)/len(data),depth_paired_samples=len(accepted),
             observed_depth_min_m=min(accepted) if accepted else '',observed_depth_max_m=max(accepted) if accepted else ''))
write('coverage_samples.csv',records);write('coverage_summary.csv',summary)
(OUT/'evidence_manifest.json').write_text(json.dumps({'inputs_sha256':sources,'definition':'Descriptive retained observations, NOT maximum operating depth or accuracy. Depth matched within 0.75 seconds; no extrapolation. Stage denominators differ.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(records),'summary':len(summary),'inputs':len(sources)}))
