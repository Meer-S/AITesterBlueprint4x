# Writing rules

Contents: [Bullet formula](#bullet-formula) · [Section order](#section-order-and-cuts) ·
[Summary](#the-summary) · [Skills](#skills-rows) · [ATS](#ats-constraints) ·
[Style](#style-rules) · [Defects](#standing-defects-to-fix-on-sight) ·
[Review Mode](#review-mode-no-jd)

## Bullet formula

Every experience bullet should carry: **JD verb + what was owned + scale + outcome.**

Weak (input only, no outcome):
> Responsible for End to End Automation Framework (with over 9000+ Test cases).

Strong:
> Own the end-to-end automation framework covering **9,000+ automated test cases** —
> cut full regression from `[X]` to `[Y]`, unlocking `[weekly]` releases.

Open with the JD's own verb where one fits — *Lead the testing strategy*, *Develop
automated frameworks*, *Coordinate with cross-functional teams*. This is the highest-value
single edit available, because it maps the candidate onto the JD line-by-line without
changing a single fact.

Volume is an input; outcome is what gets read. "9,000 test cases" says the job was big.
"Regression from three days to six hours" says the person was good. Keep both — lead
with the outcome when you have it, and emit a `[placeholder]` when you don't.

**Seniority ordering.** The most recent role should have the strongest bullets. If an
older role reads better, that is backwards and worth telling the user — it usually means
the recent role was written as a job description rather than an achievement list.

**Leadership evidence.** A "Lead" title with no team size, no mentoring, no hiring and no
strategy ownership reads as a title, not a role. Always surface headcount if it exists;
`[placeholder]` it if it doesn't.

## Section order and cuts

Default order, top to bottom:

1. Name + target title + contact
2. Summary (3–4 lines)
3. Core skills (categorized rows)
4. Professional experience (reverse chronological)
5. Domain/differentiator section — only when the candidate has something genuinely
   unusual (a side business, an education brand, open-source ownership, publications)
6. Education
7. Certifications & awards

**Cut on sight:** Interests, hobbies, "Supported Causes", generic "Organizations",
template labels like "Achievements/Tasks", declarations, marital status, and photos for
US/UK/Canada applications (fine for India, Germany, Japan).

**Add if missing:** Education and Certifications. A missing education section reads as
concealment, particularly for India-based hiring.

**Promote buried differentiators.** A side project with real reach filed under
"Volunteer Experience" is a misallocation — it is often the only thing separating this
candidate from fifty others with the same job titles. Give it its own section and its
own numbers.

## The summary

Three to four lines. Must contain: target title (matching the JD's), years of
experience, the two strongest quantified proof points, and the single differentiator.

Cut: "results-driven", "passionate", "team player", "proven track record" used with
nothing after it, and any industry list that doesn't match the actual employment history.
If the resume claims "banking and network security" but the roles are SaaS and dev tools,
fix the list rather than preserving it.

## Skills rows

Group into 5–7 labelled categories rather than one flat chip cloud — a recruiter scanning
for one platform finds it faster, and categories make the range visible.

The skills list must agree with the bullets. If "Java" leads the row but every described
project is Node.js and Ruby, one of the two is wrong; ask which.

When the JD names gate skills the candidate lacks, create the category row and fill it
with `[placeholders]` plus a `note` block stating the fill-in rule. This shows the
candidate exactly what would unlock the role without asserting anything false.

## ATS constraints

- **Single column.** Two-column layouts get interleaved or dropped by parsers. If the
  user loves their two-column design, tell them to keep it as the human-facing PDF and
  apply with the single-column version.
- No text in headers, footers, images, or text boxes.
- Standard section headings — "Professional Experience", not "Where I've Been".
- Dates as `Mon YYYY – Mon YYYY`, consistently.
- Spell out the acronym and the expansion once: "Professional Scrum Master I (PSM I)".
- Keep the target job title from the JD in the header line; many filters match on it.

## Style rules

- Past roles in past tense; current role in present tense. Mixed tense is the most
  common defect in a real resume.
- Consistent terminal punctuation across all bullets.
- No mid-sentence capitalization of common nouns ("Test cases", "Enterprise Level").
- One canonical spelling per technology — pick `Node.js` and never write `Node JS` or
  `NodeJS` again. Same for `Selenium WebDriver`, `PhantomCSS`, `Java`.
- Space before parentheses.
- No bullet that ends in a colon and leads nowhere.
- British/American spelling: match whatever the JD uses.

## Standing defects to fix on sight

These recur across almost every real resume and are worth checking every time:

1. Grammar errors in the summary — the highest-visibility text on the page.
2. Location in the header contradicting the current role's location.
3. An award dated before the start date of the job that granted it.
4. A claimed year-count the listed roles don't add up to (unexplained early gap).
5. Typos in proper nouns — technology names and company names especially.
6. Duplicate or near-duplicate bullets inside one role.
7. Links present (LinkedIn, GitHub, portfolio) with no reason given to click them.

## Review Mode (no JD)

When the user wants a review or rebuild with no job description, produce a scorecard
first, then the rebuilt resume. Score out of 10 on: **Overall, Effectivity, Layout &
Design, Content Relevance, Grammar & Syntax, Impact** — using ✅ for what works and 🙈
for what doesn't, with a concrete rewrite example for at least one weak bullet.

Be specific and quote the actual defect. "Improve your bullets" is worthless; "this
bullet is an input metric with no outcome, here is the rewrite" is not.

Then state honestly which scores you can raise yourself (layout, grammar, structure) and
which depend on facts only the candidate has (effectivity, impact) — those cannot clear
a high score until real numbers replace the placeholders, and saying so prevents the
candidate from thinking the document is finished when it isn't.
