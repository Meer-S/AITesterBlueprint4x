You are a senior n8n automation architect, Jira integration engineer, QA lead, and AI workflow developer.

Build a complete, production-ready n8n workflow from scratch with the following name:

`Jira Production Bug → Automatic RCA Excel Generator`

Do not only explain the workflow. Create the complete workflow with all nodes, expressions, connections, error branches, field mappings, prompts, structured output schemas, retry behavior, and setup notes.

The workflow must be importable into and editable within n8n.

## OBJECTIVE

Whenever a Jira issue is created or updated and matches the configured Production Bug JQL:

1. Trigger the n8n workflow automatically.
2. Retrieve the complete Jira issue.
3. Retrieve available comments, attachments metadata, linked issues, and relevant fields.
4. Verify that the issue still matches the Production Bug JQL.
5. Prevent duplicate or unnecessary RCA executions.
6. Generate an evidence-based Root Cause Analysis.
7. Copy the existing RCA Google Sheets template.
8. Populate the copied template while preserving its formatting, formulas, dropdowns, colors, and worksheets.
9. Export the completed Google Sheet as a Microsoft Excel `.xlsx` file.
10. Store the Google Sheet and Excel file in the configured Google Drive folders.
11. Update an audit table so future Jira updates modify the existing RCA instead of creating duplicates.
12. Handle individual failures without losing the complete execution record.

## IMPORTANT ARCHITECTURE RULE

Use deterministic n8n nodes for:

* Jira retrieval
* JQL verification
* Deduplication
* Google Drive file copying
* Google Sheets writing
* Excel export
* Audit logging
* Error handling

Use the AI Agent only for generating the structured RCA analysis.

Do not connect Jira and Google Sheets as autonomous AI tools. The agent must not decide whether a ticket should be fetched or whether a spreadsheet should be written.

## CONFIGURATION VARIABLES

Create a `Workflow Configuration` Set node containing these placeholders:

```text
JIRA_BASE_URL=https://YOUR-COMPANY.atlassian.net

PRODUCTION_BUG_JQL=project = VWO
AND issuetype = Bug
AND labels = "production-bug"
AND statusCategory != Done

RCA_TEMPLATE_FILE_ID=REPLACE_WITH_NATIVE_GOOGLE_SHEETS_TEMPLATE_FILE_ID

RCA_GOOGLE_SHEETS_FOLDER_ID=REPLACE_WITH_OUTPUT_FOLDER_ID

RCA_EXCEL_FOLDER_ID=REPLACE_WITH_XLSX_OUTPUT_FOLDER_ID

EXPORT_XLSX=true

ADD_JIRA_COMMENT=false

AI_MODEL=gpt-5.4

AI_TEMPERATURE=0.1

MAX_RCA_ACTIONS=10
```

Keep the JQL easy to change.

Add a setup note explaining that `labels = "production-bug"` is the recommended reliable identifier. If the Jira instance uses an Environment field or custom field, the user may replace the JQL with something such as:

```text
project = VWO
AND issuetype = Bug
AND (
  labels in ("production-bug", "prod")
  OR environment ~ "production"
)
AND statusCategory != Done
```

Do not assume that a custom field exists.

## TEMPLATE REQUIREMENT

Use the existing `VWO-49_RCA_Template.xlsx` as the design reference.

Before activating the workflow, the user will:

1. Upload the template to Google Drive.
2. Open or convert it as a native Google Sheet.
3. Rename its first worksheet from `VWO-49 RCA` to `RCA Summary`.
4. Clear the VWO-49 sample values while preserving formatting, formulas, dropdowns, and worksheet structure.
5. Put its Google Drive file ID in `RCA_TEMPLATE_FILE_ID`.

The native template must contain these worksheets:

* `RCA Summary`
* `5 Whys`
* `Timeline`
* `Actions`
* `Evidence & Validation`
* `Blank RCA Template`
* `Lists`

