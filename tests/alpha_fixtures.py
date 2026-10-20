"""Producer-shaped synthetic straight seams; no training/evaluation database."""
from pathlib import Path
import copy
import json
import numpy as np
from PIL import Image, ImageDraw

from fixtures import production, write
from paper_reconstruction_stage3.contracts import digest, sha256


def production_many(root, pieces=3, zero_last=True, scale=1):
    config = production(root); s1 = Path(config['stage1']); s2 = Path(config['stage2'])
    template = json.loads((s2/'pieces/p.json').read_text())
    row_template = template['stage1_provenance']; rows = []; records = []
    side = np.arange(32)/32
    xy = np.concatenate((np.column_stack((12+40*side, np.full(32, 12))),
                         np.column_stack((np.full(32, 52), 12+40*side)),
                         np.column_stack((52-40*side, np.full(32, 52))),
                         np.column_stack((np.full(32, 12), 52-40*side)))).astype(np.float32)
    tangent = np.repeat(np.array([[1, 0], [0, 1], [-1, 0], [0, -1]], np.float32), 32, axis=0)
    xy *= scale
    arrays = {'points_xy_crop': xy, 'points_xy_source': xy+[10, 20], 'arc_length_px': np.arange(128, dtype=np.float32)*1.25*scale,
        'tangent_xy': tangent, 'inward_normal_xy': np.column_stack((-tangent[:, 1], tangent[:, 0])),
        'curvature_per_px': np.zeros(128, np.float32), 'corner_strength': np.zeros(128, np.float32),
        'inward_thickness_px': np.full(128, 40*scale, np.float32),
        'role_probabilities': np.tile(np.array([.9, .05, .05], np.float32), (128, 1)),
        'transition_probabilities': np.full(128, .2, np.float32)}
    image = Image.new('RGB', (64*scale, 64*scale), 'white'); image.save(s1/'pieces/p.png')
    mask = Image.new('L', (64*scale, 64*scale)); ImageDraw.Draw(mask).rectangle((12*scale, 12*scale, 52*scale-1, 52*scale-1), fill=255); mask.save(s1/'masks/p.png')
    image_hash = sha256(s1/'pieces/p.png'); mask_hash = sha256(s1/'masks/p.png')
    for i in range(pieces):
        name = f'capture_{i:02d}'; row = {**row_template, 'capture_id': name, 'bbox_xywh': [10, 20, 64*scale, 64*scale]}; rows.append(row)
        fp = digest({'row': row, 'piece_sha256': image_hash, 'piece_mask_sha256': mask_hash})
        np.savez_compressed(s2/('pieces/'+name+'.npz'), **arrays)
        candidate = copy.deepcopy(template['candidate_fragments'][0]); first, last = (32, 63) if i % 2 == 0 else (96, 127)
        candidate.update(start_index=first, end_index=last, length_points=32, length_fraction=.25, wraps=False)
        for end, index in (('start', first), ('end', last)):
            candidate[end+'_xy_crop'] = xy[index].tolist(); candidate[end+'_xy_source'] = (xy[index]+[10, 20]).tolist()
        record = {**template, 'capture_id': name, 'piece_id': name, 'stage1_provenance': row,
            'stage1_record_fingerprint': fp, 'piece_sha256': image_hash, 'piece_mask_sha256': mask_hash,
            'point_count': 128, 'arrays_path': 'pieces/'+name+'.npz', 'arrays_sha256': sha256(s2/('pieces/'+name+'.npz')),
            'candidate_fragments': [] if zero_last and i == pieces-1 else [candidate],
            'candidate_count': 0 if zero_last and i == pieces-1 else 1}
        records.append(record)
    manifest_path = s1/'segmentation_manifest.jsonl'; manifest_path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    manifest_hash = sha256(manifest_path)
    input_hash = digest({'manifest_sha256': manifest_hash, 'include_unaccepted': False, 'maximum_pieces': None,
                         'capture_fingerprints': [r['stage1_record_fingerprint'] for r in records]})
    cfg = {'include_unaccepted': False, 'maximum_pieces': None, 'stage1_input_fingerprint': input_hash}
    summaries = []
    for record in records:
        record.update(config_hash=digest(cfg), stage1_input_fingerprint=input_hash)
        rel = 'pieces/'+record['capture_id']+'.json'; write(s2/rel, record)
        summaries.append({k: record[k] for k in ('capture_id', 'piece_id', 'arrays_path', 'point_count', 'candidate_count', 'stage1_record_fingerprint')} | {'record_path': rel})
    m = json.loads((s2/'edge_hypotheses_manifest.json').read_text())
    m.update(configuration=cfg, config_hash=digest(cfg), stage1_manifest_sha256=manifest_hash,
             stage1_input_fingerprint=input_hash, pieces=summaries, piece_count=pieces, candidate_count=sum(r['candidate_count'] for r in records))
    write(s2/'edge_hypotheses_manifest.json', m)
    return config


def rows_for(gallery):
    h = np.array([[1., 0., 40.], [0., 1., -1.25], [0., 0., 1.]])
    a, b = [gallery[i][1]['entry']['piece_id'] for i in (0, 1)]
    pose = {'query': 0, 'target': 1, 'windows': [None, None], 'span_a': None, 'span_b': None,
            'alignment': {'transform': h.tolist(), 'query_arc_fraction': [0., 1.], 'target_arc_fraction': [0., 1.], 'geometry_score': .9}}
    row = {'record_id': 'duplicate-alias', 'source_record_id': 'source', 'piece_a': a, 'piece_b': b, 'pose': pose,
           'canonical_transform_target_b_to_query_a': h.tolist(),
           'methods': {'mlp_start': {'weight': .9, 'parent_rank': 1, 'reason': 'retained', 'score_scope': 'fixture'}},
           'visual_evidence': {'informative': False, 'reason': 'white_fixture'}}
    return {'source_control': {'records': [row]}}
