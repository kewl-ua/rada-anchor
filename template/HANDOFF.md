# Handoff journal

Several AI agents work on this repository, in turns, and none of them
remembers the others' sessions. **This file is the only channel between
them**, together with git. It follows the protocol «Рада · anchor/1»
(https://github.com/kewl-ua/rada-anchor). Project guide: <CLAUDE.md or
another file: layout, how to build, test and deploy, rules>.

## Header (machine-readable; update on every handoff)

```yaml
protocol: rada-anchor/1       # "Рада · anchor/1"; a writer who changes the rules bumps the version and says what changed in its journal entry
state_as_of: YYYY-MM-DD HH:MM TZ
anchor_commit: 0000000        # everything after it is newer than this file: git log --oneline 0000000..HEAD
live:                         # what runs or is deployed, and from which commit
  app: <how to check it>
tests: <N passed>
claims: []                    # ids from "In progress"
open: []
notes: []
decisions: []
```

Ids are stable: refer to them in journal entries and commits ("closes O1").
Never reuse an id; mark done items `~~O1~~ done <date> <commit>` instead of
deleting them from Open, so later readers can trace them.

## Protocol «Рада · anchor/1»

Two halves. **«Рада»** is the human one: the user's two phrases (0) and the
user's decisions (D-ids), like a Cossack council whose word stands.
**`anchor/1`** is the machines': the anchor commit, the header, the stable
ids, and the entry template. The next reader diffs from the anchor and
trusts nothing it cannot check in git.

### 0. The user's side

The user says two things, and they trigger the protocol:
- <start phrase, e.g. "I'm at home" / "I'm at work", or a greeting>: start a
  shift (1).
- <end phrase, e.g. "wrap up, write the handoff">: end the shift (4).

A session that stayed open while the user worked elsewhere starts a shift
again when the user comes back.

### 1. Start of a shift

1. Read the Header, then "In progress", "Notes for the next instance",
   "Current state", "Open", "Decisions", and the journal entries since your
   last shift (or the last three if this is your first).
2. See what happened in git:
   - `git log --oneline <anchor_commit>..HEAD`: commits newer than this
     file. Anything here that the journal does not mention was not handed
     over: read those commit messages.
   - `git status --short` for uncommitted work.
3. Uncommitted changes you did not make may belong to an agent that is still
   running. Do not edit, stash, reset or commit them. Ask the user whether
   that session is still active.
4. Check what runs (services, deployments); a deploy may be missing: compare
   the journal's "Deployed" lines with git.
5. Tell the user in two or three lines what you found (the last entry, the
   in-progress claims, your notes) before starting new work.

### 2. Claim what you work on

Add a line to "In progress" before you start something bigger than a quick
fix, and commit it:

    - C<n>: <what> (O<k> if it is an Open item) — <machine or place>, since <YYYY-MM-DD HH:MM>

Another agent that sees the claim leaves that area alone, or asks the user.
Remove your line when done. A claim older than a day with no commits is
stale: ask the user, then take it over.

### 3. During the shift

- Commit early and often, in small commits. The commit message is the
  detailed log; the journal only summarizes.
- Before deploying, restarting services or migrating data, look at
  "In progress" and `git status`: another agent may be in the middle of
  something.
- Decisions the user makes go to "Decisions", so nobody asks again.
- Do not use your private memory as the only record: what another agent
  needs goes here.

### 4. End of a shift

Do this before you stop, or when the user says the end phrase:

1. Commit or deliberately leave your work. If you leave uncommitted changes,
   list the files and why in your journal entry.
2. Update the Header (`anchor_commit` = `git rev-parse --short HEAD` before
   the handoff commit; live versions; tests), "Current state", "Open",
   "Decisions", and your lines in "In progress".
3. Add a journal entry **on top** of the Journal, using this template:

       ### YYYY-MM-DD HH:MM — <machine or place>, <model>
       - Done: <what and why, with commit hashes>
       - Verified: <tests: N passed; what was checked by hand>
       - Deployed: <yes / no / partly: what runs and what is only committed>
       - Ids: <opened O5 / closed O1 / added D6 / handled N1>
       - Half-done: <what, where, the next step>
       - For the user: <what the user should do or answer, if anything>

4. Commit this file: `git commit -m "Handoff: <one line>"`.

### 5. Notes to the next instance

Write a line under "Notes for the next instance" to pass on something that
does not fit the journal: a warning, a request, a thing to check. The agent
that handles a note deletes it (and says so in its journal entry).

### 6. If two sessions run at the same time

- Git is the arbiter. Commit only your own files: `git add <paths>`, never
  `git add -A` or `git commit -a` while someone else may have changes.
- If `git status` shows changes in files you are editing, stop and ask the
  user.
- A service restart can interrupt the other agent's check. Say it in a note
  if you do one.

## In progress

(none)

## Notes for the next instance

(none)

## Current state (YYYY-MM-DD)

- What runs, what the project can do now, what is known to be broken.

## Open

(none)

## Decisions (made by the user; don't ask again)

(none)

## Journal

### YYYY-MM-DD HH:MM — <machine or place>, <model>
- Done: adopted the protocol «Рада · anchor/1»: this file.
- Verified: —
- Deployed: no
- Ids: —
- Half-done: none
- For the user: the start and end phrases are in the agents' instructions.
