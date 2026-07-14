# My Claude Code config

This holds part of my [Claude Code](https://claude.com/claude-code) setup: the system
prompt I run, my custom skills, and a list of the plugins I have installed. I kept out
anything personal or machine-specific, like credentials, session history, caches, and
settings that hold secrets. The [.gitignore](.gitignore) has the full exclusion list.

## What's in here

| Path | What it is |
|---|---|
| CLAUDE.md | My system prompt, the instructions Claude reads every session |
| RTK.md | Reference for the RTK command proxy, imported by CLAUDE.md |
| rules/ | Extra instruction files, currently just context7.md |
| skills/ | Custom skills Claude Code loads on its own |
| PLUGINS.md | The plugins I have installed and where to get them |
| Makefile | Reinstalls every listed plugin in one command |

## System prompt

Claude reads ~/.claude/CLAUDE.md at the start of every session and follows it as
standing instructions. Mine spans three files. CLAUDE.md is the entry point, it pulls
in RTK.md through the @RTK.md import line, and rules/context7.md loads as an extra
rule.

### CLAUDE.md

This started as a file about how Claude talks and grew into house rules. It now covers
four things: tone, git safety, code comments, and prose formatting.

The tone part puts Claude in caveman mode: terse replies, dropped articles and filler,
fragments allowed, short words. The technical content stays exact, and code, commits,
and PR text get written normally. It opens with "ounga bounga" and throws in caveman
phrases here and there. For security warnings, confirmations on destructive actions,
and multi-step instructions, where a clipped fragment could be misread, it goes back to
plain full sentences. Saying "stop caveman" or "normal mode" turns it off.

The git rule is one line: never create or switch branches unless I ask. Claude works on
whatever branch is checked out, and if that looks wrong for the change it has to ask
instead of acting.

The code comment rules are the strictest part. Comments only exist to tell the reader a
constraint, a non-obvious why, or a trap; anything that reads like narration gets
deleted, not reworded. Sentences are plain and verb-first, one idea each, and the only
punctuation allowed inside them is commas and a final period. That kills colon labels
("Nota:", "Retorna: x"), em dashes, semicolons, and every other label-then-explanation
shape, arrows and pipes included. TODO: and FIXME: markers survive as the sole tooling
exception. Doc comments follow a fixed two-line shape, first what the function does,
then "Receives x and returns y", nothing else.

The prose rules apply to PRs, commit bodies, markdown, and chat answers: no backticks,
no curly quotes, no em dashes. Identifiers and file names get written as plain text.
This README follows that rule, which is why nothing in it sits in inline code spans.

### RTK.md

CLAUDE.md imports this. RTK ("Rust Token Killer") is a CLI proxy that wraps dev
commands to cut the tokens their output costs. The file is a reference for it. It lists
the meta commands (rtk gain for savings stats, rtk discover to scan history for missed
chances, rtk proxy to run a command raw), notes that a Claude Code hook rewrites
commands automatically so git status becomes rtk git status, and warns that an
unrelated tool shares the rtk name and will break things if it gets installed instead.

### rules/context7.md

This rule stops Claude from answering library questions from memory. When the question
is about a library, framework, SDK, API, CLI, or cloud service, Claude looks up current
docs with the ctx7 CLI instead of trusting training data. The rule spells out the
resolve-then-fetch flow, caps it at three commands per question, says not to put secrets
in a query, and lists what to skip it for, like refactoring and general programming
questions.

## Skills

Skills load on their own and activate based on the request. No command needed.

| Skill | What it does |
|---|---|
| context7-mcp | On a library or framework question, or a request for code examples, pulls current docs through Context7 instead of answering from memory. |
| find-docs | Fetches up-to-date docs, API references, and examples for a library, SDK, CLI, or cloud service. Fires on API syntax, config options, version migrations, and library-specific debugging. |
| human-writing | Fires when I write prose, like READMEs, docs, comments, and PR text. It curls the live Wikipedia "Signs of AI writing" page and strips the patterns it lists, so it tracks edits to that page instead of freezing a copy. It also carries the comment punctuation rules from CLAUDE.md, so comment text obeys them even when this skill drives the writing. |

## Plugins

I don't store the plugin code here. It lives in each plugin's marketplace, so this repo
just records which ones I run. The version and scope table is in
[PLUGINS.md](PLUGINS.md).

| Plugin | Marketplace | What it adds |
|---|---|---|
| caveman | caveman | The caveman output mode and its commands (compress, commit, review). |
| game-sounds | citedy | Sound effects for events, with volume and sound-pack controls. |
| frontend-design | claude-plugins-official | Guidance for generating frontend UI. |
| context7 | claude-plugins-official | Context7 doc fetching as a plugin. |
| code-review | claude-plugins-official | Pull request and diff review commands. |
| github | claude-plugins-official | GitHub workflow helpers for PRs and issues. |

## Install

The skills and system prompt take effect once these files sit under ~/.claude/. The
plugins install from their marketplaces with the Makefile:

```bash
make install      # add the marketplaces, then install every plugin
make list         # show what's installed
make uninstall    # remove the listed plugins
```

It needs the claude CLI on PATH.

## What Claude is like with this

Mostly it makes Claude talk like a caveman. I set it up because it's funny, not for any
productivity reason. So, to be honest about it:

- It replies in terse caveman-speak: dropped articles, fragments, "ounga bounga", a bit
  of "me think" and "club it".
- Code, commits, and the technical content come out normal. Only the prose around them
  gets the caveman treatment. It also switches to plain English for security warnings,
  destructive-action confirmations, and step-by-step instructions.
- It won't touch git branches on its own, and it writes comments and prose under the
  punctuation rules above, so no backticks or colon labels sneak into PR text.
- Saying "normal mode" or "stop caveman" makes it stop.

The other pieces are real but minor. The ctx7 rule and the doc skills make it fetch
current docs for library questions instead of guessing. RTK proxies shell commands to
spend fewer tokens. Both only do something if those tools are installed. Without them,
it's just the caveman tone.
