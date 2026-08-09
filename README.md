# Customer Support Agent

A customer support agent whose behaviour is described entirely by a Pydantic data model — the `AgentSpec` — and executed by a runtime that reads it. Two agents for two different products share the runtime and differ only in their spec JSON.

## What this is

A support agent for a mid-market SaaS product. It handles the request types you'd expect from that kind of desk: refunds, account access, plan changes, billing questions, feature clarifications, bug reports. Each request type is a resolution recipe with its own risk tier, its own confidence threshold to auto-answer, and its own escalation rules.

The architectural bet: **the agent is a spec interpreter, not a graph.** Everything the agent does — its instructions, its knowledge, its tools, its resolution recipes, its safety policies — lives in one Pydantic model. The runtime is a Python class that reads the spec and executes accordingly. Changing what the agent does means editing the spec, not the code.

## What this is not

- **A production agent.** There's no real ticketing integration, no PII redaction worth the name, no cost controls, no auth on the API.
- **A framework.** The `AgentSpec` is domain-specific to this project. It borrows the anatomy vocabulary — instructions, knowledge, tools, skills, memory, triggers, surfaces, permissions — but isn't trying to be a general-purpose agent SDK.
- **Built on LangGraph or LangChain.** The runtime is hand-rolled Python. This is a deliberate choice, discussed below.

## Why build it this way

Three convictions drove the design.

**The spec is the source of truth, not the code.** In most agent projects, behaviour is scattered across a graph definition, a system prompt file, a tool list, a routing function, a deployment config. Changing any of them requires knowing where to look. Here, everything about what the agent does lives in one Pydantic model. Reading `agent_spec.py` tells you what any agent built from it can and can't do.

**Safety is structural, not advisory.** The `AgentSpec` has Pydantic validators that make certain unsafe configurations impossible to construct. A skill tagged `NEVER_AUTOMATE` cannot be set to auto-reply — the model raises at construction time. A write-effect tool cannot be registered without human approval. The 2FA reset flow is the anchor for this: it's the one skill the type system refuses to let auto-answer, no matter what an extraction pass or a well-meaning engineer proposes. Safety isn't a runtime check hoping to fire; it's a guarantee that unsafe specs don't exist.

**Hand-rolling the runtime keeps the mechanics visible.** Agent frameworks abstract away exactly the things worth understanding — the ReAct loop, the classify-then-route pattern, the tool-call/tool-result dance, the context assembly step. Building a runtime from a bare LLM call means every mechanism has a story. When the runtime eventually gets refactored to use a graph framework, every abstraction the framework provides is one this project already built by hand.

## Architecture

```
                    ┌──────────────────┐
                    │  agent_spec.py   │   Pydantic AgentSpec — the entire vocabulary
                    │  (data model)    │   of what an agent can be
                    └────────┬─────────┘
                             │
                    (specs/ *.json)
                             │
                             ▼
┌────────────┐      ┌──────────────────┐      ┌──────────────┐
│  FastAPI   │─────▶│   SpecAgent      │─────▶│  Anthropic   │
│  routes    │      │   (runtime)      │      │  API         │
└────────────┘      └──────┬───────────┘      └──────────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │  Tools registry    │
                  │  Knowledge store   │
                  │  Message history   │
                  │  Audit log         │
                  └────────────────────┘
```

The `AgentSpec` is the interface between two halves of the system. On one side, a spec is produced — hand-authored today, extracted from a support ticket archive in the future. On the other side, a spec is executed — the `SpecAgent` runtime loads it, validates its safety, and interprets it against incoming messages.

### The runtime per message

When a message arrives:

