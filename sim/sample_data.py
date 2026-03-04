from sim.model import PowerGraph, PowerLine, RepairTeam, RoadEdge, RoadGraph, SimulationState


def build_sample_state() -> SimulationState:
    road_edges = {
        "r1": RoadEdge("r1", "A", "B", distance_km=5.0, speed_kmph=25.0, is_open=True),
        "r2": RoadEdge("r2", "B", "C", distance_km=4.0, speed_kmph=20.0, is_open=True),
        "r3": RoadEdge("r3", "C", "D", distance_km=6.0, speed_kmph=30.0, is_open=False),
        "r4": RoadEdge("r4", "B", "D", distance_km=10.0, speed_kmph=40.0, is_open=True),
    }
    road = RoadGraph(nodes={"A", "B", "C", "D"}, edges=road_edges)

    power_lines = {
        "p1": PowerLine("p1", "S", "L1", load_kw=300.0, is_restored=True),
        "p2": PowerLine("p2", "L1", "L2", load_kw=500.0, is_restored=False),
    }
    power = PowerGraph(nodes={"S", "L1", "L2"}, lines=power_lines)

    mapping = {
        "p1": "B",
        "p2": "D",
    }

    return SimulationState(
        time_hour=0.0,
        road=road,
        power=power,
        mapping=mapping,
        road_teams=[RepairTeam("road-1", "road", start_node="A")],
        power_teams=[RepairTeam("power-1", "power", start_node="A")],
    )
