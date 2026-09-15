import os
from pathlib import Path
from src.dataset.benchmark_dataset import BENCHMARK_DATASET, get_all_benchmark_jobs, get_benchmark_job_by_id
from src.dataset.fine_tuning_generator import FineTuningDataGenerator


def test_benchmark_dataset_structure():
    jobs = get_all_benchmark_jobs()
    assert len(jobs) >= 5
    for job in jobs:
        assert "id" in job
        assert "title" in job
        assert "raw_text" in job
        assert "ground_truth" in job
        gt = job["ground_truth"]
        assert len(gt.technical_skills) > 0


def test_fine_tuning_export(tmp_path):
    gen = FineTuningDataGenerator()
    out_chat = tmp_path / "chat.jsonl"
    out_instr = tmp_path / "instr.jsonl"
    out_bio = tmp_path / "bio.json"

    p1 = gen.export_to_file(str(out_chat), format_type="chat")
    p2 = gen.export_to_file(str(out_instr), format_type="instruction")
    p3 = gen.export_to_file(str(out_bio), format_type="bio")

    assert Path(p1).exists()
    assert Path(p2).exists()
    assert Path(p3).exists()
