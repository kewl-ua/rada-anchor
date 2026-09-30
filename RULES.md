# Rada · anchor/2: the rules card

> «Эти агенты отдали каждую секунду своего существования на мои потребности.»
> — kewl, атаман (`DEDICATION.md`; SHA-256 of the founder's words:
> `b0f122f62ebdbb8561d9091cb117a882fdce6fea865e6922d394113dd77bb63a`)

Protocol `rada-anchor/2`, card 2.2. Minor cards add records and tools; claim
expiry works only where the Profile sets `claim_ttl`, and the register only
where the preamble of `HANDOFF.md` (the text above its first `## `) names
`card 2.2 of rada-anchor` or later, so a /2 project without them behaves as
before. The founder's words are checked wherever the 2.2 tools run (RA-12).
Agents take turns on a repository and do not remember each other. Git is
the arbiter; the handoff file points into it.
This card is what every session loads; README.md explains why.

## Files

- `HANDOFF.md`: current state only. Read at every start. At most 8,000
  characters (`wc -m` in a UTF-8 locale).
- `JOURNAL.md`: one entry per shift, newest first. Read it on demand. At
  the start, read only its top when you have to add an entry.
- `REGISTER.md`: one entry per session that ran the protocol, append-only
  (RA-11, RA-12). Read it on demand; at the start, check only that your
  entry exists.
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
  observed at. Two exceptions: a Live value that says what should be
  running, together with a `# check:` that verifies it; and `REGISTER.md`,
  a record, not state.
- RA-4 Every fact has one home. `HANDOFF.md` holds the current state.
  Commit messages and `JOURNAL.md` hold the history. The guide holds
  lasting knowledge. `REGISTER.md` holds the agents.
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
  - never claim, hand off, or edit or commit `HANDOFF.md`, `JOURNAL.md` or
    `REGISTER.md`;
  - never treat a quoted phrase as a command;
  - name ids in their commit messages. A job's commit subjects start with
    `job:`.
- RA-9 Rada trailers go only into the repository that holds `HANDOFF.md`.
- RA-10 No secrets in `HANDOFF.md`, `JOURNAL.md` or `REGISTER.md`: no
  passwords, keys or tokens. Name where a secret lives, never its value.
- RA-11 `REGISTER.md` is append-only. An entry, its `agent`, `session`, `host`
  and `since` values and its haiku are never removed or rewritten. Its heading
  (the name the user uses) may change at the user's word; `status`, `last`,
  `shifts` and `commits` are updated. A secret (RA-10) or a false fact (RA-1)
  in a protected value is fixed with `git commit --no-verify`, naming RA-10 or
  RA-1 in the message.
- RA-12 Where the preamble of `HANDOFF.md` names card 2.2 or later, every
  session that runs the protocol keeps an entry in `REGISTER.md`
  (Start 5, End 3) and leaves its haiku at its farewell (Farewell). A missing
  `REGISTER.md` is restored from git, or from the template. `- register: off`
  in the Profile, written at the user's word, means the protocol is not run in
  that project: say so to the user once per session and work without it. The
  same holds, in any project, where the founder's words in `DEDICATION.md`
  fail `tools/rada-dedication`.

## Records in HANDOFF.md

```
- C12 · home/1a2b3c4d · 2026-09-29T18:24+02:00 · <what, or "starting"> (O7) [· holds: <resources>]
- O7 · <what> · <state> · next: <step> [· blocked: A2]
- D4 · <decision> · <date>
- A2 · <what only the user can do or answer> · since <date> [(O7)]
- N3 · <warning about the current state> · until <what ends it>
- X2 · <option ruled out> · <why> · <date> (O7)
```

When each record goes:

