# Research — F2 outer-lock crypto candidates

Date: 2026-07-22
Question: Which Python dependency should derive a key from a passphrase and AEAD-seal the profile vault for F2?
Playbook: `formats/source-playbooks/library-evaluation.md`

## Claims

- `cryptography` latest on PyPI is **49.0.0**, uploaded **2026-06-12**. Source: https://pypi.org/project/cryptography/ (fetched 2026-07-22).
- `cryptography` downloads (pypistats): **~1,389,680,389 last month** / **~53,878,324 last day**. Source: https://pypistats.org/packages/cryptography (fetched 2026-07-22).
- `cryptography` docs cover AES-GCM AEAD and password-based KDFs (official docs site). Source: https://cryptography.io/en/49.0.0/ (fetched 2026-07-22).
- `PyNaCl` latest on PyPI is **1.6.2**, released **2026-01-01**. Source: https://pypi.org/project/PyNaCl/ (fetched 2026-07-22).
- `PyNaCl` downloads (pypistats): **~233,320,004 last month** / **~9,437,378 last day**. Source: https://pypistats.org/packages/pynacl (fetched 2026-07-22).
- `PyNaCl` docs: `nacl.pwhash.argon2id.kdf` + SecretBox (libsodium bindings). Source: https://github.com/pyca/pynacl/blob/main/docs/api/pwhash.rst (fetched 2026-07-22); repo last push **2026-04-29**. Source: https://github.com/pyca/pynacl (fetched 2026-07-22).
- Stdlib alone: `hashlib.pbkdf2_hmac` exists, but Python 3.11 has **no** high-level AEAD seal suitable for a vault file without rolling crypto. Treated as non-candidate for seal (learning-demo still needs a real AEAD).

## Liveness bar

- `cryptography`: PASS (2026-06-12 release + massive adoption).
- `PyNaCl`: PASS (2026-01-01 release + large adoption; repo activity 2026-04-29).
- Stdlib-only AEAD: FAIL (no suitable primitive without inventing crypto).

## Fit notes

- Need: passphrase → KDF → AEAD seal/open of an on-disk vault; offline; Python owns crypto.
- `PyNaCl`: one dep covers Argon2id KDF + SecretBox AEAD — tight for a learning stacked-lock demo.
- `cryptography`: broader toolkit (AES-GCM etc.); more API surface to wire by hand; industry default in Python.
- F4 will add an inner lock — either pick still works if we keep the outer seal API thin.

## Delta vs first instinct

First instinct was `cryptography` (most common Python crypto). Research still supports it, but `PyNaCl` is a stronger fit for this demo: Argon2id + box in one package without a second KDF dep.
