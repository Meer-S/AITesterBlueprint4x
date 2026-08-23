# Resume JSON spec

Input format for `scripts/build_resume.js`. Sections render in array order; every text
field accepts the inline markup `==highlight==`, `[placeholder]`, `**bold**`.

## Top level

| Key | Type | Notes |
|---|---|---|
| `output` | string | Absolute path for the .docx. `--clean` writes `<name>_CLEAN.docx` alongside it. |
| `docTitle` | string | Document metadata title. Optional. |
| `name` | string | Rendered large at the top. Uppercase reads best. |
| `title` | string | Target role line. Put the JD's exact job title here, highlighted. |
| `contact` | array of arrays | Each inner array is one line; items joined with bullets. Use `"label\|url"` for links. |
| `margin` | number | Page margin in inches, default `0.5`. Drop to `0.45` to save a page. |
| `theme` | object | Optional colour overrides: `ink`, `slate`, `accent`, `fill`, `muted`, `rule`, `font`, `highlight`. |
| `sections` | array | See below. |

Page size is A4 by default (docx-js default), which suits India, EU and UK. For US
applications set US Letter in the script's section properties.

## Section object

Include only the keys a section needs; they render in this order within the section.

| Key | Type | Renders as |
|---|---|---|
| `heading` | string | Section header with an accent rule beneath |
| `body` | string | A paragraph — use for the summary |
| `rows` | array of `[label, value]` | Bold label followed by inline value — use for skills and education |
| `roles` | array of role objects | Job entries, see below |
| `bullets` | array of strings | Standalone bullets — use for awards and certifications |
| `note` | string | Small red italic guidance. **Omitted from `--clean` output**, so it is the right place for working-copy instructions to the candidate. |

## Role object

| Key | Type | Notes |
|---|---|---|
| `title` | string | Job title. Highlight the part changed to match the JD. |
| `org` | string | Employer. Optional — omit for a heading-only entry. |
| `meta` | string | `Dates \| Location \| Domain` — the domain slot is useful for signalling industry match. |
| `bullets` | array of strings | 3–6 per role; most recent role gets the strongest. |

## Worked example

```json
{
  "output": "/mnt/user-data/outputs/Jane_Doe_DataEngineer.docx",
  "docTitle": "Jane Doe — Data Engineer",
  "name": "JANE DOE",
  "title": "==DATA ENGINEER==  ·  PIPELINES & WAREHOUSING",
  "contact": [
    ["Pune, India", "jane@example.com|mailto:jane@example.com", "+91 90000 00000"],
    ["linkedin.com/in/janedoe|https://linkedin.com/in/janedoe", "==Open to hybrid=="]
  ],
  "sections": [
    {
      "heading": "SUMMARY",
      "body": "==Data Engineer== with [8]+ years ==building and operating batch and streaming pipelines==. Cut nightly ETL runtime from [X] to [Y] across **40+ production jobs**."
    },
    {
      "heading": "CORE SKILLS",
      "rows": [
        ["==Pipelines & Orchestration==", "==Airflow== · ==dbt== · Spark · [Dagster]"],
        ["Warehousing", "[Snowflake] · [BigQuery] · PostgreSQL"],
        ["Languages", "Python · SQL · [Scala]"]
      ],
      "note": "FILL-IN RULE — enter only tools you have shipped with and could be questioned on for twenty minutes. Delete brackets you cannot honestly fill; do not soften them to \"familiar with\"."
    },
    {
      "heading": "PROFESSIONAL EXPERIENCE",
      "roles": [
        {
          "title": "==Data Engineer==",
          "org": "Acme Analytics",
          "meta": "Mar 2021 – Present  |  Pune, India  |  ==B2B analytics SaaS==",
          "bullets": [
            "==Own the ingestion layer== for **40+ production jobs**, ==cutting nightly runtime from [X] to [Y]==.",
            "==Coordinate with analytics and product teams== to define contracts, reducing schema-break incidents by [Z]%."
          ]
        }
      ]
    },
    { "heading": "EDUCATION", "rows": [["[B.E. Computer Science]", "[University] · [Year]"]] },
    { "heading": "CERTIFICATIONS", "bullets": ["[Add certifications, or delete this section.]"] }
  ]
}
```

## Build and verify

```bash
node scripts/build_resume.js spec.json
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf out.docx
pdftoppm -jpeg -r 100 out.pdf page && ls page-*.jpg     # then view the images
```

Always render and look at the result before delivering. Two things to check: the page
break should not split a role from its bullets, and a second page that is less than
half full should be tightened (reduce `margin`, or trim the weakest bullets) or accepted
deliberately because the placeholders will fill it once the candidate completes them.

## Clean-copy guardrail

`--clean` exits with status 2 and lists every remaining `[placeholder]` rather than
producing the file. This is deliberate: an unfilled bracket in a submitted resume is
worse than a shorter bullet, and the failure should happen here rather than in the
recruiter's inbox.
