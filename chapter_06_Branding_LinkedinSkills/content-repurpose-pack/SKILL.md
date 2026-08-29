---
name: content-repurpose-pack
description: Produce a ready-to-publish content pack in Pramod Dutta's Testing Academy voice (Medium article, LinkedIn post, Style C tweet-screenshot image prompts with graded controversial hooks, Style A cyber infographic prompt). Use this skill whenever the user supplies ANY content seed and wants content out of it, including a bare title or headline, a list of bullet points or numbered steps, a screenshot or image reference, an X/Twitter thread, an article, a URL, a rough voice-note-style brain dump, or just a topic. Trigger on phrases like "write a LinkedIn post", "make a Medium article", "repurpose this", "in my voice", "use my playbook", "full pack", "image prompt", "give me hooks", "make this controversial", and also trigger when the user simply drops source material or a title with steps and expects content back. Trigger even when only ONE deliverable is requested, and even when the user never mentions a playbook, skill, or brand voice.
---

# Content Repurpose Pack

Converts any content seed into a publish-ready pack in one pass. Everything below
was extracted from real sessions with this user, including the corrections made
along the way. Follow it in order.

## Step 0: Load the voice, always

Read `references/brand-voice.md` in full before writing a single line. It is the
authoritative spec for identity, the Hook/Story/Offer spine, hook patterns, story
mechanics, the offer ladder, banned phrases, signature lines, and content threads.

Never write from memory of it. Never let an earlier draft in the conversation
substitute for it. If the user supplies an updated voice document or a new
reference image mid-thread, the new one supersedes everything including your own
earlier outputs: redo, do not patch.

Then read `references/deliverable-specs.md` for the exact file formats, and
`references/worked-example.md` to see a full input-to-output pass.

**Hard rule that survives everything: no em dashes anywhere.** Use a comma, a
period, parentheses, or two sentences. Grep for them before delivering.

## Step 1: Identify the input shape

Seeds arrive in six shapes. Handle each differently.

**Bare title or headline.** Treat the title as the promise and build the framework
yourself from the content threads. Confirm nothing, just build. If the title
contains a number ("7 steps", "5 lies"), that number is a contract. See Step 2.

**Bullet points or numbered steps.** This is the most common shape. The bullets
are the framework skeleton, not the finished framework. They will usually be
rough, out of order, and written in third person or as spoken notes. Your job is
to normalize them into imperative steps, order them by dependency, and expand each
into a real section. Never just reformat the bullets and hand them back.

**Screenshot or image.** Transcribe it first, completely, before writing anything.
Screenshots carry two different payloads and you must work out which one you have:
- A *content* screenshot (a post, a thread, a code block) is source material.
- A *style reference* screenshot (a card design the user wants matched) is a spec
  update. It outranks the written spec. Diff it against
  `references/deliverable-specs.md` and state the deltas you found before using it.

**URL.** Fetch it. If unreadable, say so and ask for the content. Never invent
what a link says.

**Thread or article.** Mine it with the extraction protocol in Step 3.

**Spoken brain dump.** This user often dictates, so expect run-on sentences,
repeated ideas, third-person phrasing ("he should be clear about the roadmap"),
and self-corrections mid-thought. Convert to second person, deduplicate, and keep
every concrete number. The numbers are the signal in a dump; the phrasing is not.

## Step 2: Reconcile the promised number

When the title promises N items and the user supplies a different count, the title
wins. This happens constantly.

Real example: the user supplied 5 bullets under the title "7 step formula". The
correct move is to expand to 7 by splitting bullets that contain two distinct
actions, not to change the title to 5 and not to invent two unrelated steps.

Rules:
- Too few: split compound bullets at their natural seam. A bullet saying "do 300
  exercises and build 5 projects" is two steps.
- Too many: merge adjacent steps that share a single decision.
- Never pad with filler steps like "stay consistent" or "keep learning". A step
  must contain an action with a number, a name, or a deadline attached.
- State the mapping in one line of the delivery message so a wrong split is cheap
  to correct.

## Step 3: Mine the seed

Pull exactly five things, in this order:

1. **The one transferable thesis.** The single test, rule, or reframe the piece
   hangs on. If you cannot state it in one line, keep reading.
2. **The framework.** The numbered moves. If the user names a subset, the subset
   IS the framework; drop the rest silently.
3. **Verbatim assets.** Prompts, commands, code, file contents. Preserve them
   character-faithful. Never paraphrase them into mush.
4. **Numbers.** Sort into three buckets:
   - *The user's own prescriptions* (300 exercises, 1 hour a day, 90 days). Use
     freely and state as his method. These are opinions he owns, not claims.
   - *Independently verifiable* facts. Keep with attribution.
   - *Source-only claims* (benchmark multiples, market stats, salary bands). Soften,
     attribute, or omit, and list every one in the verify block.
   Never state a source-only number as fact. Never fabricate.
5. **The discard pile.** The original author's CTAs, community links, promo plugs,
   engagement bait. Replace with this user's links. Carrying a source author's
   promo link into a re-voiced post is a known failure; check for it explicitly.

## Step 4: Map to the voice

- Match the topic to one of the 13 content threads and name it to yourself.
- Scan the signature lines for one or two that ARE the thesis. A matched signature
  line beats a newly invented one, because repetition across posts is how a line
  becomes his.
