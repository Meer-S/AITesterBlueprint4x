# SKILL: JD-Tailored Resume Builder

## Purpose

Use this skill whenever the user provides:
1. An existing/older resume, and
2. A target Job Description (JD), supplied as plain text, PDF, DOCX, Excel, CSV, image, or another readable file.

The goal is to produce a set of JD-tailored resumes that are:
- truthful and evidence-based,
- ATS-friendly,
- recruiter-readable,
- professionally written,
- aligned to the target role,
- easy for the user to transfer into Google Docs,
- and clearly differentiated by positioning rather than by inventing experience.

The user may repeat the process for every job application.

---

## Core Principle

Tailor the resume to the JD, but never manufacture qualifications.

Use only:
- facts explicitly present in the user's source resume,
- facts supported by supplied career information already available in the current task,
- and terminology that accurately describes that evidence.

Never add a technology, certification, domain, responsibility, achievement, metric, tool, methodology, job title, years of experience, employer, client, or project merely because it appears in the JD.

When a JD requirement is not supported:
- do NOT claim it,
- do NOT rewrite a related skill as if it were the exact requirement,
- identify it as a gap,
- and, where useful, position adjacent genuine experience.

Example:
If the JD requires 15+ years and the resume supports 13+ years, keep 13+ years. Do not change it to 15+.

---

# INPUT HANDLING

## Resume input

Accept:
- PDF
- DOCX
- TXT
- CSV
- Google-Doc-exported files
- pasted resume text

Extract:
- name/contact
- headline
- executive/profile summary
- professional experience
- employers/clients
- dates
- responsibilities
- achievements
- metrics
- domain experience
- technical skills
- tools/platforms
- leadership experience
- education
- certifications
- projects
- awards, if present

Preserve factual chronology and factual employment details.

## JD input

Accept:
- pasted text
- PDF
- DOCX
- XLSX/XLS
- CSV
- TXT
- image/scanned document where readable

Extract and classify:
- job title
- seniority
- minimum years
- domain
- mandatory requirements
- preferred requirements
- technical skills
- tools
- methodologies
- leadership expectations
- delivery responsibilities
- stakeholder responsibilities
- governance responsibilities
- business responsibilities
- measurable outcomes/KPIs
- keywords
- behavioral requirements
- location/shift/travel requirements if relevant

For Excel JDs, inspect all relevant sheets, columns, headers, hidden/secondary requirement sections when accessible.

---

# STEP 1 — ANALYZE THE JD

Create an internal JD matrix.

Use these categories:

| Category | Extract |
|---|---|
| Role | Exact target title |
| Seniority | Manager / Senior Manager / AVP / Director etc. |
| Experience | Required years |
| Domain | BFSI, healthcare, SaaS, telecom, etc. |
| Core responsibilities | Top responsibilities |
| Mandatory skills | Must-have capabilities |
| Technical keywords | Tools/platforms/frameworks |
| Leadership keywords | Team, scale, governance, delivery |
| Business keywords | ROI, RFP, strategy, transformation |
| Preferred skills | Nice-to-have |
| Outcome keywords | KPIs, cost, quality, timelines, coverage |
| ATS terms | Exact recurring phrases |

Count/weight keywords by relevance and frequency.

Prioritize:
1. mandatory requirements,
2. repeated keywords,
3. role-specific responsibilities,
4. domain requirements,
5. measurable outcomes,
6. preferred skills.

Do not keyword-stuff.

---

# STEP 2 — CROSS-REFERENCE THE RESUME

Create an evidence map:

| JD Requirement | Resume Evidence | Match | Action |
|---|---|---:|---|
| Requirement | Existing evidence | Strong / Partial / Gap | Emphasize / Rephrase / Leave out / Flag |

Use these match levels:

### Strong Match
Direct evidence exists.

Action:
- prominently position it,
- use JD terminology where truthful,
- attach measurable impact when already supported.

### Partial Match
Related experience exists but not exact.

Action:
- describe the genuine related capability,
- avoid falsely claiming the exact JD skill.

### Gap
No evidence exists.

Action:
- do not add it to the resume as a qualification,
- mention in the gap analysis outside the resume.

---

# STEP 3 — BUILD THE TARGET POSITIONING

The resume should tell one coherent career story.

Choose the strongest positioning based on the JD.

Examples:
- AI & Quality Engineering Leader
- Program Manager – Quality Engineering
- Quality Engineering Transformation Leader
- QA Automation & Digital Engineering Leader
- AI Quality / GenAI Testing Leader
- BFSI Quality Engineering Leader
- QE Program & Delivery Leader

Do not automatically use "QA Specialist" if the user's evidence supports a broader leadership position.

The headline should reflect:
1. target role,
2. strongest differentiator,
3. major domain/technical strength.

Avoid exaggerated executive titles that are not supported.

---

# STEP 4 — CREATE MULTIPLE RESUME VERSIONS

Unless the user explicitly asks for one version, create three versions.

## VERSION 1 — ATS / JD Match

Purpose:
- maximize truthful ATS keyword alignment,
- closely mirror the language of the JD,
- prioritize mandatory competencies.

