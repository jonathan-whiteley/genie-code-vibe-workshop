# Adding MCP-Powered Company News to a Databricks App

A bell icon dropdown in the app header that fetches live news via the Databricks managed MCP server (`web_search_mcp`), summarizes it with `ai_query` on a Foundation Model endpoint, and renders 3 bullet cards.

---

## MCP Server Discovery

The managed MCP server at `/api/2.0/mcp/external/web_search_mcp` exposes:

| Tool | Required | Key Options |
| --- | --- | --- |
| `you-search` | `query` (str) | `count`, `freshness`, `country`, `livecrawl` |
| `you-contents` | `urls` (array) | `formats` |
| `you-research` | `input` (str) | `research_effort` |

Discovered via:

```python
from databricks_mcp import DatabricksMCPClient
client = DatabricksMCPClient(server_url, workspace_client=w)
tools = client.list_tools()  # synchronous
result = client.call_tool("you-search", {...})  # synchronous
```

---

## Key Gotchas & Fixes

### 1. Package availability in Apps runtime

- `databricks-mcp` and `mcp` must be in `requirements.txt`
- Verify they actually persist after edits (workspace file writes via API can silently fail)
- The packages install fine in the Apps runtime — no dependency conflict

### 2. Router registration crash

- If you create a new `routers/news.py` file via the workspace API, it may have metadata issues that prevent import
- **Solution**: Put the endpoint inline in `app.py` instead of a separate router file
- If you import a module but forget `app.include_router(x.router)`, the endpoint returns 404 silently (FastAPI serves `{"detail":"Not Found"}` as valid JSON)

### 3. Auth: SP vs. user token

- The user's forwarded token (`x-forwarded-access-token`) gets **403** on MCP endpoints — the app's `user_api_scopes` (`sql`, `genie`, `dashboards.genie`) don't cover MCP
- **Solution**: Use the app's **service principal** `WorkspaceClient` from `lib/deps.py`
- MCP connection permissions are handled by Admin

### 4. `lib/sql_utils` `:param` regex

- `fetch_all()` uses `re.compile(r":(\w+)")` to substitute params — URLs in news text contain patterns like `:8080`, `:29` that trigger `KeyError: 'missing param: 29'`
- **Solution**: Use `get_warehouse_client().cursor().execute(sql)` directly — no param substitution needed

### 5. `ai_query` JSON parsing

- The model sometimes wraps output in markdown fences (` ```json...``` `) or returns empty strings
- **Solution**: Strip fences, find `[` and `]` bounds, parse only that substring

### 6. Unicode in JSX

- When editing JSX via the workspace API, `\u2197` and `\u00b7` render as literal escape text, not characters
- **Solution**: Use the actual Unicode characters (`↗`, `·`) in the source

### 7. Workspace Files API write rate limit: save files sequentially

- The Workspace Files API has an undocumented but real per-workspace write rate limit: saving roughly 4 to 5 files in parallel in the same second triggers 429s.
- This feature writes several files (`app.py`, `shell.jsx`, `Homebase.html`, `requirements.txt`), so **save them one at a time, not in parallel**. Sequential writes are fine.
- This applies to any multi-file app edit (Modules 4, 5, 6), not just Company News.

---

## Final Working Implementation

### requirements.txt

Add:

```
databricks-mcp
mcp
```

### app.py — inline endpoint

Place after all other `include_router` calls, before `/healthz`:

```python
# ---------- Company News via Databricks MCP ----------
import json
from databricks_mcp import DatabricksMCPClient
from lib.deps import workspace_client, get_warehouse_client
from lib.config import get_settings

@app.get("/api/news")
def _news():
    try:
        w = workspace_client()
        host = os.environ.get("DATABRICKS_HOST", "").replace("https://", "").rstrip("/")
        server_url = f"https://{host}/api/2.0/mcp/external/web_search_mcp"
        client = DatabricksMCPClient(server_url, workspace_client=w)
        result = client.call_tool(
            "you-search",
            {"query": "Little Caesars news", "freshness": "week", "count": 5, "country": "US"},
        )
        parts = []
        for block in result.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        raw_news = "\n".join(parts)
        if not raw_news:
            return {"bullets": [], "error": "MCP returned empty"}

        # Summarize via ai_query (direct cursor to bypass :param regex)
        s = get_settings()
        esc = raw_news.replace("'", "''")[:8000]
        sql = f"""SELECT ai_query('{s.fmapi_endpoint}',
            'You are a news summarizer for Little Caesars. Produce EXACTLY 3 JSON objects "
            'in a JSON array. Each object: "headline" (max 10 words), "summary" (1 sentence '
            'max 25 words), "url" (source link). Return ONLY the raw JSON array, no markdown.'
            '\n\nRESULTS:\n{esc}') AS bullets"""
        with get_warehouse_client().cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
        if not row or not row[0]:
            return {"bullets": [], "error": "ai_query returned nothing"}

        # Robust parse: strip markdown fences, find JSON array
        raw_ai = str(row[0]).strip()
        if raw_ai.startswith("```"):
            raw_ai = raw_ai.split("\n", 1)[-1]
        if raw_ai.endswith("```"):
            raw_ai = raw_ai[:-3].strip()
        start = raw_ai.find("[")
        end = raw_ai.rfind("]") + 1
        if start == -1 or end == 0:
            return {"bullets": [], "error": f"no JSON array: {raw_ai[:150]}"}
        parsed = json.loads(raw_ai[start:end])
        bullets = [
            {"headline": b.get("headline", ""), "summary": b.get("summary", ""), "url": b.get("url", "#")}
            for b in parsed[:3]
        ]
        return {"bullets": bullets}
    except Exception as e:
        return {"bullets": [], "error": f"{type(e).__name__}: {str(e)[:300]}"}
