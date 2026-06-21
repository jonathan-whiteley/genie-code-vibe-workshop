---
name: command-center-patterns
description: "Project patterns for the Genie Code Command Center workshop. Use when building this workshop's governed metric view, embedding an AI/BI dashboard in the app, pointing the app's Ask Genie panel at your own Genie space, adding a Company News feed through the web_search_mcp MCP server, or creating a Genie space and adding sample questions or benchmarks via the REST API. Each pattern captures the field-tested shape plus the gotchas that bite first."
---

# Command Center Workshop Patterns

Field-tested patterns for the Operator Command Center workshop. Each one distills the working approach and the dead ends, so you do not rediscover them. When a task below matches what you are about to build, open the matching file in this skill and follow it.

| When you are... | Open | It covers |
|---|---|---|
| Building the governed metric view (Module 1) | `metric-view-pattern.md` | The fan-out trap (pre-aggregate each fact to one row per store-date before joining; labor has an extra `role` grain), the YAML/DDL shape, `MEASURE()` query syntax, and verification |
| Embedding the AI/BI dashboard as an iframe in the app (Module 5) | `dashboard-embed-pattern.md` | `/embed` URL vs `X-Frame-Options`, the admin-only `*.databricksapps.com` allowlist, and the third-party-cookie / managed-laptop failure chain |
| Pointing the app's Ask Genie panel at your own space (Module 5) | `genie-swap-pattern.md` | The shared-config vs per-app env precedence bug, the `lru_cache` restart requirement, and the OBO scopes behind the 403 "Invalid scope" |
| Adding a Company News feed via MCP (Module 6) | `mcp-company-news-pattern.md` | Calling the `web_search_mcp` managed MCP server from the app as its service principal, inline endpoint, the `:param`/URL trap, and fence-stripping |
| Creating a Genie space and adding sample questions / benchmarks (Module 2) | `genie-space-pattern.md` | The REST shapes (`PATCH /api/2.0/genie/spaces/{id}`, the `serialized_space` JSON string), the required 32-char question ids, and running benchmarks via the Conversation API |

These are specific to this workshop's schema, app, and resources; they complement, not replace, the ai-dev-kit skills.
