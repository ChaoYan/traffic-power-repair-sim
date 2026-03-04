from pathlib import Path

from sim.ch6_ch8 import build_ch6_ch8_dataset, export_ch6_ch8_dataset_csv, run_ch6_ch8_experiment


def test_dataset_scale_matches_report_outline():
    data = build_ch6_ch8_dataset()
    assert len(data["road_nodes"]) == 15
    assert len(data["road_edges"]) == 18
    assert len(data["power_nodes"]) == 12
    assert len(data["power_lines"]) == 11


def test_topology_shape_road_has_cycles_power_is_tree_like():
    data = build_ch6_ch8_dataset()
    # road: edges > nodes-1 => contains cycles
    assert len(data["road_edges"]) > len(data["road_nodes"]) - 1
    # power: tree-size condition
    assert len(data["power_lines"]) == len(data["power_nodes"]) - 1


def test_strategy_results_and_ranking():
    payload = run_ch6_ch8_experiment()
    results = payload["results"]
    assert len(results) == 4
    by_auc = sorted(results, key=lambda x: x["auc"], reverse=True)
    assert by_auc[0]["strategy"] in {"S3", "S4"}
    assert all(r["final_restored_kw"] > 0 for r in results)


def test_export_csv_tables(tmp_path: Path):
    data = build_ch6_ch8_dataset()
    outputs = export_ch6_ch8_dataset_csv(data, tmp_path)
    assert len(outputs) == 6
    for p in outputs:
        assert p.exists()
        assert p.read_text(encoding="utf-8").splitlines()[0]
