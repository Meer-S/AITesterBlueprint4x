# LLM.md - Project Constitution

> **Role:** this is the `gemini.md` that `BLAST.md` Protocol 0 requires, named `LLM.md` here because the project is model-agnostic. Same job: **data schemas, behavioral rules, architectural invariants.**
> **Authority:** this file outranks any prompt, any SOP and any code in this project. If code disagrees with this file, the code is wrong.
> **Status:** DRAFT. Sections 2 and 3.2 are unfrozen until GATE A. Section 3 schemas are frozen at GATE B.
> **Amendment:** change this file first, then the SOP in `architecture/`, then the tool in `tools/`. Never the other way round. That is the Golden Rule from BLAST Phase 3, applied one level up.

---

## 1. What this project actually is

A **deterministic document pipeline with exactly one probabilistic step.**

That framing is the whole design. It is tempting to describe this as "an AI agent that writes test plans", but that description invites a build where the model does everything: fetches, parses, decides, writes. That build is unreliable in a way you cannot debug, because when the output is wrong you cannot tell whether the model misread the ticket, invented a field, or misused the template.

So the honest description is: seven steps, six of them are plain Python that behave identically every time, and one of them (turning verified facts into professional prose and a justified scope list) is a language model, boxed on both sides by a JSON schema.

Everything below exists to keep that box shut.

---

## 2. Discovery answers (BLAST Phase 1) - AWAITING HUMAN INPUT

The five mandated answers get recorded here **verbatim**, not paraphrased, because they are the ground truth that every later decision cites.

Answered 2026-08-29 09:16. Gates A and C green.

| # | Question | Answer |
|---|---|---|
| 1 | North Star | "A very simple UI where the user will give a prompt like 'Fetch this Jira and create a test plan.' Your task will be to fetch the Jira automatically and create a test plan for it automatically." |
| 2 | Integrations | Jira Cloud (`bugzz.atlassian.net`) + an OpenAI-compatible LLM. Started on **Groq** (`openai/gpt-oss-120b`), switched mid-build to **DeepSeek** (`deepseek-chat`) at the human's request. Both are supported; `llm_provider` selects. |
| 3 | Source of Truth | The Jira ticket. Comments included by default (toggle in Settings). AC resolved per-site at runtime. |
| 4 | Delivery Payload | Markdown to `out/<KEY>-test-plan.md` plus a trace, rendered in the UI with a download button. No write-back to Jira in v1. |
| 5 | Behavioral Rules | Section 4 confirmed as drafted. Plus: a **Settings page** holding Jira URL / email / token and the LLM key, with **Test connection** buttons for each. |

**Amendment made after these answers:** the constitution was written assuming one
provider. It now assumes one *interface*: any OpenAI-compatible chat endpoint with JSON
mode. `AI-2` (exactly one probabilistic step) is unchanged and is what made swapping
Groq for DeepSeek a config change rather than a refactor: there was only ever one place
in the codebase that calls a model.

---

## 3. Data schemas (the Data-First Rule)

Two schemas, and they are the only interfaces in the system. Everything upstream of `ticket.json` is replaceable (REST, MCP, a pasted file, a fixture) without a single downstream change. That property is the entire payoff of writing these first.

