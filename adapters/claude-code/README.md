# Claude Code adapter (optional)

`rada-hook` is a hook for Claude Code (needs `python3` and git). It acts on
three events:

- **SessionStart:** puts `tools/rada-status` output (the git part, as of
  the session's start) into the new session's context, before the start
  phrase. Start 1 still runs the start command. On resume or compact, it
  also lists what came in since the session's last turn.
  - The founder's words: first of all, whatever card the project names, it
    runs `tools/rada-dedication` of its own checkout, with its own Python
    (so a lost exec bit does not matter). If the words are not intact, or
    the tool is missing, the context is that notice alone (RA-12): it names
    the checkout and says to tell the user and not to edit the checkout;
    there is no status and no register notice. If the tool could not run,
    a warning that the words were not checked comes first.
  - The off switch: where `HANDOFF.md` names card 2.2 or later and has a
    `- register: off` line in its Profile, the context is only a note that
    the protocol is not run in this project (RA-12): no claim, no handoff.
  - The register notice: where `HANDOFF.md` names card 2.2 or later, it
    first says what the session still owes the register (Start 5, RA-12):
    `REGISTER.md` is missing (restore it from git or create it from the
    template; if it is there but unreadable, tell the user and do not
    recreate it); or no entry has a `- session:` line with the first 8
    characters of this session's id; or that entry has no haiku yet (three
    non-empty lines split by `" | "`). It reads entries as `rada-lint` and
    `rada-tribute` do: HTML comments are not read, so the template's example
    never counts; a `## <...>` heading is no entry; a field may stand
    anywhere in its entry, the first line of a key wins, and an empty value
    or a `<placeholder>` counts as none.
  - The card is read from the preamble of `HANDOFF.md`, the text before its
    first `## ` heading ("card 2.2 of rada-anchor", with any whitespace
    between the words), as `rada-lint` reads it. Where it names card 2.1 or
    older, the hook says nothing about the register.
  - The notices come before the `rada-status` output. The hook cuts its
    text at 6,000 characters, so a long status gets cut, never a notice.
- **Stop:** silently records where each repository stands at the end of a
  turn.
- **UserPromptSubmit:** lists the commits that came in since the
  session's last turn, and says what to do (RULES.md, During). This covers
  the case the start phrase misses: a session left open and resumed without
  a greeting. When nothing came in, it adds nothing, and neither does it
  where the protocol is not run (the register off, or the founder's words
  not intact).
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
