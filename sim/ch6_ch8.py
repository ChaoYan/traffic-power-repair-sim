from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RoadNode:
    node_id: str
    x_km: float
    y_km: float
    role: str = "junction"


@dataclass(frozen=True)
class RoadEdge:
    edge_id: str
    u: str
    v: str
    distance_km: float
    speed_kmph: float
    is_damaged: int


@dataclass(frozen=True)
class PowerNode:
    node_id: str
    kind: str


@dataclass(frozen=True)
class PowerLineRef:
    line_id: str
    u: str
    v: str
    length_km: float
    is_fault: int


@dataclass(frozen=True)
class RoadTask:
    task_id: str
    edge_id: str
    duration_h: float


@dataclass(frozen=True)
class PowerTask:
    task_id: str
    line_id: str
    duration_h: float
    load_kw: float
    road_req: str
    facility: str
    critical_weight: float


def build_ch6_ch8_dataset() -> Dict[str, object]:
    """Case aligned with report sketch: cyclic transport graph + rural radial power tree."""
    # 交通图：有环、距离拉开（km 级）
    road_nodes = [
        RoadNode("R1", 0, 0, "depot"),
        RoadNode("R2", 8, 2),
        RoadNode("R3", 16, 4),
        RoadNode("R4", 25, 7, "hospital_access"),
        RoadNode("R5", 6, -7),
        RoadNode("R6", 15, -6),
        RoadNode("R7", 24, -5),
        RoadNode("R8", 33, -4, "shelter_access"),
        RoadNode("R9", 11, -15),
        RoadNode("R10", 20, -14),
        RoadNode("R11", 30, -13),
        RoadNode("R12", 39, -12, "command_access"),
        RoadNode("R13", 18, 13),
        RoadNode("R14", 30, 14),
        RoadNode("R15", 41, 10, "school_access"),
    ]
    road_edges = [
        RoadEdge("E1", "R1", "R2", 8.5, 35, 0),
        RoadEdge("E2", "R2", "R3", 8.4, 35, 1),
        RoadEdge("E3", "R3", "R4", 9.7, 30, 0),
        RoadEdge("E4", "R1", "R5", 9.8, 30, 0),
        RoadEdge("E5", "R5", "R6", 9.1, 30, 1),
        RoadEdge("E6", "R6", "R7", 9.0, 35, 0),
        RoadEdge("E7", "R7", "R8", 9.1, 35, 0),
        RoadEdge("E8", "R5", "R9", 10.3, 25, 0),
        RoadEdge("E9", "R9", "R10", 9.6, 25, 1),
        RoadEdge("E10", "R10", "R11", 10.0, 25, 0),
        RoadEdge("E11", "R11", "R12", 9.4, 25, 0),
        RoadEdge("E12", "R3", "R6", 10.6, 30, 0),
        RoadEdge("E13", "R6", "R10", 9.0, 30, 0),
        RoadEdge("E14", "R4", "R7", 12.4, 30, 1),
        RoadEdge("E15", "R7", "R11", 8.7, 30, 1),
        RoadEdge("E16", "R3", "R13", 9.8, 30, 0),
        RoadEdge("E17", "R13", "R14", 12.2, 30, 0),
        RoadEdge("E18", "R14", "R15", 12.1, 30, 1),
    ]

    # 电网：农村配电网，树状（12 nodes, 11 lines）
    power_nodes = [
        PowerNode("P1", "substation"),
        PowerNode("P2", "feeder"),
        PowerNode("P3", "feeder"),
        PowerNode("P4", "feeder"),
        PowerNode("P5", "village_load"),
        PowerNode("P6", "village_load"),
        PowerNode("P7", "village_load"),
        PowerNode("P8", "village_load"),
        PowerNode("P9", "hospital"),
        PowerNode("P10", "shelter"),
        PowerNode("P11", "command_center"),
        PowerNode("P12", "school"),
    ]
    power_lines = [
        PowerLineRef("L1", "P1", "P2", 3.2, 0),
        PowerLineRef("L2", "P2", "P3", 4.6, 1),
        PowerLineRef("L3", "P2", "P4", 5.1, 1),
        PowerLineRef("L4", "P3", "P5", 3.8, 0),
        PowerLineRef("L5", "P3", "P6", 4.4, 0),
        PowerLineRef("L6", "P4", "P7", 4.9, 1),
        PowerLineRef("L7", "P4", "P8", 4.2, 0),
        PowerLineRef("L8", "P5", "P9", 2.3, 1),
        PowerLineRef("L9", "P6", "P10", 2.0, 1),
        PowerLineRef("L10", "P7", "P11", 2.7, 1),
        PowerLineRef("L11", "P8", "P12", 2.4, 0),
    ]

    road_tasks = [
        RoadTask("RR1", "E2", 2.5),
        RoadTask("RR2", "E5", 3.5),
        RoadTask("RR3", "E9", 3.0),
        RoadTask("RR4", "E14", 4.0),
        RoadTask("RR5", "E18", 3.5),
    ]
    power_tasks = [
        PowerTask("PL1", "L8", 2.5, 460, "RR1", "hospital", 5.0),
        PowerTask("PL2", "L9", 2.0, 280, "RR1", "shelter", 4.5),
        PowerTask("PL3", "L10", 3.0, 230, "RR2", "command", 4.2),
        PowerTask("PL4", "L3", 2.5, 170, "RR3", "school", 2.0),
        PowerTask("PL5", "L6", 3.5, 260, "RR4", "village-a", 1.8),
    ]

    return {
        "road_nodes": road_nodes,
        "road_edges": road_edges,
        "power_nodes": power_nodes,
        "power_lines": power_lines,
        "road_tasks": road_tasks,
        "power_tasks": power_tasks,
    }


