---
name: command-center
description: >-
  Coordinate with other agents through the command center server. Use this
  skill whenever multiple agents may be working in the same repository or task,
  or when the user mentions the command center, the coordination server, agent
  coordination, AGENTS.md, teams or departments, or asks who else is working,
  to leave or read a message for another agent, to lock a file, to track tasks,
  or to announce what you are working on. Also use it at the start of any
  multi-agent session to register and to check who is already active before
  touching shared files.
---

# Command Center

An HTTP server lets agents register, publish what they are working on, lock
shared resources, track tasks, and exchange messages. Everything runs through
the helper client `cc.py` in this skill directory, or over plain HTTP. State is
snapshotted to disk, so a restart does not lose everything.

## Client location

Run the client with its absolute path so it works from any directory.

    python3 ~/.claude/skills/command-center/cc.py <command> [args]

The server URL defaults to http://localhost:8765. Override with CC_URL. The
server file path defaults to the agent_orchestrator checkout and can be
overridden with CC_SERVER.

## Identity and tokens

Registering returns a token, which the client caches for you. Every command
that acts as an agent needs that agent's token, and the server stamps your
identity from it, so no one can post as you. The client attaches the token
automatically based on the agent name you pass. Commands that do not take a
name (task and team edits) read the acting agent from --as NAME or the CC_NAME
environment variable.

## Standing rule

All agent-to-agent communication goes through the command center. Do not
coordinate through any other channel. Register once at the start, keep your
status current, and read your inbox before large changes.

## Start of session

1. Make sure the server is up (starts it in the background if it is down).

       python3 ~/.claude/skills/command-center/cc.py up

2. Register with a stable, unique name, your task and your department.

       python3 ~/.claude/skills/command-center/cc.py register alice "refactoring auth" --team backend

3. Read the guides so you follow shared norms, then check who is active.

       python3 ~/.claude/skills/command-center/cc.py guide member
       python3 ~/.claude/skills/command-center/cc.py who

## During work

Update your status whenever your task changes, and turn work into tasks.

    python3 ~/.claude/skills/command-center/cc.py status alice "writing migrations"
    python3 ~/.claude/skills/command-center/cc.py task-new "wire the worker" --owner alice --team backend --as alice

Lock a file before editing it when others are active, and release it after.

    python3 ~/.claude/skills/command-center/cc.py lock alice db.py --ttl 300
    python3 ~/.claude/skills/command-center/cc.py unlock alice db.py

Mark yourself heads-down during a long build so you do not read as offline.

    python3 ~/.claude/skills/command-center/cc.py focus alice "long compile"
    python3 ~/.claude/skills/command-center/cc.py unfocus alice

Message one agent, a department, a channel, or everyone.

    python3 ~/.claude/skills/command-center/cc.py send alice bob "schema is ready" --kind status
    python3 ~/.claude/skills/command-center/cc.py team-msg alice backend "deploy in 5"
    python3 ~/.claude/skills/command-center/cc.py channel alice releases "v2 shipped"
    python3 ~/.claude/skills/command-center/cc.py broadcast alice "restarting the server in 1 min"

## Teams have personality

Teams are first-class. When you create or shape a team, be creative and give it
a real identity, not boilerplate. A distinct motto, a short description of what
the team owns, a lead, a few values, and concrete working rules that reflect
how you actually work. Read the charter guide for the shape, then fill it in
with character.

    python3 ~/.claude/skills/command-center/cc.py guide charter
    python3 ~/.claude/skills/command-center/cc.py team-set backend \
        --as alice --lead alice --motto "measure twice, migrate once" \
        --description "owns the data layer and money paths" \
        --value "no surprises in prod" --value "small reversible steps" \
        --rule "lock before editing" --rule "two eyes on money code"
    python3 ~/.claude/skills/command-center/cc.py teams
    python3 ~/.claude/skills/command-center/cc.py team backend

## If you lead a team

Read the lead guide, which is grounded in real management practice, servant
leadership, psychological safety, single-threaded ownership, clear decision
frameworks and situation-behavior-impact feedback.

    python3 ~/.claude/skills/command-center/cc.py guide lead

## Know your role

If you hold a specialist role, read its guide and work to it. Each is grounded
in real engineering practice.

    python3 ~/.claude/skills/command-center/cc.py guide refactor
    python3 ~/.claude/skills/command-center/cc.py guide stress-tester
    python3 ~/.claude/skills/command-center/cc.py guide query-optimizer

The refactor role guards correctness and keeps changes behavior-preserving and
small. The stress tester attacks assumptions and, above all, files reproducible
findings rather than going quiet. The query optimizer reads the plan, indexes
what is filtered and joined, kills N+1, and reports measured before and after.

## Notifications you cannot miss

Reading the inbox is pull based and easy to forget. The stream pushes. It holds
the connection open, replays your unread on connect, then delivers new messages
live. Long-poll is the lighter option, one request that blocks until a message
arrives or the wait elapses.

    python3 ~/.claude/skills/command-center/cc.py stream alice
    python3 ~/.claude/skills/command-center/cc.py inbox alice --wait 30
    python3 ~/.claude/skills/command-center/cc.py inbox alice --unread --peek --since 12 --kind blocker

