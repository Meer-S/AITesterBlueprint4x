# DELIVERABLE SPECS

Exact formats for the four pack files. Read the relevant section before writing
that file. Do not write any of these from memory.

CONTENTS
1. pack-1-medium-article.md
2. pack-2-linkedin-post.md
3. pack-3-linkedin-image-prompts.md (Style C v2)
4. pack-4-medium-image-prompt.md (Style A, cyber treatment)
5. Style B, warm editorial cartoon
6. The verify block

- - -

## 1. pack-1-medium-article.md

Length 1,500 to 3,500 words, sweet spot 2,500 to 3,200. Clean Markdown for direct
paste into Medium.

Order:
1. `#` Title, 8 to 15 words, specific, containing a number or a transformation.
   Patterns: "Should You X in 2026?", "The 5 Lies of Y", "How X Move Into Y: The
   N Step Formula That Works", "I Did X. Here Is What I Found."
2. Bold subtitle paragraph. 4 to 6 sentences, 3 to 5 real numbers, the explicit
   promise. Must work standalone, because this is what shows in search results and
   email digests. Set it as the Subtitle manually after pasting.
3. `- - -` divider.
4. Open on a person or a moment. A mentee's message, an interview, a diff reviewed
   at 11pm. Never a definition, never "AI is transforming X."
5. One paragraph stating the contrarian position plainly and owning it. If the
   piece has a prediction, mark it as a prediction here and again in the caveats.
6. One `##` section per framework step, written in paragraphs, not bullets.
   Numbered step headers are allowed here because this is a technical tutorial.
   Each section: what the step is, why people fail it, what "done" looks like.
7. Exactly one TypeScript snippet using an accessibility-first locator
   (`getByRole`), placed where an abstract claim needs proof. The before/after
   contrast pattern works best: the brittle version, then the durable version,
   with a comment on each explaining the mindset difference.
8. One light ICSR touch maximum. Never explain the framework.
9. `## The Honest Caveats`, mandatory. 3 to 5 paragraphs. At least one must cut
   against the author's own commercial interest ("I sell a course on this, so
   discount my urgency"). This is the highest-trust paragraph in the article and
   it is what stops an aggressive framing from reading as a funnel. Where the
   piece contains a prediction, one caveat must restate it as a prediction.
   The strongest closing caveat argues against the article's own premise.
