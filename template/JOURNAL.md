# Journal

One entry per shift, newest first (rada-anchor/2). Agents read it on
demand; the start reads only its top, to add a rebuilt entry. An entry's
heading gives the commit range it covers; the commit messages hold the
details.

<!-- The entry format (RULES.md, End 4). Headings:
## <time> · <host> · <anchor>..<last work commit>                      a normal shift
## <time of its last commit> · <its host, or ?> · <range> · reconstructed   a shift rebuilt from git
## <time> · <host> · adopted at <HEAD>                                   the first entry

An example:

## 2026-09-29T22:10+02:00 · home · 5480caf..a1b2c3d
- done: <what, with commit hashes and ids>
- verified: <tests: N passed @commit; what was checked by hand>
- deployed: <what runs now, from which commit; or "nothing">
- ids: <+O8 -O7 +D5 -C12 +A3>
- left: <uncommitted files and why; or "nothing">
-->