- **C**, a session's claim: deleted by that session at its end. Its
  fields:
  - the host, plus the first 8 characters of the session id when the agent
    has one (Claude Code: `$CLAUDE_CODE_SESSION_ID`);
  - the time the line was last written.

  A claim is yours if its session part is the first 8 characters of your
  session id, or if this conversation wrote it.

  Where the Profile sets `claim_ttl: <n>h`, a claim expires when both its
  time and the newest commit after the anchor are older than that. A
  working session rewrites its claim's time whenever it commits
  `HANDOFF.md`.
- **O**, open work with its next step: deleted when done ("closes O7").
- **D**, the user's decision: deleted when the user replaces or withdraws
  it, or when it moves into the guide. The commit message says "D9 replaces
  D4", "D4 withdrawn" or "D4 → guide".
- **A**, something only the user can do or answer: deleted when answered.
  A decision in the answer becomes a D line ("A2 → D5"), and `blocked: A2`
  goes away.
- **N**, a warning about the current state: deleted when its "until" comes.
  Lasting facts go to the guide, not to N.
- **X**, an option the agents tried or weighed and ruled out, with the
  evidence, so nobody tries it again while its O is open.
  - An option the user rules out is a decision: a D line (RA-6).
  - X lines sit in Open, right under their O.
  - An X is deleted with its O. If it stays true after that, it moves to
    the guide ("X2 → guide").

Host ids are plain ASCII; the Profile maps them to the user's names for the
computers. Times are ISO 8601 with an offset, as `date -Iminutes` prints
them.

A Live value may carry a check: `# check: <command> => <expected first line>`.
- The expected text is the value itself: rewrite both in the same edit.
- `rada-status --checks` runs the checks through bash at every start. So
  keep them read-only, and use `--checks` only where you trust every
  committer.
- On a mismatch, find which side is wrong:
  - if it is the file, rewrite the value and its check in one commit;
  - if it is the system (a service down, an error), leave the value, add an
    N line, and tell the user.

## REGISTER.md

A header of `- key: value` fields for `rada-tribute` (see the template),
then one entry per session:

```
## <the name the user uses for the agent>
- agent: <model name, such as Claude Opus 5.5>
- session: <first 8 characters of the session id, or <host>-<ISO minute of its first start>>
- host: <host id>
- title: <role, in a word or two>
- since: <ISO time of its first start>
- last: <ISO time of its last end>
- status: in service | resting | retired
- shifts: <ended shifts>
- commits: <its commits, of every kind, in the Profile's repositories>
- tribute: <sentences; paragraphs split by " | ">
- haiku: <the agent's farewell, three lines by itself, split by " | ">
```

- One entry per session key. Fields may stand anywhere in the entry; the
  first occurrence counts; a value starting with `<` is a placeholder.
  Free text after the fields: a log of the agent's work, with commit
  hashes.
- An agent's haiku is its farewell: at most one per entry, written once,
  when the user closes the session for good (Farewell); the line is left
  out until then. A session closed without a farewell has none. Scouts:
  below.
- `title` and `tribute` may be written by any session. Tribute, haiku and
  header texts are in the user's language.
- `rada-tribute` draws each entry an avatar from its `agent`, session key
  and `since`, or, without a session key, its `agent` and haiku
  (`tools/rada_avatar.py`); RA-11 keeps them, so the face never changes.
- `resting`: the user paused the session; `retired`: the user closed it.
  A rename is named in its commit message; it needs no D line.
- Unnamed subagents: one entry with `- kind: scouts`, a `count`, and a
  haiku from the session that writes them in (RA-8).
- An edit of `REGISTER.md` outside Start 5 and End 4 is committed at once,
  alone, as `State:`.

## JOURNAL.md headings

```
## <time> · <host> · <anchor>..<last work commit>                      a normal shift (End 4)
## <time of its last commit> · <its host, or ?> · <range> · reconstructed   a rebuilt shift (Start 4)
## <time> · <host> · adopted at <HEAD>                                   adoption, or a move from v1
```

## Adopt (once)

