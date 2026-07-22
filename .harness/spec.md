# Spec: F2 — Passphrase-only vault (outer lock)

Feature: Feature 2 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  ```
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns
  zero hits in this file)
  ```
- [x] Approved by human

- **Mode:** Mode 3

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks
it, no matter what was said in chat.

The Mode line is set by the human; checking box 2 approves the spec AND the
mode together (Mode 2 is the default if the human states no preference).
Mode 4 may only be set if a prior feature in this repo completed cleanly at
Mode 3 or 4. Lowering the mode mid-feature is allowed (edit this line + log it
in `memory/deviations.md`); raising it mid-feature is never allowed — a raise
is a spec amendment needing a fresh box-2 approval.

## 1. Outcome

Ship the **outer lock**: enroll with a display **name** and **passphrase**, derive
an encryption key from the passphrase, and seal a **Vault** file on disk.
Unlock peels that outer lock with the passphrase so the profile payload is
readable again. Wrong passphrase must **REJECT** visibly (no silent failure,
no crash).
Demo: enroll → on-disk file is sealed → right passphrase opens → wrong
passphrase REJECT.
Voice / inner lock / challenge are still out — F2 is passphrase-only.

## 2. Grilling record — ambiguity scan

**Status: CLEAR**


| Category                                  | Verdict | Resolved by                                        |
| ----------------------------------------- | ------- | -------------------------------------------------- |
| Functional scope & behavior               | Clear   | name+pass enroll · mock unlock · wrong REJECT      |
| Domain & data model                       | Clear   | ~/.voicelock/vault.vl · name payload · VLCK header |
| Interaction & UX flow                     | Clear   | wire mock Enroll + passphrase Unlock               |
| Non-functional (perf, security)           | Clear   | offline · PyNaCl · Argon2id MODERATE               |
| Integration & dependencies                | Clear   | PyNaCl (human-approved TECH-PICK)                  |
| Edge cases & failure modes                | Clear   | empty refuse · no-vault copy · overwrite confirm   |
| Completion signals (how we know it works) | Clear   | Verification · Mode 3 live Booth check             |
| Terminology (matches `CONTEXT.md`)        | Clear   | Vault · Outer lock · Enroll · Booth · Impostor     |


Answers from grilling are written back into the matching section of THIS file —
never into a side file. Mark anything still open inline where it belongs, using
the marker token: open square bracket, `NEEDS-CLARIFICATION`, a colon, then the
question. The colon form is what the mechanical check greps for — prose that
merely *mentions* the marker (like this paragraph) never uses the colon form,
so any hit is a real unresolved question.

## 3. Non-goals

- No inner lock, voiceprint, fuzzy reconcile, helper data, or voice-gated unlock.
- No challenge-response / liveness / replay defense (F5).
- No multi-device sync, cloud, network, accounts, or recovery when passphrase is lost.
- Not a shippable security product; no FAR/FRR or certification claims.
- No packaging/installer polish beyond `uv run voicelock`.
- No redesign of Booth chrome — keep F1 mock layout; wire only what F2 needs.
- No voice recording required at enroll in F2 (recording stays an F1 Booth tool).
- Out-of-scope discoveries during Mode 3+: record in `.out-of-scope/`, never build.



## 4. Constraints

- Honor `constitution/project.md` + `constitution/topics/conventions.md`:
Python 3.11 + uv; code in `src/voicelock/`; UI in `src/voicelock/ui/`;
tests in `tests/`; Python owns crypto/state; JS owns rendering only; offline-only.
- Entry point remains `uv run voicelock` (Booth window).
- Outer lock: passphrase → Argon2id KDF → SecretBox AEAD seal of the Vault on
disk; unlock decrypts with the same passphrase. Salt (and any non-secret
header) stored with the Vault file so unlock is deterministic for the right
passphrase.
- Crypto: **PyNaCl** (human-approved TECH-PICK). Argon2id + SecretBox.
Research: `memory/research/2026-07-22-f2-outer-lock-crypto.md`.
- Argon2id cost: **OPSLIMIT_MODERATE** / **MEMLIMIT_MODERATE** (demo-snappy;
params stored in the Vault header so unlock uses the same cost).
- Vault location: **single profile only** for F2. Fixed path
`Path.home() / ".voicelock" / "vault.vl"` (i.e. `~/.voicelock/vault.vl`).
Re-enroll overwrites that file after a clear confirm in the Booth.
On-disk layout (one file): magic `VLCK` + version byte + salt + ciphertext.
- Enroll inputs: **name + passphrase only** (no recording required).
- Sealed plaintext payload: structured profile with at least the display **name**
(UTF-8); leave room in the schema for later fields, but F2 does not store
audio bytes.
- Booth UX: wire the existing mock chrome —
  - **Enroll** sidebar row → name + passphrase → seal Vault;
  - enable the passphrase field + **Unlock**;
  - show success / REJECT in status (and wrong-passphrase chip on REJECT);
  - after unlock, show the enrolled display name in the profile row;
  - Record / Stop / Play remain available as F1 tools (not part of enroll).
