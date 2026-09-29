# Lines for the agents' instructions

Put the lines between the two `---` lines below (not the `---` lines
themselves) into the instructions that every session loads by itself. Replace the `<...>`
parts with your own.

For Claude Code, that is the user's `~/.claude/CLAUDE.md`:

- `@path` is an import. Claude Code does not import a path inside a code
  block or a code span.
- An import in a project's `CLAUDE.md` that points outside the project
  stays off until someone approves the external-imports dialog.
- Cowork sessions skip imports outside the working directory even from
  `~/.claude/CLAUDE.md`. There, paste the card's text instead.

After the change, run `/context` in a new session and check that RULES.md
is listed.

Import the card from a checkout of the release tag, not from a working
copy you edit. That way the rules change only when you move the checkout:

```
git clone https://github.com/kewl-ua/rada-anchor ~/.rada/src
git -C ~/.rada/src worktree add --detach ~/.rada/v2 v2
```

---

## Handoff between sessions: rada-anchor/2

Agents work on <project> in turns and hand work over through
`<absolute path of the repository>/HANDOFF.md`. The rules card:

@~/.rada/v2/RULES.md

The start command, run in the same turn as reading HANDOFF.md:
`~/.rada/v2/tools/rada-status <absolute path of the repository>; date -Iminutes; <service checks, if any>`

The user's phrases are commands:
- "<start phrase>", "<another>", or any greeting at the start: start a
  shift. A session that stayed open while the user was away starts a shift
  too, because another agent may have worked in between.
- "<end phrase>", or the user saying they are leaving: end the shift, then
  confirm in one line.

Only the session the user talks to directly runs the protocol (RA-8). The
project guide: `<path>`.

---

Agents other than Claude Code: paste the text of RULES.md in place of the
import line, and keep that copy at the version your `HANDOFF.md` names.