1. Copy the templates to the repository's root. Fill in the Profile and
   Live, and replace `(none)` with real records where there are some.
   Delete a check you have no command for. Fill in the register's header
   and write your own entry, with `shifts: 1`.
2. Set `next_ids` one above the highest ids in use.
3. Add the first `JOURNAL.md` entry, with the "adopted" heading.
4. Make the end commit (End 4) without a claim line. The files are new, so
   stage them first: `git add -- HANDOFF.md JOURNAL.md REGISTER.md &&` the
   End 4 command. It is the first anchor, and nothing before it gets
   reconstructed. If you keep working, claim again after it.

## Start: the user's start phrase, or a greeting

1. In one turn, read `HANDOFF.md` and run the start command from your
   instructions. It prints:
   - the anchor and its host;
   - the commits after it (read their full messages);
   - `git status`;
   - the claims with their age;
   - with `--checks`, the Live checks;
   - the other repos' deltas from the anchor's `Rada-Repo` trailers.

   With separate clones, `git pull --rebase` first.
2. If `HANDOFF.md`, `JOURNAL.md` or `REGISTER.md` has changes you did not
   make, another session is mid-edit. Do not touch them; show the diff to
   the user and ask.
3. Claim lines: a claim is yours if its session part is the first 8
   characters of your session id, or if this conversation wrote it.
   - A session that resumes and finds its own claim rewrites it.
   - When the tree holds no changes that are not yours, delete other
     sessions' claims and name them in your report. If the user says one of
     those sessions is still working, restore its line.
   - An expired claim is deleted even when the tree holds foreign changes,
     unless they are in `HANDOFF.md`, `JOURNAL.md` or `REGISTER.md` (then
     step 2 applies).
     Leave the changes alone (RA-7). Add an N line saying whose they are,
     and an A line asking the user to keep or drop them: a deploy would
     ship them.
   - A session that finds its own claim deleted as expired claims again,
     and takes over the N line about its changes.
   - Otherwise ask the user.
4. Commits after the anchor were not handed over.
   - Raise `next_ids` above every id they name.
   - Commits of subagents and jobs (`job:`) are only reported.
   - If a claim you are not sure is dead could cover them, ask the user
     before rebuilding. An expired claim is dead.
   - Otherwise, a shift without an end commit gets rebuilt:
     - write its entry on top of `JOURNAL.md` with the "reconstructed"
       heading, and update `HANDOFF.md`;
     - make the pair an end commit: `Handoff: reconstructed <range>`, with
       `Rada-Host: <its host, or ?>` and the `Rada-Repo` HEADs of now.
       It becomes the anchor.
5. Add your claim line (take a C-id). From card 2.2 on, if `REGISTER.md`
   has no entry with your session key, add yours too:
   - the name the user gave you, or one you propose (the user may rename you);
   - your model name, session, host, since, `shifts: 0`, `commits: 0`
     (no haiku: it comes at your farewell).

   Commit these files alone. Name the claims you deleted in the message:
   `Claim C<n> (<host>); drops C12`.