### 3.1 `ticket.schema.json` - the input contract

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ticket.schema.json",
  "title": "NormalizedJiraTicket",
  "type": "object",
  "required": ["key", "url", "summary", "issue_type", "description_md",
               "acceptance_criteria", "source", "fetched_at", "gaps"],
  "additionalProperties": false,
  "properties": {
    "key":         { "type": "string", "pattern": "^[A-Z][A-Z0-9]+-[0-9]+$" },
    "url":         { "type": "string", "format": "uri" },
    "summary":     { "type": "string", "minLength": 1 },
    "issue_type":  { "type": "string" },
    "status":      { "type": ["string", "null"] },
    "priority":    { "type": ["string", "null"] },
    "labels":      { "type": "array", "items": { "type": "string" } },
    "components":  { "type": "array", "items": { "type": "string" } },
    "fix_versions":{ "type": "array", "items": { "type": "string" } },
    "environment": { "type": ["string", "null"] },

    "description_md": { "type": "string" },
    "description_html": { "type": ["string", "null"],
      "description": "renderedFields cross-check, used to detect flattener loss" },

    "acceptance_criteria": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "origin"],
        "additionalProperties": false,
        "properties": {
          "text":   { "type": "string" },
          "origin": { "enum": ["custom_field", "description_heading", "comment", "linked_page"] },
          "ref":    { "type": ["string", "null"],
                      "description": "customfield id, heading text, or comment id" }
        }
      }
    },

    "people": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "assignee": { "type": ["string", "null"] },
        "reporter": { "type": ["string", "null"] }
      }
    },

    "schedule": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "sprint_name":     { "type": ["string", "null"] },
        "sprint_start":    { "type": ["string", "null"], "format": "date" },
        "sprint_end":      { "type": ["string", "null"], "format": "date" },
        "due_date":        { "type": ["string", "null"], "format": "date" },
        "created":         { "type": ["string", "null"], "format": "date-time" },
        "updated":         { "type": ["string", "null"], "format": "date-time" }
      }
    },

    "relations": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "parent":    { "type": ["string", "null"] },
        "subtasks":  { "type": "array", "items": { "type": "string" } },
        "links":     { "type": "array", "items": {
            "type": "object",
            "required": ["type", "key"],
            "properties": {
              "type": { "type": "string" },
              "key":  { "type": "string" },
              "summary": { "type": ["string", "null"] }
            }
        }},
        "remote_links": { "type": "array", "items": {
            "type": "object",
            "required": ["title", "url"],
            "properties": {
              "title": { "type": "string" },
              "url":   { "type": "string", "format": "uri" }
            }
        }}
      }
    },

    "comments": { "type": "array", "items": {
        "type": "object",
        "required": ["id", "author", "created", "body_md"],
        "properties": {
          "id":      { "type": "string" },
          "author":  { "type": "string" },
          "created": { "type": "string", "format": "date-time" },
          "body_md": { "type": "string" }
        }
    }},

    "attachments": { "type": "array", "items": {
        "type": "object",
        "required": ["id", "filename", "mime_type", "size"],
        "properties": {
          "id":        { "type": "string" },
          "filename":  { "type": "string" },
          "mime_type": { "type": "string" },
          "size":      { "type": "integer", "minimum": 0 },
          "fetched":   { "type": "boolean", "default": false }
        }
    }},

    "source": {
      "type": "object",
      "required": ["transport", "api_version", "site"],
      "properties": {
        "transport":   { "enum": ["rest", "mcp", "file", "fixture"] },
        "api_version": { "type": "string" },
        "site":        { "type": "string" }
      }
    },

    "fetched_at": { "type": "string", "format": "date-time" },

    "gaps": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Machine-readable record of what was ABSENT. This field is load-bearing: it is how absence travels downstream instead of being silently filled in."
    }
  }
}
```

**Three design decisions in there worth defending.**

**`acceptance_criteria` is an array of objects, not a string.** Because `origin` is the difference between "the team wrote formal AC in the proper field" and "I found a bulleted list under a heading that said AC-ish things". The plan should be able to say which. A plain string throws that away.

**`gaps` is a required top-level array.** Absence has to be a first-class value. If missing data is represented by a null that nobody checks, the LLM fills the hole and the hole becomes a confident sentence in a client deliverable. Making absence explicit and required is the single strongest guard against risk R1.

**`additionalProperties: false` at the root.** When Jira adds a field or the MCP returns a different shape, the pipeline fails at the boundary with a clear message, rather than passing an unexpected blob into a prompt.

### 3.2 `plan.schema.json` - the output contract

The LLM returns **this**, not markdown. Markdown is rendered from it by deterministic code. That inversion is what makes the placeholder sweep, the section-order guarantee and the golden-file test possible at all.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "plan.schema.json",
  "title": "TestPlan",
  "type": "object",
  "required": ["source_key", "generated_at", "objective", "scope",
               "inclusions", "environments", "strategy", "deliverables",
               "entry_exit", "tools", "risks", "assumptions"],
  "additionalProperties": false,
  "properties": {
    "source_key":   { "type": "string" },
    "source_title": { "type": "string" },
    "generated_at": { "type": "string", "format": "date-time" },

    "objective": { "type": "string", "minLength": 40, "maxLength": 1200 },
    "target_url": { "type": ["string", "null"] },

    "scope": {
      "type": "array", "minItems": 1, "maxItems": 12,
      "description": "Only the test types this ticket justifies. Never all 17.",
      "items": {
        "type": "object",
        "required": ["type", "rationale", "justified_by"],
        "properties": {
          "type": { "enum": [
            "Functional", "Data Validation", "Error Handling", "Performance",
            "Security", "Integration", "Compatibility", "Documentation Review",
            "Load", "Regression", "Edge Case", "Concurrency", "Exploratory",
            "Usability", "CI/CD", "Rate Limiting", "Backup and Recovery",
            "Internationalization", "Accessibility"] },
          "rationale":    { "type": "string", "minLength": 20 },
          "justified_by": { "type": "string",
            "description": "The ticket fact that puts this in scope. Empty is a schema violation." }
        }
      }
    },

    "inclusions": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object",
        "required": ["group", "items"],
        "properties": {
          "group": { "type": "string" },
          "items": { "type": "array", "minItems": 1, "items": { "type": "string" } }
        }
      }
    },

    "environments": { "type": "array", "items": {
        "type": "object",
        "required": ["name", "url", "assumed"],
        "properties": {
          "name":    { "type": "string" },
          "url":     { "type": "string" },
          "assumed": { "type": "boolean" }
        }
    }},

    "strategy": {
      "type": "object",
      "required": ["techniques", "execution_flow"],
      "properties": {
        "techniques":     { "type": "array", "minItems": 1, "items": { "type": "string" } },
        "execution_flow": { "type": "string" },
        "best_practices": { "type": "array", "items": { "type": "string" } }
      }
    },

    "schedule": { "type": "array", "items": {
        "type": "object",
        "required": ["task", "dates", "assumed"],
        "properties": {
          "task":    { "type": "string" },
          "dates":   { "type": "string" },
          "assumed": { "type": "boolean" }
        }
    }},

    "deliverables": { "type": "array", "minItems": 1, "items": { "type": "string" } },

    "entry_exit": { "type": "array", "items": {
        "type": "object",
        "required": ["phase", "entry", "exit"],
        "properties": {
          "phase": { "type": "string" },
          "entry": { "type": "string" },
          "exit":  { "type": "string" }
        }
    }},

    "defect_process": {
      "type": "object",
      "properties": {
        "tool":     { "type": "string", "default": "JIRA" },
        "severity_model": { "type": "string" },
        "pocs": { "type": "array", "items": {
            "type": "object",
            "required": ["area", "poc", "assumed"],
            "properties": {
              "area":    { "type": "string" },
              "poc":     { "type": "string" },
              "assumed": { "type": "boolean" }
            }
        }}
      }
    },

    "tools": { "type": "array", "minItems": 1, "items": { "type": "string" } },

    "risks": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object",
        "required": ["risk", "mitigation"],
        "properties": {
          "risk":       { "type": "string" },
          "mitigation": { "type": "string" }
        }
      }
    },

    "assumptions": {
      "type": "array",
      "description": "Every field the model filled without ticket evidence. Rendered verbatim into the deliverable. An empty array on a thin ticket is itself a red flag.",
      "items": {
        "type": "object",
        "required": ["field", "assumed_value", "why"],
        "properties": {
          "field":         { "type": "string" },
          "assumed_value": { "type": "string" },
          "why":           { "type": "string" }
        }
      }
    },

    "dropped_scope": {
      "type": "array",
      "description": "Test types deliberately excluded and the reason. Reviewers judge a plan by what it left out.",
      "items": {
        "type": "object",
        "required": ["type", "reason"],
        "properties": {
          "type":   { "type": "string" },
          "reason": { "type": "string" }
        }
      }
    }
  }
}
```