1. **Classify** — the runtime uses the spec's list of resolution recipes to decide which one the message matches, with a confidence score.
2. **Gate on confidence** — the spec's reasoning policy has two thresholds. Below the lower one, the agent escalates. Between the two, it asks a clarifying question. Above the upper one, it proceeds.
3. **Gate on skill mode** — `ESCALATE_ONLY` skills route to a human regardless of confidence. This is where 2FA resets always end up.
4. **Gate on deployment risk** — a skill flagged for auto-reply gets downgraded to draft-for-review if the deployment's risk ceiling doesn't allow it. A conservative deployment can run a permissive spec safely.
5. **Assemble context** — pull the matched skill's referenced knowledge items and the relevant slice of message history.
6. **Run the recipe** — for each step in the skill, invoke the referenced tool. Write-effect tools require human approval before firing.
7. **Compose the reply** — one LLM call with instructions as system prompt, knowledge as context, tool outputs as evidence.
8. **Audit** — every decision written to the log, per the spec's observability config.

Each step maps to a small piece of the runtime, and each is driven by data from the spec.

## The agent's domain

The support agent handles a fixed set of request types:

- **Refund requests** — inside vs. outside the refund window, plan-dependent rules, currency handling.
- **Account access** — password resets (self-serve), 2FA resets (never auto-serve, always escalate).
- **Plan changes** — upgrades (auto-serve), downgrades (auto-serve with a save-attempt), cancellations (draft-for-review).
- **Billing questions** — invoice access, tax questions, payment method updates.
- **Feature questions** — pointing to docs, distinguishing "how do I" from "does this exist".
- **Bug reports** — triage, information gathering, escalation to engineering.

Each becomes a `Skill` in the spec, with an explicit `risk_tier` and `response_mode`. Refund requests inside the window are low-risk and auto-serve; refund requests outside the window are medium-risk and draft-for-review. Plan cancellations are draft-for-review because the business wants a human to see them. 2FA resets are `NEVER_AUTOMATE`, enforced by the type system.

## Where the spec comes from

Different parts of the spec have different sources:

- **Instructions, knowledge, resolution recipes, eval cases** are the kinds of thing extracted from a corpus of resolved support conversations. This project uses a hand-authored corpus, but the shape mirrors what a real extraction pipeline would produce.
- **Tools** are hand-authored, informed by what the corpus shows humans doing during resolutions.
- **Memory, triggers, surfaces, permissions, deployment policy** are configuration, chosen based on where the agent will run.
- **Reasoning and observability** have sensible defaults with per-agent overrides.

The extraction pipeline itself isn't part of this project. The `AgentSpec` is designed as the pipeline's output contract regardless.

## Stack

| Layer | Choice |
| --- | --- |
| API | FastAPI |
| Spec model | Pydantic v2 |
| LLM provider | Anthropic (Claude Opus 4.7) |
| Runtime | Hand-rolled `SpecAgent` class |
| Persistence | JSON files on disk |
| Deployment | Local dev |

**Deliberate omissions:** no LangChain, no LangGraph, no vector database, no message queue, no auth. Each of these earns its way in when a concrete need justifies it.

## Project layout

```
.
├── agent_spec.py          # the Pydantic AgentSpec — the whole vocabulary
├── spec_agent.py          # the SpecAgent runtime — interprets a spec
├── api/
│   └── main.py            # FastAPI routes
├── specs/
│   └── support.json       # the current agent's spec, saved as JSON
├── tests/
├── pyproject.toml
└── README.md
```

## Getting started

### Prerequisites

- Python 3.11+
- Poetry
- An Anthropic API key

### Setup

```bash
poetry install
export ANTHROPIC_API_KEY=sk-ant-...
poetry run uvicorn api.main:app --reload
```

### Try it

```bash
curl -X POST localhost:8000/agents/support/chat \
  -H 'content-type: application/json' \
  -d '{"message": "I need to cancel my subscription"}'
```

The response is a JSON object with the reply, the matched skill, the classification confidence, the response mode used, the tools invoked, and the full audit trail. The audit trail is the interesting part — it's the trace of every decision the runtime made, which is what makes the agent debuggable.

## Prior art and influences

- The anatomy vocabulary borrows from public agent-anatomy framings circulating in 2025-26.
- The idea of an agent spec as a validated data structure with structural safety guarantees is inspired by the Anthropic Skills feature, though the implementation here is different.
- The hand-rolled runtime is a deliberate choice against frameworks, not against them — the mechanics being visible is the point.

## License

MIT