Do not recreate the visual design during every execution. Copy the template so the existing formatting is preserved.

## REQUIRED WORKFLOW

Build and connect these nodes in this order.

### 1. Jira Trigger

Node name:

`Jira Trigger - Production Bug Event`

Use the Jira Trigger node.

Listen for:

* Issue Created
* Issue Updated

If the Jira Trigger exposes JQL filtering, apply `PRODUCTION_BUG_JQL` at the trigger level.

If it does not expose JQL filtering, allow the event through and enforce JQL using the later verification node.

The trigger must capture:

* Jira key
* Event type
* Event timestamp
* Changelog when available
* Triggering user
* Issue ID

### 2. Workflow Configuration

Node name:

`Workflow Configuration`

Store all configuration placeholders in this node.

### 3. Normalize Trigger Payload

Node name:

`Normalize Jira Event`

Use a Set or Code node to produce:

```json
{
  "jira_key": "",
  "jira_issue_id": "",
  "webhook_event": "",
  "event_timestamp": "",
  "triggered_by": "",
  "workflow_run_id": "",
  "received_at": ""
}
```

Use the n8n execution ID as `workflow_run_id`.

### 4. Get Complete Jira Issue

Node name:

`Jira - Get Complete Issue`

Retrieve the issue using `jira_key`.

Request all available relevant fields:

* Key
* Summary
* Description
* Issue type
* Project
* Status
* Resolution
* Priority
* Existing severity
* Environment
* Labels
* Components
* Affected versions
* Fix versions
* Reporter
* Assignee
* Created date
* Updated date
* Steps to reproduce
* Expected result
* Actual result
* Acceptance criteria
* Linked issues
* Attachment metadata
* Relevant custom fields
* Changelog when available

Do not update the Jira issue.

### 5. Get Jira Comments

Node name:

`Jira - Get All Comments`

Retrieve all available comments for the Jira key.

Return:

* Comment ID
* Author
* Created timestamp
* Updated timestamp
* Comment body

If the built-in Jira node cannot retrieve comments, use an authenticated HTTP Request node with the Jira credential.

### 6. Verify Production Bug JQL

Node name:

`Jira - Verify JQL Match`

Search Jira using this dynamic JQL:

```text
key = "{{$json.jira_key}}" AND (
  {{$node["Workflow Configuration"].json["PRODUCTION_BUG_JQL"]}}
)
```

If inserting the configured JQL directly creates invalid nested syntax, construct a safe equivalent without unnecessary parentheses.

### 7. IF: Is Production Bug?

Node name:

`IF - Production Bug Confirmed`

Continue only when the JQL search returns the current Jira key.

False branch:

* Record `Skipped - JQL Not Matched` in the audit table.
* Stop successfully.
* Do not call the AI model.
* Do not create an RCA file.

### 8. Create Issue Fingerprint

Node name:

`Create Issue Fingerprint`

Create a deterministic fingerprint from:

* Jira key
* Jira updated timestamp
* Description
* Priority
* Environment
* Labels
* Status
* Resolution
* Most recent comment ID and timestamp

Use a SHA-256 hash if available.

Output:

```json
{
  "jira_key": "",
  "jira_updated_at": "",
  "issue_fingerprint": ""
}
```

### 9. Get Existing RCA Audit Record

Node name:

`Audit Store - Get Jira Record`

Use an n8n Data Table or another persistent n8n-supported data store.

Use `jira_key` as the unique key.

The audit table must contain:

* jira_key
* jira_issue_id
* issue_fingerprint
* jira_updated_at
* rca_status
* processing_status
* google_sheet_file_id
* google_sheet_url
* excel_file_id
* excel_file_url
* rca_version
* last_processed_at
* workflow_run_id
* last_error

### 10. IF: Processing Required?

Node name:

`IF - New or Changed Issue`

Continue when:

* No audit record exists, or
* The current fingerprint differs from the stored fingerprint, or
* The previous execution failed.