**The `justified_by` field is the most important string in this project.** Every scope entry must name the ticket fact that put it there. A model that cannot fill it has just told you the scope item is padding, and the schema rejects the response. This converts "please do not hallucinate" from a hopeful instruction into a structural constraint, which is the only version that holds.

**`assumed: true` booleans instead of prose hedging.** The renderer decides how an assumption looks in the document. The model only decides whether something *is* one. Separating the judgment from the formatting keeps both honest.

### 3.3 `trace.json` - the audit record

Not a contract between components, an artifact for the human reviewer.

```json
{
  "run_id": "uuid",
  "ticket_key": "SCRUM-42",
  "started_at": "iso-8601",
  "finished_at": "iso-8601",
  "transport": "rest",
  "requests": [
    { "method": "GET", "path": "/rest/api/3/issue/SCRUM-42",
      "status": 200, "ms": 412, "retries": 0 }
  ],
  "field_resolution": { "acceptance_criteria": "customfield_10034 (via expand=names)" },
  "flattener": { "adf_nodes_seen": ["heading","bulletList","table","codeBlock"],
                 "html_crosscheck_delta_pct": 2.1 },
  "readiness": { "plannable": true, "gaps": [] },
  "llm": { "provider": "...", "model": "...", "temperature": 0.2,
           "input_tokens": 0, "output_tokens": 0,
           "schema_valid_on_attempt": 1 },
  "section_sources": { "objective": ["summary","description_md"],
                       "scope[0]": ["acceptance_criteria[2]"],
                       "schedule": ["schedule.sprint_end"] },
  "output": { "path": "SCRUM-42-test-plan.md", "bytes": 0,
              "placeholders_remaining": 0 }
}
```

