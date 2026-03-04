from pathlib import Path

from sim.wandb_reporting import (
    render_markdown_report_en,
    render_markdown_report_zh,
    save_text,
    summarize_results,
)


def _mock_results():
    return [
        {"strategy": "S1", "auc": 100.0, "makespan": 12.0, "final_restored_kw": 1000.0},
        {"strategy": "S4", "auc": 200.0, "makespan": 9.0, "final_restored_kw": 1000.0},
    ]


def test_summarize_results():
    summary = summarize_results(_mock_results())
    assert summary.best_strategy == "S4"
    assert summary.worst_strategy == "S1"
    assert len(summary.strategy_rows) == 2


def test_render_and_save_reports(tmp_path: Path):
    summary = summarize_results(_mock_results())
    figs = [Path("a.png"), Path("b.png")]
    zh = render_markdown_report_zh(summary, "http://example.com", figs)
    en = render_markdown_report_en(summary, "http://example.com", figs)
    assert "协同抢修实验报告" in zh
    assert "各图表解释" in zh
    assert "Coordinated Repair Experiment Report" in en
    assert "Figure-by-figure interpretation" in en

    out = save_text(tmp_path / "r.md", en)
    assert out.exists()
    assert "http://example.com" in out.read_text(encoding="utf-8")
