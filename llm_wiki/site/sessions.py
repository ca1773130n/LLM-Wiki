"""Static-site renderers for inbound harness session history."""

from __future__ import annotations

import html
import json
from collections import Counter
from typing import Dict, Iterable, List

from ..harness_sessions import HarnessSession
from .search import token_set


def _esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _subagents(session: HarnessSession) -> List[Dict[str, object]]:
    items = session.metadata.get("subagents") if isinstance(session.metadata, dict) else []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _subagent_count_label(session: HarnessSession) -> str:
    count = len(_subagents(session))
    if count == 0:
        return "—"
    return f"{count} subagent" + ("" if count == 1 else "s")


def session_search_entries(sessions: Iterable[HarnessSession]) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    for session in sessions:
        text = " ".join([
            session.title,
            session.summary,
            session.project_name,
            session.harness,
            session.agent_label,
            session.model,
            " ".join(session.tools_used),
            " ".join(session.files_touched),
            " ".join(session.decisions),
        ])
        tokens = token_set(text)
        entries.append({
            "id": session.id,
            "title": session.title or session.slug,
            "kind": "session",
            "type": "session",
            "href": session.href,
            "summary": session.summary or session.redacted_preview,
            "source_path": session.raw_transcript_path,
            "tokens": tokens,
            "len": len(tokens),
            "created_ts": None,
            "project": session.project_name,
            "model": session.model,
            "harness": session.harness,
            "date": session.date,
            "tools": list(session.tools_used),
        })
    return sorted(entries, key=lambda e: (str(e["date"]), str(e["title"])), reverse=True)


def render_sessions_index(site_title: str, sessions: List[HarnessSession]) -> str:
    rows = []
    for session in sorted(sessions, key=lambda s: (s.started_at or "", s.title), reverse=True):
        rows.append(
            "<tr>"
            f"<td><a href='{_esc(session.safe_project)}/{_esc(session.filename)}.html'>{_esc(session.title or session.slug)}</a></td>"
            f"<td>{_esc(session.agent_label or session.harness)}</td>"
            f"<td>{_esc(session.project_name)}</td>"
            f"<td>{_esc(session.date)}</td>"
            f"<td><code>{_esc(session.model or 'unknown')}</code></td>"
            f"<td>{session.message_count}</td>"
            f"<td>{session.tool_call_count}</td>"
            f"<td>{_esc(_subagent_count_label(session))}</td>"
            "</tr>"
        )
    body = "".join(rows) or "<tr><td colspan='8'>No harness sessions ingested yet.</td></tr>"
    tool_counts = Counter(tool for session in sessions for tool in session.tools_used)
    stats = (
        f"{len(sessions)} sessions total"
        + (f" · tools: {', '.join(f'{k} {v}' for k, v in tool_counts.most_common(5))}" if tool_counts else "")
    )
    return _page(
        title=f"Sessions — {site_title}",
        depth=1,
        body=f"""
<main id="main-content" class="page sessions-page">
  <p><a href="../index.html">← Home</a></p>
  <section class="panel">
    <h1>All sessions</h1>
    <p class="lead">{_esc(stats)}</p>
    <p class="muted">Inbound Claude Code, Codex, and other harness histories compiled as project memory.</p>
  </section>
  <section class="panel">
    <table>
      <thead><tr><th>Session</th><th>Agent</th><th>Project</th><th>Date</th><th>Model</th><th>Msgs</th><th>Tools</th><th>Subagents</th></tr></thead>
      <tbody>{body}</tbody>
    </table>
  </section>
</main>
""",
    )


