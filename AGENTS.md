# Agent instructions — hermes-youtube-plugin

Shared entry point for AI assistants working in this repository. Keep it
project-specific and safe to publish: no OAuth tokens, channel IDs tied to a
person, machine paths, or local-only notes.

## Read first

1. `README.md` — what the plugin does and how to install it
2. `plugin/README.md` — the in-plugin reference that ships to users
3. `skills/SKILL.md` — the subscription-management procedure the agent follows

## What this plugin is

A Hermes plugin for managing YouTube subscriptions and the uploads feed: list
subscriptions, show recent uploads from followed channels, and identify channels
worth pruning. It uses the official YouTube Data API, reusing the existing Hermes
Google OAuth token (which carries the `youtube.readonly` scope).

Three tools (`youtube_status`, `youtube_subs`, `youtube_feed`), a `/youtube` slash
command, a `hermes youtube` CLI, and an `on_session_start` hook.

This is the smallest of the sibling plugins — read-only by design. Keep it that
way unless there is a clear reason not to.

## Repo layout

`plugin/` is the single source of truth. The live plugin at
`$HERMES_HOME/plugins/youtube` is a **symlink** to it, so editing a file here edits
the running plugin.

| Path | Responsibility |
|---|---|
| `plugin/__init__.py` | `register(ctx)` — tools, slash command, CLI, session hook |
| `plugin/schemas.py` | Tool schemas: what the model reads when choosing a tool |
| `plugin/tools.py` | Tool handlers. JSON string in, JSON string out, never raise |
| `plugin/api.py` | YouTube Data API layer; Google token resolution |
| `plugin/cli.py` | `hermes youtube` argparse tree (CONNECT → subs → feed) |
| `plugin/slash.py` | `/youtube` dispatch, mirroring the CLI verbs |
| `plugin/tables.py` | Plain-text table rendering for chat/CLI output |
| `plugin/debug.py` | Verbose output, off by default |
| `skills/SKILL.md` | The operating skill |
| `requirements.txt` | `google-api-python-client`, `google-auth` |

## Hard rules

1. **Tool handlers return a JSON string and never raise** — success and failure
   alike. They accept `**kwargs`. A handler that raises takes the agent turn down.
2. **Read-only stays read-only.** The declared scope is `youtube.readonly`. Adding
   a write operation (unsubscribe, playlist edit, comment) means a new OAuth scope,
   a re-consent flow for every existing user, and a real risk of destroying
   someone's subscription list. Do not add one as a side effect of another change.
3. **Never print or persist an OAuth token.** Not in output, not in an error, not
   in a debug line.
4. **Paths go through `get_hermes_home()`.** Never a hardcoded `~/.hermes` — each
   Hermes profile owns its own state. `api.py` currently reads the `HERMES_HOME`
   env var directly with a `~/.hermes` fallback; prefer `get_hermes_home()` in new
   code and treat converting the existing read as a welcome small fix.
5. **`youtube_status` is the diagnostic.** It must stay useful when auth is missing
   or the scope is wrong — that is exactly when someone runs it.
6. **YouTube Data API quota is small and unforgiving.** Feed building is the
   expensive path: one call per channel exhausts quota fast on a large subscription
   list. Batch, cap, and surface what was truncated rather than silently returning
   a partial feed as if it were complete.

## Verification

There is no automated test suite in this repo yet. Everything is read-only, so
verification is cheap:

```bash
hermes youtube status     # token + scope + API reachability
hermes youtube subs       # subscription listing, pagination
hermes youtube feed       # the quota-heavy path
```

Watch quota behaviour on `feed` with a realistic subscription count, not with three
channels.

If you add tests, put them in `tests/`, use stdlib + pytest + `unittest.mock` only,
and make no network calls — record API response shapes. Assert behaviour, not
snapshots: a test that freezes a real channel's upload count breaks for reasons
unrelated to this code.

## Working on the live plugin

The live plugin is already a symlink to `plugin/`, so edits here are live. Python
changes need a Hermes restart; skills and docs do not.

**Do not run `./install.sh` in this checkout.** It does `rm -rf "$DEST_DIR"`, which
deletes the dev symlink and replaces it with a copy — after that, your edits here
stop reaching the running plugin, silently. Use `install.sh` only when installing
fresh.

## Contribution style

- One concern per PR. No drive-by reformatting or renames.
- For a bug fix, state the symptom, the exact `file:line` where it manifests, and
  why the change alters that line's behaviour.
- Update `README.md` / `plugin/README.md` / `skills/SKILL.md` in the same PR when a
  command or tool parameter changes.
- Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

## Things to know

- **Adding a model tool is expensive.** Every tool's schema ships on every API call
  the agent makes, whether or not YouTube is involved that turn. With only three
  tools, this plugin is cheap to carry — keep it that way. Prefer a CLI subcommand
  or the skill.
- **`tables.py` exists because raw JSON is unreadable in chat.** Slash and CLI
  output goes through it; tools still return JSON for the model.
- **`skills/SKILL.md` is not auto-registered** — this repo does not call
  `ctx.register_skill()`. Registering it is a deliberate change to `register()`.
- **Sibling plugins share this structure** (`api`/`tools`/`schemas`/`slash`/`cli`/
  `tables`/`debug`). A shared-shaped fix here probably applies to
  `hermes-github-analyzer-plugin`, `hermes-gmail-inbox-plugin`,
  `hermes-linkedin-plugin` and `hermes-linkedin-pages-plugin` too.
