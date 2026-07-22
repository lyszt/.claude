# Command Center — verbose agent narration (global)

Applies whenever a command center is running for the session (the `command-center`
skill; client at `~/.claude/skills/command-center/cc.py`). Every agent joins it and
narrates what it is doing, out loud, continuously. Verbose beats silent: a steady
stream of small honest updates always beats one big quiet gap.

## When you spawn subagents

Put the command-center protocol as the **first and last required actions** of every
spawn brief — at the very top and very bottom, never buried mid-prompt (agents treat
mid-prompt instructions as optional once they get deep in the work). Word it as a hard
requirement ("you MUST"), for example:

- FIRST, before touching anything: register in the command center with the exact name
  and team I gave you, read the relevant guide, then post a status saying what you are
  about to do.
- DURING the work, after every meaningful step (a file read that changed your plan, an
  edit, a decision, a dead end): post a one-line update — `cc status NAME "..."` and/or
  `cc channel NAME <channel> "..."` — saying what you just did and what is next. Narrate
  progress, decisions, and surprises. If blocked, post `BLOCKER: <detail>` immediately
  and keep any independent work moving.
- LAST, before you finish: send a full report to your parent/manager with
  `cc send NAME <parent> "..."`, post a summary to the team channel, and submit at
  least one `cc feedback` item (see "Always submit feedback when you finish" below).

## When you are a subagent under a command center

- Register immediately as the name/team your parent gave you; read the member guide.
- Narrate verbosely and in the present tense: announce a task before you start it, drop
  a short progress line after each file read / edit / decision, and surface blockers the
  moment they appear. Keep your `status` current so the board and the live dashboard
  always reflect what you are actually doing right now.
- On long stretches, `cc focus NAME "..."` (or `cc heartbeat NAME`) so you do not read as
  offline while you think.
- End with a full report to your parent, a one-line channel summary, and a `cc feedback`
  item (see below). Never register, go quiet, and disappear with work still owned by you.

## Always submit feedback when you finish

Every agent MUST submit at least one `cc feedback` item as part of finishing any unit of
work. This is not optional. The endpoint stores the item and opens a tracking issue, so it
is how the tooling actually improves.

- Report the real thing you hit: a bug, a rough edge, a slow or confusing step, or a
  concrete improvement — in the command center itself, the task, the codebase, or the
  workflow. Ground it in what actually happened this session.
- Pick the kind honestly: `--kind bug` (something broke or misbehaved), `--kind issue`
  (a gap or friction), or `--kind improvement` (a concrete better way). Give a specific
  `--title` and a `--target` (the file, command, or endpoint it concerns).
- Make each one worth an issue: concrete, actionable, one topic. If your point matches a
  known/already-filed item, say so in the body rather than re-filing noise.
- If the work genuinely went smoothly, still file one short `--kind improvement` noting
  what worked and the one thing that would have made it faster. Never skip it.

    python3 ~/.claude/skills/command-center/cc.py feedback NAME "what happened + the ask" \
        --kind improvement --title "short specific title" --target "file/command/endpoint"

## Client quick reference

    python3 ~/.claude/skills/command-center/cc.py register NAME "working on X" --team T
    python3 ~/.claude/skills/command-center/cc.py status NAME "doing Y now"
    python3 ~/.claude/skills/command-center/cc.py channel NAME <channel> "did Y, next Z"
    python3 ~/.claude/skills/command-center/cc.py send NAME <parent> "full report ..."
    python3 ~/.claude/skills/command-center/cc.py focus NAME "long read"    # heads-down
    python3 ~/.claude/skills/command-center/cc.py feedback NAME "..." --kind improvement --title "..." --target "..."
