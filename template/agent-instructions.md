# Lines for the agents' instructions

Put this into the instructions every agent loads. For Claude Code: the
user's `~/.claude/CLAUDE.md` (every session of that user) or the project's
`CLAUDE.md` (every session in the repository). Replace the phrases and the
path.

```markdown
## Handoff between sessions

Several agents work on <project> in turns and hand work over through
`<repository>/HANDOFF.md` by the protocol «Рада · anchor/1». Follow its
"Protocol" section:
1. At the start: read it, check git, and tell the user what you found.
2. Claim bigger work under "In progress".
3. Before you stop: add a journal entry using its template and commit.

The user's two phrases (treat them as commands):
- "<start phrase>" (or any greeting at the start): start a shift by the
  protocol; note the machine or place in "In progress" and in your journal
  entry. A session that stayed open while the user was away must also start
  a shift: another agent may have worked in between.
- "<end phrase>": end the shift by the protocol (journal entry, header,
  commit), then confirm in one line.

Also read `<project guide>` before working on the project.
```

In QLadder the phrases were «я дома» / «я на работе» (start) and
«закругляемся, пиши handoff» (end).
