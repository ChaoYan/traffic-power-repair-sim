from run_simulation import run_mvp_simulation
from sim.sample_data import build_sample_state


def test_shortest_path_time():
    state = build_sample_state()
    # A->B->D = 5/25 + 10/40 = 0.2 + 0.25 = 0.45
    assert state.road.shortest_path_time("A", "D") == 0.45


def test_restored_load():
    state = build_sample_state()
    assert state.power.restored_load() == 300.0


def test_reachability():
    state = build_sample_state()
    assert state.is_power_task_reachable("p2", "A") is True


def test_run_mvp_simulation_timeline():
    result = run_mvp_simulation(debug=False)
    assert result["final_time_hour"] == 3.0
    assert result["final_restored_load_kw"] == 800.0
    assert len(result["history"]) == 2
    assert result["history"][0]["restored_load_kw"] == 300.0
    assert result["history"][1]["restored_load_kw"] == 800.0
