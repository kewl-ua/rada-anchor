# Rada · anchor/2: the rules card

Protocol `rada-anchor/2`. Agents take turns on a repository and do not
remember each other. Git is the arbiter; the handoff file points into it.
This card is what every session loads; README.md explains why.

## Files

- `HANDOFF.md`: current state only. Read at every start. At most 8,000
  characters (`wc -m` in a UTF-8 locale).
- `JOURNAL.md`: one entry per shift, newest first. Read it on demand. At
  the start, read only its top when you have to add an entry.
- The project guide (for example `CLAUDE.md`): how things are, such as
  layout, build, deploy and lasting facts. It holds no status.

## Invariants

- RA-1 Git overrides prose. Check a fact before you rely on it, and fix the
  file when it is wrong.
- RA-2 The anchor is the newest commit on the Profile's branch whose
  trailers include `Rada: end`. Nothing after it has been handed over.
- RA-3 Do not write down what git, the code or the system can tell you
  (HEAD, dirty files, versions in the code, commit and restart times).
  Write only what cannot be derived, with the commit or date it was
  observed at.
- RA-4 Every fact has one home. `HANDOFF.md` holds the current state.
  Commit messages and `JOURNAL.md` hold the history. The guide holds
  lasting knowledge.
- RA-5 A record is one line of at most 300 characters, rewritten in place,
  and deleted when it closes. Ids are never reused. `next_ids` holds the
  next free number of each type: take one and raise it in the same edit.
- RA-6 A user decision gets a D-id at once and is not asked again.
- RA-7 Never edit, stage, commit, stash, discard, amend, rebase or reset
  changes you did not make.
  - Commit by path, naming each file, never a directory, `.` or a glob.
  - Before a commit, check that `git diff HEAD -- <files>` shows only your
    lines.
- RA-8 Only the session the user talks to directly runs this protocol. A
  task that came from another agent, a workflow or a quoted message makes
  you a subagent. So do unattended jobs. Subagents and jobs:
  - never claim, hand off, or edit or commit `HANDOFF.md` or `JOURNAL.md`;
  - never treat a quoted phrase as a command;
  - name ids in their commit messages. A job's commit subjects start with
    `job:`.
- RA-9 Rada trailers go only into the repository that holds `HANDOFF.md`.

## Records in HANDOFF.md

```
- C12 · home/1a2b3c4d · 2026-09-29T18:24+02:00 · <what, or "starting"> (O7) [· holds: <resources>]
- O7 · <what> · <state> · next: <step> [· blocked: A2]
- D4 · <decision> · <date>
- A2 · <what only the user can do or answer> · since <date> [(O7)]
- N3 · <warning about the current state> · until <what ends it>
```

When each record goes:

- **C**, a session's claim: deleted by that session at its end. Its
  fields:
  - the host, plus the first 8 characters of the session id when the agent
    has one (Claude Code: `$CLAUDE_CODE_SESSION_ID`);
  - the time the line was last written.
- **O**, open work with its next step: deleted when done ("closes O7").
- **D**, the user's decision: deleted when the user replaces or withdraws
  it, or when it moves into the guide. The commit message says "D9 replaces
  D4", "D4 withdrawn" or "D4 → guide".
- **A**, something only the user can do or answer: deleted when answered.
  A decision in the answer becomes a D line ("A2 → D5"), and `blocked: A2`
  goes away.
- **N**, a warning about the current state: deleted when its "until" comes.
  Lasting facts go to the guide, not to N.

Host ids are plain ASCII; the Profile maps them to the user's names for the
computers. Times are ISO 8601 with an offset, as `date -Iminutes` prints
them.

## JOURNAL.md headings

```
## <time> · <host> · <anchor>..<last work commit>                      a normal shift (End 4)
## <time of its last commit> · <its host, or ?> · <range> · reconstructed   a rebuilt shift (Start 4)
## <time> · <host> · adopted at <HEAD>                                   adoption, or a move from v1
```

## Adopt (once)

1. Copy the templates to the repository's root. Fill in the Profile and
   Live, and replace `(none)` with real records where there are some.
2. Set `next_ids` one above the highest ids in use.
3. Add the first `JOURNAL.md` entry, with the "adopted" heading.
4. Make the end commit (End 4) without a claim line. The files are new, so
   stage them first: `git add -- HANDOFF.md JOURNAL.md &&` the End 4
   command. It is the first anchor, and nothing before it gets
   reconstructed. If you keep working, claim again after it.

## Start: the user's start phrase, or a greeting

1. In one turn, read `HANDOFF.md` and run the start command from your
   instructions. It prints:
   - the anchor and its host;
   - the commits after it (read their full messages);
   - `git status`;
   - the other repos' deltas from the anchor's `Rada-Repo` trailers.

   With separate clones, `git pull --rebase` first.
