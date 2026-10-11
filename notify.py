#!/usr/bin/env python3
"""Event hook: nudge the user when an agent becomes blocked (waiting for input).

Herdr runs this on every `pane_agent_status_changed` event with the event JSON
in HERDR_PLUGIN_EVENT_JSON. We only act when the new status is `blocked`.
A small debounce in HERDR_PLUGIN_STATE_DIR avoids repeat toasts for flapping.
"""

import json
import os
import subprocess
import time

HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")
STATE_DIR = os.environ.get("HERDR_PLUGIN_STATE_DIR", "/tmp")
DEBOUNCE_S = 300  # don't re-notify the same pane within 5 minutes


def find_status(node):
    """Recursively find (agent_status, info) in the event JSON, any wrapping."""
    if isinstance(node, dict):
        if "agent_status" in node:
            return node.get("agent_status"), node
        for v in node.values():
            hit = find_status(v)
            if hit[0] is not None:
                return hit
    elif isinstance(node, list):
        for v in node:
            hit = find_status(v)
            if hit[0] is not None:
                return hit
    return None, {}


def debounced(pane_id):
    """True if we already notified for this pane recently."""
    if not pane_id:
        return False
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        path = os.path.join(STATE_DIR, "agent-watch-notified.json")
        try:
            with open(path) as f:
                seen = json.load(f)
        except (OSError, ValueError):
            seen = {}
        now = time.time()
        seen = {k: v for k, v in seen.items() if now - v < DEBOUNCE_S}
        if pane_id in seen:
            return True
        seen[pane_id] = now
        with open(path, "w") as f:
            json.dump(seen, f)
        return False
    except OSError:
        return False  # state dir unavailable: notify anyway


def main():
    raw = os.environ.get("HERDR_PLUGIN_EVENT_JSON", "")
    if not raw:
        return
    try:
        event = json.loads(raw)
    except ValueError:
        return

    status, info = find_status(event)
    if status != "blocked":
        return

    pane_id = info.get("pane_id", "?")
    if debounced(pane_id):
        return

    name = info.get("display_agent") or info.get("agent") or "Agent"
    detail = info.get("title") or ""
    body = f"{name} ({pane_id}) needs your input"
    if detail:
        body += f": {detail}"

    try:
        subprocess.run(
            [HERDR, "notification", "show", "Agent waiting for you",
             "--body", body, "--sound", "request"],
            capture_output=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


if __name__ == "__main__":
    main()
