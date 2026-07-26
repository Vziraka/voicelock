# The middle-lock commitment tag hangs off Argon2id, not a bare hash

The textbook code-offset fuzzy commitment stores `H(s)` — a plain hash of the
secret — beside the helper data so a reconciliation can be checked. F4's secret
is deliberately short (`KEY_BITS = 32`), because the reliable-bit budget buys
more resistance to genuine voice noise as repetition depth than as key length.
Those two choices are incompatible: a stored `sha256(s)` would let anyone who has
already peeled the outer passphrase lock enumerate 2³² candidates in seconds and
recover the middle key, so the middle lock would add no work at all beyond the
outer one. We therefore derive **both** the commitment tag and the SecretBox key
from a single Argon2id stretch of the secret under different info strings, making
each guess cost a memory-hard KDF instead of a hash. The alternative was a longer
secret with shallower repetition, which we rejected because depth is what absorbs
the within-speaker variation the lock exists to survive — and the fixtures
under-represent that variation, so trading depth away would be trading against
the live demo. The cost is one extra Argon2id per unlock (INTERACTIVE parameters;
the outer lock already pays MODERATE), which keeps the whole suite around 11 s.
This is a strengthening inside spec §4's pinned helper-data structure, not a
departure from it: the helper still carries exactly {LSH seed, reliability mask,
XOR offset `P`, `H(s)`}.