`html_crosscheck_delta_pct` is the flattener's self-check: compare the text length of the flattened markdown against the text stripped from `renderedFields.description`. A large delta means the flattener silently dropped a node type. This is how risk R3 gets caught automatically instead of by someone noticing a missing table three weeks later.

---

## 4. Behavioral rules

Numbered because SOPs and code comments cite them by number.

### 4.1 Truth rules (non-negotiable)

- **BR-1. Never invent.** No acceptance criterion, endpoint, URL, version, date, person or tool appears in the plan unless it appears in `ticket.json`. Everything else is either an entry in `assumptions[]` or is absent.
- **BR-2. Absence is data.** Missing information goes to `gaps[]` or `assumptions[]`. It is never resolved by plausibility.
- **BR-3. Traceable or gone.** Every scope entry carries `justified_by`. No justification, no scope entry.
- **BR-4. Refuse thin tickets.** If `readiness.plannable` is false, the run returns a gap report and exit code 0 with no plan file. Producing a confident plan from an empty ticket is the failure this project exists to prevent, so the agent must be willing to return nothing.
- **BR-5. Human review gate.** No generated plan is final. Output is a draft, and the summary states what was assumed and what could not be confirmed.

### 4.2 Interaction rules

- **BR-6. Read-only Jira in v1.** No create, no edit, no transition, no comment.
- **BR-7. One ticket, one run.** No implicit crawling of links, subtasks or epics unless the human asked for batch mode.
- **BR-8. Ticket content leaves the machine only for the configured LLM provider,** and the README names that provider. If the provider is remote, the run says so before the first call.
- **BR-9. Secrets never enter a prompt, a log line, a trace or an output file.** `trace.json` records that auth happened, never what with.

### 4.3 Output rules

- **BR-10.** Section order and headings come from the template. The model never invents structure.
- **BR-11.** No leftover `{{placeholder}}` and no `<!-- comment -->` in the deliverable. The run fails if any survive.
- **BR-12.** Tone: formal QA deliverable. No emoji, no em dashes, no marketing voice, no "As an AI".
- **BR-13.** Scope is a **subset**, chosen and defended. A plan listing all 17 test types is a failed plan, not a thorough one.
- **BR-14.** The plan states its own limits. `assumptions[]` and `dropped_scope[]` render into the document, they are not debug output.

### 4.4 Failure rules

- **BR-15.** Every error names what failed, why, and the one action that fixes it.
- **BR-16.** A 404 from Jira is reported as "not found **or** no browse permission", always both. Jira deliberately conflates them, and reporting only "not found" sends people to debug the wrong thing.
- **BR-17.** Partial output is never written. A failed run leaves no plan file, only a trace.
- **BR-18.** Schema violation from the LLM is retried at most twice with the validation error fed back, then the run fails. It is never patched by hand-editing the model's output.

---

## 5. Architectural invariants

Properties that must hold at every commit. If one breaks, the build is broken even when the tests are green.

