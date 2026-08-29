# SOP 05 - Build Plan

**Tool:** `tools/plan_build.py` · **Layer:** 3 · **Purity:** PROBABILISTIC, schema-gated

## Goal
`ticket.json` -> `plan.json` conforming to `schemas/plan.schema.json`. This is **the only component in the system permitted to call a model** (AI-2).

## Provider

Provider-agnostic across OpenAI-compatible endpoints. Selected by the `llm_provider`
setting; both are called with `requests` and no SDK dependency.

| Provider | Base URL | Default model | Default TPM budget |
|---|---|---|---|
| `deepseek` | `https://api.deepseek.com/v1` | `deepseek-chat` | 60000 |
| `groq` | `https://api.groq.com/openai/v1` | `openai/gpt-oss-120b` | 8000 |

Temperature `0.2`, `response_format: {"type":"json_object"}` on both.

The TPM budget is per provider because it drives the slimming loop below. Groq's free
tier is tight (8000, and the `max_tokens` reservation counts against it), so a rich
ticket gets slimmed. DeepSeek's ceiling is far higher, so slimming rarely engages and
the model sees the full ticket. Same pipeline, same schema gate, different headroom.

## Prompt contract
**System:** the role, the 6 standing instructions from `LLM.md` section 6, and the literal JSON schema.
**User:** the whole `ticket.json`, pretty-printed.

The prompt **does not contain the markdown template**. The model never sees the output format, so it cannot drift from it. Format is `render.py`'s job, and `render.py` cannot hallucinate. This inversion is what makes the placeholder sweep and section-order guarantee mechanical.

## Standing instructions (each traceable to a rule)
1. Use only facts present in the supplied ticket object (BR-1)
2. Every scope entry needs `justified_by` naming the ticket fact. Cannot fill it -> drop the entry into `dropped_scope` (BR-3, BR-13)
3. Anything filled without ticket evidence goes in `assumptions[]` with a reason (BR-2)
4. Never invent URLs, dates, versions, names or tools (BR-1)
5. Formal QA tone, no emoji, no em dashes (BR-12)
6. Return JSON only

## Retry policy
On schema violation: feed the validator's error message back to the model and retry. **Maximum 2 retries, then the run fails.** Never hand-patch the model's output (BR-18).

## Edge cases
| Case | Behavior |
|---|---|
| No API key | `LLMError` naming the Settings page |
| 401 from Groq | "Groq API key rejected, check Settings" |
| 429 | honour `Retry-After`, 2 attempts |
| Model returns prose around the JSON | strip to the outermost `{...}` before parsing, then validate |
| Still invalid after 2 retries | fail the run, write no plan file (BR-17) |
| Ticket over the context budget | progressive slimming, see below |
| 413 from Groq (TPM limit) | slim harder and retry once, then report the tier limit and the exact token counts |

## Token budget and progressive slimming

Groq enforces a tokens-per-minute cap per organisation and tier (8,000 TPM on the
free tier for `openai/gpt-oss-120b`). A rich ticket plus the pretty-printed schema
exceeded it during the first live run: 13,910 requested against an 8,000 limit.

The payload is therefore slimmed before the call, cheapest loss first:

| Level | What is dropped | Why it is safe |
|---|---|---|
| always | `description_html` | It exists ONLY for the flattener loss cross-check in `normalize`. The model never needed it, and it roughly doubles the description's size. |
| always | `unknown_adf_nodes`, `source`, `fetched_at`, `url` | Bookkeeping. Not requirements. |
| always | schema is minified, not pretty-printed | Same information, far fewer tokens |
| 1 | attachments reduced to filenames | Sizes and mime types do not inform a plan |
| 2 | comments capped at 5, each truncated to 400 chars | Comments are supporting context, not the requirement |
| 3 | comments dropped entirely | |
| 4 | `description_md` truncated to 6000 chars | Last resort, because this IS the requirement |

Any level at or above 2 records a gap on the ticket so the truncation appears in the
deliverable rather than being silent (BR-2).

Estimation uses 4 characters per token, which is approximate. The loop slims until the
estimate fits the budget, and slims one level further on a real 413.

**`max_tokens` counts against the TPM limit.** This is the non-obvious part, and it cost
two failed runs to find. Groq bills the *reservation*, not the actual completion length, so
`prompt_tokens + max_tokens` must fit inside the tier's TPM. With a 2,669-token prompt and
`max_tokens: 8000`, Groq reported "Requested 10669" against an 8000 limit: the prompt was
never the problem, the reservation was. So `max_tokens` is computed per call as
`tpm_limit - estimated_prompt_tokens - safety_margin`, floored at 1500 (below which a full
plan cannot be returned) and capped at 8000. The TPM limit is a setting, defaulting to 8000
for the Groq free tier.

## Output
`plan.json` in `.tmp/`, plus the token counts, the slim level used, and the attempt
number for the trace.
