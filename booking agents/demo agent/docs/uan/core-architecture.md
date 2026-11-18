# UAN-CORE Architecture (Implemented on Repo Bus)

| Field | Value |
|---|---|
| UAN core version | 0.1.0 |
| Domain pack | VOICE-AIN (`voice_agent_network`) |
| Authority | `coordination/` + `coordination/scripts/coord.py` |
| Decision | ADR-002 |

## Principle

**Build the core once. Specialize through domain packs.**

This workspace implements UAN-CORE by **evolving** the existing repository coordination bus. It does **not** introduce a parallel `src/uan/` runtime.

## Layers

```mermaid
flowchart TB
  subgraph control [ControlPlane]
    Cmd[Agent00_coordinator]
  end
  subgraph exec [ExecutionPlane]
    CLI[coord.py]
    Tasks[tasks/records]
    Attempts[tasks/attempts]
    CursorTask[Cursor_Task_same_session]
  end
  subgraph mem [MemoryPlane]
    Shared[shared-context]
    SM[Supermemory]
  end
  subgraph domain [DomainPlane]
    VoiceAIN[VOICE-AIN]
  end
  subgraph gov [SecurityGovernance]
    Approvals[Human_approvals]
    ERP[ERPNext_blocked]
  end
  subgraph ops [OperationsInterface]
    Status[coord_status]
    DocsHealth[check_docs.py]
  end
  Cmd --> CLI
  CLI --> Tasks
  CLI --> Attempts
  Cmd -.-> CursorTask
  CLI --> Shared
  Cmd --> VoiceAIN
  Cmd --> Approvals
  ERP -.-> Approvals
  CLI --> Status
  DocsHealth --> ops
  SM -.-> mem
```

## Interfaces

| Interface | Contract | Store |
|---|---|---|
| Messages | `schemas/message.schema.json` | `messages/inbox|archive` |
| Tasks | `schemas/task.schema.json` | `tasks/records` |
| Handoffs | `schemas/handoff.schema.json` | `handoffs/*.json` |
| Config | `config/uan.json` | aliases, routes, concurrency |
| Domain | `domains/voice_agent_network/domain.yaml` | VOICE-AIN metadata |

## Non-claims

- Not a continuously running multi-agent OS.
- Not production deploy automation.
- Not a replacement for Retell/Cal.com provider consoles.
