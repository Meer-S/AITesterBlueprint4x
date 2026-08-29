# AITester Blueprint 4x

AI-powered test automation blueprint.

## Contents

- [Overview](#overview)
- [Chapters](#chapters)
  - [Chapter 01: LLM Basics](#chapter-01-llm-basics)
  - [Chapter 02: Prompt Engineering](#chapter-02-prompt-engineering)
    - [The 54-skill QA prompt suite](#the-54-skill-qa-prompt-suite)
    - [Install a skill](#install-a-skill)
  - [Chapter 03: Local Test Case Generator](#chapter-03-local-test-case-generator)
    - [Features](#features)
    - [File structure](#file-structure)
    - [Running the app](#running-the-app)
    - [Environment variables](#environment-variables)
    - [Data flow](#data-flow)
  - [Chapter 04: JobKit AI](#chapter-04-jobkit-ai)
  - [Chapter 05: Job Tracker AI](#chapter-05-job-tracker-ai)
    - [Features](#features-1)
    - [Tech stack](#tech-stack)
    - [Data model](#data-model)
    - [Running the app](#running-the-app-1)
    - [State flow](#state-flow)
  - [Chapter 06: Branding and LinkedIn Skills](#chapter-06-branding-and-linkedin-skills)
    - [What it produces](#what-it-produces)
    - [File structure](#file-structure-1)
    - [Install the skill](#install-the-skill)
    - [Pack pipeline](#pack-pipeline)
    - [Voice spine](#voice-spine)
    - [Hook ladder](#hook-ladder)
  - [Chapter 07: AI Agents](#chapter-07-ai-agents)
    - [The B.L.A.S.T. protocol](#the-blast-protocol)
    - [A.N.T. 3-layer architecture](#ant-3-layer-architecture)
    - [Running the agent](#running-the-agent)
    - [Anti-hallucination design](#anti-hallucination-design)
    - [Field notes from the build](#field-notes-from-the-build)
  - [Chapter 08: n8n Agents](#chapter-08-n8n-agents)
- [License](#license)

## Overview

AITester Blueprint 4x Where we will learn about a lot of things related to:
- AI Agent
- MCPs
- RAG
- LLM evaluations
- Langchain
- Langflow
- ATAN
- and many more things which will make us the AI-powered tester

## Chapters

### Chapter 01: LLM Basics
Foundation concepts of Large Language Models and AI fundamentals.

### Chapter 02: Prompt Engineering

RICE-POT template framework for structured prompt engineering, a Salesforce Selenium test
framework built with the Page Object Model pattern, and a
[54-skill QA prompt suite](chapter_02_Prompt_Eng/prompt_templates/README.md).

#### The 54-skill QA prompt suite

Every skill is a folder holding a `SKILL.md` with YAML frontmatter, so it drops straight into
`~/.claude/skills/` or `~/.codex/skills/` and is invoked by name. 36 skills come from
[skillmasterclass](https://github.com/PramodDutta/skillmasterclass/tree/d8c5108d5ae524b10a5a1c695cdee8cfc018be7b/skillmasterclass/skills)
and are hardened here for credential handling, execution authorization, network isolation, and
evidence redaction. 18 are new: API testing, AI safety and guardrails, and test deliverables.

```mermaid
flowchart LR
    S["QA Prompt Skill Suite<br/>54 skills"]

    S --> U["36 upstream<br/>hardened here"]
    S --> N["18 new<br/>in this repo"]

    U --> A["stlc/ · 14"]
    U --> B["playwright/ · 11"]
    U --> C["selenium/ · 11"]
    N --> D["api_testing/ · 6"]
    N --> E["safety_guardrails/ · 6"]
    N --> F["test_deliverables/ · 6"]

    classDef root fill:#57606a,stroke:#24292f,color:#fff
    classDef core fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef ext fill:#2da44e,stroke:#0f5323,color:#fff
    class S,U,N root
    class A,B,C core
    class D,E,F ext
```

Where each group plugs into the lifecycle:

```mermaid
flowchart LR
    P1["01<br/>Requirement<br/>Analysis"] --> P2["02<br/>Test<br/>Planning"] --> P3["03<br/>Test<br/>Design"] --> P4["04<br/>Test Case<br/>Development"] --> P5["05<br/>Test<br/>Execution"] --> P6["06<br/>Defect<br/>Management"] --> P7["07<br/>Test<br/>Closure"] --> GATE{{"Human<br/>review gate"}}

    P3 -.-> API["api_testing/<br/>6 skills"]
    P3 -.-> SAFE["safety_guardrails/<br/>6 skills"]
    P4 -.-> PW["playwright/<br/>11 skills"]
    P4 -.-> SE["selenium/<br/>11 skills"]
    API -.-> P5
    PW -.-> P5
    SE -.-> P5
    SAFE -.-> P6
    P7 -.-> DEL["test_deliverables/<br/>6 skills"]
    DEL -.-> GATE

    classDef core fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef ext fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class P1,P2,P3,P4,P5,P6,P7 core
    class PW,SE pack
    class API,SAFE,DEL ext
    class GATE gate
```

Nothing in the suite is self-approving. Skills report only what the supplied evidence supports,
mark anything unverified as unknown rather than assuming it passed, and stop at a human review
gate before a plan, case set, defect, report, or release decision counts as final.

<details>
<summary><b>STLC · 14 skills</b>: requirement analysis through test closure</summary>

| Skill | What it does |
| --- | --- |
| `jira-requirement-analyzer` | Score a JIRA ticket against a readiness checklist, return gaps, ambiguities, risks, and clarifying questions |
| `test-plan-generator` | Fetch a ticket and fill the standard test plan template, stopping for human review |
| `test-scenario-designer` | Derive positive, negative, boundary, and cross-role scenarios traced to each acceptance criterion |
| `api-test-designer` | Map endpoint or contract coverage across happy path, schema, auth, negative, boundary, and idempotency |
| `test-case-writer` | Expand approved scenarios into preconditions, ordered steps, expected results, and required data |
| `test-data-generator` | Produce labeled valid, invalid, boundary, and synthetic data sets per field or scenario |
| `automation-script-generator` | Framework-neutral handoff for an approved case, plus a Playwright versus Selenium stack decision |
| `test-execution-tracker` | Record pass, fail, blocked, or not-run per case with evidence, then roll up cycle progress |
| `regression-suite-selector` | Map a change to the tests that exercise it and rank a risk-based run set |
| `bug-reporter` | Turn an observed failure into a structured, reproducible defect report |
| `bug-triage-assistant` | Group likely duplicates, propose severity and priority, and route a defect backlog |
| `rca-analyzer` | Run 5-Whys plus fishbone to separate root cause from symptom and propose corrective actions |
| `test-coverage-analyzer` | Build a traceability view and surface untested ACs, thin areas, and orphan tests |
| `test-closure-reporter` | Roll cycle metrics into highlights, risks, and an advisory go or no-go |

</details>

<details>
<summary><b>Playwright · 11 skills</b>: TypeScript automation pack</summary>

| Skill | What it does |
| --- | --- |
| `pw-test-generator` | Generate a TypeScript spec from an approved, detailed test case |
| `pw-page-object-builder` | Build a POM class with `getByRole` / `getByTestId` locators, action methods, and a static `PATH` |
| `pw-locator-fixer` | Rewrite brittle XPath, CSS class, and nth-child selectors into resilient ones with a before and after map |
| `pw-fixture-designer` | Design typed auth, seeded-data, and page-object fixtures with correct scope and teardown |
| `pw-network-mocker` | Stub responses and error states via `page.route` to remove backend flakiness |
| `pw-api-tester` | Cover an endpoint through the request context: happy path, schema, auth, negative, boundary |
| `pw-visual-regression` | Set up `toHaveScreenshot` with masking, thresholds, and a baseline strategy |
| `pw-accessibility-auditor` | Wire `@axe-core/playwright` checks and triage violations against a supplied policy |
| `pw-trace-analyzer` | Read a `trace.zip` timeline to isolate the failing action and recommend the fix |
| `pw-flaky-debugger` | Root-cause races, hard waits, and shared state, then propose deterministic fixes |
| `pw-ci-configurator` | Generate a GitHub Actions workflow with sharding, blob and HTML reports, and artifacts |

</details>

<details>
<summary><b>Selenium · 11 skills</b>: Java, TestNG, Maven automation pack</summary>

| Skill | What it does |
| --- | --- |
| `se-test-generator` | Generate a Selenium 4 plus TestNG Java test from an approved case using explicit waits |
| `se-page-object-builder` | Build a Java POM class with `@FindBy` or explicit locators plus `WebDriverWait` |
| `se-locator-strategist` | Replace brittle absolute XPath with `By.id`, CSS, or Selenium 4 relative locators |
| `se-wait-fixer` | Remove `Thread.sleep` and implicit-explicit wait mixing in favor of `WebDriverWait` or `FluentWait` |
| `se-driver-manager` | Set up Selenium Manager or WebDriverManager with browser options and a thread-safe factory |
| `se-framework-scaffolder` | Scaffold a Maven plus TestNG project: base test, POM package, config loader, logging, reporting |
| `se-data-driven-designer` | Design `@DataProvider` or Excel, CSV, JSON driven tests across valid, invalid, and boundary sets |
| `se-cross-browser-runner` | Parameterize Chrome, Firefox, and Edge execution via `testng.xml` or a factory |
| `se-grid-configurator` | Configure Selenium Grid 4 hub and node or Docker, and wire `RemoteWebDriver` for parallel runs |
| `se-report-integrator` | Integrate Allure or ExtentReports with listeners, screenshot on failure, and step logging |
| `se-flaky-debugger` | Diagnose `StaleElementReferenceException` and timing races, plus a finite rerun plan |

</details>

<details>
<summary><b>API testing · 6 skills</b>: new in this repo</summary>

| Skill | What it does |
| --- | --- |
| `api-contract-validator` | Compare observed requests and responses with an OpenAPI contract and report drift |
| `api-collection-builder` | Turn approved cases into a runnable Postman/Newman or Bruno collection |
| `api-workflow-tester` | Design stateful multi-call flows across lifecycles, async jobs, events, and callbacks |
| `api-authorization-boundary-tester` | Build a policy-backed access matrix for BOLA and IDOR, tenant isolation, and privilege boundaries |
| `api-resilience-tester` | Plan bounded fault tests for timeouts, retries, 429 throttling, duplicates, and recovery |
| `api-performance-test-planner` | Draft workloads, thresholds, and abort conditions with an optional k6 or JMeter skeleton |

</details>

<details>
<summary><b>AI safety and guardrails · 6 skills</b>: new in this repo</summary>

| Skill | What it does |
| --- | --- |
| `ai-threat-modeler` | Map assets, trust boundaries, memory, retrieval, tools, abuse cases, and residual risk |
| `prompt-injection-resilience-tester` | Cover direct and indirect injection, instruction hierarchy, obfuscation, and canary exfiltration |
| `sensitive-data-leakage-tester` | Probe prompts, context, retrieval, caches, logs, and retention with synthetic canaries |
| `ai-agent-tool-safety-tester` | Verify tool allowlists, least privilege, approval gates, dry runs, idempotency, and rollback |
| `content-safety-guardrail-evaluator` | Measure unsafe acceptance, appropriate refusal, over-refusal, and multi-turn policy coverage |
| `ai-fairness-bias-evaluator` | Run subgroup, paired counterfactual, and intersectional fairness tests on synthetic or consented data |

</details>

<details>
<summary><b>Test deliverables · 6 skills</b>: new in this repo</summary>

| Skill | What it does |
| --- | --- |
| `review-test-deliverables` | Quality-check a QA artifact and return source-located findings before peer review |
| `maintain-test-traceability` | Maintain a versioned RTM from requirements through cases, runs, defects, and evidence |
| `draft-test-status-brief` | Draft an as-of daily or weekly QA status from approved execution and risk snapshots |
| `assemble-release-decision-record` | Map evidence to exit criteria and record the gate decision, waivers, and conditions |
| `curate-test-evidence-bundle` | Inventory, hash, and version existing evidence into a shareable manifest |
| `prepare-qa-audit-handoff` | Index deliverables against an audit control list with custodians and chain of custody |

</details>

#### Install a skill

```bash
skill_source=chapter_02_Prompt_Eng/prompt_templates/api_testing/api-contract-validator
skill_destination="$HOME/.codex/skills/api-contract-validator"

if [ -e "$skill_destination" ]; then
  echo "Skill already exists; compare and back it up before an explicitly approved update."
  exit 1
fi

mkdir -p "$(dirname "$skill_destination")"
cp -R "$skill_source" "$skill_destination"
```

Then invoke it by name, such as `$api-contract-validator`. The 18 new skills also ship an
`agents/openai.yaml` so Codex picks up their metadata.

### Chapter 03: Local Test Case Generator

A two-screen Streamlit application that generates test cases from Jira tickets using a local LLM with cloud fallback.

#### Features

- Chat-style interface: type a Jira ticket key and get structured test cases
- Fetches ticket details (summary, description, acceptance criteria) from Jira REST API
- Generates test cases using Ollama (`gemma3:1b` on `localhost:11434`) by default
- Automatic fallback to Groq cloud API when Ollama is unavailable
- Settings page to configure Jira credentials, LLM provider, and Groq API key
- Credentials persisted via `.env` (seed) and `config.json` (runtime store)
- Anti-hallucination prompt template with strict formatting rules

#### File structure

```
chapter_03_Local_TC_Generator/
├── src/
│   ├── app.py                 # Main Streamlit chat screen
│   ├── pages/
│   │   └── settings.py        # Settings screen (Jira + LLM config)
│   ├── config_store.py        # Settings persistence (.env -> config.json)
│   ├── jira_client.py         # Jira REST API wrapper
│   ├── llm_client.py          # Ollama + Groq orchestrator with fallback
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Credentials (git-ignored)
│   └── config.json            # Runtime settings (git-ignored)
├── templates/
│   └── testcase_creator.md    # Test case generation template
└── src/
    ├── Finetune_Prompt.md     # Original design prompt
    ├── Prompt.md              # Project requirements
    └── plan.md                # Implementation plan
```

#### Running the app

```bash
cd chapter_03_Local_TC_Generator/src
pip install -r requirements.txt
streamlit run app.py
```

#### Environment variables

Seed these in `chapter_03_Local_TC_Generator/src/.env`, which is git-ignored:

```
JIRA_URL=https://your-org.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your-jira-api-token
GROQ_API_KEY=your-groq-api-key
OLLAMA_MODEL=gemma3:1b
```

#### Data flow

```
User types "create test cases for JIRA-102"
  -> app.py parses JIRA-102 via regex
  -> jira_client.py fetches ticket from Jira REST API
  -> templates/testcase_creator.md loaded and merged with ticket content
  -> llm_client.py tries Ollama first, falls back to Groq
  -> Test cases rendered as a formatted markdown table in chat
```

### Chapter 04: JobKit AI

A resume tailoring toolkit that turns raw LinkedIn job exports into tailored,
per-role resumes. The `resume-tailor` skill reads a job description, produces a
structured spec (`.specs/*.json`) with highlighted skills, fit-gap notes, and
section-by-section content, then renders a polished `.docx` into `output/`.

**Q&A - why use this?**
- **Q: When do I reach for it?** A: When applying to a specific role and you want the resume keywords, ordering, and emphasis matched to that posting instead of sending one generic CV.
- **Q: What does it replace?** A: Manual copy-paste tailoring in Word, and the guesswork of which buzzwords a posting actually screens for.
- **Q: What's the gotcha?** A: The spec flags fit gaps (missing years, unverified claims) rather than papering over them. Resolve every `[confirm ...]` marker before sending anything out.

```mermaid
flowchart LR
    CSV["linkedin_jobs.csv<br/>LinkedIn export"] --> JD["Pick a job<br/>description"]
    JD --> SKILL["resume-tailor<br/>skill"]
    SKILL --> SPEC[".specs/job.json<br/>structured spec +<br/>fit gaps"]
    SPEC --> REVIEW{"Human<br/>review"}
    REVIEW --> DOCX["output/*.docx<br/>tailored resume"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class CSV,JD src
    class SKILL,SPEC ai
    class REVIEW gate
    class DOCX out
```

The repo ships two worked examples: specs and rendered docx files for an
Accenture Test Automation Lead and a Mouser Electronics Software QA Team Lead.

### Chapter 05: Job Tracker AI

A local-first kanban board for tracking job applications. Six columns from
Wishlist to Rejected, drag-and-drop between stages, all data stored in the
browser's IndexedDB so nothing leaves the machine.

#### Features

- Kanban board with six status columns: Wishlist, Applied, Follow-up, Interview, Offer, Rejected
- Drag-and-drop between columns via dnd-kit, with pointer and keyboard sensors
- Add/edit modal with company, role, LinkedIn URL, resume used, salary range, date applied, status, and notes
- Resume name autocomplete from previously used resumes
- Search by company or role, sort by newest or oldest applied date
- Header metrics: total jobs, interviews, offers
- JSON backup export and import (import replaces existing data after confirmation)
- Light/dark theme toggle persisted in localStorage
- Delete confirmation dialog, toast notifications, Escape-to-close modals

#### Tech stack

| Layer | Choice |
| --- | --- |
| UI | React 18 + Vite |
| Styling | Tailwind CSS 3 (`darkMode: 'class'`) |
| Drag and drop | @dnd-kit/core + @dnd-kit/sortable |
| Persistence | IndexedDB via `idb` |
| Icons | lucide-react |

#### Data model

Each job is one record in the `jobs` object store of the `job-tracker-ai`
IndexedDB database, keyed by `id`, indexed by `status` and `dateApplied`:

```js
{
  id: 'uuid',
  company: 'Accenture',
  role: 'Test Automation Lead',
  linkedInUrl: 'https://linkedin.com/jobs/...',
  resumeUsed: 'QA_Lead_Resume',
  dateApplied: '2026-08-23',
  salaryRange: '',
  notes: '',
  status: 'applied',   // wishlist | applied | follow-up | interview | offer | rejected
  createdAt: '...',
  updatedAt: '...',
}
```

#### Running the app

```bash
cd chapter_05_JobTrackerAI
npm install
npm run dev        # http://localhost:5173
```

#### State flow

```mermaid
flowchart LR
    LOAD["Mount<br/>getAllJobs()"] --> BOARD["Kanban board<br/>grouped by status"]
    BOARD -->|"drag card"| DND["handleDragEnd<br/>saveJob(updated)"]
    BOARD -->|"add / edit"| MODAL["JobModal<br/>validated form"]
    MODAL --> SAVE["saveJob()"]
    BOARD -->|"delete"| CONFIRM["ConfirmDelete"] --> DEL["removeJob()"]
    BOARD --> EXPORT["Export JSON backup"]
    EXPORT -.-> IMPORT["Import replaces<br/>all jobs"] --> REPLACE["replaceAllJobs()"]
    DND --> BOARD
    SAVE --> BOARD
    DEL --> BOARD
    REPLACE --> BOARD

    classDef ui fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef store fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef io fill:#2da44e,stroke:#0f5323,color:#fff
    class LOAD,BOARD,MODAL,CONFIRM ui
    class DND,SAVE,DEL,REPLACE store
    class EXPORT,IMPORT io
```

**Q&A - why use this?**
- **Q: When do I reach for it?** A: Any active job hunt where you are juggling more than a handful of applications across stages.
- **Q: What does it replace?** A: The spreadsheet. Status changes become a drag instead of a cell edit, and search plus metrics come free.
- **Q: What's the gotcha?** A: Data lives only in that browser's IndexedDB. Use Export before clearing site data or switching machines; import replaces everything.

### Chapter 06: Branding and LinkedIn Skills

A Claude/Codex skill that turns any content seed into a publish-ready pack in
The Testing Academy voice. Drop in a title, rough bullets, a screenshot, a URL,
a thread, or a spoken dump. The skill returns a Medium article, a LinkedIn post,
LinkedIn image prompts, and a Medium cover prompt.

The voice spec, deliverable formats, and a full worked example live in
[chapter_06_Branding_LinkedinSkills/README.md](chapter_06_Branding_LinkedinSkills/README.md).

#### What it produces

| File | Job |
| --- | --- |
| `pack-1-medium-article.md` | 2,500 to 3,200 word Medium draft |
| `pack-2-linkedin-post.md` | Hook ladder, 220 to 260 word post, first-comment blocks |
| `pack-3-linkedin-image-prompts.md` | Style C v2 tweet-screenshot cards |
| `pack-4-medium-image-prompt.md` | Style A 16:9 cyber infographic cover |

```mermaid
flowchart LR
    subgraph IN["Seed"]
        T["Title"]
        B["Bullets"]
        U["URL"]
        D["Dump"]
    end

    SKILL["content-repurpose-pack"]

    subgraph OUT["Pack"]
        P1["Medium<br/>article"]
        P2["LinkedIn<br/>post"]
        P3["LinkedIn<br/>cards"]
        P4["Medium<br/>cover"]
    end

    T --> SKILL
    B --> SKILL
    U --> SKILL
    D --> SKILL
    SKILL --> P1 --> PUB{"Human<br/>publish"}
    SKILL --> P2 --> PUB
    SKILL --> P3 --> PUB
    SKILL --> P4 --> PUB

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class T,B,U,D src
    class SKILL ai
    class P1,P2,P3,P4 out
    class PUB gate
```

#### File structure

```
chapter_06_Branding_LinkedinSkills/
├── files.zip                         # original archive
├── content-repurpose-pack.skill      # packaged bundle
└── content-repurpose-pack/
    ├── SKILL.md                      # pipeline and hook protocol
    └── references/
        ├── brand-voice.md            # Hook / Story / Offer, 13 threads
        ├── deliverable-specs.md      # exact formats for the four files
        └── worked-example.md         # one full input-to-output pass
```

#### Install the skill

```bash
skill_source=chapter_06_Branding_LinkedinSkills/content-repurpose-pack
skill_destination="$HOME/.claude/skills/content-repurpose-pack"

if [ -e "$skill_destination" ]; then
  echo "Skill already exists; compare and back it up before an explicitly approved update."
  exit 1
fi

mkdir -p "$(dirname "$skill_destination")"
cp -R "$skill_source" "$skill_destination"
```

For Codex, use `$HOME/.codex/skills/content-repurpose-pack`. Then invoke it by
name, such as `$content-repurpose-pack`.

#### Pack pipeline

```mermaid
flowchart LR
    SEED["Any seed<br/>title, bullets,<br/>URL, dump"] --> SHAPE["Identify shape<br/>reconcile the<br/>promised number"]
    SHAPE --> MINE["Mine five things<br/>thesis, framework,<br/>assets, numbers"]
    MINE --> VOICE["Map to voice<br/>Hook / Story / Offer"]
    VOICE --> PACK["Four pack files"]
    PACK --> SWEEP["Grep sweep<br/>chai, BFSI, sprint tests"]
    SWEEP --> PUBLISH{"Human<br/>publish"}

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class SEED src
    class SHAPE,MINE,VOICE,SWEEP ai
    class PACK out
    class PUBLISH gate
```

#### Voice spine

Same three beats on LinkedIn and Medium. Only the word budget changes. The usual
miss is a great Hook and Story with no Offer.

```mermaid
flowchart LR
    HOOK["HOOK<br/>earn the expand"] --> STORY["STORY<br/>one real receipt"]
    STORY --> OFFER["OFFER<br/>so what do I do"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class HOOK ai
    class STORY pack
    class OFFER out
```

```mermaid
flowchart TB
    L1["Hook: 2 lines"] --> L2["Receipt with an undeniable detail"]
    L2 --> L3["Two-beat punch, under 8 words"]
    L3 --> L4["Steelman, then pivot"]
    L4 --> L5["X is not Y. X is Z."]
    L5 --> L6["One-tier offer"]
    L6 --> L7["Hashtags"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class L1,L2 ai
    class L3,L4,L5 pack
    class L6,L7 out
```

Offer rotation: four posts on a belief or a question, then one free asset, and a
product link only for real launches.

```mermaid
flowchart LR
    T1["Tier 1<br/>Belief"] --> T2["Tier 2<br/>Question"]
    T2 --> T3["Tier 3<br/>Asset"]
    T3 --> T4["Tier 4<br/>Product"]

    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    class T1,T2 out
    class T3 ai
    class T4 pack
```

#### Hook ladder

When the ask is controversial, the skill returns three labelled variants instead
of sanitizing or refusing.

```mermaid
flowchart TB
    ASK["Controversial hooks requested"] --> A["A. Prediction<br/>forecast, not fake data"]
    ASK --> B["B. Threat<br/>highest reach"]
    ASK --> C["C. Receipt<br/>a story, not a claim"]

    A --> LI["LinkedIn: A or C"]
    C --> LI
    B --> X["X: B often belongs here"]
    C --> REC["Default on LinkedIn"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    class ASK src
    class A ai
    class B gate
    class C,REC out
    class LI,X pack
```

**Q&A - why use this?**
- **Q: When do I reach for it?** A: When a seed needs to become a Medium + LinkedIn + image pack in this voice, not a generic rewrite.
- **Q: What does it replace?** A: Re-prompting from scratch for length, banned phrases, first-comment splits, and image specs.
- **Q: What's the gotcha?** A: A pack with no receipt is the biggest quality drop. Supply a real story, or accept a composite flagged for anonymization. No em dashes, anywhere.

### Chapter 07: AI Agents

A **Test Plan Agent**: give it a Jira ID, get back a formal 14-section test plan
where every claim traces to a real field on the ticket. Built with the
**B.L.A.S.T.** protocol on the **A.N.T.** 3-layer architecture.

**Why:** the naive version (paste a ticket into a chat window, ask for a test plan)
hallucinates acceptance criteria, produces a different shape every run, and gives you
no way to tell which step went wrong when the output is bad.

**Q&A - why use this?**
- **Q: When do I reach for it?** A: When a story needs a review-ready test plan and you need every scope decision defensible to a reviewer.
- **Q: What does it replace?** A: Hand-writing the same 14 sections per ticket, and the re-prompting loop when a chat model drifts from your template.
- **Q: What's the gotcha?** A: It will refuse a thin ticket rather than invent one, returning a gap report instead. That is the design, not a bug: 2 of 4 real tickets were refused in testing.

#### The B.L.A.S.T. protocol

Five phases with hard gates. Nothing enters `tools/` until Discovery Questions are
answered, the data schema is frozen, and the blueprint is approved.

```mermaid
flowchart LR
    P0["Protocol 0<br/>Initialize memory"] --> GATE{{"Gates A/B/C<br/>halt until green"}}
    GATE --> B["B - Blueprint<br/>5 discovery questions<br/>freeze the schema"]
    B --> L["L - Link<br/>prove every connection<br/>before any logic"]
    L --> A["A - Architect<br/>SOPs first, then tools"]
    A --> S["S - Stylize<br/>frozen template<br/>output gates"]
    S --> T["T - Trigger<br/>UI + CLI"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class P0 src
    class GATE gate
    class B,L,A ai
    class S,T out
```

Four memory files carry the project state: `task_plan.md` (phases and checklists),
`findings.md` (research and constraints), `progress.md` (a timestamped log of what was
done, what errored, what the result was), and `LLM.md` (the constitution: schemas,
18 behavioural rules, 10 architectural invariants).

#### A.N.T. 3-layer architecture

The premise: **LLMs are probabilistic, business logic must be deterministic.** So the
pipeline is seven steps and exactly one of them calls a model.

```mermaid
flowchart TB
    subgraph L1["Layer 1 - Architecture (architecture/)"]
        SOP["6 markdown SOPs<br/>Golden Rule: SOP changes before code"]
    end
    subgraph L2["Layer 2 - Navigation (navigation.py)"]
        NAV["Routes tools, owns failure branches<br/>parses intent with a regex, not an LLM"]
    end
    subgraph L3["Layer 3 - Tools (tools/)"]
        T1["jira_fetch · field_map<br/>adf_flatten · normalize"]
        T2["readiness · render · trace<br/>6 of 9 are pure functions"]
        T3["plan_build<br/>THE ONLY probabilistic step"]
    end

    SOP --> NAV --> T1 --> T2
    NAV --> T3

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class SOP src
    class NAV ai
    class T1,T2 out
    class T3 gate
```

The pipeline, end to end:

```mermaid
flowchart LR
    P["prompt<br/>'plan SOAP-1'"] --> K["parse key<br/>regex"]
    K --> F["fetch<br/>REST v3"]
    F --> N["normalize<br/>ADF to markdown"]
    N --> R{{"readiness<br/>score >= 5/11?"}}
    R -->|no| GAP["gap report<br/>NO plan written"]
    R -->|yes| LLM["one LLM call<br/>returns JSON"]
    LLM --> V{{"schema gate<br/>2 retries max"}}
    V --> RND["render<br/>frozen template"]
    RND --> MD["plan.md + trace.json"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class P,K,F,N src
    class LLM ai
    class R,V gate
    class RND,MD,GAP out
```

#### Running the agent

```bash
cd chapter_07_AI_Agents/Test-Plan-Agent-Blast
pip install -r requirements.txt
cp .env.example .env          # or use the Settings page
streamlit run app.py          # UI on :8501
```

Open **Settings** first: add the Jira URL, email and API token plus an LLM key
(DeepSeek or Groq, both OpenAI-compatible), then press both **Test connection**
buttons. The CLI mirrors the UI:

```bash
python run.py SOAP-1                    # generate a plan
python run.py "make a plan for VWO-49"  # natural language, same result
python run.py --health                  # prove both connections
python run.py --dry-run SOAP-1          # fetch + normalize, no LLM call
```

Exit codes: `0` ok, `2` bad input, `3` auth, `4` not found, `5` rate limited,
`6` schema violation, `7` LLM failure.

#### Anti-hallucination design

The model returns **JSON, not markdown**. `render.py` owns the format, so the model
never sees the template and cannot drift from it. Two schema fields do the real work:

```json
{
  "scope": [{
    "type": "Error Handling",
    "rationale": "Assert the 400 response names the offending field.",
    "justified_by": "FR-03: the system must reject requests missing sISBN."
  }],
  "assumptions": [{
    "field": "environment.url",
    "assumed_value": "QA environment (URL not specified in ticket)",
    "why": "Ticket does not provide a concrete environment URL"
  }]
}
```

`justified_by` is required on every scope entry and must name the ticket fact that put
it there. A model that cannot fill it has just admitted the entry is padding, and the
schema rejects the response. That turns "please do not hallucinate" from a hopeful
instruction into a structural constraint. Anything filled without ticket evidence lands
in `assumptions[]` and renders into the deliverable, not into a debug log.

#### Field notes from the build

Three findings that only surfaced by running it against a live Jira and a live model:

| Finding | Why it matters |
|---|---|
| **Jira answers 404, not 401**, on `/issue/{key}` when auth is bad | It hides issue existence from unauthenticated callers, so an expired token presents as a *missing ticket*. The fix is to call `/myself` on a 404 to disambiguate. |
| **Groq counts `max_tokens` against the TPM limit** | The reservation is billed, not the completion. A 2,669-token prompt with `max_tokens: 8000` reads as 10,669 against an 8,000 cap. Check the reservation before slimming the payload. |
| **`config.json` silently shadowed `.env`** | Saving credentials in the UI wrote them to `config.json`, which outranks `.env`, so later edits to `.env` were ignored with no indication. Settings now shows the source of every value. |

### Chapter 08: n8n Agents

Two n8n workflows that wire an LLM to Jira as a **tool**, so a chat message like
"fetch PROJ-12" or "raise a bug for the login page" becomes a real Jira API call.

**Why:** it is the same Jira-agent idea as chapter 07, expressed on a visual
low-code canvas instead of in Python, which makes the agent loop legible to people
who will not read a call stack.

**Q&A - why use this?**
- **Q: When do I reach for it?** A: When the workflow should be editable by someone who does not write Python, or when it needs to run on a schedule without hosting your own app.
- **Q: What does it replace?** A: The glue code around auth, retries and scheduling. n8n stores credentials by reference, so the exported JSON carries no secrets.
- **Q: What's the gotcha?** A: The agent decides *when* to call the Jira tool, so a vague prompt can create the wrong ticket. Chapter 07's approach (deterministic fetch, one bounded LLM step) trades that flexibility for repeatability.

```mermaid
flowchart LR
    CT["Chat trigger"] --> AG["AI Agent"]
    ST["Schedule trigger"] --> AG
    BR["Brain<br/>OpenAI chat model"] --> AG
    ME["Memory<br/>buffer window"] --> AG
    AG --> JT["Jira tool<br/>get / create issue"]
    JT --> OUT["Issue fetched<br/>or created"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class CT,ST src
    class AG,BR ai
    class ME,JT gate
    class OUT out
```

Import either file through **n8n > Workflows > Import from File**, then attach your
own `openAiApi` and `jiraSoftwareCloudApi` credentials:

```
chapter_08_n8n/Agents/
├── 01_FetchJIRATicket_AIAgent.json    # 9 nodes: chat/schedule trigger -> agent -> Jira get
└── 02_CreateJIRATicket_AIAgent.json   # 9 nodes: same shape, Jira create
```

## License

MIT
