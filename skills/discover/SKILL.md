---
name: discover
description: Deep documentation discovery across all available sources — Confluence/wiki, GitHub, JIRA, Slack, and semantic code search via Captain MCP. Fans out across multiple sources in parallel, ranks findings by authoritativeness, surfaces contradictions, and gives a verified/unverified/unknown verdict. Use when you need to validate an assumption, confirm a design decision, understand how something works internally, or back up a suggestion with real documentation. Can be invoked from other skills as a validation step.
---

# Discover — Deep Documentation Discovery

Search across all available documentation sources, synthesize what's found, and give a confident verdict — not just a list of links.

This skill is designed to be used:
- **Standalone** — "how does X work internally?" / "what's the policy on Y?" / "has anyone discussed Z?"
- **From other skills** — `/validate`, `/brain`, `/gaps` can invoke this to validate assumptions before stating them as fact

---

## Phase 0: Frame the Query

Before searching, clarify what you're actually looking for:

1. **Identify the question type:**
   - **How does X work?** — looking for technical documentation, architecture docs, or code
   - **What's the decision/policy on X?** — looking for design docs, ADRs, JIRA decisions, wiki pages
   - **Has this been discussed?** — looking for Slack threads, JIRA comments, PR discussions
   - **Is this the right way to do X?** — looking for best practices, runbooks, internal standards
   - **What does X do in code?** — looking for implementation via code search

2. **Extract search terms:** Identify 2-4 specific terms or phrases to search for. Think about:
   - The exact name of the system, service, or concept
   - Synonyms or alternate names that might be used internally
   - Related terms that documentation might use instead

3. **State your search plan** before executing:
   > _"Searching for: [topic]. Query terms: [terms]. Sources: [which ones are relevant]."_

---

## Phase 1: Fan-Out Search

Search all relevant sources **in parallel** (do not wait for one before starting the next). Use Captain MCP tools.

### Source 1: Confluence / Internal Wiki
*Most authoritative for policies, architecture, and official documentation.*

```
mcp: search_confluence_content
query: <search terms>
```

For each result, fetch the full page if it looks directly relevant:
```
mcp: get_confluence_page
pageId: <id from search result>
```

### Source 2: GitHub Pages & Internal Docs
*Authoritative for technical specs, API docs, and project-level documentation.*

```
mcp: search_github_pages
query: <search terms>
```

### Source 3: Semantic Code Search
*Canonical for understanding actual behavior — what the code actually does.*

```
mcp: search_semantic_code
query: <search terms describing behavior>
```

Also use for finding implementations:
```
mcp: jarvis_codesearch
query: <search terms>
```

### Source 4: JIRA
*Authoritative for decisions, rationale, and accepted/rejected approaches.*

```
mcp: search_jira_issues
query: <search terms>
```

Look specifically for:
- Resolved/Done tickets that document decisions
- Design proposals or RFCs
- Known bugs or limitations

### Source 5: Slack
*Lowest authoritativeness but captures tribal knowledge, recent discussions, and context that never made it to docs.*

```
mcp: search_slack
query: <search terms>
```

Use for:
- Recent discussions about the topic
- Questions others asked with answers
- Decisions made in chat that weren't documented

### Source 6: Unified Context (fallback)
*If targeted searches return sparse results, cast a wider net:*

```
mcp: unified_context_search
query: <search terms>
```

---

## Phase 2: Evaluate & Rank Findings

For each finding, assess:

**Authoritativeness tier:**
| Tier | Sources | Weight |
|------|---------|--------|
| 🟢 Official | Confluence wiki, official GitHub docs, architecture docs | Highest |
| 🔵 Code | Actual implementation, code comments, tests | High — reflects real behavior |
| 🟡 Decisions | JIRA resolved tickets, design docs, PR descriptions | Medium — captures intent |
| 🟠 Discussion | Slack threads, PR comments, JIRA comments | Low — informal, may be outdated |

**Recency:** More recent sources override older ones for the same claim. Note dates where available.

**Specificity:** A source that directly addresses the question outweighs one that mentions the topic tangentially.

---

## Phase 3: Synthesize

Don't dump raw results — synthesize into a clear answer.

### Look for:

**Consensus:** Do multiple sources agree? That increases confidence.

**Contradictions:** Do sources disagree? Surface this explicitly — it's important signal.
- e.g. _"The Confluence page says X, but the code does Y — this may be outdated documentation."_

**Gaps:** Did nothing authoritative address this?
- e.g. _"No official documentation found. Only a Slack thread from 8 months ago mentions this."_

**Freshness issues:** Is the documentation old relative to what the code actually does?

---

## Phase 4: Discovery Report

Produce a structured report:

```
## Discovery Report

**Query:** <what was searched for>
**Search terms used:** <terms>

---

### What the docs say

<Synthesized answer — not a list of links, a clear statement of what was found>

**Key sources:**
- 🟢 [Source title](url) — <one-line summary of what this source says> (date if available)
- 🔵 [Code reference](url) — <what the implementation shows>
- 🟡 [JIRA-123](url) — <decision captured here>
- 🟠 [Slack thread](url) — <what was discussed, with caveat about informality>

---

### Contradictions & Conflicts
<If any sources disagree, call it out explicitly>
- <Source A> says X, but <Source B> says Y — likely explanation: <hypothesis>

(or "No contradictions found across sources.")

---

### Gaps & Missing Documentation
<What couldn't be found, or what should be documented but isn't>
- No official documentation found for <specific aspect>
- Only informal sources found for <specific aspect> — consider creating a wiki page

(or "Coverage is thorough — no significant gaps found.")

---

### Verdict

**Confidence:** <HIGH / MEDIUM / LOW>

🟢 VERIFIED — Multiple authoritative sources confirm this.
🟡 PARTIALLY VERIFIED — Some documentation exists but incomplete or potentially outdated.
🔴 UNVERIFIED — No authoritative documentation found. Findings based on informal sources only.
⚪ UNKNOWN — Nothing found across any source. This may be undocumented.

**Summary:** <1-3 sentences — the direct answer to the original question, with honest confidence level>
```

---

## Invocation from Other Skills

When called from another skill (e.g. `/validate`, `/brain`, `/gaps`), a condensed format is acceptable:

```
## Discovery: <topic>
**Verdict:** <VERIFIED / PARTIALLY VERIFIED / UNVERIFIED / UNKNOWN>
**Finding:** <one paragraph summary>
**Best source:** <most authoritative source found>
**Caveat:** <any contradictions or freshness concerns>
```

The calling skill should treat UNVERIFIED or UNKNOWN findings as assumptions, not facts, and flag them accordingly.

---

## Important Notes

- **Search in parallel** — do not run sources sequentially; fan out all searches at once
- **Fetch full pages** for the top 1-2 Confluence results — summaries are often not enough
- **Never fabricate sources** — if nothing was found, say so clearly rather than citing something vague
- **Contradictions are valuable findings** — surface them, don't pick a winner and suppress the other
- **Slack is a last resort for authoritativeness** — but it often contains context found nowhere else
- **Date your findings** — documentation freshness matters; a 3-year-old wiki page about a system that's been rewritten is worse than no documentation
- If `unified_context_search` and all targeted searches return nothing, tell the user explicitly: _"This topic appears to be undocumented internally. Consider creating a wiki page."_