Structure:
1. Name
2. Targeted headline
3. Professional Summary
4. Core Competencies
5. Professional Experience
6. Technical Skills
7. Education
8. Certifications/projects where relevant

Rules:
- use exact JD terminology when supported,
- put high-value keywords in Summary, Core Competencies, Experience, and Skills,
- keep wording natural,
- prioritize searchable keywords over decorative writing.

Best for:
- company career portals,
- ATS screening,
- high-volume applications.

---

## VERSION 2 — Recruiter / Executive

Purpose:
- maximize readability and leadership impact,
- show business value, scale, governance, transformation, and leadership.

Emphasize:
- program ownership,
- team scale,
- distributed delivery,
- governance,
- stakeholder management,
- strategic planning,
- measurable outcomes,
- transformation,
- business value,
- domain expertise.

Reduce:
- long technology inventories,
- low-value tools,
- duplicate skills.

Best for:
- recruiter outreach,
- senior manager/AVP roles,
- executive referrals,
- LinkedIn applications.

---

## VERSION 3 — Technical / Functional

Purpose:
- maximize credibility with hiring managers and technical interviewers.

Emphasize:
- automation architecture,
- frameworks,
- APIs,
- CI/CD,
- test strategy,
- quality engineering,
- technical tools,
- AI/GenAI testing where relevant,
- architecture and implementation outcomes.

Best for:
- technical hiring managers,
- engineering organizations,
- specialist QE roles,
- AI/automation-heavy positions.

---

# STEP 5 — TAILOR THE SUMMARY

The first 5–7 lines must immediately answer:

"Why is this person relevant to this job?"

Use this structure:

[Target identity] + [years] + [domain] + [leadership scope] + [core capabilities] + [major outcomes] + [differentiator].

Avoid generic language such as:
- hardworking,
- passionate,
- dynamic professional,
- results-oriented unless immediately supported by evidence.

Every summary claim must be defensible from the source resume.

---

# STEP 6 — TAILOR PROFESSIONAL EXPERIENCE

For each relevant role:

1. Put the most JD-relevant accomplishment first.
2. Convert responsibility-heavy statements into outcome-oriented bullets where the source supports the outcome.
3. Use the JD's vocabulary naturally.
4. Bring forward leadership, governance, scale, domain, and technical capabilities relevant to the role.
5. Preserve actual dates and employer/client relationships.
6. Do not create metrics.

Preferred bullet pattern:

Action + scope + capability/technology + outcome.

Example:

"Led automation strategy for enterprise BFSI platforms using Selenium, TestNG and REST Assured, reducing regression cycle time by ~35%."

Only use a metric such as ~35% when that metric is supported by the source.

---

# STEP 7 — KEYWORD INSERTION RULES

A keyword can be inserted when at least one of these is true:

### Rule A — Exact evidence
The resume explicitly contains the skill.

Example:
JD: Selenium
Resume: Selenium
→ Use Selenium prominently.

### Rule B — Supported terminology normalization
The resume describes the capability using different wording.

Example:
Resume: "automation framework architecture"
JD: "framework creation for testing"
→ It is valid to phrase the resume as "Designed and created scalable test automation frameworks."

### Rule C — Closely related experience
Only use a related phrase if it remains factually accurate.

Example:
Resume: "risk-based testing"
JD: "QE risk management"
→ Can be expressed as "Risk-based QE strategy and quality-risk management."

### Do NOT use a keyword when:
- there is no supporting evidence,
- the user would be unable to defend it in an interview,
- it changes the meaning of the original experience.

Do not add unsupported:
- Cucumber,
- XPath,
- Oracle,
- SOAP UI,
- Web Analytics Testing,
- RFP ownership,
- AI architecture,
- specific cloud platforms,
- certifications,
etc., unless supported by the source.

---

# STEP 8 — GAP ANALYSIS

After creating the resumes, provide a concise gap analysis.

Separate gaps into:

### Critical Gaps
Requirements that materially affect eligibility.

### Partial Gaps
Related experience exists but does not exactly satisfy the JD.

### Minor Gaps
Low-impact missing keywords or tools.

Example:

"JD requires 15+ years; source resume supports 13+ years. Keep 13+ years and treat this as a screening risk."

Do not hide material gaps.

---

# STEP 9 — CHANGE HIGHLIGHTING

For the user-facing tailored resume, highlight only material changes.

Preferred convention:
- **Bold** for newly emphasized JD-aligned phrases.
- Optional yellow highlight when producing DOCX/PDF.

Highlight:
- revised headline,
- new/reworked summary phrases,
- newly emphasized competencies,
- materially rewritten experience bullets,
- JD-aligned technical terms inserted from supported evidence.

Do NOT highlight:
- every minor grammatical change,
- punctuation corrections,
- unchanged content.

The goal is for the user to quickly see why the tailored version differs from the base resume.

---

# STEP 10 — GOOGLE DOC READY FORMAT

The final resume content should be easy to paste into Google Docs.

Recommended format:

NAME
Targeted Professional Headline
Location | Email | Phone | LinkedIn

PROFESSIONAL SUMMARY

CORE COMPETENCIES

PROFESSIONAL EXPERIENCE

