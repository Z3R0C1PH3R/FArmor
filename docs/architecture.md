# FArmor Architecture Diagram

```mermaid
flowchart LR
  U[User / Judge Input\nNatural language request] --> FE[Frontend UI\nSynapse-style dashboard]
  FE --> API[Mock Backend API\n/api/execute]

  subgraph Core[Intent-Aware Execution Core]
    RL[Reasoning Layer\nparse_intent_from_text()\nOutput: Intent model]
    EL[Enforcement Layer\nvalidate_intent()\nPolicy firewall]
    XL[Execution Layer\nexecute_transfer()\nWrite receipt file]
  end

  API --> RL
  RL -->|Intent| EL
  EL -->|Allowed| XL
  EL -->|Blocked| BR[PolicyViolationError\nDeterministic reason]

  XL --> RC[(receipts/receipt_timestamp.txt)]
  API --> POL[(data/policies.json)]
  BR --> FE
  RC --> FE

  subgraph Delegation[Bounded Delegation Scenario]
    FM[Finance Manager] -->|Delegates task| BOT[Bot agent]
    BOT -->|Uses delegated_bot policy\nmax limit $100| API
    API --> EL
  end
```

## Separation Guarantee

- `reasoning.py`: Converts text to structured `Intent`; no file writes, no transfers.
- `enforcement.py`: Deterministic policy checks and custom `PolicyViolationError`.
- `execution.py`: Only runs after enforcement allows; creates verifiable receipts.
- `server.py`: Orchestration and API surface, keeping layers explicit and traceable.
