# Phase 0 Checkpoint — Linux Host Requested (Stage 1 On Hold)

Date: 2026-09-07
Phase: 0 — Foundation
Status: ACTIVE HANDOFF

## GOAL

Before loading the prepared Stage 1 FRED cadence, verify that this host can
actually run unattended automation. It cannot. This checkpoint records that
finding, the resulting decision to move the persistent host to a Linux
server, and the deployment request written for the sysadmin who manages it.

## SUMMARIZED STATE SHA

`7780a18744b3f623cb12c3567b20b9124b2b4e8c`

This is the exact implementation state summarized by this checkpoint.

## WHAT CHANGED

- Added `docs/operations/LINUX_HOST_DEPLOYMENT_REQUEST.md`: a deployment
  request (written in Russian, for the sysadmin) specifying Docker Engine
  with boot autostart, a non-root service user, ~20 GB across the two named
  volumes, egress limited to the two approved API hosts, zero inbound
  ports, secret handling for the FRED key, backup coverage of both volumes,
  and six open questions about the target environment.
- No code, runtime, or cadence changes. Stage 1 remains exactly as prepared
  by the previous checkpoint: built, live-verified, and **not loaded**.

## VERIFIED

Host capability findings on `Mac-mini-Mihail.local`, all read-only checks:

- **Power settings are correct for a server** — `pmset -g`: `sleep 0`
  (system sleep disabled), `standby 0`, `autorestart 1` (restarts after
  power failure). This part needs no change.
- **Docker Desktop does not autostart** —
  `~/Library/Group Containers/group.com.docker/settings-store.json`
  contains `"AutoStart": false` alongside
  `"AutoStartError": "option disabled because operation is not permitted
  when registering app service"`, indicating a prior attempt to enable it
  did not take.
- **No automatic login is configured** — `defaults read
  /Library/Preferences/com.apple.loginwindow autoLoginUser` reports the
  key does not exist. Login items are only `Blip` and `Google Drive`;
  Docker is not among them.
- **Docker Desktop is the only runtime present** — `colima`, `lima` and
  `podman` are all absent. `/Library/LaunchDaemons` contains only
  `com.docker.socket.plist` and `com.docker.vmnetd.plist`, which are
  Docker Desktop's privileged helpers (socket forwarding, vmnet); they do
  not start the Linux VM that hosts the daemon.

Combined consequence: after any reboot this host reaches the login window,
no user session starts, Docker Desktop therefore never launches, and no
container runs regardless of its `restart: unless-stopped` policy. A
`launchd` LaunchAgent would not fire either, since LaunchAgents require an
active user session. With the gap-check report still unimplemented, such a
failure would be silent.

Facts gathered for the deployment request (measured, not estimated):

- Mean RAW payload size: **647 bytes** (5 files, 3237 bytes total).
- Database size: **8111 kB** at 40 observations.
- `compose.yml` declares **no `ports:` on any service** — nothing is
  published outside the Docker network.
- `src/transport/read_only_http.py` enforces
  `ALLOWED_HOSTS = {"api.exchange.coinbase.com", "api.stlouisfed.org"}`
  and rejects any non-HTTPS scheme, with test coverage.
- `Dockerfile` declares **no `USER`**, so the collector container
  currently runs as root — recorded in the request as something to fix
  before migration.
- `git fetch origin` + `git rev-parse main origin/main` matched
  (`7780a18...`) before this session's edits — no drift.

## UNKNOWN

Everything about the target Linux server, pending the sysadmin's answers:
distribution and version, CPU/RAM, egress filtering policy, existing
backup mechanism, preferred code-delivery method (git clone vs. internal
registry), logging/monitoring requirements, and preferred secret store.
These are the six open questions at the end of the request document.

Also still unknown: whether Stage 1 should be enabled on the Mac mini as
an interim measure while waiting for the server, or held entirely.

## BLOCKERS

- Unattended automation on the current Mac mini host is blocked by the two
  findings above (no Docker autostart, no auto-login). Fixing them would
  require changing macOS login-window security settings, which is the
  owner's decision, not something to change silently.
- Migration to the Linux host is blocked until the server exists and the
  sysadmin's answers arrive.

## DECISIONS

- **Pursue a Linux host with `systemctl enable docker`** rather than
  hardening the Mac mini. A Linux daemon starts at boot with no GUI
  session involved, which removes the entire class of failure found above.
  The owner confirmed a real Linux server and sysadmin are available.
- **Scheduling will live inside the compose stack** as a container with
  `restart: unless-stopped`, not as a host-level cron or systemd timer.
  This keeps the sysadmin's responsibility minimal (Docker + storage +
  egress) and makes the stack portable between hosts. This supersedes the
  `launchd` mechanism decision from the 2026-09-07 cadence-plan checkpoint
  for the Linux target; the `launchd` template remains valid only for the
  Mac mini and is still not loaded.
- The collector container must run as a non-root user before migration.
  Deliberately not changed in this session: the container writes to a
  mounted volume, and altering ownership semantics could break the
  currently verified setup, so it warrants its own verified change.
- The persistent-host decision recorded on 2026-09-06 (Mac mini) is **not
  yet superseded** — it stays in force until a Linux host actually exists
  and is verified, at which point that migration gets its own checkpoint.

## FILES CHANGED

- `docs/operations/LINUX_HOST_DEPLOYMENT_REQUEST.md` (new).
- This checkpoint file.
- `CHECKPOINT_INDEX.json` and `PROJECT_STATE.json` pointers.

## VALIDATION

Read-only host inspection only (`pmset`, `defaults read`, `docker
inspect`, `docker info`, filesystem checks) plus `grep` against committed
source for the security claims quoted in the request. No code changed, so
no test run was warranted; the previous checkpoint's 44/44 suite and three
green CI guards on `7780a18` remain the current validation state.

## SAFETY BOUNDARIES

- `PROJECT_STATE.live_ingestion_allowed` **unchanged, still `false`**.
- No `launchd` job loaded; no scheduler of any kind running. `docker
  compose ps` still shows only `crypto-intelligence-db-1`.
- **No macOS system or security settings were modified.** Auto-login and
  Docker Desktop autostart were inspected only; changing them is left to
  the owner.
- No collection was performed this session — no network fetch, no database
  write.
- No secrets read or transmitted. The request document names the FRED key
  as a requirement but contains no key material.
- The request document is a draft **for the owner to send**; nothing was
  transmitted to any third party from this session.

## ONE NEXT ACTION

Owner sends `docs/operations/LINUX_HOST_DEPLOYMENT_REQUEST.md` to the
sysadmin and reports back the answers to its six open questions, which
unblock preparing the migration. In parallel, decide whether to enable
Stage 1 on the Mac mini as an interim measure — accepting that any reboot
silently stops collection until someone logs in — or to hold Stage 1
entirely until the Linux host is ready. Do not load any scheduler or flip
`live_ingestion_allowed` until that decision is explicit.
