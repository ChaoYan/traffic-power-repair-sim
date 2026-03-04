from __future__ import annotations

from dataclasses import dataclass, field
import heapq
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class RoadEdge:
    edge_id: str
    u: str
    v: str
    distance_km: float
    speed_kmph: float
    is_open: bool = True

    @property
    def travel_hours(self) -> float:
        return self.distance_km / self.speed_kmph


@dataclass(frozen=True)
class PowerLine:
    line_id: str
    u: str
    v: str
    load_kw: float
    is_restored: bool = False


@dataclass(frozen=True)
class RepairTeam:
    team_id: str
    team_type: str  # road | power
    start_node: str
    work_hours: float = 3.0


@dataclass
class RoadGraph:
    nodes: Set[str]
    edges: Dict[str, RoadEdge]

    def neighbors(self, node: str) -> List[Tuple[str, RoadEdge]]:
        out: List[Tuple[str, RoadEdge]] = []
        for edge in self.edges.values():
            if not edge.is_open:
                continue
            if edge.u == node:
                out.append((edge.v, edge))
            elif edge.v == node:
                out.append((edge.u, edge))
        return out

    def shortest_path_time(self, source: str, target: str) -> Optional[float]:
        if source not in self.nodes or target not in self.nodes:
            return None
        pq: List[Tuple[float, str]] = [(0.0, source)]
        best: Dict[str, float] = {source: 0.0}
        while pq:
            cur_t, node = heapq.heappop(pq)
            if node == target:
                return cur_t
            if cur_t > best.get(node, float("inf")):
                continue
            for nxt, edge in self.neighbors(node):
                cand = cur_t + edge.travel_hours
                if cand < best.get(nxt, float("inf")):
                    best[nxt] = cand
                    heapq.heappush(pq, (cand, nxt))
        return None


@dataclass
class PowerGraph:
    nodes: Set[str]
    lines: Dict[str, PowerLine]

    def restored_load(self) -> float:
        return sum(line.load_kw for line in self.lines.values() if line.is_restored)


@dataclass
class SimulationState:
    time_hour: float
    road: RoadGraph
    power: PowerGraph
    mapping: Dict[str, str]  # power_line_id -> road_node
    road_teams: List[RepairTeam] = field(default_factory=list)
    power_teams: List[RepairTeam] = field(default_factory=list)

    def is_power_task_reachable(self, line_id: str, team_node: str) -> bool:
        road_node = self.mapping.get(line_id)
        if road_node is None:
            return False
        return self.road.shortest_path_time(team_node, road_node) is not None
