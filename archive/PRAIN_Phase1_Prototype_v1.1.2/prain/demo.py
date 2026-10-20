import json
from dataclasses import asdict
from . import PRAINRuntime, Observation


def main():
    runtime = PRAINRuntime(
        policies=[{"policy_id": "demo.read.v1", "action": "read", "target": "runtime.status",
                   "required_capability": "state:read"}],
        evaluators={"healthy": lambda obs: obs.payload.get("healthy") is True},
    )
    observation = Observation.create("demo", "health", {"healthy": True}, "demo-observation-1")
    event = runtime.ingest(observation)
    evaluation = runtime.evaluate(observation, "healthy")
    receipt, decision = runtime.request_action(
        "read", "runtime.status", "state:read", "demo-agent", {"fields": ["healthy"]},
        correlation_id=event.correlation_id, idempotency_key="demo-read-1")
    print(json.dumps({
        "observation": asdict(observation),
        "event_id": event.event_id,
        "evaluation": evaluation,
        "policy_decision": decision,
        "execution_receipt": asdict(receipt) if receipt else None,
        "runtime": runtime.snapshot(),
        "note": "Reference prototype. Action execution is simulated only; not production-ready.",
    }, indent=2))

if __name__ == "__main__":
    main()