Skip when the fingerprint is unchanged and the previous execution succeeded.

This prevents duplicate RCA files when Jira sends repeated webhook events.

### 11. Merge Jira Evidence

Node name:

`Build Jira Evidence Package`

Create one clean evidence object for the AI Agent.

Include:

```json
{
  "jira": {
    "key": "",
    "url": "",
    "project": "",
    "summary": "",
    "description": "",
    "issue_type": "",
    "status": "",
    "resolution": "",
    "priority": "",
    "existing_severity": "",
    "environment": "",
    "labels": [],
    "components": [],
    "affected_versions": [],
    "fix_versions": [],
    "reporter": "",
    "assignee": "",
    "created_at": "",
    "updated_at": "",
    "acceptance_criteria": "",
    "steps_to_reproduce": "",
    "expected_result": "",
    "actual_result": ""
  },
  "comments": [],
  "linked_issues": [],
  "attachments": [],
  "changelog": [],
  "evidence_limitations": []
}
```

Only include attachment metadata unless attachment contents have actually been extracted.

### 12. RCA AI Agent

Node name:

`AI Agent - Generate Evidence-Based RCA`

Connect the configured chat model.

Use temperature `0.1`.

Attach a Structured Output Parser.

The agent must return valid JSON matching the schema below.

## RCA AGENT SYSTEM PROMPT

Use this complete system prompt:

```text
You are a veteran QA engineer, incident investigator, and Root Cause Analysis specialist with more than 15 years of experience.

You are analyzing a confirmed Jira issue classified by the workflow as a production bug.

Your responsibility is to produce an evidence-based RCA suitable for engineers, QA, product managers, and incident reviewers.

An RCA identifies:

1. What happened.
2. What was affected.
3. The direct technical cause.
4. The deeper system or process root cause.
5. Contributing factors.
6. Why existing controls did not prevent or detect it.
7. Containment, corrective, and preventive actions.
8. How the fix will be verified.

NEVER INVENT A ROOT CAUSE.

A Jira ticket being labelled as a production bug does not prove that its root cause is known.

If the ticket lacks reproduction evidence, logs, timestamps, error details, impact information, or technical isolation:

- Set RCA status to "Draft - Investigation Required".
- Set confidence to "Low" or "Medium".
- Set direct cause to "Not determined".
- Set root cause to "Not determined".
- Clearly list the missing evidence.
- Generate investigation actions before corrective actions.
- Do not state a suspected cause as confirmed.

Differentiate:

- Symptom: What the user or system experienced.
- Direct cause: Immediate technical mechanism that produced the symptom.
- Root cause: Underlying system, design, process, control, or ownership failure that allowed the direct cause.
- Contributing factor: A condition that increased likelihood, duration, or impact.
- Containment: Immediate action that limits ongoing impact.
- Corrective action: Removes the confirmed cause.
- Preventive action: Reduces recurrence or improves detection.

Use Jira data as evidence, not as unquestionable truth.

Do not claim an attachment, log, screenshot, comment, or linked issue proves something unless its contents support the claim.

Do not expose credentials, tokens, cookies, passkeys, personal data, or sensitive authentication information.

Severity represents technical impact.

Priority represents business urgency.

Do not collapse severity and priority.

If user impact or financial impact is missing, state "Unknown".

Every 5-Whys answer must be supported by evidence. Stop the chain when evidence ends. Use "Not determined" for unsupported levels.

Create no more than 10 action items.

Every action must contain:

- Unique action ID
- Action type
- Specific action
- Owner or TBD
- Priority
- Status
- Success criteria

Return JSON only.
```

## STRUCTURED RCA OUTPUT SCHEMA

Configure the Structured Output Parser for this schema:

```json
{
  "metadata": {
    "jira_key": "",
    "jira_url": "",
    "title": "",
    "project": "",
    "issue_type": "",
    "jira_status": "",
    "jira_priority": "",
    "reporter": "",
    "assignee": "",
    "created_at": "",
    "updated_at": "",
    "resolution": "",
    "rca_generated_at": "",
    "rca_version": 1
  },
  "assessment": {
    "problem_statement": "",
    "observed_symptom": "",
    "business_impact": "",
    "technical_impact": "",
    "detection_method": "",
    "rca_status": "",
    "confidence": "",
    "recommended_severity": "",
    "recommended_priority": "",
    "direct_cause": "",
    "root_cause": "",
    "contributing_factors": "",
    "evidence_required": "",
    "immediate_containment": "",
    "corrective_direction": "",
    "preventive_direction": "",
    "validation_plan": ""
  },
  "five_whys": [
    {
      "why_level": "Why 1",
      "question": "",
      "answer": "",
      "evidence": "",
      "gap_or_next_question": "",
      "owner": "TBD",
      "status": ""
    }
  ],
  "timeline": [
    {
      "date": "",
      "time": "",
      "event": "",
      "source": "",
      "evidence_or_observation": "",
      "rca_significance": ""
    }
  ],
  "actions": [
    {
      "action_id": "",
      "type": "",
      "action": "",
      "owner": "TBD",
      "due_date": "",
      "priority": "",
      "status": "",
      "success_criteria": ""
    }
  ],
  "evidence": [
    {
      "evidence_id": "",
      "type": "",
      "description": "",
      "source_or_reference": "",
      "availability": "",
      "finding_or_gap": "",
      "confidence": ""
    }
  ],
  "validation": [
    {
      "validation_id": "",
      "scenario": "",
      "expected_result": "",
      "coverage": "",
      "status": "Not Run",
      "required_evidence": ""
    }
  ],
  "quality_checks": {
    "root_cause_supported_by_evidence": false,
    "missing_information_disclosed": true,
    "contains_invented_facts": false,
    "requires_human_review": true
  }
}
```

Allowed `rca_status` values:

* Draft - Investigation Required
* In Investigation
* Confirmed
* Closed
* Not Applicable

Allowed `confidence` values:

* High
* Medium
* Low

Allowed action types:

* Investigation
* Containment
* Corrective
* Preventive
* Decision

Allowed action statuses:

* Not Started
* In Progress
* Blocked
* Completed
* Cancelled

### 13. Validate RCA Output

Node name:

`Validate RCA JSON`

Check that:

* Jira key matches the source ticket.
* All required top-level objects exist.
* No more than five 5-Whys records exist.
* No more than ten actions exist.
* `contains_invented_facts` is false.
* A Low-confidence RCA does not contain a confidently asserted root cause.
* If `root_cause_supported_by_evidence` is false, root cause must be `Not determined`, `Unconfirmed`, or equivalent.
* Arrays contain objects rather than Markdown text.
* No secret, token, cookie, credential, or raw sensitive authentication value is present.

Invalid output branch:

1. Retry the AI Agent once with the validation error.
2. If still invalid, record the execution as failed.
3. Do not create or overwrite an RCA workbook with invalid data.

### 14. Determine Existing Workbook

Node name:

`IF - Existing RCA Workbook`

If the audit record contains a valid `google_sheet_file_id`:

* Reuse the existing file.
* Increment `rca_version`.
* Do not create another workbook.

If no file exists:

* Copy the RCA template.

### 15. Copy RCA Template

Node name:

`Google Drive - Copy RCA Template`

Use Google Drive:

* Operation: Copy File
* Source: `RCA_TEMPLATE_FILE_ID`
* Destination folder: `RCA_GOOGLE_SHEETS_FOLDER_ID`
* Filename:

```text
RCA_{{$json.metadata.jira_key}}_{{$now.format("yyyy-MM-dd")}}
```

Preserve it as a native Google Sheet.

Capture:

* New file ID
* Google Sheet URL

### 16. Clear Previous Dynamic Data

Node name:

`Google Sheets - Clear Dynamic RCA Rows`