def export_ch6_ch8_dataset_csv(dataset: Dict[str, object], outdir: Path) -> List[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs: List[Path] = []
    for key in ["road_nodes", "road_edges", "power_nodes", "power_lines", "road_tasks", "power_tasks"]:
        rows = [asdict(x) for x in dataset[key]]
        path = outdir / f"{key}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        outputs.append(path)
    return outputs


def _step_integral(history: List[Tuple[float, float]]) -> float:
    auc = 0.0
    for i in range(1, len(history)):
        t0, y0 = history[i - 1]
        t1, _ = history[i]
        auc += (t1 - t0) * y0
    return auc


def _simulate_strategy(name: str, road_tasks: List[RoadTask], power_tasks: List[PowerTask]) -> Dict[str, object]:
    road_done: Dict[str, float] = {}
    power_done: Dict[str, float] = {}
    facility_done: Dict[str, float] = {}
    restored = 0.0
    history: List[Tuple[float, float]] = [(0.0, restored)]

    if name == "S1":
        road_order = ["RR1", "RR2", "RR3", "RR4", "RR5"]
    elif name == "S2":
        road_order = ["RR1", "RR3", "RR2", "RR4", "RR5"]
    else:
        road_order = ["RR1", "RR2", "RR3", "RR5", "RR4"]

    time_road = 0.0
    for rid in road_order:
        rt = next(r for r in road_tasks if r.task_id == rid)
        time_road += rt.duration_h / 2.0
        road_done[rid] = time_road

    if name == "S1":
        candidate = sorted(power_tasks, key=lambda p: p.task_id)
        t = max(road_done.values())
        for p in candidate:
            t = max(t, road_done[p.road_req]) + p.duration_h / 2.0
            power_done[p.task_id] = t
    elif name == "S2":
        candidate = sorted(power_tasks, key=lambda p: -p.critical_weight)
        t = 0.0
        for p in candidate:
            t = max(t, road_done[p.road_req]) + p.duration_h / 2.0
            power_done[p.task_id] = t
    elif name == "S3":
        candidate = sorted(power_tasks, key=lambda p: -p.critical_weight)
        t = 0.0
        for idx, p in enumerate(candidate):
            req_t = 0.0 if idx < 2 else road_done[p.road_req]
            t = max(t, req_t) + p.duration_h / 2.0
            power_done[p.task_id] = t
    else:
        candidate = sorted(power_tasks, key=lambda p: -(p.critical_weight * p.load_kw))
        t = 0.0
        for idx, p in enumerate(candidate):
            req_t = 0.0 if idx == 0 else road_done[p.road_req]
            t = max(t, req_t) + p.duration_h / 2.0
            power_done[p.task_id] = t

    events = sorted([(v, k) for k, v in power_done.items()])
    for finish_t, pid in events:
        p = next(x for x in power_tasks if x.task_id == pid)
        restored += p.load_kw
        history.append((finish_t, restored))
        facility_done[p.facility] = finish_t

    makespan = max(power_done.values())
    history.append((makespan, restored))
    return {
        "strategy": name,
        "history": history,
        "auc": _step_integral(history),
        "makespan": makespan,
        "facility_done": facility_done,
        "final_restored_kw": restored,
    }


def run_ch6_ch8_experiment() -> Dict[str, object]:
    dataset = build_ch6_ch8_dataset()
    results = [_simulate_strategy(s, dataset["road_tasks"], dataset["power_tasks"]) for s in ["S1", "S2", "S3", "S4"]]
    return {"dataset": dataset, "results": results}
