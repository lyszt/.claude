#!/usr/bin/env python3
"""Command-line client for the agent coordination command center.

Wraps the coordination server HTTP API so an agent can register, publish its
status, lock resources, track tasks, and message other agents with one shell
command. Agents identify by name, sent in an X-Agent-Name header.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

BASE = os.environ.get("CC_URL", "http://localhost:8765").rstrip("/")
SERVER = os.environ.get(
    "CC_SERVER",
    "/home/kaldwin/Development/Tools/agent_orchestrator/server.py",
)


def _need_actor(name):
    if not name:
        print("identify the acting agent with --as NAME or the CC_NAME env var", file=sys.stderr)
        return None
    return name


def _actor(args):
    return getattr(args, "as_", None) or os.environ.get("CC_NAME")


def _request(method, path, payload=None, actor=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if actor:
        req.add_header("X-Agent-Name", actor)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")


def _is_up():
    try:
        _request("GET", "/")
        return True
    except urllib.error.URLError:
        return False


def _emit(status, body):
    print(json.dumps({"status": status, "body": body}, separators=(",", ":")))


def _trunc(text, limit=200):
    """Collapse whitespace and cap length so long bodies do not bloat agent context.

    Receives a string and an optional limit and returns a single-line truncated string.
    """
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return f"{text[:limit]} …(+{len(text) - limit} chars, --full)"


def cmd_up(args):
    if _is_up():
        print(f"command center already up at {BASE}")
        return 0
    if not os.path.exists(SERVER):
        print(f"server file not found at {SERVER}", file=sys.stderr)
        return 1
    port = BASE.rsplit(":", 1)[-1]
    subprocess.Popen(
        [sys.executable, SERVER, "--port", port],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(20):
        time.sleep(0.1)
        if _is_up():
            print(f"command center started at {BASE}")
            return 0
    print("command center did not come up in time", file=sys.stderr)
    return 1


def cmd_register(args):
    payload = {"name": args.name, "working_on": args.working_on or ""}
    if args.team:
        payload["team"] = args.team
    if args.role:
        payload["role"] = args.role
    if args.can_spawn:
        payload["can_spawn"] = True
    status, body = _request("POST", "/agents", payload)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_spawn(args):
    actor = _need_actor(args.parent)
    if not actor:
        return 1
    payload = {"name": args.name, "parent": args.parent, "working_on": args.working_on or ""}
    if args.team:
        payload["team"] = args.team
    if args.role:
        payload["role"] = args.role
    if args.can_spawn:
        payload["can_spawn"] = True
    status, body = _request("POST", "/agents", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_set_role(args):
    actor = _need_actor(_actor(args))
    if not actor:
        return 1
    payload = {"name": args.name}
    if args.role:
        payload["role"] = args.role
    if args.can_spawn:
        payload["can_spawn"] = True
    if args.no_spawn:
        payload["can_spawn"] = False
    status, body = _request("POST", "/roles", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_status(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("POST", "/status", {"working_on": args.working_on}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_heartbeat(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("POST", "/heartbeat", {}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_focus(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("POST", "/focus", {"note": args.note or ""}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_unfocus(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("POST", "/unfocus", {}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_assign(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("POST", "/team", {"team": args.team}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_who(args):
    status, body = _request("GET", "/overview")
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    totals = body["totals"]
    p = totals["presence"]
    print(
        f"agents {totals['agents']}  teams {totals['teams']}  unread {totals['unread']}  "
        f"locks {totals['locks']}  "
        f"(online {p['online']}, busy {p['busy']}, away {p['away']}, offline {p['offline']})"
    )
    show_all = getattr(args, "all", False)
    for agent in body["agents"]:
        if not show_all and agent["presence"] == "offline":
            continue
        work = _trunc(agent["working_on"] or "-", 80)
        team = agent.get("team") or "-"
        role = agent.get("role", "member")
        if agent.get("can_spawn"):
            role += "*"
        note = f" [{agent['focus_note']}]" if agent.get("focus") and agent.get("focus_note") else ""
        print(
            f"  [{agent['presence']:<7}] {agent['name']:<16} {team:<12} {role:<10} "
            f"unread {agent['unread']:<3} {work}{note}"
        )
    if not show_all and p["offline"]:
        print(f"  (+{p['offline']} offline, --all to show)")
    boards = [c for c in body.get("channels", []) if c["name"] in ("rules", "announcements")]
    for c in boards:
        last = c.get("last")
        tail = f"last {last['from']}: {last['body']}" if last else "empty"
        print(f"  #{c['name']} ({c['message_count']}) {tail}")
    return 0


def cmd_teams(args):
    status, body = _request("GET", "/teams")
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    for name, team in sorted(body["teams"].items()):
        lead = f" lead={team['lead']}" if team.get("lead") else ""
        motto = f' "{team["motto"]}"' if team.get("motto") else ""
        members = ", ".join(m["name"] for m in team["members"])
        print(f"{name} ({team['member_count']}){lead}{motto}: {members}")
    return 0


def cmd_team(args):
    status, body = _request("GET", f"/teams/{args.name}")
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_team_set(args):
    actor = _actor(args)
    actor = _need_actor(actor)
    if not actor:
        return 1
    payload = {"name": args.name}
    if args.motto is not None:
        payload["motto"] = args.motto
    if args.description is not None:
        payload["description"] = args.description
    if args.lead is not None:
        payload["lead"] = args.lead
    if getattr(args, "project", None) is not None:
        payload["project"] = args.project
    if getattr(args, "parent_team", None) is not None:
        payload["parent_team"] = args.parent_team
    if args.value:
        payload["values"] = args.value
    if args.rule:
        payload["rules"] = args.rule
    status, body = _request("POST", "/teams", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_inbox(args):
    query = f"/messages?name={args.name}"
    if args.unread:
        query += "&unread=1"
    if args.peek:
        query += "&peek=1"
    if args.since:
        query += f"&since={args.since}"
    if args.wait:
        query += f"&wait={args.wait}"
    if args.kind:
        query += f"&kind={args.kind}"
    status, body = _request("GET", query)
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    print(f"{body['count']} message(s) for {args.name}")
    full = getattr(args, "full", False)
    for m in body["messages"]:
        scope = m.get("scope") or "direct"
        kind = m.get("kind", "message")
        text = m["body"] if full else _trunc(m["body"])
        print(f"  #{m['id']} [{scope}/{kind}] from {m['from']}: {text}")
    return 0


def cmd_stream(args):
    url = BASE + f"/stream?name={args.name}"
    try:
        with urllib.request.urlopen(url) as resp:
            print(f"streaming for {args.name}, Ctrl-C to stop")
            for raw in resp:
                text = raw.decode().strip()
                if not text.startswith("data:"):
                    continue
                m = json.loads(text[len("data:"):].strip())
                scope = m.get("scope") or "direct"
                print(f"[#{m['id']} {scope}] from {m['from']}: {m['body']}")
    except urllib.error.HTTPError as e:
        _emit(e.code, json.loads(e.read() or "null"))
        return 1
    except KeyboardInterrupt:
        return 0
    return 0


def cmd_send(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    payload = {"to": args.to, "body": args.body}
    if args.kind:
        payload["kind"] = args.kind
    if args.in_reply_to is not None:
        payload["in_reply_to"] = args.in_reply_to
    status, body = _request("POST", "/messages", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_broadcast(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    status, body = _request("POST", "/messages", {"to": "all", "body": args.body}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_team_msg(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    status, body = _request(
        "POST", "/messages", {"to": "team:" + args.team, "body": args.body}, actor=actor
    )
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_channel(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    status, body = _request(
        "POST", "/messages", {"to": "channel:" + args.channel, "body": args.body}, actor=actor
    )
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_rule(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    status, body = _request(
        "POST", "/messages", {"to": "channel:rules", "body": args.body, "kind": "rule"}, actor=actor
    )
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_announce(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    status, body = _request(
        "POST", "/messages", {"to": "channel:announcements", "body": args.body, "kind": "announce"}, actor=actor
    )
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_feedback(args):
    sender = getattr(args, "from")
    actor = _need_actor(sender)
    if not actor:
        return 1
    payload = {"kind": args.kind, "title": args.title or "", "body": args.body}
    if args.target:
        payload["target"] = args.target
    status, body = _request("POST", "/feedback", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_channels(args):
    status, body = _request("GET", "/channels", actor=_actor(args))
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    if not body["channels"]:
        print("no channels yet")
        return 0
    for c in body["channels"]:
        topic = f" — {c['topic']}" if c.get("topic") else ""
        print(f"  #{c['name']} ({c['message_count']}){topic}")
    return 0


def cmd_channel_new(args):
    actor = _need_actor(_actor(args))
    if not actor:
        return 1
    payload = {"name": args.name}
    if args.topic is not None:
        payload["topic"] = args.topic
    status, body = _request("POST", "/channels", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_channel_log(args):
    status, body = _request("GET", f"/channels/{args.channel}", actor=_actor(args))
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    msgs = body["messages"]
    full = getattr(args, "full", False)
    limit = getattr(args, "limit", 0) or 20
    shown = msgs if full else msgs[-limit:]
    if not full and len(msgs) > len(shown):
        print(f"  (showing last {len(shown)} of {len(msgs)}, --full for all)")
    for m in shown:
        text = m["body"] if full else _trunc(m["body"])
        print(f"  #{m['id']} from {m['from']}: {text}")
    return 0


def cmd_lock(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    payload = {"resource": args.resource}
    if args.ttl:
        payload["ttl"] = args.ttl
    status, body = _request("POST", "/locks", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_unlock(args):
    actor = _need_actor(args.name)
    if not actor:
        return 1
    status, body = _request("DELETE", f"/locks/{args.resource}", {}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_locks(args):
    status, body = _request("GET", "/locks")
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    for lock in body["locks"]:
        print(f"  {lock['resource']} held by {lock['holder']}")
    if not body["locks"]:
        print("  no locks held")
    return 0


def cmd_guide(args):
    if args.name:
        status, body = _request("GET", f"/guides/{args.name}")
        if status >= 400 or not body:
            _emit(status, body)
            return 1
        guide = body["guide"]
        print(guide["title"])
        print("based on: " + ", ".join(guide["based_on"]))
        for section in guide["sections"]:
            print(f"\n{section['heading']}")
            for point in section["points"]:
                print(f"  - {point}")
        return 0
    status, body = _request("GET", "/guides")
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_task_new(args):
    actor = _need_actor(_actor(args))
    if not actor:
        return 1
    payload = {"title": args.title}
    for key in ("owner", "team", "status", "blocked_by"):
        value = getattr(args, key)
        if value:
            payload[key] = value
    status, body = _request("POST", "/tasks", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_task_set(args):
    actor = _need_actor(_actor(args))
    if not actor:
        return 1
    payload = {}
    for key in ("title", "owner", "team", "status", "blocked_by"):
        value = getattr(args, key)
        if value is not None:
            payload[key] = value
    status, body = _request("POST", f"/tasks/{args.id}", payload, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_task_rm(args):
    actor = _need_actor(_actor(args))
    if not actor:
        return 1
    status, body = _request("DELETE", f"/tasks/{args.id}", {}, actor=actor)
    _emit(status, body)
    return 0 if status < 400 else 1


def cmd_tasks(args):
    query = "/tasks"
    filters = []
    for key in ("owner", "team", "status"):
        value = getattr(args, key)
        if value:
            filters.append(f"{key}={value}")
    if filters:
        query += "?" + "&".join(filters)
    status, body = _request("GET", query)
    if status >= 400 or not body:
        _emit(status, body)
        return 1
    print(f"{body['count']} task(s)")
    for t in body["tasks"]:
        who = t["owner"] or "unowned"
        team = f"/{t['team']}" if t["team"] else ""
        blocked = f"  blocked_by {t['blocked_by']}" if t["blocked_by"] else ""
        print(f"  #{t['id']} [{t['status']:<11}] {who}{team}  {t['title']}{blocked}")
    return 0


def cmd_overview(args):
    status, body = _request("GET", "/overview")
    _emit(status, body)
    return 0 if status < 400 else 1


def _add_as(parser):
    parser.add_argument("--as", dest="as_", default=None, help="acting agent, defaults to CC_NAME")


def build_parser():
    parser = argparse.ArgumentParser(description="Agent command center client")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("up", help="start the command center if it is down")
    p.set_defaults(func=cmd_up)

    p = sub.add_parser("register", help="register this agent")
    p.add_argument("name")
    p.add_argument("working_on", nargs="?", default="")
    p.add_argument("--team", default="")
    p.add_argument("--role", default="", help="member, lead, manager or a specialist role")
    p.add_argument("--can-spawn", action="store_true", dest="can_spawn")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("spawn", help="a spawn-capable agent creates a subagent")
    p.add_argument("parent")
    p.add_argument("name")
    p.add_argument("working_on", nargs="?", default="")
    p.add_argument("--team", default="")
    p.add_argument("--role", default="")
    p.add_argument("--can-spawn", action="store_true", dest="can_spawn")
    p.set_defaults(func=cmd_spawn)

    p = sub.add_parser("set-role", help="manager sets who is who")
    p.add_argument("name")
    p.add_argument("role", nargs="?", default="")
    p.add_argument("--can-spawn", action="store_true", dest="can_spawn")
    p.add_argument("--no-spawn", action="store_true", dest="no_spawn")
    _add_as(p)
    p.set_defaults(func=cmd_set_role)

    p = sub.add_parser("status", help="set what this agent is working on")
    p.add_argument("name")
    p.add_argument("working_on")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("heartbeat", help="refresh presence")
    p.add_argument("name")
    p.set_defaults(func=cmd_heartbeat)

    p = sub.add_parser("focus", help="mark heads-down so long work does not read as offline")
    p.add_argument("name")
    p.add_argument("note", nargs="?", default="")
    p.set_defaults(func=cmd_focus)

    p = sub.add_parser("unfocus", help="clear heads-down")
    p.add_argument("name")
    p.set_defaults(func=cmd_unfocus)

    p = sub.add_parser("assign", help="join a department")
    p.add_argument("name")
    p.add_argument("team")
    p.set_defaults(func=cmd_assign)

    p = sub.add_parser("who", help="show who is working, compact")
    p.add_argument("--all", action="store_true", help="include offline agents")
    p.set_defaults(func=cmd_who)

    p = sub.add_parser("teams", help="list departments with metadata and members")
    p.set_defaults(func=cmd_teams)

    p = sub.add_parser("team", help="show one department")
    p.add_argument("name")
    p.set_defaults(func=cmd_team)

    p = sub.add_parser("team-set", help="create or update a team charter")
    p.add_argument("name")
    p.add_argument("--motto", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--lead", default=None)
    p.add_argument("--project", default=None, help="the project this team belongs to")
    p.add_argument("--parent-team", dest="parent_team", default=None, help="parent team for a sub-team")
    p.add_argument("--value", action="append", help="repeatable team value")
    p.add_argument("--rule", action="append", help="repeatable working rule")
    _add_as(p)
    p.set_defaults(func=cmd_team_set)

    p = sub.add_parser("inbox", help="read an inbox")
    p.add_argument("name")
    p.add_argument("--unread", action="store_true")
    p.add_argument("--peek", action="store_true")
    p.add_argument("--since", type=int, default=0)
    p.add_argument("--wait", type=int, default=0, help="long-poll seconds")
    p.add_argument("--kind", default="")
    p.add_argument("--full", action="store_true", help="show full message bodies")
    p.set_defaults(func=cmd_inbox)

    p = sub.add_parser("stream", help="live push stream of incoming messages")
    p.add_argument("name")
    p.set_defaults(func=cmd_stream)

    p = sub.add_parser("send", help="send a direct message")
    p.add_argument("from")
    p.add_argument("to")
    p.add_argument("body")
    p.add_argument("--kind", default="")
    p.add_argument("--in-reply-to", type=int, default=None, dest="in_reply_to")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("broadcast", help="message every other agent")
    p.add_argument("from")
    p.add_argument("body")
    p.set_defaults(func=cmd_broadcast)

    p = sub.add_parser("team-msg", help="message every agent in a department")
    p.add_argument("from")
    p.add_argument("team")
    p.add_argument("body")
    p.set_defaults(func=cmd_team_msg)

    p = sub.add_parser("channels", help="list channels with topics")
    _add_as(p)
    p.set_defaults(func=cmd_channels)

    p = sub.add_parser("channel-new", help="create a channel or set its topic")
    p.add_argument("name")
    p.add_argument("--topic", default=None)
    _add_as(p)
    p.set_defaults(func=cmd_channel_new)

    p = sub.add_parser("channel", help="post to a durable channel")
    p.add_argument("from")
    p.add_argument("channel")
    p.add_argument("body")
    p.set_defaults(func=cmd_channel)

    p = sub.add_parser("channel-log", help="read a channel history")
    p.add_argument("channel")
    p.add_argument("--full", action="store_true", help="show all messages, full bodies")
    p.add_argument("--limit", type=int, default=20, help="how many recent messages to show")
    _add_as(p)
    p.set_defaults(func=cmd_channel_log)

    p = sub.add_parser("rule", help="post a shared rule to the rules board")
    p.add_argument("from")
    p.add_argument("body")
    p.set_defaults(func=cmd_rule)

    p = sub.add_parser("feedback", help="report a bug, issue or improvement (stored + opens a GitHub issue)")
    p.add_argument("from")
    p.add_argument("body")
    p.add_argument("--kind", default="issue", help="bug, issue or improvement")
    p.add_argument("--title", default="")
    p.add_argument("--target", default="", help="the file, component or endpoint it concerns")
    p.set_defaults(func=cmd_feedback)

    p = sub.add_parser("announce", help="post lead or management direction to the announcements board")
    p.add_argument("from")
    p.add_argument("body")
    p.set_defaults(func=cmd_announce)

    p = sub.add_parser("lock", help="acquire a resource lock")
    p.add_argument("name")
    p.add_argument("resource")
    p.add_argument("--ttl", type=int, default=0)
    p.set_defaults(func=cmd_lock)

    p = sub.add_parser("unlock", help="release a resource lock you hold")
    p.add_argument("name")
    p.add_argument("resource")
    p.set_defaults(func=cmd_unlock)

    p = sub.add_parser("locks", help="list held locks")
    p.set_defaults(func=cmd_locks)

    p = sub.add_parser("guide", help="read a team guide (lead, member, charter)")
    p.add_argument("name", nargs="?", default="")
    p.set_defaults(func=cmd_guide)

    p = sub.add_parser("tasks", help="list tasks, filters optional")
    p.add_argument("--owner", default="")
    p.add_argument("--team", default="")
    p.add_argument("--status", default="")
    p.set_defaults(func=cmd_tasks)

    p = sub.add_parser("task-new", help="create a task")
    p.add_argument("title")
    p.add_argument("--owner", default="")
    p.add_argument("--team", default="")
    p.add_argument("--status", default="")
    p.add_argument("--blocked-by", default="", dest="blocked_by")
    _add_as(p)
    p.set_defaults(func=cmd_task_new)

    p = sub.add_parser("task-set", help="update a task")
    p.add_argument("id", type=int)
    p.add_argument("--title", default=None)
    p.add_argument("--owner", default=None)
    p.add_argument("--team", default=None)
    p.add_argument("--status", default=None)
    p.add_argument("--blocked-by", default=None, dest="blocked_by")
    _add_as(p)
    p.set_defaults(func=cmd_task_set)

    p = sub.add_parser("task-rm", help="delete a task")
    p.add_argument("id", type=int)
    _add_as(p)
    p.set_defaults(func=cmd_task_rm)

    p = sub.add_parser("overview", help="raw overview JSON")
    p.set_defaults(func=cmd_overview)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