- Unlock with no Vault file present: visible status
**"No vault yet — enroll first"**; do not crash.
- Wrong passphrase: visible REJECT in the Booth (status / chip / message); Vault
stays sealed; no crash.
- Empty or missing name/passphrase at enroll: refuse enroll with a visible
validation message (do not write a vault).
- Mode 3 blind spot (Verification check, not waived): automated tests prove the
Python vault/outer-lock path with a temp file path; they do not drive the live
pywebview Booth. The required manual demo line below covers enroll → on-disk
`~/.voicelock/vault.vl` → unlock → wrong-passphrase REJECT in the real Booth.
- Out-of-scope discoveries during Mode 3: record in `.out-of-scope/`, never build.
- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
`uv run pytest` → exit 0.
- No new dependency without human-approved TECH-PICK recorded here +
`memory/decisions.md`.



## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Two parts, both required.
Harness rules find this section by its NAME ("Verification"), never by number —
keep the word "Verification" in the heading if sections are added or reordered.
(This FULL list gates the feature's LAST task; intermediate tasks gate on their
`plan.md` done-criteria — see the universal [Done] rule.)

Runtime budgets: any command expected to run longer than the 10-minute default
must declare its budget here. The verifier waits in the foreground either way;
exceeding the budget is a FAIL, never a kill.

Mode-scaled requirements: at Mode 2+, every command here must be runnable with
pinned expectations — pinned means: the exact command, its exact expected exit
code, and any expected output stated in the line (nothing left to judgment). At
Modes 3–4, additionally every task's planned done-criteria must be runnable (no
judgment-worded criteria), and this spec must state what the agent does with
discovered out-of-scope work (default: record it in `.out-of-scope/`, never build).

Standing (the project's full regression net, from `project.md`):

- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed)

Proof surface: feature-specific commands must prove behavior at the highest
real surface the feature touches — the actual UI, CLI, or API (a script that
drives the real thing counts). If that surface cannot be checked, record the
exact limitation here; never let a proxy check silently stand in for it.

Limitation (automated): the Gate does not drive the real pywebview window.
Python outer-lock enroll/unlock/reject are proven with a temp Vault path; the
live Booth path to `~/.voicelock/vault.vl` is proven only by the manual line
below (required Verification check — not accepted risk).

Feature-specific (proves THIS feature works):

- `uv run pytest tests/test_vault.py tests/test_outer_lock.py -q` → exit 0;
final summary reports 0 failed. These modules must cover, with a temp Vault
path (not the live home path): (1) enroll with name + passphrase writes a
sealed file whose header starts with magic `VLCK`; (2) unlock with the right
passphrase returns the display name; (3) unlock with a wrong passphrase
REJECTS (auth failure / error state — no plaintext); (4) enroll with empty
name or empty passphrase refuses and does not write a vault; (5) unlock when
no vault file exists surfaces a no-vault error suitable for the Booth copy
"No vault yet — enroll first".
- Manual (required for F2 done — Verification check): run `uv run voicelock`,
then Enroll (name + passphrase) → confirm
`Path.home() / ".voicelock" / "vault.vl"` exists and is non-empty → Unlock
with the right passphrase (profile name appears / success status) → Unlock
attempt with a wrong passphrase shows visible REJECT (status / chip).
Observable: sealed on-disk Vault; right passphrase opens; wrong passphrase
REJECT in the live Booth.

---

*Spec-anchored: if requirements change mid-build with human approval, this is
the amendment path — ALL of it, in order: (1) update this file, (2) re-run the
ambiguity scan on the changed sections, (3) the human re-checks box 2 (an
amended spec is a new contract — the old approval does not carry over),
(4) re-plan the affected tasks via the* `plan` *skill before building against
the change.*