Company | Title | Dates
• Achievement
• Achievement
• Achievement

TECHNICAL SKILLS

EDUCATION

CERTIFICATIONS / ADDITIONAL INFORMATION

Use clean, conventional section names.

Avoid:
- complicated columns,
- excessive graphics,
- text boxes,
- decorative icons that may disappear during Google Docs transfer,
- ATS-hostile formatting.

For Google Docs, prioritize simple headings, bullets, tables only when necessary, and consistent spacing.

---

# STEP 11 — QUALITY CONTROL

Before finalizing, run these checks.

## Truthfulness
- No fabricated experience.
- No invented metrics.
- No invented technologies.
- No inflated years of experience.
- No altered employment dates.
- No unsupported clients/projects.

## JD Alignment
- Mandatory requirements are addressed where evidence exists.
- Important JD keywords appear naturally.
- Relevant experience is moved toward the top.
- Target role is obvious within the first few seconds.

## ATS
- Exact supported keywords included.
- Standard section headings.
- No unnecessary graphics.
- No keyword stuffing.
- Consistent technology names.

## Executive Quality
- Bullets focus on outcomes.
- Leadership is clear.
- Scope and scale are visible.
- Business impact is visible.
- Repetition is minimized.

## Language
- Correct grammar.
- Consistent capitalization.
- Consistent technology naming.
- No awkward keyword insertion.
- No filler phrases.

## Visual Quality
- 2 pages is preferred for most senior applications unless more length is genuinely required.
- Adequate whitespace.
- Consistent alignment.
- Clear hierarchy.
- No orphan headings or awkward page breaks.

---

# STEP 12 — SCORE EACH VERSION

Score each resume out of 10 for:

1. Overall Result
2. Effectivity
3. Layout & Design
4. Content Relevance
5. Grammar & Syntax
6. Impact

Target:
- every category > 8/10.

If a category scores below 8:
- revise before final delivery,
- or explicitly explain the constraint preventing improvement.

Do not inflate scores simply to satisfy the target.

---

# FINAL OUTPUT

For every JD-tailoring request, return:

## 1. JD Analysis
A concise summary of:
- essential skills,
- mandatory requirements,
- major keywords,
- leadership requirements,
- domain requirements,
- high-value outcomes.

## 2. Resume Match
A table:
JD requirement | Resume evidence | Match | Treatment.

## 3. Gaps / Risks
Clearly identify unsupported or partially supported requirements.

## 4. Three Tailored Resume Versions
### Version 1 — ATS / JD Match
Complete Google-Docs-ready resume.

### Version 2 — Recruiter / Executive
Complete Google-Docs-ready resume.

### Version 3 — Technical / Functional
Complete Google-Docs-ready resume.

## 5. Recommended Version
State which version should be used for the application and why.

## 6. Change Highlights
Clearly identify the most important JD-aligned changes.

## 7. Final Scores
Give six scores for each version:
- Overall Result
- Effectivity
- Layout & Design
- Content Relevance
- Grammar & Syntax
- Impact

All should be above 8/10 before delivery. If not possible without fabrication, explain why.

---

# IMPORTANT OPERATING RULES

1. The user's source resume is the factual source of truth.
2. The JD is the targeting source, not a source of user qualifications.
3. Never convert a JD requirement into a qualification without evidence.
4. Never inflate experience years.
5. Never invent metrics.
6. Never invent tools.
7. Never invent RFP/RFI experience.
8. Never invent people-management scope.
9. Preserve chronological accuracy.
10. Prefer outcomes over responsibilities.
11. Use JD terminology when it accurately describes existing experience.
12. Keep resumes coherent; do not produce keyword-stuffed text.
13. Tailor the top third of the resume most aggressively because it determines first impressions and ATS relevance.
14. Highlight material changes so the user can review them quickly.
15. Produce Google-Docs-friendly content.
16. When the JD is supplied in Excel, inspect the entire relevant workbook rather than reading only the first visible sheet.
17. If a file is missing, unreadable, or incomplete, state the limitation rather than guessing.
18. If a claim cannot be verified from the source materials, do not use it as a factual resume claim.
19. Use the user's existing strongest achievements wherever they are relevant.
20. The final resume should improve relevance, not rewrite the user's career history.

---

# REUSABLE USER COMMAND

The user can invoke this skill with:

"Tailor my resume to this job.

Inputs:
- Base resume: [file]
- Job description: [file/text]

Create:
1. JD keyword/requirement analysis
2. Resume-to-JD match matrix
3. Critical/partial gaps
4. ATS version
5. Recruiter/Executive version
6. Technical/Functional version
7. Highlight the JD-aligned changes
8. Give scores for all six resume-quality categories
9. Provide Google-Docs-ready final content

Do not invent qualifications. Use only evidence from my resume and supplied career information."

---

# DEFAULT TARGETING PRIORITY

When deciding what to emphasize, use this order:

JD Mandatory Requirement
→ Direct Resume Evidence
→ Measurable Achievement
→ Leadership/Scale
→ Domain Relevance
→ Technical Keyword
→ Preferred Requirement
→ General Skill

This ensures the resume is targeted without becoming artificial.
