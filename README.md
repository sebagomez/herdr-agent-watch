# Agent Watch — herdr plugin

**A nudge the moment any herdr agent is waiting for you.**

Desktop notification + sound when an agent flips to `blocked`. That's it —
no dashboard, no sidebar changes. It's designed as a companion to
[herdr-radar](https://github.com/hhdebb/herdr-radar), which owns the
always-visible display; this plugin covers the case where you're not looking
at the terminal at all.

## Install

```sh
herdr plugin install sebagomez/herdr-agent-watch
```

Or local, for developing:

```sh
herdr plugin link /path/to/herdr-agent-watch
```

Requires herdr ≥ 0.9.0 and Python 3 (no other dependencies).

## How it works

- `notify.py` is an `[[events]]` hook on herdr's `pane.agent_status_changed`
  event, which carries the new `agent_status` plus pane/workspace/agent info.
- It acts only on transitions to `blocked`, then fires
  `herdr notification show … --sound request`.
- A 5-minute debounce per pane (state in `HERDR_PLUGIN_STATE_DIR`) avoids
  repeat toasts if an agent flaps.

## Files

| File | What |
|---|---|
| `herdr-plugin.toml` | manifest: blocked-event hook |
| `notify.py` | blocked → desktop notification |
