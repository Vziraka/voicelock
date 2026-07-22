# Plan — F2 — Passphrase-only vault (outer lock)

## Active context
- Updated: 2026-07-22
- Spec: `spec.md` · Feature: Feature 2 from `roadmap.md` · Mode: Mode 3 · Phase: implement
  (next: Task 3 — Booth Enroll/Unlock chrome; Tasks 1–2 DONE)
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only when the Gate exited 0 **and** the Reviewer approved.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — Pin approved PyNaCl dependency (`pyproject.toml`, `uv.lock`)
  - state: DONE
  - rejects: 0
  - files: `pyproject.toml`, `uv.lock`
  - notes: Human-approved TECH-PICK (Argon2id + SecretBox). Added via `uv add pynacl` → `pynacl>=1.6.2` / lock 1.6.2. No vault code. Verdict: `2026-07-22-F2-T1.json`.
  - done-criteria:
    - `uv sync` → exit 0
    - `uv run python -c "import nacl; from nacl import pwhash, secret; print(nacl.__version__)"` → exit 0
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [x] **Task 2** — Vault file + outer lock engine (`src/voicelock/vault.py`, outer-lock helpers as needed, `tests/test_vault.py`, `tests/test_outer_lock.py`)
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/vault.py`, `tests/test_vault.py`, `tests/test_outer_lock.py`
  - notes: Injectable `path=` for tests. Layout VLCK+version+opslimit+memlimit+salt+SecretBox. Argon2id MODERATE. Errors: ValidationError / AuthError / NoVaultError ("No vault yet — enroll first"). Default path helper present (live wiring is Task 4). Verdict: `2026-07-22-F2-T2.json`.
  - done-criteria:
    - `uv run pytest tests/test_vault.py tests/test_outer_lock.py -q` → exit 0; final summary reports 0 failed. Must cover, with a temp Vault path: (1) enroll with name + passphrase writes a sealed file whose header starts with magic `VLCK`; (2) unlock with the right passphrase returns the display name; (3) unlock with a wrong passphrase REJECTS (auth failure / error state — no plaintext); (4) enroll with empty name or empty passphrase refuses and does not write a vault; (5) unlock when no vault file exists surfaces a no-vault error suitable for the Booth copy "No vault yet — enroll first".
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [ ] **Task 3** — Booth chrome for Enroll + Unlock (DOM hooks only) (`src/voicelock/ui/index.html`)
  - state: DOING
  - rejects: 0
  - files: `src/voicelock/ui/index.html` (and any split CSS/JS under `src/voicelock/ui/` if extracted)
  - notes: Keep F1 mock layout/branding. Enable Enroll sidebar row → name + passphrase fields (no recording required for enroll). Enable passphrase field + Unlock control. Hooks for success / REJECT status, wrong-passphrase chip on REJECT, post-unlock profile display name, no-vault status copy, and overwrite-confirm before re-enroll. Record / Stop / Play stay as F1 tools. Python bridge wiring is Task 4 — this task only prepares chrome + JS hooks.
  - done-criteria:
    - `uv run python -c "from pathlib import Path; t = Path('src/voicelock/ui/index.html').read_text(encoding='utf-8').lower(); assert 'enroll' in t; assert 'passphrase' in t or 'pass-input' in t; assert 'unlock' in t; assert 'wrong passphrase' in t; assert 'no vault yet' in t or 'enroll first' in t; assert 'fonts.googleapis.com' not in t; assert 'fonts.gstatic.com' not in t"` → exit 0
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [ ] **Task 4** — Bridge Enroll/Unlock to outer lock + live `~/.voicelock/vault.vl`; `uv run voicelock` end-to-end
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py` (BoothApi), `src/voicelock/ui/index.html` (wire hooks), any thin glue under `src/voicelock/`
  - notes: LAST task — Gate runs the FULL Verification list from `spec.md`. Default vault path is `Path.home() / ".voicelock" / "vault.vl"`; re-enroll overwrites only after clear Booth confirm. Wrong passphrase → visible REJECT (status / chip); no vault → "No vault yet — enroll first"; empty enroll inputs → visible validation, no write. After unlock, show enrolled display name in the profile row. Auto-discovered out-of-scope work → `.out-of-scope/`, never build.
  - done-criteria: FULL list from `spec.md` **Verification** (standing + feature-specific + required manual demo line)
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-22 — F2 Task 3 DOING (Booth Enroll/Unlock chrome). Tasks 1–2 DONE.
2. Vault engine ready: `vault.py` + temp-path tests; PyNaCl 1.6.2.
3. Task 3 = DOM hooks only; Task 4 wires bridge + live `~/.voicelock/vault.vl`.
4. Mode 3 blind spot: live Booth enroll → unlock → wrong REJECT (Task 4 Verification).
5. Diff base Task 3: see handoff after DOING commit.
