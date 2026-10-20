from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from paper_reconstruction_stage3.contracts import FROZEN, digest, sha256
RELEASE = Path(__file__).resolve().parent / "frozen_stage2_release.json"

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def arrays(n=64):
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return {"points_xy": np.column_stack((31 + 20 * np.cos(angles), 31 + 20 * np.sin(angles))).astype(np.float32),
        "arc_length_px": (np.arange(n) * 2 * np.pi * 20 / n).astype(np.float32),
        "tangent_xy": np.column_stack((-np.sin(angles), np.cos(angles))).astype(np.float32),
        "inward_normal_xy": np.column_stack((-np.cos(angles), -np.sin(angles))).astype(np.float32),
        "curvature_per_px": np.full(n, 0.05, np.float32), "corner_strength": np.zeros(n, np.float32), "inward_thickness_px": np.full(n, 15, np.float32)}

def images(image, mask):
    image.parent.mkdir(parents=True, exist_ok=True)
    mask.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 64), "white").save(image)
    m = Image.new("L", (64, 64), 0)
    ImageDraw.Draw(m).ellipse((11, 11, 51, 51), fill=255)
    m.save(mask)

def candidate():
    return {"start_index": 60, "end_index": 3, "length_points": 8, "wraps": True, "rank": 1, "score": 0.9, "source": "default", "hypothesis": "parent_raw", "split_threshold": None}

def base_config(root, mode):
    return {"mode": mode, "output": str(root / "audit"), "release": str(RELEASE), "identity_policy": "frozen" if mode == "production" else "contract", "resume": False, "quiet": True, "rehash_resume": False, "limit_puzzles": None, "geometry_only": False, "allow_legacy_stage2": False}

def production(root, zero=False):
    s1, s2 = root / "stage1", root / "stage2"
    images(s1 / "pieces/p.png", s1 / "masks/p.png")
    row = {"capture_id": "capture_p", "schema_version": "paper-segmentation-manifest-1.0", "accepted": True, "bbox_xywh": [10, 20, 64, 64], "original_size_hw": [200, 200], "piece_path": "pieces/p.png", "piece_mask_path": "masks/p.png"}
    (s1 / "segmentation_manifest.jsonl").write_text(json.dumps(row) + "\n")
    image_hash, mask_hash = sha256(s1 / "pieces/p.png"), sha256(s1 / "masks/p.png")
    record_hash = digest({"row": row, "piece_sha256": image_hash, "piece_mask_sha256": mask_hash})
    manifest_hash = sha256(s1 / "segmentation_manifest.jsonl")
    input_hash = digest({"manifest_sha256": manifest_hash, "include_unaccepted": False, "maximum_pieces": None, "capture_fingerprints": [record_hash]})
    cfg = {"include_unaccepted": False, "maximum_pieces": None, "stage1_input_fingerprint": input_hash}
    a = arrays()
    xy = a.pop("points_xy")
    a.update({"points_xy_crop": xy, "points_xy_source": xy + [10, 20], "role_probabilities": np.tile(np.array([0.9, 0.05, 0.05], np.float32), (64, 1)), "transition_probabilities": np.full(64, 0.2, np.float32)})
    (s2 / "pieces").mkdir(parents=True)
    np.savez_compressed(s2 / "pieces/p.npz", **a)
    c = candidate()
    c["candidate_id"] = "candidate_0001"
    for name, i in (("start", 60), ("end", 3)):
        c[name + "_xy_crop"] = xy[i].tolist()
        c[name + "_xy_source"] = (xy[i] + [10, 20]).tolist()
    release = {"release_version": "1.0.0", "model_format": "onnx", "runtime": "onnxruntime-cpu", "model_sha256": FROZEN["onnx"], "source_checkpoint_sha256": FROZEN["checkpoint"], "release_manifest_sha256": FROZEN["release"]}
    r = {**release, "schema_version": "stage2.edge-hypotheses.v1", "capture_id": "capture_p", "piece_id": "capture_p", "config_hash": digest(cfg), "stage1_input_fingerprint": input_hash, "stage1_record_fingerprint": record_hash, "stage1_provenance": row, "piece_sha256": image_hash, "piece_mask_sha256": mask_hash,
        "point_order": "clockwise_circular", "role_names": ["seam", "page_border", "uncertain"], "point_count": 64, "arrays_path": "pieces/p.npz", "arrays_sha256": sha256(s2 / "pieces/p.npz"), "overlay_path": None, "candidate_count": 0 if zero else 1, "candidate_fragments": [] if zero else [c],
        "coordinate_frames": {"crop_to_source_homography": [[1, 0, 10], [0, 1, 20], [0, 0, 1]], "piece_crop": {"origin": "top_left", "x_axis": "right", "y_axis": "down", "units": "pixels"}, "source_capture": {"origin": "top_left", "x_axis": "right", "y_axis": "down", "units": "pixels", "size_hw": [200, 200]}}}
    write(s2 / "pieces/p.json", r)
    summary = {k: r[k] for k in ("capture_id", "piece_id", "arrays_path", "point_count", "candidate_count", "stage1_record_fingerprint")}
    summary["record_path"] = "pieces/p.json"
    m = {**release, "schema_version": "stage2.edge-hypotheses-manifest.v1", "status": "complete", "truth_free": True, "config_hash": digest(cfg), "configuration": cfg, "piece_count": 1, "candidate_count": r["candidate_count"], "stage1_manifest_sha256": manifest_hash, "stage1_input_fingerprint": input_hash, "pieces": [summary]}
    write(s2 / "edge_hypotheses_manifest.json", m)
    return {**base_config(root, "production"), "stage1": str(s1), "stage2": str(s2)}
