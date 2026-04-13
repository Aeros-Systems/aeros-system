import math
from typing import Dict, Any, List


class Engine:
    """
    AEROS Core Decision Engine
    --------------------------
    Deterministic, auditable decision layer with:
    - Shared-state driven arbitration
    - Constraint-based task scoring
    - Human-first doctrine enforcement
    - Basic HiveMind memory for adaptive behavior
    """

    # -----------------------------
    # Initialization
    # -----------------------------
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}

        # Global system health
        self.resources: float = 1.0
        self.continuity: str = "NORMAL"

        # HiveMind memory (lightweight & auditable)
        self.hivemind = {
            "history": [],
            "weights": {
                "human": 3.0,
                "containment": 2.0,
                "continuity": 1.5,
                "risk": 1.5,
                "time": 1.0
            }
        }

    # -----------------------------
    # Ingestion
    # -----------------------------
    def ingest_node(self, node_id: str, role: str, position, priority: int = 1):
        self.nodes[node_id] = {
            "role": role,
            "position": position,
            "priority": priority,
            "active": True
        }

    def ingest_event(self, event: Dict[str, Any]):
        self.tasks[event["id"]] = {
            "type": event.get("type", "suppression"),
            "location": event["location"],
            "priority": event.get("priority", 1),
            "status": "PENDING",
            "assigned": None,
            "progress": 0.0
        }

    # -----------------------------
    # Utility
    # -----------------------------
    def _distance(self, a, b):
        return math.dist(a, b)

    def _update_continuity(self):
        active = sum(1 for n in self.nodes.values() if n["active"])
        if active < 2:
            self.continuity = "FRACTURED"
        elif active < 4:
            self.continuity = "DEGRADED"
        else:
            self.continuity = "NORMAL"

    # -----------------------------
    # Decision Scoring
    # -----------------------------
    def _score(self, node, task, distance):

        w = self.hivemind["weights"]

        # BENEFIT MODEL
        human_gain = 1.0 if task["type"] == "forward" else 0.6
        containment = 0.8
        continuity = 0.6

        benefit = (
            w["human"] * human_gain +
            w["containment"] * containment +
            w["continuity"] * continuity
        )

        # RISK MODEL
        platform_risk = min(1.0, distance / 100)
        escalation_risk = 0.2

        risk = w["risk"] * (platform_risk + escalation_risk)

        # TIME COST
        time_cost = w["time"] * (distance * 0.05)

        # HUMAN-FIRST OVERRIDE
        if task["type"] == "forward":
            benefit += 100

        return benefit - risk - time_cost

    # -----------------------------
    # Main Cycle
    # -----------------------------
    def step(self) -> Dict[str, Any]:

        self._update_continuity()
        self.resources = max(0.0, self.resources - 0.01)

        active_nodes = {
            nid: n for nid, n in self.nodes.items()
            if n["active"]
        }

        # ASSIGN TASKS
        for task in self.tasks.values():

            if task["status"] != "PENDING":
                continue

            best_node = None
            best_score = -999999

            for nid, node in active_nodes.items():
                d = self._distance(node["position"], task["location"])
                score = self._score(node, task, d)

                if score > best_score:
                    best_score = score
                    best_node = nid

            if best_node and self.resources > 0.05:
                task["assigned"] = best_node
                task["status"] = "ACTIVE"

        # EXECUTION
        for task in self.tasks.values():

            if task["status"] == "ACTIVE":
                task["progress"] += 0.25

                if task["progress"] >= 1.0:
                    task["status"] = "DONE"

                    # HiveMind memory capture
                    self.hivemind["history"].append({
                        "type": task["type"],
                        "node": task["assigned"]
                    })

        return {
            "tasks": self.tasks,
            "nodes": self.nodes,
            "cycle_state": {
                "done": sum(1 for t in self.tasks.values() if t["status"] == "DONE"),
                "active": sum(1 for t in self.tasks.values() if t["status"] == "ACTIVE"),
                "pending": sum(1 for t in self.tasks.values() if t["status"] == "PENDING"),
                "continuity": self.continuity,
                "resources": round(self.resources, 3)
            }
        }
