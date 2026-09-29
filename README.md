# Rada · anchor

**rada-anchor** is a repository-native handoff protocol for AI coding
agents that take turns on one repository. A small handoff file keeps the
current state; an anchor commit in git marks what has been handed over.

*Русская версия: [README.ru.md](README.ru.md).*

| | |
|---|---|
| Version | `rada-anchor/2` (v1: tag [`v1`](../../tree/v1)) |
| Origin | devised while building [QLadder](https://qladder.com), a ladder and lobby server for Cossacks 3 |
| Scope | several agents, or one agent in several sessions, on one repository |
| The rules | [RULES.md](RULES.md): the card every session loads |
| Templates | [template/HANDOFF.md](template/HANDOFF.md), [template/JOURNAL.md](template/JOURNAL.md), [template/agent-instructions.md](template/agent-instructions.md) |
| Tooling (optional) | [tools/rada-status](tools/rada-status) |

## Why

QLadder was built by several Claude Code sessions, started from the user's
different computers (home, work), all working on the same server and
repository. None of them remembered what the others did. Chat history stays
in the session that had it, and an agent's private memory is not shared
either.

What every session does share is **the repository**. So the protocol puts
the handoff there: a handoff file with the current state, and the git
history, which it points into.

The protocol is not about QLadder. It works wherever agents take turns on a
repository: different machines, different sessions, different models, or a
person joining in.

## The name

Two halves, as the work has two sides.

- **Rada** is the human half. It is named after the Cossack council whose
  word stands. The user steers the protocol with a start phrase and an end
  phrase. The user's decisions are written down once and not asked again.
- **anchor** is the machines' half: a commit in git that marks where the
  handoff ends. The next reader starts from the anchor and trusts nothing it
  cannot check in git.

## What v2 changes, and why

Version 1 was written for people to read: one file held the rules, the
state, and a journal. After five days of QLadder, measured on its real
`HANDOFF.md` (71 revisions, 7 shifts, 2 computers):

- **The start cost grew with the project's age, not with its open work.**
  - The file was about 33,000 characters (about 9,500 tokens), read in full
    at every start. It grew by about 1,500 tokens a day.
  - An agent needed about 1,000 tokens of it.
  - The rules section (about 1,200 tokens) never changed, yet it was
    re-read 66 times.
  - Closed items took 1,350 tokens, and the journal 3,700.
- **The end-of-shift ritual was the weak point.**
  - 2 of 7 shifts ended without a handoff, and the next agent rebuilt the
    entry from git. Both of those sessions were still alive, only idle.
  - The anchor hash was written by hand and moved only 6 times in 71
    revisions.
  - Other values copied by hand went stale too: test counts, versions,
    dates.
- **Open items turned into diaries.** One item grew to 2,400 characters of
  progress log, with sentences in it that had stopped being true.
- **Claims never collided, but they went stale.** 20 of 57 handoff commits
  were bookkeeping (claims, shift starts).
- **Commits in the project's other repositories were invisible** to the
  anchor.

So v2:

1. **Keeps the rules out of the state file.** The card [RULES.md](RULES.md)
   is loaded with the agents' instructions, pinned to a release tag of this
   repository. For Claude Code, it is imported from `~/.claude/CLAUDE.md`.
2. **Derives the anchor** instead of storing it. The anchor is the newest
   commit with the trailer `Rada: end`. If a shift ends without one, the
   next agent sees the whole shift after the old anchor, which is exactly
   what it has to inspect. It rebuilds the entry, and its commit becomes the
   new anchor.
3. **Keeps the handoff file hot and small.**
   - Every record is one line, rewritten in place, and deleted when closed.
   - The whole file stays within 8,000 characters.
   - History goes to commit messages and `JOURNAL.md`, which nobody reads
     at the start.
4. **Adds Asks**, a list of what waits on the user, which used to get lost
   in the journal.
5. **Records the heads of the other repositories** in the end commit
   (`Rada-Repo` trailers), so the next agent sees their commits too.
6. **Writes down only what cannot be derived**, together with the commit or
   date it was observed at.

On the same QLadder state, the handoff file shrank from about 34,000 to
about 5,000 characters. From then on it grows with open work, not with age.

### What v2 does not add

Before v2, several further proposals were weighed against the QLadder
history, and each was dropped for a reason:

- **A directory of state files, a JSONL ledger, a JSON schema.** Every
  extra file is one more tool call at the start. Agents edit files by exact
  string replacement, and long escaped JSON lines are the hardest thing to
  edit that way.
- **A required CLI.** It is one more thing to install, keep in step with
  the spec, and find missing on a fresh machine. `tools/rada-status` is
  optional.
- **Claims scoped by path globs, a dependency graph.** They solve problems
  that never occurred. Overlapping claims never happened; stale claims did.
  With a few open items, one `blocked:` word is enough.
- **Databases, embeddings, daemons.** Git plus a text file is the whole
  point.

A draft of v2 was then tested by agents acting it out on scratch
repositories. That test is where the exact end-commit command, the rebuilt
entry as an end commit, the eager `next_ids` and the shared-tree rules came
from.

## How a shift goes

```mermaid
flowchart TD
    A(["the user: start phrase"]) --> B["read HANDOFF.md<br/>+ start command, in one turn"]
    B --> C{"commits after<br/>the anchor?"}
    C -- "a shift without an end" --> R["rebuild its JOURNAL entry from git,<br/>commit it as an end commit"]
    C -- "none, or only read them" --> D["claim line, commit it alone"]
    R --> D
    D --> E["tell the user in 2-3 lines<br/>(delta, deleted claims, Asks, Notes)"]
    E --> F["work: small commits with ids;<br/>D for decisions, A for questions"]
    F --> G(["the user: end phrase"])
    G --> H["update HANDOFF.md,<br/>JOURNAL entry on top"]
    H --> I["end commit with trailers:<br/>Rada: end, Rada-Host, Rada-Repo"]
```

## The handoff file

`HANDOFF.md` holds the current state and nothing else. It is read at every
start and stays within 8,000 characters (`wc -m`). Sections, in this order:

| Section | Holds |
|---|---|
| Profile | host ids, the branch, languages, the other repositories |
| Live | a YAML block of what runs and from which commit, the tests with the commit they ran at, `next_ids` |
| Claims | `C` lines, one per session |
| Asks | `A` lines: what only the user can do or answer |
| Notes | `N` lines: warnings about the current state, each with what ends it |
| Open | `O` lines: open work with its state and next step |
| Decisions | `D` lines: the user's decisions in force |

A record is one line of at most 300 characters:

```
- C12 · home · 2026-09-29T18:24+02:00 · the draw page (O7) · holds: web
- O7 · tournament draw · live on the demo · next: seeded pots · blocked: A2
- D4 · Sign-in with Steam only · 2026-09-24
- A2 · Pick the seeding rule for the draw · since 2026-09-29 (O7)
- N3 · The demo database is mid-migration: do not restart demo · until O7 is deployed
```

- **Ids are never reused.** `next_ids` holds the next free number of each
  type. An agent takes one and raises it in the same edit, so a shift that
  dies halfway does not leave a used id behind.
- **Closed records are deleted.** Their history is in git
  (`git log --grep='\<O7\>'`) and in `JOURNAL.md`.
- **Decisions leave the file** when the user replaces or withdraws them, or
  when they become plain facts about the project and move into the guide.
- **Host ids are plain ASCII** (`home`, `work`). The Profile gives the names
  the user calls the computers by.

A ready file: [template/HANDOFF.md](template/HANDOFF.md).

## The journal

`JOURNAL.md` holds one entry per shift, newest first. It is an audit trail:
agents read it when they need to know why, not at the start. The heading of
an entry carries the commit range it covers:

```
## 2026-09-29T22:10+02:00 · home · 5480caf..a1b2c3d
- done: tournaments phase 6: the bot announces a series (O15; 1234abc, 5678def)
- verified: tests: 170 passed @a1b2c3d; the notice in a live room
- deployed: web @a1b2c3d; server unchanged
- ids: -O15 +A4 -C24
- left: nothing
```

An entry rebuilt from git by the next agent ends its heading with
`· reconstructed`.

## The anchor

The end commit of a shift commits `HANDOFF.md` and `JOURNAL.md` together.
Its message ends with one trailer block:

```
Handoff: tournaments phase 6

Co-Authored-By: Claude <noreply@anthropic.com>
Rada: end
Rada-Host: home
Rada-Repo: 34c1ef5a90b1 ~/server
Rada-Repo: 7bc4ea3c02d4 ~/spec
```

- **Write the trailers with `git commit --trailer`.** Git reads trailers
  only from the last paragraph of a message. A blank line before a
  `Co-Authored-By` line, or a line of prose in the block, silently hides
  `Rada: end`, and then the shift looks unhanded. `--trailer` adds to the
  existing block.
  - Check: `git log -1 --format='%(trailers:key=Rada,valueonly)'` prints
    `end`.
- **The anchor** is the newest commit whose trailers include `Rada: end`:

  ```
  git log --format='%h %(trailers:key=Rada,valueonly)' | awk '$2=="end"{print $1; exit}'
  ```

  A commit that only quotes the line in its body does not count.
- **The delta** is `git log <anchor>..HEAD`. Every commit in it is new to
  the reader, including bookkeeping.
- **The other repositories** each get a trailer
  `Rada-Repo: <12-character HEAD> <path>`, and their delta is
  `git -C <path> log <hash>..HEAD`. The path is absolute or starts with
  `~/`, and it may contain spaces.
- **Never amend or squash an end commit.** An amend with a new message
  drops the trailers. A squash merge buries them in the squashed message.
  With pull requests, merge with a merge commit or rebase. Fix a wrong end
  commit with a new one.
- **Trailers stay in the repository that holds the handoff file.** Public
  repositories get ids in their commit messages at most.

## The rules

The normative text is [RULES.md](RULES.md): nine invariants, the records
and when each is deleted, and the adopt, start, during and end steps. In
short:

- **Start:**
  - read `HANDOFF.md` and run the start command in one turn;
  - leave alone a handoff file another session is editing;
  - read the delta, and rebuild a missing shift as an end commit of its own;
  - clear the claims of other sessions when the tree holds none of their
    changes, and name them in the report;
  - claim;
  - report in two or three lines.
- **During:**
  - commit small, by file, with ids in the messages;
  - commit every edit of the handoff file at once;
  - the user's decisions become D lines, and questions become A lines;
  - no restart while there are foreign changes or a live claim on the
    resource;
  - no amend, rebase or reset.
- **End:**
  - run the start command again, in case someone handed over meanwhile;
  - update the state;
  - add a journal entry on top;
  - make the end commit with `--trailer`, and check it;
  - confirm in one line.

## Two sessions at the same time

A claim is a courtesy, not a lock. What prevents damage is RA-7: never
touch changes you did not make. The protocol works in two setups.

**One shared working tree** (one server, one user, as in QLadder). Both
sessions see each other's uncommitted changes and share git's index.

- `git commit -- <files>` commits only those files, whatever the other
  session has staged.
- But it takes the whole working-tree content of each file, including the
  other session's edits to the same file. So check
  `git diff HEAD -- <files>` first. This is also why the handoff file is
  committed after every edit and never left dirty.
- A new file is staged and committed in one command, so it never waits in
  the shared index.
- No amend, rebase or reset: HEAD may be the other session's commit.
- Never delete `.git/index.lock`: it means the other session is running
  git.
- A restart deploys the working tree, so check `git status` for changes
  that are not yours first.

**Separate clones**, where pushes decide:

- `git pull --rebase` before reading, and before the claim and end
  commits; push right after them.
- Keep the history linear.
- Add `JOURNAL.md merge=union` to `.gitattributes`.
- After a rebase, check `next_ids` against the highest ids in the file.

## Adopting it

1. Copy [template/HANDOFF.md](template/HANDOFF.md) and
   [template/JOURNAL.md](template/JOURNAL.md) to the repository's root.
   Fill in the Profile, and set `next_ids` one above the ids in use.
2. Check out a release tag of this repository, for example to `~/.rada/v2`.
   Add the lines of
   [template/agent-instructions.md](template/agent-instructions.md) to the
   instructions every session loads by itself. That file explains where
   they go, and how to check that the card loaded.
3. Keep a project guide next to it (layout, build, test, deploy, lasting
   facts). The handoff file says what is going on; the guide says how
   things are.
4. Make the first end commit (RULES.md, Adopt). It is the first anchor.

### From v1

1. Move lasting facts out of `HANDOFF.md` into the guide or docs:
   "Current state", and the knowledge buried in long Open items.
2. Move the journal to `JOURNAL.md` as it is.
3. Rewrite the records as one-liners:
   - drop closed items;
   - set `next_ids` one above the highest ids used so far;
   - turn "For the user" lines that are still pending into Asks.
4. Delete the Protocol section and the header's hand-kept fields
   (`anchor_commit`, `state_as_of`, the id lists), and add the Profile.
5. Replace the v1 lines in the agents' instructions with the v2 ones.
6. Make the migration commit a v1 handoff and a v2 end commit at once: a
   journal entry that says the rules changed, plus the `Rada: end`
   trailers.

## Changing the rules

The card is versioned in this repository, and releases are tags (`v1`,
`v2`). A project names the version it follows in its `HANDOFF.md` title,
and its agents import the card from a checkout of that tag. Whoever changes
the rules raises the version, tags it, moves the checkout, and says what
changed in the journal entry.

## License

MIT, see [LICENSE](LICENSE).
