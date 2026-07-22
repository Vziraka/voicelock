# Harness Architecture (v0.5)

How the harness itself works — the task lifecycle and the file map. View these
**rendered** (VS Code Mermaid preview, GitHub, or mermaid.live), not as raw text.
This describes the harness, not your project — your project's architecture lives
in `memory/codebase-map.md`.

## Task lifecycle

Green = human touchpoint · purple = clean-context verifier · red = reject path.
The diagram shows **Mode 1** (fully supervised). At Modes 2–4 the same graph
runs, but the green "verify" / "go" / commit-message nodes are passed without
waiting — the human touchpoints compress to spec approval, escalations, and
the feature-end checkpoint. The gates never change; who pushes between them
does. (The mode contract lives in `constitution/universal.md`.)

```mermaid
flowchart TD
    intake["intake — once per repo<br/>(recon | scaffold)"] --> design
    design["/design → roadmap.md<br/>(optional · TECH-PICK per technology)"] --> spec
    spec["/spec — grilling + TECH-PICK<br/>→ spec.md CLEAR"] --> ok{"HUMAN checks<br/>'Approved by human'"}
    ok --> plan["/plan → tasks TODO<br/>rejects: 0 · Feature: Fn"]
    plan --> impl["/implement — ONE task<br/>auto-commit local → REVIEW"]
    impl --> v{"HUMAN: 'verify'"}
    v --> sub["verifier subagent — clean context<br/>(VERIFIER-PROMPT verbatim)"]
    sub --> gate["verify-gate: task commands<br/>(full Verification list at feature's last task)<br/>+ scope diff base..head"]
    gate -->|PASS| review["verify-review: Spec + Standards<br/>default REJECT"]
    gate -->|FAIL| rej
    review -->|APPROVE| wrap["wrap-up: ADR → learn(verdict) →<br/>handoff → DONE last → roadmap"]
    review -->|REJECT| rej["feedback appended · rejects+1<br/>task → TODO"]
    wrap --> commit{"HUMAN approves commit message<br/>→ commit + push"}
    rej --> commit
    commit --> go{"HUMAN 'go'<br/>(new session)"}
    go --> impl
    rej -.->|"rejects = 3"| esc["ESCALATE_HUMAN"]

    classDef human fill:#12261a,stroke:#3fb950,color:#e6edf3
    classDef verif fill:#1a1526,stroke:#bc8cff,color:#e6edf3
    classDef bad fill:#2d1416,stroke:#f85149,color:#e6edf3
    class ok,v,commit,go human
    class sub,gate,review verif
    class rej,esc bad
```

## File map — who writes what

```mermaid
flowchart LR
    subgraph rules["constitution/ — the rules"]
        U["universal.md 🔒"]
        P["project.md (learns)"]
        C["topics/conventions.md"]
    end
    subgraph state["state files — current feature"]
        R["roadmap.md"]
        S["spec.md"]
        PL["plan.md"]
        H["handoff.md"]
        CX["CONTEXT.md"]
    end
    subgraph mem["memory/"]
        M["codebase-map.md"]
        D["decisions.md (append + human-approved archive moves)"]
        V["verdicts/ 🔒 append-only"]
        DV["deviations.md 🔒 append-only"]
    end
    subgraph fmt["formats/"]
        A["ADR.md"]
        T["TECH-PICK.md"]
        VP["VERIFIER-PROMPT.md"]
    end

    designSkill["design"] --> R & CX & M & D
    specSkill["spec"] --> S
    specSkill -. "new dependency" .-> T
    planSkill["plan"] --> PL
    implSkill["implement"] --> PL & H
    verifySkills["verify-gate + verify-review 🔒"] -. "read Verification section + diff" .-> S
    verifySkills --> PL & H
    wrapSkill["wrap-up"] --> PL & R & H & A
    learnSkill["learn"] --> V & P
    wrapSkill --> M
    curateSkill["curate"] --> P
    VP -. "spawns fresh eyes" .-> verifySkills

    classDef prot stroke:#8b949e,stroke-dasharray:4 3
    class U,V,DV,verifySkills prot
```

🔒 = protected (`protected.txt`): human-only, except the append-only paths
(verdicts/, deviations.md) where the agent may add new entries but never
modify existing ones.
