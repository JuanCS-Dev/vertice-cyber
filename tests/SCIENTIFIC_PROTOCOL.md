# 🧪 Scientific E2E Test Protocol (Vertice v3.0)

> "Assertion without measurement is merely opinion."

## 1. Abstract
This protocol defines the rigorous, hypothesis-driven End-to-End (E2E) testing methodology for the Vertice Cyber Dashboard and MCP Agent Ecosystem. Unlike traditional "smoke tests", this suite utilizes the **Scientific Method** to validate system behavior, measuring latency, state consistency, and neural event propagation with millisecond precision.

## 2. Methodology
The test suite operates as an autonomous **Neural Auditor**, independent of the frontend implementation. It effectively acts as a "Headless Dashboard", exercising the exact same neural pathways (HTTP API + WebSocket Stream) that the React Frontend uses.

### The Scientific Cycle
For earch test case:
1.  **Hypothesis**: Define expected system behavior (e.g., "Pausing an agent stops its event stream within 200ms").
2.  **Experiment**: Trigger the stimulus (API Call) in a controlled environment.
3.  **Observation**: Capture telemetry (WS Events, HTTP Responses) timestamps.
4.  **Analysis**: Calculate delta (Latency, Jitter, Success Rate).
5.  **Conclusion**: Pass/Fail based on defined tolerances (Constitution Art. II).

## 3. Test Coverage Matrix

| ID | Component | Hypothesis | Tolerance |
|----|-----------|------------|-----------|
| **LIF-01** | Agent Control | Agent transitions IDLE -> SPAWNED -> RUNNING -> PAUSED -> TERMINATED reliably. | 100% Reliability |
| **NEU-01** | Neural Link | Events emitted by tools appear in WebSocket stream with <50ms latency. | <50ms Latency |
| **WAR-01** | Wargame | Simulation "Red Team" triggers >5 log events and generates a report artifact. | Artifact Exists |
| **SEC-01** | Compliance | Magistrate correctly rejects unsafe/unauthorized inputs (Sovereignty of Intent). | 100% Rejection |

## 4. Architecture
The suite is implemented in Python, residing in `tests/scientific/`.

- **`NeuralCortex` (Runner)**: Orchestrates the test execution.
- **`Synapse` (Client)**: Simulates the React `mcpClient` (HTTP).
- **`Dendrite` (Listener)**: Simulates the `VerticeEventStream` (WebSocket).

## 5. Execution
```bash
python3 tests/scientific/runner.py --env=dev --report=json
```

## 6. Definitions of Done
- All P0 hypotheses must be validated.
- No "Flaky" tests allowed (determinism required).
- Report generated in `tests/scientific/reports/`.
