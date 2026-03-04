from __future__ import annotations

import argparse
from dataclasses import replace
from typing import Any, Dict, List

from sim.sample_data import build_sample_state


def run_mvp_simulation(debug: bool = False) -> Dict[str, Any]:
    state = build_sample_state()

    # 记录一个简单的离散过程：t=0 时 p2 未恢复；t=3h 后恢复 p2。
    history: List[Dict[str, float]] = []

    def snapshot(t: float) -> None:
        history.append(
            {
                "time_hour": t,
                "restored_load_kw": state.power.restored_load(),
                "travel_time_a_to_d_h": state.road.shortest_path_time("A", "D") or -1.0,
                "p2_reachable": 1.0 if state.is_power_task_reachable("p2", team_node="A") else 0.0,
            }
        )

    snapshot(0.0)

    # 模拟执行一次抢修任务：3 小时后恢复 p2
    state.time_hour = 3.0
    p2 = state.power.lines["p2"]
    state.power.lines["p2"] = replace(p2, is_restored=True)
    snapshot(3.0)

    result = {
        "final_time_hour": state.time_hour,
        "final_restored_load_kw": state.power.restored_load(),
        "history": history,
    }

    if debug:
        print("=== MVP Step-1 Check (with timeline) ===")
        for row in history:
            print(row)

    return result


def maybe_log_wandb(result: Dict[str, Any], entity: str, project: str, enabled: bool) -> None:
    if not enabled:
        return

    import wandb

    run = wandb.init(
        entity=entity,
        project=project,
        config={
            "scenario": "mvp_step1",
            "strategy": "single_power_restore_demo",
            "notes": "from meeting+report guided first implementation",
        },
    )

    for row in result["history"]:
        run.log(row, step=int(row["time_hour"]))

    run.summary["final_time_hour"] = result["final_time_hour"]
    run.summary["final_restored_load_kw"] = result["final_restored_load_kw"]
    run.finish()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MVP simulation and optionally log to W&B.")
    parser.add_argument("--debug", action="store_true", help="Print timeline rows to stdout.")
    parser.add_argument("--wandb", action="store_true", help="Enable W&B logging.")
    parser.add_argument("--entity", default="chaoyan", help="W&B entity name.")
    parser.add_argument("--project", default="traffic-power-repair-sim", help="W&B project name.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_mvp_simulation(debug=args.debug)
    maybe_log_wandb(result, entity=args.entity, project=args.project, enabled=args.wandb)


if __name__ == "__main__":
    main()
