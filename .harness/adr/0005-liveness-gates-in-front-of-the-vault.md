# Liveness gates in front of the vault — zero `vault.py` changes for F8

The AV-capture liveness check (challenge-word match + lip-sync) sits
entirely outside the three nested crypto locks, wrapping `vault.unlock()`
from `app.py`: `BoothApi.unlock()` computes the voice/face embeddings
exactly as before, then runs `_liveness_passes()`
(`challenge.check()` + `lipsync.is_live()`), and only calls `vault_unlock()`
once both pass. A failed liveness attempt makes **zero** calls into the
vault layer — it never learns whether the underlying passphrase/voice/face
would have matched, symmetric with how a wrong passphrase today never
reaches the voice or face checks. This keeps `vault.py`, `outerlock.py`,
`middlelock.py`, and `facelock.py` byte-for-byte unchanged: F8 adds a gate
in front of the existing three-lock peel, not a fourth AEAD layer (ADR
0002 already scoped the liveness gate as symmetric with the three-factor
design at a conceptual level; F8's spec Q6 grilling resolved the exact
ordering, and Task 3 is what implements it).

The main alternative considered — interleaving the liveness check between
individual lock peels, or running it only after the vault opens — was
rejected because either would let a replay attacker learn partial
information (e.g., that the passphrase alone was right, or that voice/face
matched) even while ultimately failing liveness, undermining the gate's
whole point of teaching a replay attacker nothing.

*Recorded at F8 Task 3's completion (2026-07-28). Full reasoning:
`spec.md` (F8) §1 Outcome, §2 Q6 · `plan.md` decision 8.*