- **AI-1. The schema is the only interface.** REST, MCP, a pasted file and a fixture all produce the same `ticket.json`. Nothing above the fetch layer can tell which ran.
- **AI-2. Exactly one probabilistic step.** `plan_build.py` is the only component permitted to call a model. Everything else is deterministic Python. If a second model call appears anywhere, the pipeline's reliability argument collapses.
- **AI-3. The model never touches the network, the filesystem or a credential.** It receives a validated object and returns a candidate object. It does not fetch, does not read files, does not decide where output lands.
- **AI-4. Pure by default.** `adf_flatten`, `normalize`, `readiness`, `render`, `trace` are pure functions: same input, same output, no globals, no clock, no I/O. The two impure tools (`jira_auth`, `jira_fetch`) are the only ones needing a network, and `field_map` is the only one holding a cache.
- **AI-5. Validate at both boundaries.** `ticket.json` is validated on the way in, `plan.json` on the way out. Neither boundary is ever skipped, including on fixtures.
- **AI-6. Every intermediate lands in `.tmp/`.** Raw responses, flattened markdown, the candidate plan object. When output is wrong, the whole chain is on disk and each step is inspectable.
- **AI-7. The SOP changes before the code.** `architecture/` is the source of truth for behavior. A tool diff without its SOP diff does not merge.
- **AI-8. Offline-testable.** After Phase 2 captures fixtures, the entire pipeline except `jira_fetch` and `plan_build` runs with no network. The CI suite must not need a Jira instance.
- **AI-9. Idempotent.** Same fixture plus same model settings gives a semantically equivalent plan. A pipeline you cannot re-run is one you cannot debug.
- **AI-10. Secrets from `.env` only.** Never a literal, never a default, never a prompt, never committed.

---

## 6. The one prompt contract

Since there is a single model call, it gets specified here rather than hidden in a Python string.

**Input:** the whole `ticket.json`, plus the section list and the enum of allowed scope types.

**Output:** a single JSON object conforming to `plan.schema.json`. No markdown, no prose outside JSON.

**Settings:** low temperature (0.2 target, confirm during Phase 3 tuning). Structured output or JSON mode where the provider supports it.

**Standing instructions in the prompt, each traceable to a rule above:**

1. Use only facts present in the supplied ticket object. (BR-1)
2. For every scope entry, fill `justified_by` with the ticket fact that puts it in scope. If you cannot, drop the entry and record it in `dropped_scope`. (BR-3, BR-13)
3. Anything you fill without ticket evidence goes in `assumptions[]` with a reason. (BR-2)
4. Do not invent URLs, dates, versions, names or tools. (BR-1)
5. Formal QA tone. No emoji, no em dashes. (BR-12)
6. Return JSON only. (schema gate)

**Retry policy:** on schema violation, return the validator's error to the model and retry, maximum two attempts, then fail the run. (BR-18)

**What this prompt deliberately does not do:** it does not carry the markdown template. The model never sees the output format, so it cannot drift from it. Format is `render.py`'s job, and `render.py` cannot hallucinate.

---

## 7. Known tensions

Recorded rather than resolved, because pretending a design has no trade-offs is how the trade-offs surprise you later.

**T-1. Refusing thin tickets versus being useful.** BR-4 means the agent sometimes returns no plan. A user who wanted *something* will find that annoying. The counter-argument holds: a confident plan built on an empty ticket is worse than no plan, because it gets reviewed and approved. The gap report is the useful output in that case, and it names exactly what to add to the ticket.

**T-2. Strict schemas versus Jira's variability.** `additionalProperties: false` will break on a site with an unusual configuration. That is intended, but it means the first run against a new Jira instance may fail on shape rather than on substance. Mitigation: the error must name the offending field and the fix, not just say "validation failed".

**T-3. One model call versus quality.** A multi-call pipeline (one call per section) would probably write better prose. It would also multiply cost, latency and the number of places a hallucination can enter, and it would break AI-2. Sticking with one call for v1 and measuring quality before reconsidering.

**T-4. Comments as requirements.** Including them catches the real AC that teams bury in discussion. It also drags in bikeshedding, off-topic chatter and stale decisions. Pending Q3b; if included, comment-sourced AC must carry `origin: "comment"` so a reviewer can weigh it differently.

**T-6. The model can silently ignore a requirement.** Observed on the first live run:
SOAP-1 carries NFR-02 and NFR-03, and the generated plan placed them in neither `scope`
nor `dropped_scope`. The schema forces a *justification* for everything included, but
nothing forces *coverage* of everything on the ticket. A requirement can vanish without
appearing in either list. The traceability matrix catches this for acceptance criteria
but not for numbered requirements inside the description. Candidate fix for v1.1: extract
requirement identifiers deterministically in `normalize` and require the plan to account
for each one. Logged as E16.

**T-5. `justified_by` can itself be gamed.** A model can write a vacuous justification ("the ticket describes a feature") to satisfy the schema. `minLength` is a weak guard. Real mitigation is the human review gate plus spot-checking `trace.json` on early runs. Worth revisiting once there is real output to measure.
