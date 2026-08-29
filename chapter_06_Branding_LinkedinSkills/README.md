# Chapter 06: Branding and LinkedIn Skills

A Claude/Codex skill that turns any content seed into a publish-ready pack in
Pramod Dutta's Testing Academy voice. Drop in a title, a handful of rough
bullets, a screenshot, a URL, a thread, or a spoken brain dump. The skill
returns four files: a Medium article, a LinkedIn post, LinkedIn image prompts,
and a Medium cover prompt.

This is not a generic "write a post" prompt. It encodes the Hook / Story / Offer
spine, the word budgets, the banned phrases, the image specs, and the failure
modes observed in real sessions.

## Contents

- [The big picture](#the-big-picture)
- [What it produces](#what-it-produces)
- [File layout](#file-layout)
- [Install the skill](#install-the-skill)
- [How a pack is produced](#how-a-pack-is-produced)
  - [Seed shapes](#seed-shapes)
  - [Mining the seed](#mining-the-seed)
  - [Voice spine](#voice-spine)
  - [Offer ladder](#offer-ladder)
  - [Controversial hooks](#controversial-hooks)
  - [Closing sweep](#closing-sweep)
- [Worked example](#worked-example)
- [Thirteen content threads](#thirteen-content-threads)
- [Q&A](#qa)
- [Trigger phrases](#trigger-phrases)

## The big picture

A seed goes in. Four publish-ready files come out. A human still hits publish.

```mermaid
flowchart LR
    subgraph IN["What you drop in"]
        T["Bare title"]
        B["Bullets"]
        S["Screenshot"]
        U["URL"]
        A["Thread"]
        D["Spoken dump"]
    end

    SKILL["content-repurpose-pack<br/>Hook / Story / Offer"]

    subgraph OUT["What you get back"]
        P1["pack-1<br/>Medium article"]
        P2["pack-2<br/>LinkedIn post"]
        P3["pack-3<br/>LinkedIn cards"]
        P4["pack-4<br/>Medium cover"]
    end

    T --> SKILL
    B --> SKILL
    S --> SKILL
    U --> SKILL
    A --> SKILL
    D --> SKILL
    SKILL --> P1
    SKILL --> P2
    SKILL --> P3
    SKILL --> P4
    P1 --> PUB{"Human<br/>publish"}
    P2 --> PUB
    P3 --> PUB
    P4 --> PUB

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class T,B,S,U,A,D src
    class SKILL ai
    class P1,P2,P3,P4 out
    class PUB gate
```

## What it produces

| File | Job |
| --- | --- |
| `pack-1-medium-article.md` | 2,500 to 3,200 word Medium draft, paste-ready Markdown |
| `pack-2-linkedin-post.md` | Hook ladder + 220 to 260 word post + first-comment blocks |
| `pack-3-linkedin-image-prompts.md` | Style C v2 tweet-screenshot cards (hook, mechanism, closer) |
| `pack-4-medium-image-prompt.md` | Style A 16:9 cyber infographic for the Medium cover |

If you ask for a single deliverable, it still ships as its own file. Deliverables
are never merged.

```mermaid
flowchart TB
    PACK["One pack run"]

    PACK --> M["pack-1 Medium article<br/>2,500 to 3,200 words"]
    PACK --> L["pack-2 LinkedIn post<br/>220 to 260 words"]
    PACK --> C["pack-3 LinkedIn image prompts<br/>Style C v2, 4:5"]
    PACK --> I["pack-4 Medium cover prompt<br/>Style A, 16:9"]

    L --> LC["First comments<br/>prompts, syllabi, links"]
    L --> LH["Hook ladder A / B / C"]
    C --> C1["Variant 1 Hook<br/>posted at publish"]
    C --> C2["Variant 2 Mechanism<br/>comment + Instagram"]
    C --> C3["Variant 3 Closer<br/>repost in 5 to 7 days"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    class PACK ai
    class M,L,C,I out
    class LC,LH,C1,C2,C3 pack
```

## File layout

```
chapter_06_Branding_LinkedinSkills/
├── README.md                         # this file
├── files.zip                         # original archive
├── content-repurpose-pack.skill      # packaged .skill bundle
└── content-repurpose-pack/           # installable skill folder
    ├── SKILL.md                      # pipeline, hook protocol, closing sweep
    └── references/
        ├── brand-voice.md            # identity, spine, 13 threads, signature lines
        ├── deliverable-specs.md      # exact formats for the four pack files
        └── worked-example.md         # one full input-to-output pass
```

`files.zip` holds the same materials as a flat archive plus the `.skill` bundle.
The folder is the copy to install: `SKILL.md` reads
`references/brand-voice.md`, not a sibling file.

```mermaid
flowchart LR
    ZIP["files.zip"] --> SKILLFILE["content-repurpose-pack.skill"]
    ZIP --> FOLDER["content-repurpose-pack/"]
    FOLDER --> MD["SKILL.md"]
    FOLDER --> REF["references/"]
    REF --> BV["brand-voice.md"]
    REF --> DS["deliverable-specs.md"]
    REF --> WE["worked-example.md"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class ZIP,SKILLFILE src
    class FOLDER,MD ai
    class REF,BV,DS,WE out
```

## Install the skill

Copy the folder only when the destination name is unused:

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

For Codex, point `skill_destination` at `$HOME/.codex/skills/content-repurpose-pack`
instead. Then invoke it by name, such as `$content-repurpose-pack`.

You can also drop `content-repurpose-pack.skill` into a client that accepts
packaged `.skill` files. It is a zip of the same folder.

## How a pack is produced

The skill runs in order. It re-reads the voice spec every time; an earlier draft
in the conversation does not substitute for it.

```mermaid
flowchart TB
    S0["0. Load the voice<br/>brand-voice, specs, example"]
    S1["1. Identify the seed shape"]
    S2["2. Reconcile the promised number<br/>title wins, split do not pad"]
    S3["3. Mine five things"]
    S4["4. Map to the voice<br/>thread, signature line, receipt"]
    S5["5. Write four separate files"]
    S6["6. Controversial hook ladder<br/>only if asked"]
    S7["7. Closing sweep<br/>grep, word count, three tests"]
    PUB{"Human publish"}

    S0 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> PUB

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class S0,S1,S2,S3 ai
    class S4,S6 pack
    class S5,S7 out
    class PUB gate
```

1. **Load the voice.** Read `brand-voice.md`, then the deliverable specs, then the
   worked example. Hard rule: no em dashes anywhere.
2. **Identify the seed.** Six shapes: bare title, bullets, screenshot, URL,
   thread/article, spoken brain dump. Each is handled differently.
3. **Reconcile the promised number.** If the title says "7 steps" and the bullets
   are 5, the title wins. Split compound bullets. Never pad with filler.
4. **Mine five things.** The transferable thesis, the framework, verbatim assets,
   numbers (owned vs verifiable vs source-only), and a discard pile of the
   original author's CTAs.
5. **Map to the voice.** Pick one of the 13 content threads, reuse a signature
   line if it fits, re-angle one example into QA/SDET, and find a receipt.
6. **Write the four files.** Templates live in `deliverable-specs.md`.
7. **Closing sweep.** Grep for em dashes and banned phrases, count words, then
   run the chai test, the BFSI CTO test, and the next-sprint test.

### Seed shapes

```mermaid
flowchart TB
    SEED["Incoming seed"] --> Q{What shape is it?}

    Q --> T["Bare title"]
    Q --> B["Bullets or steps"]
    Q --> S["Screenshot"]
    Q --> U["URL"]
    Q --> A["Thread or article"]
    Q --> D["Spoken brain dump"]

    T --> T1["Title is the promise<br/>build the framework"]
    B --> B1["Normalize, order,<br/>expand. Never reformat only"]
    S --> S1{"Content or style?"}
    S1 --> S2["Content: transcribe first"]
    S1 --> S3["Style: image beats<br/>the written spec"]
    U --> U1["Fetch it. Never invent<br/>what a link says"]
    A --> A1["Mine with the<br/>extraction protocol"]
    D --> D1["Second person, dedupe,<br/>keep every number"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class SEED src
    class Q,S1 gate
    class T,B,S,U,A,D ai
    class T1,B1,S2,S3,U1,A1,D1 out
```

### Mining the seed

Pull exactly five things, in this order. Source-only stats are never stated as fact.

```mermaid
flowchart LR
    M1["1. Thesis<br/>one transferable line"] --> M2["2. Framework<br/>the numbered moves"]
    M2 --> M3["3. Verbatim assets<br/>prompts, code, files"]
    M3 --> M4["4. Numbers"]
    M4 --> M5["5. Discard pile<br/>their CTAs, not yours"]

    M4 --> N1["Owned prescriptions<br/>use freely"]
    M4 --> N2["Verifiable facts<br/>keep with attribution"]
    M4 --> N3["Source-only claims<br/>soften, attribute, or omit"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class M1,M2,M3,M5 ai
    class M4,N1,N2 out
    class N3 gate
```

### Voice spine

Every LinkedIn post and every Medium article uses the same three beats. Only the
word budget changes.

```mermaid
flowchart LR
    HOOK["HOOK<br/>earn the expand"] --> STORY["STORY<br/>one real receipt"]
    STORY --> OFFER["OFFER<br/>so what do I do"]

    HOOK --> H1["LinkedIn: 2 lines<br/>15 to 25 words"]
    HOOK --> H2["Medium: title + subtitle<br/>+ first 2 paragraphs"]
    STORY --> S1["LinkedIn: 120 to 160"]
    STORY --> S2["Medium: 60 to 75%"]
    OFFER --> O1["LinkedIn: 40 to 60"]
    OFFER --> O2["Medium: Caveats +<br/>Bottom Line + CTA"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class HOOK ai
    class STORY pack
    class OFFER out
    class H1,S1,O1 ai
    class H2,S2,O2 out
```

| Beat | Job | LinkedIn | Medium |
| --- | --- | --- | --- |
| Hook | Earn the expand. Create a gap. | 2 lines, 15 to 25 words | Title + bold subtitle + first 2 paragraphs |
| Story | Pay it off with one thing that happened | 120 to 160 words | 60 to 75% of the article |
| Offer | Convert attention into a next action | 40 to 60 words | Honest Caveats + Bottom Line + italic CTA |

LinkedIn total is 220 to 260 words. 280 is the hard ceiling. The usual miss is a
great Hook and Story with no Offer.

How a LinkedIn post is assembled, in order:

```mermaid
flowchart TB
    L1["Hook line 1: claim, condition, or receipt"] --> L2["Hook line 2: narrowing or list promise"]
    L2 --> L3["Optional circle checklist, 4 to 6 items"]
    L3 --> L4["The receipt, with an undeniable detail"]
    L4 --> L5["Two-beat punch. Standing alone. Under 8 words"]
    L5 --> L6["Steelman the counter-argument, then pivot"]
    L6 --> L7["Definitional reversal. X is not Y. X is Z."]
    L7 --> L8["Offer: one tier only"]
    L8 --> L9["Hashtags. 5 to 7. QA, SDET, and topic tags"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class L1,L2 ai
    class L3,L4,L5,L6,L7 pack
    class L8,L9 out
```

### Offer ladder

One tier per post. Rotate. Roughly four posts on Tier 1 or 2, then one on Tier 3.
Tier 4 only for actual launches.

```mermaid
flowchart TB
    T1["Tier 1: Belief<br/>a rule they can use on Monday<br/>no link"] --> T2["Tier 2: Question<br/>binary or specific<br/>never what do you think"]
    T2 --> T3["Tier 3: Asset<br/>name it in the body<br/>link in the first comment"]
    T3 --> T4["Tier 4: Product<br/>course or masterclass<br/>body link allowed, reach hit accepted"]

    T1 -.-> R["Rotate. Six straight course links<br/>burns the senior-colleague voice"]
    T4 -.-> R

    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class T1,T2 out
    class T3 ai
    class T4 pack
    class R gate
```

### Controversial hooks

When you ask for controversial, provocative, or bold hooks, the skill does not
refuse and does not sanitize. It returns a graded ladder:

```mermaid
flowchart TB
    ASK["User asks for controversial hooks"] --> A["A. The prediction<br/>aggressive claim, marked as a forecast"]
    ASK --> B["B. The threat<br/>hard deadline, highest reach"]
    ASK --> C["C. The receipt<br/>a story, not a claim"]

    A --> LI["LinkedIn: A or C"]
    C --> LI
    B --> X["X: B often belongs here"]
    C --> REC["Recommended default<br/>nobody argues with what happened"]
    B --> FAIL["Named failure mode:<br/>people argue the deadline,<br/>not the work"]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    class ASK src
    class A ai
    class B gate
    class C,REC out
    class LI,X pack
    class FAIL gate
```

- **A. The prediction.** Aggressive claim, marked as a forecast, timing record
  admitted as imperfect.
- **B. The threat.** Closest to a hard deadline, highest reach, often fails the
  BFSI CTO test. Belongs on X more often than LinkedIn.
- **C. The receipt.** A story, not a claim. Recommended default for LinkedIn.

### Closing sweep

Run this on every file, every time. Use the shell, do not eyeball it.

```mermaid
flowchart LR
    G1["grep em dashes<br/>must be 0"] --> G2["grep banned phrases<br/>game-changer, leverage, ..."]
    G2 --> W["Word count<br/>Medium 2,500 to 3,200<br/>LinkedIn 220 to 260"]
    W --> C{"Over 280?"}
    C -->|yes| CUT["Cut steelman first,<br/>checklist second.<br/>Never cut the receipt"]
    C -->|no| T
    CUT --> T["Three tests"]
    T --> T1["Chai: colleague or brand?"]
    T --> T2["BFSI CTO: nod or wince?"]
    T --> T3["Next sprint: usable or clickbait?"]
    T1 --> PUB{"Human publish"}
    T2 --> PUB
    T3 --> PUB

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef gate fill:#bf8700,stroke:#7a5600,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    class G1,G2,W,CUT ai
    class C,T,T1,T2,T3 gate
    class PUB out
```

## Worked example

The bundled example starts from a dictated title ("7 step formula") plus five
rough third-person bullets about moving from manual QA into automation.

```mermaid
flowchart LR
    IN["5 rough bullets<br/>third person, compound"] --> SPLIT["Split at natural seams<br/>exercises vs projects<br/>GitHub vs LinkedIn"]
    SPLIT --> OUT["7 imperative steps<br/>nothing invented"]

    IN --> THESIS["Buried aside becomes the spine:<br/>coding fear dies at repetition volume"]
    IN --> RECEIPT["No story in the seed.<br/>Build one, flag anonymization"]
    RECEIPT --> PUNCH["Nobody rejected his skill.<br/>They rejected the silence."]

    classDef src fill:#57606a,stroke:#24292f,color:#fff
    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    class IN src
    class SPLIT,THESIS,RECEIPT ai
    class OUT out
    class PUNCH pack
```

What the skill did:

- Expanded 5 bullets to 7 by splitting compound items (exercises vs projects,
  GitHub vs LinkedIn). Nothing invented.
- Converted third person to second person. Kept every number: 90 days, 300 to
  400 exercises, 10 a day, 1 hour, 5 projects.
- Pulled the real thesis out of a closing aside: coding fear is cured by
  repetition volume, not by understanding.
- Built a receipt the seed did not contain (four interviews dying at "send us
  your GitHub") and flagged anonymization in the verify block.
- Recommended hook C, assigned hook B to X, and reported a 292-to-270 word cut.

That gap between the input and the output is the gap the skill exists to close.

## Thirteen content threads

Every piece connects to at least one. Name the thread to yourself before writing.

```mermaid
flowchart TB
    ROOT["Name one thread before writing"]

    ROOT --> CAREER["Career"]
    ROOT --> AI["AI verification"]
    ROOT --> TOOLS["Tools and infra"]
    ROOT --> PATH["Path and workflow"]

    CAREER --> C1["1. The Math Doesn't Work"]
    CAREER --> C2["10. Career Stakes"]
    CAREER --> C3["12. Learning Path, 90 Days"]

    AI --> A1["2. AI Tests AI"]
    AI --> A2["3. Pattern Recognition"]
    AI --> A3["4. Quality Gates"]
    AI --> A4["5. Speed"]

    TOOLS --> I1["6. Infrastructure"]
    TOOLS --> I2["7. Stability"]
    TOOLS --> I3["8. Deep Debugging"]

    PATH --> P1["9. Migration, Selenium to Playwright"]
    PATH --> P2["11. Foundation repo"]
    PATH --> P3["13. Workflow, ICSR in practice"]

    classDef ai fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef pack fill:#8250df,stroke:#4a1f8f,color:#fff
    classDef out fill:#2da44e,stroke:#0f5323,color:#fff
    classDef src fill:#57606a,stroke:#24292f,color:#fff
    class ROOT src
    class CAREER,AI,TOOLS,PATH ai
    class C1,C2,C3,A1,A2,A3,A4 pack
    class I1,I2,I3,P1,P2,P3 out
```

## Q&A

- **Q: When do I reach for it?** A: Any time you have a seed (even a bare
  headline) and want a Medium + LinkedIn + image pack in this voice, not a
  generic rewrite.
- **Q: What does it replace?** A: Re-prompting from scratch for voice, length,
  image specs, and first-comment splits. Those rules already live in the skill.
- **Q: What's the gotcha?** A: A pack with no receipt is the biggest quality
  drop. If the seed has no real story, supply one or accept a composite flagged
  for anonymization. Also grep for em dashes before publishing; they sneak in.

## Trigger phrases

The skill is meant to fire on "write a LinkedIn post", "make a Medium article",
"repurpose this", "in my voice", "full pack", "give me hooks", and also when you
simply drop source material or a title with steps and expect content back.
It triggers even when only one deliverable is requested.