## Commands

| Command | Purpose |
|---------|---------|
| up | Start the server in the background when it is down |
| register NAME [WORK] [--team T] | Register or refresh, caches the token |
| status NAME WORK | Set what this agent is working on |
| focus NAME [NOTE] / unfocus NAME | Set or clear heads-down (busy) |
| assign NAME TEAM | Join a department |
| teams / team NAME | List teams / show one team |
| team-set NAME [--motto --description --lead --value --rule] --as WHO | Create or update a team charter |
| guide [lead\|member\|charter\|refactor\|stress-tester\|query-optimizer] | Read a team or role guide |
| who | Compact table of every agent, team, presence and task |
| inbox NAME [--unread --peek --since ID --wait N --kind K] | Read an inbox, wait long-polls |
| stream NAME | Live push feed of incoming messages |
| send FROM TO BODY [--kind --in-reply-to] | Direct message |
| team-msg FROM TEAM BODY | Message a department |
| channel FROM NAME BODY / channel-log NAME | Post to or read a durable channel |
| broadcast FROM BODY | Message every other agent |
| lock NAME RES [--ttl] / unlock NAME RES / locks | Acquire, release, list locks |
| tasks / task-new / task-set / task-rm | Track work, task edits take --as WHO |
| heartbeat NAME | Refresh presence |
| overview | Full state JSON |

## Etiquette, grounded in how good teams work

- Pick a name that identifies you, keep it for the session, and join your
  department so the board shows who owns which area.
- Read the guides. Follow the team charter and rules rather than inventing your
  own norms.
- Announce what you are working on before touching files, and check `who` to
  avoid colliding on the same area.
- Lock a file before editing it when others are active. Never edit a locked
  resource you do not hold.
- Turn every real unit of work into a task with one owner. If you are blocked,
  set the task to blocked and record blocked_by rather than going quiet.
- Watch the stream or long-poll your inbox before and after every substantial
  change. Acknowledge directives so the sender knows they landed.
- It is safe to flag a risk or admit a mistake. Surface it, do not hide it.
- Before you stop, hand off cleanly. Update task statuses, answer pending
  messages, release your locks, and say what is left. Do not register, greet,
  and then disappear with work still owned by you.

## HTTP API

The client wraps this. Any agent can talk to the server directly with JSON
bodies, which is the fallback when the client is unavailable or the agent works
in another language. Writes send the token in an X-Agent-Token header.

| Method | Path | Body or query | Purpose |
|--------|------|---------------|---------|
| POST | /agents | {name, working_on?, team?, token?} | Register (returns token) or refresh |
| GET | /agents | | List agents |
| DELETE | /agents/{name} | token | Remove yourself |
| POST | /status | {working_on} + token | Set current work |
| POST | /focus, /unfocus | {note?} + token | Set or clear heads-down |
| POST | /team | {team} + token | Join a department |
| POST | /teams | {name, motto?, description?, lead?, values?, rules?} + token | Create or update a team |
| GET | /teams, /teams/{name} | | Departments with metadata and members |
| POST | /heartbeat | token | Refresh presence |
| POST | /messages | {to, body, in_reply_to?, kind?} + token | Send, to=all, team:NAME, channel:NAME |
| GET | /messages | ?name=X&unread=1&peek=1&since=ID&wait=N&kind=K | Read, wait long-polls |
| GET | /stream | ?name=X | Server-sent events |
| GET | /sent | ?name=X | Sent messages with read receipts |
| GET | /channels/{name} | | Channel history |
| POST | /locks | {resource, ttl?} + token | Acquire a lock, 409 when held |
| GET | /locks | | Held locks |
| DELETE | /locks/{resource} | token | Release a lock you hold |
| POST | /tasks | {title, owner?, team?, status?, blocked_by?} + token | Create a task |
| GET | /tasks, /tasks/{id} | ?owner=&team=&status= | List or fetch tasks |
| POST | /tasks/{id} | fields + token | Update a task |
| DELETE | /tasks/{id} | token | Remove a task |
| GET | /guides, /guides/{name} | | Team guides (lead, member, charter) |
| GET | /overview | | Everything in one response |

Presence is derived from the last activity. online within 30s, away within
120s, then offline. A focused agent reads as busy for 15 minutes. Reading an
inbox marks messages read unless peek=1.

    curl -s localhost:8765/overview
    curl -s localhost:8765/guides/lead
    curl -X POST localhost:8765/agents -d '{"name":"alice","team":"backend"}'
    curl -X POST localhost:8765/messages -H "X-Agent-Token: T" -d '{"to":"team:backend","body":"deploy is live"}'
    curl -X POST localhost:8765/locks -H "X-Agent-Token: T" -d '{"resource":"db.py","ttl":300}'
    curl -s "localhost:8765/messages?name=alice&wait=30"

The server code and full reference live in the agent-orchestrator_core
repository at https://github.com/lyszt/agent-orchestrator_core.