```

### shell.jsx — NewsDropdown component

Place before the `TopBar` component. Renders from the bell icon in the top-right header:

```jsx
const NewsDropdown = () => {
  const [open, setOpen] = useState(false);
  const [news, setNews] = useState(null); // null=not loaded, []=failed
  const [hidden, setHidden] = useState(false);
  const ref = useRef(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  // Fetch news on first open
  useEffect(() => {
    if (!open || news !== null) return;
    fetch('/api/news', { credentials: 'include' })
      .then(r => r.json().catch(() => ({bullets:[], error: 'HTTP ' + r.status})))
      .then(d => {
        if (d && d.bullets && d.bullets.length > 0) {
          setNews(d.bullets);
        } else {
          setNews([]);
          setHidden(true);  // hide notification dot
        }
      })
      .catch(() => { setNews([]); setHidden(true); });
  }, [open]);

  const LCE_ORANGE = '#FF5F00';
  const LCE_ORANGE_LIGHT = '#FFF3E8';
  const LCE_ORANGE_MED = '#FFD6AD';

  return (
    <div ref={ref} style={{ position:'relative', display:'flex' }}>
      <button className="hb-iconbtn" onClick={() => setOpen(o => !o)} style={{ position:'relative', background:'transparent', border:0, cursor:'pointer', display:'flex', padding:4 }}>
        <Icon name="bell" size={19} color={open ? '#fff' : 'var(--db-navy-300)'} />
        {!hidden && <span style={{ position:'absolute', top:1, right:1, width:7, height:7, borderRadius:999, background: LCE_ORANGE, border:'1.5px solid var(--db-navy-800)' }} />}
      </button>

      {open && (
        <div style={{
          position:'absolute', top:'calc(100% + 10px)', right:0, width:360,
          background:'#fff', borderRadius:14, boxShadow:'var(--shadow-xl)',
          border:`1.5px solid ${LCE_ORANGE_MED}`, overflow:'hidden', zIndex:100,
          animation:'hb-rise var(--dur-base) var(--ease-out)',
        }}>
          <div style={{ height:4, background: LCE_ORANGE }} />
          <div style={{ padding:'16px 20px' }}>
            <div style={{ display:'flex', alignItems:'center', marginBottom:14 }}>
              <span style={{ fontSize:13, fontWeight:600, color:'var(--db-navy-800)' }}>Company News</span>
              <span style={{ marginLeft:'auto', fontSize:10.5, color:'var(--db-gray-text)' }}>via MCP web search</span>
            </div>

            {news === null ? (
              <div style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 0' }}>
                <div style={{ width:16, height:16, border:`2.5px solid ${LCE_ORANGE_MED}`, borderTop:`2.5px solid ${LCE_ORANGE}`, borderRadius:'50%', animation:'hb-spin 0.8s linear infinite' }} />
                <span style={{ fontSize:13, color:'var(--db-navy-600)' }}>Fetching latest news...</span>
              </div>
            ) : news.length === 0 ? (
              <div style={{ fontSize:13, color:'var(--db-gray-text)', padding:'10px 0' }}>No news available right now.</div>
            ) : (
              <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
                {news.map((b, i) => (
                  <div key={i} style={{ display:'flex', alignItems:'flex-start', gap:10 }}>
                    <div style={{ width:7, height:7, borderRadius:'50%', background: LCE_ORANGE, marginTop:5, flexShrink:0 }} />
                    <div style={{ flex:1 }}>
                      <div style={{ fontSize:13, fontWeight:600, color:'var(--db-navy-800)', lineHeight:1.35 }}>{b.headline}</div>
                      <div style={{ fontSize:12, color:'var(--db-navy-600)', marginTop:2, lineHeight:1.4 }}>
                        {b.summary}
                        {b.url && b.url !== '#' && (
                          <a href={b.url} target="_blank" rel="noopener noreferrer"
                             style={{ marginLeft:6, fontSize:11, color: LCE_ORANGE, fontWeight:500, textDecoration:'none' }}>Source ↗</a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
```

### TopBar — replace bell button with `<NewsDropdown />`

In the TopBar component, replace the static bell `<button>` with:

```jsx
<NewsDropdown />
```

### Homebase.html — add CSS keyframe

Add to the `<style>` block:

```css
@keyframes hb-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
```

---

## Permissions Required

- No new `app.yaml` resources or `user_api_scopes` needed
- MCP connection permissions are managed by Admin (SP access to `web_search_mcp` is pre-configured)
- Existing SQL warehouse resource handles `ai_query`

---

## From-Scratch Checklist

1. Add `databricks-mcp` + `mcp` to `requirements.txt`
2. Add the inline `/api/news` endpoint in `app.py` (not a separate router file)
3. Use `DatabricksMCPClient(url, workspace_client=w)` with the SP's client
4. Use direct `get_warehouse_client().cursor()` for `ai_query` — never `fetch_all` with raw user text containing URLs
5. Always strip markdown fences from `ai_query` output before JSON parsing
6. Add the `NewsDropdown` component + `hb-spin` CSS keyframe
7. Use real Unicode chars in JSX source, not `\uXXXX` escapes
8. Deploy via `databricks apps deploy <app-name> --source-code-path <path>`