- Re-angle at least one example into the QA/SDET world (a `getByRole` locator, a
  flaky suite, coverage debt, a framework migration) so it lands with the actual
  audience rather than a generic AI crowd.
- Find the receipt. Every piece needs one real thing that happened with one detail
  that could not be invented. If the seed contains no receipt, say so and ask for
  one, or build the piece around a named-year timeline instead. A piece with no
  receipt is the single biggest quality drop available.
- India context only where natural. Never forced.

## Step 5: Produce the deliverables as separate files

Default full pack, four files:

1. `pack-1-medium-article.md`
2. `pack-2-linkedin-post.md`
3. `pack-3-linkedin-image-prompts.md`
4. `pack-4-medium-image-prompt.md`

If the user asks for a single deliverable, still ship it as its own file. Never
merge deliverables into one file. Full templates are in
`references/deliverable-specs.md`; do not write these from memory.

Every text deliverable ends with a `VERIFY BEFORE PUBLISHING` block. For Medium,
wrap it in an HTML comment so it cannot ship by accident.

## Step 6: The controversial hook protocol

When the user asks for controversial, provocative, or bold hooks, they want reach.
They also have 42K followers and a BFSI-heavy audience, so an overclaim costs more
than it earns. Do not refuse and do not sanitize. Produce a graded ladder instead.

Always produce three variants, labelled, in this order of increasing risk:

- **A. The prediction.** Makes the aggressive claim but marks it as a forecast and
  admits the author's timing record is imperfect. "2027 is the last comfortable
  year for a manual-only tester. I have been wrong about timing before. I am not
  wrong about the direction." Keeps the controversy, loses the overclaim.
- **B. The threat.** Closest to what the user usually asks for, highest reach,
  fails the BFSI CTO test. A deadline neither of you can support pulls comments
  from people arguing with the deadline instead of doing step 1.
- **C. The receipt.** A story, not a claim. Nobody can argue with what happened to
  a real person, so replies fill with "this happened to me" instead of
  "you are fearmongering."

Then do three things, briefly, in the delivery message:
1. Say which one you would post and why, in two sentences.
2. Name the specific failure mode of the riskiest variant rather than calling it
   "risky". Vague caution reads as hedging and gets ignored.
3. Suggest the platform split. B often belongs on X where the format rewards it,
   A or C on LinkedIn.

Never fabricate a statistic to make a hook land. A prediction stated as a
prediction is fair game. A prediction stated as data is not, and reputation is
the asset being spent.

## Step 7: The closing sweep

Run all of this on every file, every time. Use the shell, do not eyeball it.
(The em dash inside the first grep pattern below is the search character itself
and is the one place in this skill where it is allowed. Do not "fix" it.)

```bash
cd <output-dir>
grep -c '—' pack-*.md                      # must be 0 everywhere
grep -in 'game-changer\|leverage\|dive deep\|unleash\|revolutioniz\|cutting-edge\|synergy\|supercharge\|unlock the power\|fast-paced\|no secret\|seamless\|at the end of the day\|needless to say' pack-*.md
wc -w pack-1-medium-article.md             # target 2,500 to 3,200
```

Then count the LinkedIn body excluding hashtags. It must be 220 to 260, with 280
as a hard ceiling. Drafting reliably overshoots, so expect to cut.

**Cut order when over budget:** the steelman paragraph first, the checklist
second, connective tissue third. Never cut the receipt. Never cut the two-beat
punch line.

Then the three voice tests:
1. *Chai test.* Senior colleague talking over chai, or a brand?
2. *BFSI CTO test.* Would a serious banking CTO nod, or wince?
3. *Next-sprint test.* Usable in their next sprint, or clickbait?

All three must pass. If the piece fails only the BFSI test and the user explicitly
asked for controversy, ship it and name the failure rather than quietly softening
the work.

## Delivery message rules

The files carry the content. The message carries the judgment. Keep it short and
put only things in it that are not already in the files:

- Any spec change you detected from a supplied reference image.
- The bullet-to-step mapping if you expanded or merged.
- Which hook you would actually post, and the failure mode of the one you would not.
- Anything you cut to hit word count, so the user can overrule it.
- One genuine risk, if there is one. The anonymization of a mentee story is the
  most common.

Do not summarize the files back. Do not list the deliverables. The user can read.

## Iteration rules (how this user gives feedback)

- Terse feedback is scope surgery, not confusion. "write only X, Y, Z" means those
  become the entire framework. "add only 3" means cut to 3. Execute the cut, then
  state the interpretation in one line so it is cheap to correct.
- Never overwrite a delivered file. New feedback produces a new version or a fresh
  pack.
- A newly supplied reference document or example image outranks all prior drafts
  and all prior formatting decisions.

## Failure modes observed in real sessions (do not repeat)

- Emojis or markdown bold in a LinkedIn body. Both are invisible on the platform
  and are voice violations.
- Numbered lists where the recipe demands arrows.
- Reformatting the user's rough bullets instead of expanding them into steps.
- Writing a great Hook and Story and then just stopping. The Offer beat is the one
  that goes missing. If the post ends on a beautiful line with no next action,
  the piece is unfinished.
- Blowing the LinkedIn word budget by cramming prompts into the body instead of
  the pre-split first-comment blocks.
- Carrying the source author's promo link into the re-voiced version.
- Reciting the source's unverifiable stats as fact.
- Describing the tweet images instead of writing their exact text.
- Ignoring a supplied style-reference screenshot because a written spec already
  existed. The image wins.