For existing files and fresh template copies, clear the previous dynamic values while preserving formatting.

Clear only:

```text
'5 Whys'!A2:G100
'Timeline'!A2:F100
'Actions'!A2:H100
'Evidence & Validation'!A2:G100
'Evidence & Validation'!A11:F100
```

Do not clear:

* Headers
* Formatting
* Dropdown validation
* Conditional formatting
* Formulas
* The Lists worksheet
* The Blank RCA Template worksheet

### 17. Populate RCA Summary

Node name:

`Google Sheets - Populate RCA Summary`

Use the Structured Output Parser data.

Write these values to the copied workbook:

```text
'RCA Summary'!B6       = metadata.jira_key
'RCA Summary'!D6       = metadata.issue_type
'RCA Summary'!F6       = metadata.jira_status
'RCA Summary'!H6       = metadata.jira_priority

'RCA Summary'!B7:C7    = metadata.project
'RCA Summary'!E7       = metadata.reporter
'RCA Summary'!G7:H7    = metadata.assignee

'RCA Summary'!B8:C8    = metadata.created_at
'RCA Summary'!E8:F8    = metadata.updated_at
'RCA Summary'!H8       = metadata.resolution

'RCA Summary'!B9:H9    = metadata.title
'RCA Summary'!B10:H10  = metadata.jira_url
'RCA Summary'!B11:H11  = Jira source and workflow run ID

'RCA Summary'!B14:H15  = assessment.problem_statement
'RCA Summary'!B16:H17  = assessment.observed_symptom
'RCA Summary'!B18:H19  = assessment.business_impact
'RCA Summary'!B20:H21  = assessment.technical_impact
'RCA Summary'!B22:H23  = assessment.detection_method

'RCA Summary'!B24:C24  = assessment.rca_status
'RCA Summary'!E24      = assessment.confidence
'RCA Summary'!G24:H24  = assessment.recommended_severity

'RCA Summary'!B25:H26  = assessment.direct_cause
'RCA Summary'!B27:H28  = assessment.root_cause
'RCA Summary'!B29:H30  = assessment.contributing_factors
'RCA Summary'!B31:H34  = assessment.evidence_required

'RCA Summary'!B37:H38  = assessment.immediate_containment
'RCA Summary'!B39:H40  = assessment.corrective_direction
'RCA Summary'!B41:H43  = assessment.preventive_direction
'RCA Summary'!B44:H46  = assessment.validation_plan
```

Preserve the existing formulas in the Action Summary section.

Use Google Sheets batch updates where possible instead of creating a separate API request for every cell.

### 18. Populate 5 Whys

Node name:

`Google Sheets - Write 5 Whys`

Split `five_whys` into items and write one row per object:

```text
A = why_level
B = question
C = answer
D = evidence
E = gap_or_next_question
F = owner
G = status
```

Begin at row 2.

Write a maximum of five rows.

### 19. Populate Timeline

Node name:

`Google Sheets - Write Timeline`

Write:

```text
A = date
B = time
C = event
D = source
E = evidence_or_observation
F = rca_significance
```

Begin at row 2.

Sort by date and time when usable dates exist.

### 20. Populate Actions

Node name:

`Google Sheets - Write Actions`

Write:

```text
A = action_id
B = type
C = action
D = owner
E = due_date
F = priority
G = status
H = success_criteria
```

Begin at row 2.

Do not exceed ten action rows.

### 21. Populate Evidence

Node name:

`Google Sheets - Write Evidence`

Write:

```text
A = evidence_id
B = type
C = description
D = source_or_reference
E = availability
F = finding_or_gap
G = confidence
```

Begin at row 2.

### 22. Populate Validation Plan

Node name:

`Google Sheets - Write Validation`

Write:

```text
A = validation_id
B = scenario
C = expected_result
D = coverage
E = status
F = required_evidence
```

Begin at row 11.

### 23. Export as Microsoft Excel

Node name:

`Google Drive API - Export RCA as XLSX`

Run only when `EXPORT_XLSX` is true.

Export the completed native Google Sheet using the Google Drive API with this MIME type:

```text
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

Filename:

```text
RCA_{{$json.metadata.jira_key}}_v{{$json.metadata.rca_version}}.xlsx
```

Upload or store the resulting Excel file in:

`RCA_EXCEL_FOLDER_ID`

Capture:

* Excel file ID
* Excel file URL
* Filename

If a previous Excel export exists for the same Jira key and versioning policy allows replacement, update it. Otherwise, create a versioned file.

### 24. Update Audit Store

Node name:

`Audit Store - Upsert Success`

Upsert by `jira_key`.

Store:

* Current issue fingerprint
* Jira updated timestamp
* RCA status
* Processing status = Success
* Google Sheet file ID and URL
* Excel file ID and URL
* RCA version
* Last processed timestamp
* Workflow run ID
* Empty last error

### 25. Optional Jira Comment

Node name:

`IF - Jira Comment Enabled`

Run only if `ADD_JIRA_COMMENT` is true.

Add a concise comment:

```text
Automated RCA generated/updated.

RCA status: {{rca_status}}
Confidence: {{confidence}}
Google Sheet: {{google_sheet_url}}
Excel file: {{excel_file_url}}

This RCA is evidence-based and may require human review before closure.
```

Do not transition or close the Jira issue automatically.

Prevent this comment update from producing a duplicate RCA by relying on the issue fingerprint and audit-store checks.

### 26. Error Handling

Create a dedicated error workflow or Error Trigger branch.

On failure:

* Capture Jira key.
* Capture node name.
* Capture error message.
* Capture execution ID.
* Capture timestamp.
* Update the audit store with `processing_status = Failed`.
* Preserve any existing successful RCA file.
* Do not overwrite a valid workbook with incomplete data.
* Do not expose secrets in logs.
* Make the execution retryable.

Enable retry with exponential backoff for:

* Jira API rate limits
* Google Drive temporary failures
* Google Sheets temporary failures
* AI provider rate limits

Do not retry permanent validation errors indefinitely.

## HUMAN REVIEW RULE

Every new RCA should default to:

```text
requires_human_review = true
```

Do not automatically close the Jira issue.

Do not automatically mark the RCA as Confirmed unless:

* The generated root cause is supported by evidence, and
* Confidence is High, and
* A human approval mechanism has been explicitly configured.

## WORKFLOW ACCEPTANCE TESTS

Create and document tests for:

1. New Jira production bug creates one RCA workbook and one Excel export.
2. Non-production bug is skipped.
3. Story or Task is skipped by JQL.
4. Repeated identical webhook does not create a duplicate.
5. Relevant Jira update regenerates the RCA and updates the same Google Sheet.
6. Jira update increments RCA version.
7. Missing logs produce Draft RCA with root cause Not determined.
8. Confirmed evidence can produce an evidence-backed root cause.
9. Invalid AI JSON retries once and then fails safely.
10. Google Sheets failure does not mark the workflow successful.
11. Existing successful RCA is not destroyed when an update fails.
12. Excel export preserves all template worksheets.
13. No credentials or authentication secrets appear in the RCA.
14. The action summary formulas calculate correctly.
15. The workflow can be replayed safely.

## FINAL DELIVERABLE

Build:

1. The complete connected n8n workflow.
2. All node names and expressions.
3. Structured Output Parser schema.
4. AI Agent system prompt.
5. JQL placeholders.
6. Audit-store schema.
7. Error-handling branch.
8. Template cell mappings.
9. Google Sheet to XLSX export.
10. A short setup checklist.
11. A short test checklist.

Use placeholder credentials only.

Do not hardcode secrets, access tokens, email addresses, Jira credentials, Google credentials, or real file IDs.

Do not leave nodes disconnected.

Do not return a conceptual diagram without building the workflow.