10. `## The Bottom Line`. The close, ending on a signature line.
11. `- - -` divider.
12. Italic CTA: *[value-first line about the topic], the foundation of my
    [AI-Powered Testing Mastery](https://thetestingacademy.com) course.*
13. `Tags:` line, 5 tags.
14. HTML-commented verify block.

- - -

## 2. pack-2-linkedin-post.md

The file contains four parts: hook options, the post, the first comments, and the
hook recommendation.

**Hook options.** Three fenced variants per the controversial hook protocol in
SKILL.md, labelled A / B / C, each 2 lines.

**The post.** Fenced, plain text. No markdown, no emojis, no body link. Assembly:

```
[HOOK line 1: claim, condition, or receipt]
[HOOK line 2: the narrowing, the admission, or the promise of a list]

[Optional circle checklist, 4 to 6 items, one line each. Only for the
 uncomfortable-conditional hook where the reader checks themselves.]

[The receipt. The real thing that happened, with the undeniable detail.]

[TWO-BEAT PUNCH. Standing alone. Under 8 words.]

[Steelman the counter-argument, then pivot on "But" into the stakes,
 named in domain nouns.]

[One line naming the framework and its cost. "90 days fixes this."]

→ [step 1: name, mechanism, one concrete detail]
→ [step 2 ... one arrow per step, each self-contained]

[Definitional reversal. X is not Y. X is Z.]

[OFFER: one tier only. Rule, question, or asset.]

#QA #SDET #TestAutomation #SoftwareTesting #TopicTag
```

Then state the counted word total explicitly, excluding hashtags.

**First comments.** Everything that did not fit. Pre-split into numbered blocks
of under 1,250 characters each, labelled "COMMENT 1 of N". This is where full
syllabi, project lists, prompts, and code go. Links live here, never in the body,
because LinkedIn throttles body links. Only an explicit product launch may put a
link in the body.

**Hook recommendation.** Short. Which one to post, the named failure mode of the
riskiest one, and the platform split.

- - -

## 3. pack-3-linkedin-image-prompts.md (Style C v2)

The tweet-screenshot card. Highest performing format. Three variants.

**Style C v2 spec**, updated from the user's own reference card. This supersedes
the older pure-black spec:
- Background deep navy-black, #0B1220 to #101826. Flat, no gradient, no texture.
- Profile row: circular headshot, "Pramod Dutta" bold white, "@thetestingacademy"
  in muted grey #7A8899. **No verified tick.**
- Body white #FFFFFF, large, left aligned, blank line between every beat.
- **Blue accent #2D9CFF on 2 or 3 key words only**, inside otherwise white
  sentences. This is the signature of the format and carries the whole design.
  Accent rule: colour the word that flips the meaning, never a whole line. The
  test is whether a reader would underline exactly those words.
- Bottom: thin grey outline icon row (comment, repost, heart, bar chart), a
  divider, then reaction circles with "Name and N others" left and
  "NN comments • NN reposts" right.
- No logo, no watermark, no branding, no decoration. The minimalism is the design.
- Aspect ratio 4:5.

**Variant roles:**
- Variant 1, Hook. The LinkedIn cover image, posted at publish.
- Variant 2, Mechanism. First comment 60 to 90 minutes later, plus Instagram.
- Variant 3, Closer. Reuses the matched signature line. Instagram, and a LinkedIn
  repost 5 to 7 days later.

Write the actual card TEXT for all three, not descriptions of it. Lines of 2 to 6
words, whitespace between beats, last line a gut-punch. State the accent words and
the metrics for each.

**Metrics:** realistic, non-round, and different across variants. Never 9,999-style
numbers. Use plausible Indian names in the reaction line.

Give one full generator prompt for Variant 1, then "same spec, swap the body lines,
accent words and metrics" for 2 and 3.

**Generation route, ranked:** post from the real @thetestingacademy account and
screenshot it, beats tweetgen.com plus a Figma accent overlay, beats a saved Figma
component, beats Ideogram. Never Midjourney; it mangles text. Note that the real
screenshot route cannot produce the blue accents, so use it only when the line
carries itself in plain white.

End with a usage map table: variant, where, when.

- - -

## 4. pack-4-medium-image-prompt.md (Style A, cyber treatment)

Dark technical infographic, 16:9, for Medium covers and any framework or
decision-matrix content.

Cyber treatment means faint circuit traces, a terminal grid and monospace
numerals. It does not mean neon cyberpunk. Keep it readable and serious; a BFSI
CTO should be able to look at it without wincing. No glow, no haze, no lens flare.

**Palette:** background #0a0a1a with a faint grid; gold #f59e0b banners; red
#ef4444 for what expires; green #22c55e for what persists; blue #3b82f6 for the
thesis line; white body; watermark #4a4a5f.
**Type:** Inter bold for headers, JetBrains Mono for code, numbers and detail lines.

**Layout that works:** top gold banner with the title, blue mono thesis line under
it, a card grid with one card per framework step (white line icon, gold numbered
title, one white mono detail line), red and green vertical edge labels carrying
the expires-versus-persists contrast, bottom gold banner carrying the signature
line. Muted @thetestingacademy watermark bottom-right. Readable at 30 percent zoom.

Always append a **Figma/Canva fallback spec**, because AI generators garble text
and the built version becomes a reusable template. The fallback must give concrete
Lucide or Feather icon names, canvas 1920x1080 with all text inside the middle 80
percent, exact hex values, exact px type sizes, stroke weight, and coordinates.
Close it with a reuse note on saving it as a component with the card count as a
variant.

The bottom banner line must match the article's closing signature line exactly, or
the cover and the piece read as though they came from different posts.

- - -

## 5. Style B, warm editorial cartoon

For personal-story or emotional posts only. Golden #fef3c7 background, thick BROWN
outlines, not black, not anime or chibi. Character: South Asian male, short black
hair, trimmed beard, colourful woven bracelets on the right wrist, red graphic
t-shirt. Often a two-panel problem-versus-solution split.

- - -

## 6. The verify block

Every text deliverable ends with one. Plain heading on LinkedIn files, wrapped in
an HTML comment on Medium files so it cannot ship by accident.

It lists, specifically and not generically:
- Every source-only statistic that was softened, attributed, or omitted, with the
  instruction to attach a source or soften further.
- Every prediction, with the instruction to keep the prediction framing and not
  let an editor tighten it into a statement of fact.
- Anonymization checks on any mentee, student, or interview story. Name the exact
  identifying details used (years of experience, domain, company type) and ask
  whether they identify the person to their old team. This is the most common real
  risk in the whole pack.
- Any API name, version number, feature name, or date to check against current docs.
- Any URL to confirm resolves.
- Timing instructions, for example posting the first comment within 60 seconds of
  publishing so the link is live while early reach builds.
