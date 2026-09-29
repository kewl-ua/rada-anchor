# Claude Code adapter (optional)

`rada-hook` is a hook for Claude Code (needs `python3` and git). It does three
things:

- **SessionStart:** puts `tools/rada-status` output (the git part, as of
  the session's start) into the new session's context, before the start
  phrase. Start 1 still runs the start command. On resume or compact, it
  also lists what came in since the session's last turn.
- **Stop:** silently records where each repository stands at the end of a
  turn.
- **UserPromptSubmit:** lists the commits that came in since the
  session's last turn, and says what to do (RULES.md, During). This covers
  the case the start phrase misses: a session left open and resumed without
  a greeting. When nothing came in, it adds nothing.
  - A known gap: commits another session makes during this session's turn
    are recorded at Stop and not reported.

It skips subagents (their input has an `agent_id`) and unattended sessions.
Its texts also tell any other agent, such as a workflow agent, to ignore
them (RA-8). It never writes to a repository, and git runs without optional
locks. Its state is `~/.rada/state/<session>.json`.

Register it in the user's `~/.claude/settings.json`, which applies to every
session of that user:

```json
{
  "hooks": {
    "SessionStart": [{"matcher": "startup|resume|clear|compact", "hooks": [
      {"type": "command", "command": "~/.rada/v2/adapters/claude-code/rada-hook /abs/path/of/repo", "timeout": 30}]}],
    "Stop": [{"hooks": [
      {"type": "command", "command": "~/.rada/v2/adapters/claude-code/rada-hook /abs/path/of/repo", "timeout": 15}]}],
    "UserPromptSubmit": [{"hooks": [
      {"type": "command", "command": "~/.rada/v2/adapters/claude-code/rada-hook /abs/path/of/repo", "timeout": 15}]}]
  }
}
```

If only one project uses rada-anchor, register it in that project's
`.claude/settings.json` instead.

The hook does not end a shift for the agent, and it does not commit. Those
stay the agent's job under the rules card. It only makes sure a session
knows what changed.