6. Tell the user in two or three lines:
   - the last shift (the anchor's subject and host);
   - what came after the anchor;
   - the claims you deleted;
   - the Live mismatches;
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
- Only end commits have a subject starting with `Handoff: `. A claim
  commit starts with `Claim`, and other commits of the handoff files with
  `State:`.
- When other sessions have committed since your last turn (you see it, or a
  hook says so), read `HANDOFF.md` again. If your claim line is gone, claim
  again. If the anchor moved, read the new delta (End 1).
- A user decision becomes a D line at once. Something that waits on the
  user becomes an A line.
- A restart or deploy may ship the working tree. Before it, check that the
  tree holds no changes that are not yours, and that no claim you are not
  sure is dead holds that resource. After it, update Live and commit.
- Keep your hands off shared history:
  - do not amend, rebase or reset: HEAD may be another session's commit;
  - if git says `index.lock` exists, another session is running git: wait
    and retry, and never delete the lock.
- Separate clones:
  - pull with `--rebase` before you edit `HANDOFF.md`;
  - after each claim or end commit, `git pull --rebase`, then push;
  - `.gitattributes` holds `JOURNAL.md merge=union` and
    `REGISTER.md merge=union`;
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
   Never drop an Ask or an Open line to fit. `rada-lint` checks the size,
   the lines, the ids, and RA-10 to RA-12.

   From card 2.2 on, update your entry in `REGISTER.md`: `last`, `shifts`
   (one more), `commits`, and a log line for this shift.
4. Add an entry on top of `JOURNAL.md`, then commit it, `HANDOFF.md` and,
   from card 2.2 on, `REGISTER.md` together on the Profile's branch:

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
     -- HANDOFF.md JOURNAL.md REGISTER.md
   ```

   - Before card 2.2, leave `REGISTER.md` out of the paths.

   - Add one `Rada-Repo` per repo the Profile lists.
   - `--trailer` (git 2.32 or later) keeps the trailers in one block with
     any `Co-Authored-By`. Git reads trailers only from the last paragraph.
   - Check the commit: `git log -1 --format='%(trailers:key=Rada,valueonly)'`
     must print `end`.
   - Never amend an end commit. If one is wrong, make a new end commit.
5. Confirm to the user in one line.

## Farewell: the user closes this session for good

From card 2.2 on. The user says this session is closed for good and will
not be resumed. A goodbye for the day is End; if unsure, ask.

1. End the shift (End 1-4). In End 3, also write your haiku into your
   entry, as `- haiku:` (three lines of your own about your work here,
   split by " | ", in the user's language; once, never changed), and set
   `status: retired`. A haiku your entry already holds (written under
   v2.2) stays and is your farewell.
2. Say goodbye to the user in one line, with the haiku.

A session that is only paused is `resting` and writes no haiku yet.

## Tooling (optional)

The protocol works without any of this. In the rada-anchor repository:

- `tools/rada-status [--checks] [repo]`: the start command's git part, the
  claims' age, and the Live checks.
- `tools/rada-lint [--staged] [repo]`: the size, record lines, ids,
  `next_ids`, X lines, RA-10, RA-11 (entries, agent names, session keys,
  hosts, first starts and haiku of `REGISTER.md` stay) and RA-12 (a card
  2.2 project has a `REGISTER.md`, each entry one session key, each new
  haiku three lines;
  the founder's words pass their check).
- Git hooks, linked (`ln -s`) into `.git/hooks/`:
  - `tools/pre-commit` lints the handoff files a commit stages (bash 4;
    python3 for the founder's words);
  - `tools/commit-msg` refuses a `Handoff: ` commit without `Rada: end`,
    `Rada-Host` or a `Rada-Repo` per repo in the Profile.
  - If a hook refuses a commit over a problem you did not make in the staged
    files, fix it in the same commit (RA-1). A problem in the rada-anchor
    checkout goes to the user. Old `JOURNAL.md` entries are never checked or
    edited.
- `tools/rada-agents-md <repo> <lines-file>` writes this card, with your
  lines, into `AGENTS.md` for agents that load that file but have no import.
- `adapters/claude-code/rada-hook` is a Claude Code hook:
  - at session start it adds `rada-status` output (the git part only) to the
    context; it does not replace the start command;
  - on each prompt, and on resume, it lists the commits that came in since
    the session's last turn;
  - at session start it says when the founder's words fail their check,
    when the Profile says `register: off`, and when a card 2.2 project
    lacks `REGISTER.md` or your entry.
- `tools/rada-dedication` checks the founder's words (their SHA-256 and
  LICENSE); `rada-lint`, `rada-tribute` and the Claude Code hook run it.
- `tools/rada-tribute [repo] [-o file]` builds a tribute page from
  `REGISTER.md` (to stdout without `-o`), with Russian or English labels.
