# Plan — F2 — Passphrase-only vault (outer lock)

## Active context
- Updated: 2026-07-22
- Spec: `spec.md` · Feature: Feature 2 from `roadmap.md` · Mode: Mode 3 · Phase: complete
  (F2 DONE — all Tasks 1–4; next roadmap: F3)
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

- [x] **Task 3** — Booth chrome for Enroll + Unlock (DOM hooks only) (`src/voicelock/ui/index.html`)
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Enroll panel (name+pass), overwrite-confirm banner, enabled passphrase+Unlock, wrong-passphrase / no-vault / success chips, profile display hooks. Record/Stop/Play unchanged. Bridge calls stubbed for Task 4. Verdict: `2026-07-22-F2-T3.json`.
  - done-criteria:
    - `uv run python -c "from pathlib import Path; t = Path('src/voicelock/ui/index.html').read_text(encoding='utf-8').lower(); assert 'enroll' in t; assert 'passphrase' in t or 'pass-input' in t; assert 'unlock' in t; assert 'wrong passphrase' in t; assert 'no vault yet' in t or 'enroll first' in t; assert 'fonts.googleapis.com' not in t; assert 'fonts.gstatic.com' not in t"` → exit 0
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [x] **Task 4** — Bridge Enroll/Unlock to outer lock + live `~/.voicelock/vault.vl`; `uv run voicelock` end-to-end
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/app.py`, `src/voicelock/ui/index.html`, `tests/test_booth_api.py`
  - notes: BoothApi.enroll/unlock → vault at injectable path (default `~/.voicelock/vault.vl`). Re-enroll needs_confirm unless overwrite. JS overwrite yes re-clicks Enroll. Bridge tests use temp path. Verdict: `2026-07-22-F2-T4.json`. Manual Booth PASS human-attested.
  - done-criteria: FULL list from `spec.md` **Verification** (standing + feature-specific + required manual demo line)
  - feedback:
    - 2026-07-22 human attested **manual PASS** (Booth demo: Enroll → `~/.voicelock/vault.vl` → Unlock right → Unlock wrong REJECT). Re-verify Gate with attestation.
    - 2026-07-22 ESCALATE_HUMAN (subagent Gate): automated `ruff`/`pytest`/`test_vault+outer_lock` all exit 0; scope PASS. Required Manual Booth demo cannot run without human (pywebview). Awaiting **manual PASS** or FAIL notes: `uv run voicelock` → Enroll → `~/.voicelock/vault.vl` → Unlock right → Unlock wrong REJECT.

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-22 — F2 COMPLETE (Mode 3). Outer lock + Booth enroll/unlock shipped.
2. Vault at `~/.voicelock/vault.vl` · PyNaCl Argon2id MODERATE + SecretBox · VLCK.
3. Verdicts F2-T1..T4 on disk · rejects all 0 · lessons none.
4. Next roadmap: F3 — Voiceprint on screen (blocked-by F1 only).
5. Feature-end checkpoint: await human commit/push approval.