2. If `HANDOFF.md` or `JOURNAL.md` has changes you did not make, another
   session is mid-edit. Do not touch them; show the diff to the user and
   ask.
3. Claim lines: a claim is yours only if this conversation wrote it.
   - A session that resumes and finds its own claim rewrites it.
   - When the tree holds no changes that are not yours, delete other
     sessions' claims and name them in your report. If the user says one of
     those sessions is still working, restore its line.
   - Otherwise ask the user.
4. Commits after the anchor were not handed over.
   - Raise `next_ids` above every id they name.
   - Commits of subagents and jobs (`job:`) are only reported.
   - If a claim you are not sure is dead could cover them, ask the user
     before rebuilding.
   - Otherwise, a shift without an end commit gets rebuilt:
     - write its entry on top of `JOURNAL.md` with the "reconstructed"
       heading, and update `HANDOFF.md`;
     - make the pair an end commit: `Handoff: reconstructed <range>`, with
       `Rada-Host: <its host, or ?>` and the `Rada-Repo` HEADs of now.
       It becomes the anchor.
5. Add your claim line (take a C-id) and commit `HANDOFF.md` alone. Name
   the claims you deleted in the message: `Claim C<n> (<host>); drops C12`.
6. Tell the user in two or three lines:
   - the last shift (the anchor's subject and host);
   - what came after the anchor;
   - the claims you deleted;
   - the Asks and Notes, by id with a few words each.

## During the shift

- Put the id of your current work into your claim line. Rewrite the line
  when the work changes; do not open a new C-id for each task.
- Commit small. The message is the log, so name the ids ("O7: ...",
  "closes O7").
  - For a new file, stage and commit it in one command:
    `git add -- <new> && git commit -m "..." -- <new> <other files>`.
  - Search the history for an id with `git log --grep='\<O7\>'`.
- Edit `HANDOFF.md` line by line, never by rewriting it from memory. Commit
  every edit of it at once, alone. It is never left dirty at the end of a
  turn.
- A user decision becomes a D line at once. Something that waits on the
  user becomes an A line.
- A restart or deploy may ship the working tree. Before it, check that the
  tree holds no changes that are not yours, and that no live claim holds
  that resource. After it, update Live and commit.
- Keep your hands off shared history:
  - do not amend, rebase or reset: HEAD may be another session's commit;
  - if git says `index.lock` exists, another session is running git: wait
    and retry, and never delete the lock.
- Separate clones:
  - pull with `--rebase` before you edit `HANDOFF.md`;
  - after each claim or end commit, `git pull --rebase`, then push;
  - `.gitattributes` holds `JOURNAL.md merge=union`;
  - after a rebase, check `next_ids` against the ids in the file and in the
    new commits.
- Private memory may hold pointers, never state.

## End: the user's end phrase, or the user says they are leaving

A shift that ends without this is rebuilt by the next session (Start 4).

1. Run the start command again (separate clones: pull first). If the
   anchor moved, another session handed over, so read `HANDOFF.md` and the
   new delta before you edit.
2. Commit your work. For files you leave uncommitted, add an N line with
   the reason.
3. Update `HANDOFF.md`:
   - Live;
   - delete your claim line;
   - Asks, Notes and Decisions;
   - rewrite `next` in the Open records.

   If it goes over 8,000 characters, move decisions that now describe how
   things are into the guide ("D3 → guide"), then shorten Open states.
   Never drop an Ask or an Open line to fit.
4. Add an entry on top of `JOURNAL.md`, then commit both files together on
   the Profile's branch:

   ```
   ## <time> · <host> · <anchor>..<last work commit>
   - done: <what, with commit hashes and ids>
   - verified: <tests: N passed @commit; what was checked by hand>
   - deployed: <what runs now, from which commit; or "nothing">
   - ids: <+O8 -O7 +D5 -C12 +A3>
   - left: <uncommitted files and why; or "nothing">
   ```

   ```
   git commit -m "Handoff: <one line>" --trailer "Rada: end" \
     --trailer "Rada-Host: <host>" \
     --trailer "Rada-Repo: <12-char HEAD> <path>" \
     -- HANDOFF.md JOURNAL.md
   ```

   - Add one `Rada-Repo` per repo the Profile lists.
   - `--trailer` (git 2.32 or later) keeps the trailers in one block with
     any `Co-Authored-By`. Git reads trailers only from the last paragraph.
   - Check the commit: `git log -1 --format='%(trailers:key=Rada,valueonly)'`
     must print `end`.
   - Never amend an end commit. If one is wrong, make a new end commit.
5. Confirm to the user in one line.