def _render_subagent_tree(session: HarnessSession) -> str:
    children = _subagents(session)
    if not children:
        return "<section class='panel'><h2>Subagent sessions</h2><p class='muted'>No subagent transcripts attached.</p></section>"
    rows = []
    for child in children:
        files = child.get("files_touched") if isinstance(child.get("files_touched"), list) else []
        commands = child.get("commands_run") if isinstance(child.get("commands_run"), list) else []
        files_html = "".join(f"<li><code>{_esc(item)}</code></li>" for item in files[:12]) or "<li class='muted'>No files recorded.</li>"
        commands_html = "".join(f"<li><code>{_esc(item)}</code></li>" for item in commands[:8]) or "<li class='muted'>No commands recorded.</li>"
        rows.append(
            "<li class='subagent-node'>"
            f"<h3>{_esc(child.get('title') or child.get('id') or 'Subagent session')}</h3>"
            f"<p class='muted'>{_esc(child.get('started_at') or 'unknown time')} · "
            f"{_esc(child.get('message_count') or 0)} msgs · {_esc(child.get('tool_call_count') or 0)} tools</p>"
            f"<p>{_esc(child.get('summary') or 'No summary yet.')}</p>"
            f"<details><summary>Files and commands</summary><h4>Files touched</h4><ul>{files_html}</ul><h4>Commands run</h4><ul>{commands_html}</ul></details>"
            "</li>"
        )
    return (
        "<section class='panel subagent-tree'>"
        f"<details><summary>Subagent sessions ({len(children)})</summary>"
        "<p class='muted'>Child agent transcripts are hidden by default so the top-level session list stays focused.</p>"
        f"<ul>{''.join(rows)}</ul>"
        "</details></section>"
    )


def render_session_detail(site_title: str, session: HarnessSession) -> str:
    def list_items(items: List[str], code: bool = False) -> str:
        if not items:
            return "<p class='muted'>None recorded.</p>"
        if code:
            return "<ul>" + "".join(f"<li><code>{_esc(item)}</code></li>" for item in items) + "</ul>"
        return "<ul>" + "".join(f"<li>{_esc(item)}</li>" for item in items) + "</ul>"

    metadata = {
        "id": session.id,
        "kind": "session",
        "project": session.project_name,
        "harness": session.harness,
        "model": session.model,
        "date": session.date,
    }
    return _page(
        title=f"Session: {session.title or session.slug} — {site_title}",
        depth=2,
        body=f"""
<main id="main-content" class="page session-detail">
  <p><a href="../index.html">← All sessions</a></p>
  <script type="application/json" id="llmwiki-metadata">{_esc(json.dumps(metadata, ensure_ascii=False, sort_keys=True))}</script>
  <section class="panel">
    <p class="eyebrow">{_esc(session.agent_label or session.harness)} · { _esc(session.date) } · { _esc(session.branch or 'unknown branch') }</p>
    <h1>{_esc(session.title or session.slug)}</h1>
    <p class="lead">{_esc(session.summary or session.redacted_preview or 'No summary yet.')}</p>
    <dl class="meta-grid">
      <dt>Project</dt><dd>{_esc(session.project_name)}</dd>
      <dt>Model</dt><dd><code>{_esc(session.model or 'unknown')}</code></dd>
      <dt>Messages</dt><dd>{session.message_count}</dd>
      <dt>Tool calls</dt><dd>{session.tool_call_count}</dd>
      <dt>Tokens</dt><dd>{session.token_total}</dd>
    </dl>
  </section>
  <section class="panel"><h2>Key decisions</h2>{list_items(session.decisions)}</section>
  <section class="panel"><h2>Files touched</h2>{list_items(session.files_touched, code=True)}</section>
  <section class="panel"><h2>Commands run</h2>{list_items(session.commands_run, code=True)}</section>
  <section class="panel"><h2>Tools used</h2>{list_items(session.tools_used)}</section>
  {_render_subagent_tree(session)}
  <section class="panel"><h2>Redacted preview</h2><pre>{_esc(session.redacted_preview)}</pre></section>
</main>
""",
    )


def _page(title: str, body: str, depth: int = 0) -> str:
    prefix = "../" * max(depth, 0)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <link rel="stylesheet" href="{_esc(prefix)}assets/style.css">
</head>
<body>
{body}
</body>
</html>
"""
