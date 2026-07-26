# F4 — Fuzzy reconcile: turning a noisy voiceprint into a stable key

Research date: 2026-07-23. Liveness bar: a release OR commit since ~2025-07 (~12 months). Gray zone = FAIL = `unconfirmed`.
All library facts below are from PRIMARY sources (PyPI JSON API, GitHub commits API, pypistats API, official docs) fetched 2026-07-23.

## 1. The construction (code-offset fuzzy commitment / secure sketch)

- The standard construction is the **code-offset fuzzy commitment** (Juels & Wattenberg, 1999) — a.k.a. the code-offset secure sketch in the fuzzy-extractor framework (Dodis, Ostrovsky, Reyzin, Smith, 2004/2008). This is a RECOGNIZED, named construction, not invented. — background, standard textbook crypto.
- Enroll: binarize the reference embedding to an n-bit string `b`; pick a random secret `s`; ECC-encode `s` to an n-bit codeword `c = Encode(s)`; publish non-secret helper `P = b XOR c`. Store `H(s)` (a hash) beside the vault to verify a reconciliation succeeded.
- Unlock: binarize the fresh embedding to `b'`; compute `b' XOR P = b' XOR b XOR c = c XOR e`, where `e = b XOR b'` is the bit-flip error pattern; ECC-decode recovers `c` (hence `s`) iff Hamming weight of `e` <= the code's correction capacity `t`. A different speaker produces a large `e` (beyond `t`), so decode fails / yields the wrong `s` (caught by `H(s)` mismatch).
- The recovered `s` (or `H(s)`) is the stable secret; feed it into HKDF/Argon2id -> PyNaCl SecretBox key for the middle lock. This matches our intended pipeline exactly.
- Binarization is typically done by (a) **sign bits** of each coordinate (threshold at 0 or at a per-dimension median learned at enrollment), or (b) **random-hyperplane LSH / SimHash**: draw m fixed random Gaussian vectors r_i, bit_i = sign(<x, r_i>). LSH lets you generate MORE bits than the 192 dimensions (m projections) from one seed stored as helper data. — Charikar SimHash / Goemans-Williamson rounding, standard.
- Key quantitative property of SimHash: for L2-normalized vectors, P(bit differs) = theta/pi where theta is the angle between the two embeddings. — Charikar 2002 (standard result).

### The 192-bit budget problem (verified by arithmetic on OUR measured separation)
- Same-speaker cosine distance <= 0.29 => cosine similarity >= 0.71 => angle = arccos(0.71) ~= 44.7deg = 0.780 rad => per-bit flip prob ~= 0.780/pi ~= **0.248** (genuine BER ~25%). Expected Hamming distance over 192 bits ~= 47.6 flips.
- Different-speaker cosine ~0.83 => similarity ~0.17 => angle = arccos(0.17) ~= 80.2deg = 1.40 rad => per-bit flip prob ~= **0.446** (impostor BER ~45%). Expected Hamming ~= 85.6 flips over 192 bits.
- Consequence: a genuine match already flips ~25% of bits. A BCH code at the nearest primitive length n=255 (m=8) obeys redundancy (n-k) <= m*t = 8t; correcting t=48 errors needs 384 redundancy bits > 255 — **impossible**. Even t=25 (13% BER) leaves k=55. So raw sign bits give a genuine error rate too high for any code to both correct genuine noise AND carry a usable-length key AND reject impostors (only a ~20-point BER margin genuine-vs-impostor).
- What people actually do to fix this (all recognized): (1) **reliability / reliable-component selection** — keep only bits whose |projection| is large (far from the threshold), discarding noisy near-threshold bits, which drops genuine BER to ~10-15%; (2) **LSH bit expansion** — project 192 dims to 512-1024 bits so there is redundancy AND key-entropy budget (note: expansion raises the ABSOLUTE error count but NOT the error FRACTION, so it must be paired with reliability selection); (3) **multi-enrollment averaging** of several reference embeddings before binarizing; (4) concatenated codes (e.g. repetition inner + BCH/RS outer, as in Hao-Anderson-Daugman iris fuzzy commitment). — standard biometric-cryptosystem literature.
- Honest bottom line for construction: the ECC library is NOT the hard part or the main learning value; the binarization + reliability selection is. 192 raw sign-bits alone are too few/too noisy for a strong key.

## 2. ECC library candidates (liveness verified 2026-07-23)

### galois — PASS (live)
- Latest version 0.4.11, uploaded 2026-05-02T18:21:26Z. — https://pypi.org/pypi/galois/json (fetched 2026-07-23)
- Most recent GitHub commit 2026-05-03T14:03:27Z ("Fix typo"). — https://api.github.com/repos/mhostetter/galois/commits (2026-07-23)
- Downloads last month: 254,593. — https://pypistats.org/api/packages/galois/recent (2026-07-23)
- requires_python >=3.7; depends on numpy>=1.21.0, numba>=0.55, typing_extensions>=4.0.0; wheels provided. — https://pypi.org/pypi/galois/json (2026-07-23)
- Provides real binary BCH over GF(2): `galois.BCH(n, k)`, and `decode(..., errors=True)` returns (message, number_of_corrected_errors). — https://mhostetter.github.io/galois/latest/api/galois.BCH/ (2026-07-23)
- Offline/Windows/Py3.11 feasibility: OK. numba 0.66.0 requires numpy<2.5,>=1.22 (— https://pypi.org/pypi/numba/json 2026-07-23), and our lock pins numpy 2.2.6 (pyproject numpy>=2.0,<2.3; uv.lock numpy==2.2.6) so no numpy conflict. Cost: drags in numba + llvmlite (heavy native deps, but reliably wheeled for win/py3.11).
- Fit: excellent BCH API with error-count reporting (ideal for a code-offset demo), best docs/adoption of the live options.

### komm — PASS (live, freshest)
- Latest version 0.31.0, uploaded 2026-07-05T20:20:51Z. — https://pypi.org/pypi/komm/json (2026-07-23)
- Downloads last month: 4,810. — pypistats komm (WebFetch 2026-07-23; API was rate-limited but the docs/PyPI recency confirm active).
- requires_python >=3.10; depends only on numpy>=2.1.1, tqdm>=4.67.0, typeguard>=4.4.3; wheels provided. — https://pypi.org/pypi/komm/json (2026-07-23)
- numpy>=2.1.1 is satisfied by our numpy 2.2.6 — no conflict, and NO native/numba dep (much lighter than galois).
- Provides `BCHCode(mu, delta)`: length n=2^mu-1, narrow-sense primitive BCH. — https://komm.dev/ref/BCHCode/ (2026-07-23)
- Error-correcting DECODE confirmed: BlockCode has no decode() method, but komm ships a separate `BerlekampDecoder` for BCH/RS (bounded-distance decoding). — https://komm.dev/ref/BlockCode/ (2026-07-23)
- License: GPL-3.0 (viral copyleft). — https://pypi.org/pypi/komm/json (2026-07-23). Fine for a private learning demo, but flag it if the repo is ever distributed.
- Fit: BCH with real decoder, lightest dependency footprint of the live options, freshest release. BCH parameterized by (mu, delta) rather than direct (n, k) — slightly less ergonomic; lower adoption/docs maturity than galois.

### reedsolo — FAIL the liveness bar (but massive adoption)
- Latest STABLE version 1.7.0, uploaded 2023-01-17T05:10:17Z; newest artifact of ANY kind is pre-release 2.0.31b1, uploaded 2023-04-09 (earlier 2.0.x releases yanked). — https://pypi.org/pypi/reedsolo/json (2026-07-23)
- Most recent GitHub commit 2025-05-05T23:35:21Z ("Bump v2.1.3b1"). — https://api.github.com/repos/tomerfiliba-org/reedsolomon/commits (2026-07-23)
- Liveness verdict: 2025-05-05 commit is ~14.5 months before today and BEFORE the ~2025-07 bar; newest PyPI artifact is ~39 months old. This is a GRAY ZONE -> record as `unconfirmed`/FAIL by the strict bar, DESPITE huge adoption (2,767,333 downloads last month — https://pypistats.org/api/packages/reedsolo/recent 2026-07-23). Universal py3-none-any wheel, pure-Python fallback + optional Cython. — PyPI JSON 2026-07-23.
- Fit: Reed-Solomon is SYMBOL-based (bytes), awkward for a bit-level Hamming fuzzy commitment; you would treat the XOR error pattern as symbol errors, which inflates the error count (one flipped bit corrupts a whole symbol). Not the natural choice here.

### bchlib — FAIL the liveness bar
- Latest version 2.1.3, uploaded 2024-08-06T05:40:17Z; most recent GitHub commit 2024-09-12T14:18:57Z. — https://pypi.org/pypi/bchlib/json and https://api.github.com/repos/jkent/python-bchlib/commits (2026-07-23). Both are ~22-23 months old -> outside the ~12-month bar -> FAIL.
- Downloads last month: 43,194. — https://pypistats.org/api/packages/bchlib/recent (2026-07-23).
- It is a C EXTENSION (wrapper over the Linux-kernel BCH lib), requires a compiler unless a matching wheel exists; wheels are published for manylinux/macOS/Windows py3.10-3.11. — https://pypi.org/pypi/bchlib/json (2026-07-23).
- Fit: bchlib is the "classic" fuzzy-commitment BCH choice, and it does have Windows py3.11 wheels, BUT it fails our liveness bar (stale ~22mo) and adds a native build/wheel dependency. Do not pick it.

### unireedsolomon — FAIL (effectively dead)
- Latest version 1.0.6, uploaded 2023-04-15T01:17:01Z; most recent commit 2023-05-07T09:12:14Z. — https://pypi.org/pypi/unireedsolomon/json and https://api.github.com/repos/lrq3000/unireedsolomon/commits (2026-07-23). ~38 months old -> FAIL.
- Downloads last month: 325. — https://pypistats.org/api/packages/unireedsolomon/recent (2026-07-23). Pure-Python, no deps, but negligible adoption and dead. Also RS/symbol-based (same mismatch as reedsolo). Do not pick.

### Live pure-Python-only options
- Of the candidates, komm (numpy-only, no native code) is the closest to "live + light + BCH." galois is live but pulls native numba/llvmlite. reedsolo/unireedsolomon are the only truly dependency-free pure-Python options but both FAIL the liveness bar and are RS (symbol) not BCH (bit).

## 3. "Build it by hand" — pure-numpy repetition / majority-vote code (no new dep)

- A repetition code (repeat each secret bit r times, decode by majority vote) is the simplest RECOGNIZED ECC and a legitimate code-offset inner code — repetition inner codes appear in real biometric fuzzy-commitment schemes. It is defensible for a learning demo and needs ZERO new dependency (numpy is already present; XOR + reshape + majority is trivial).
- Limits given our budget (genuine per-bit flip p~=0.25 on raw sign bits):
  - r=5: P(a key bit majority-decodes wrong) = P(Binomial(5,0.25) >= 3) ~= 0.104. For a k-bit key, all-correct prob = (1-0.104)^k -> for k=128 this is ~1e-6 (unusable).
  - r=7: block error ~= 0.071; 192 sign bits give only floor(192/7) ~= 27 key bits, and all-correct prob 0.929^27 ~= 0.14 (unusably high genuine reject rate).
  - To repeat a 128-bit key even 7x needs 896 bits, but we only have 192 sign bits — so pure repetition on the raw 192 bits CANNOT deliver both a strong key and a low genuine-reject rate.
- Honest verdict: "no new dependency via repetition" IS realistic ONLY if paired with (a) seeded LSH/Gaussian projection in numpy to expand to ~512-1024 bits (no dep) and (b) reliability masking to push genuine BER down to ~10-15%. Then a modest repetition code works and yields a modest (tens-of-bits) guessing-entropy secret — which is FINE for a labeled learning demo and is stretched through Argon2id/HKDF anyway. Pure repetition on raw 192 sign-bits, with no expansion/masking, is NOT realistic.

## 4. Recommendation

Hand-roll the code-offset fuzzy commitment in pure numpy (no new dependency) as the primary path, and reserve a named-BCH dependency (komm) only if the writeup needs a "recognized ECC library" for credibility. See paragraph below.

## Delta vs first instinct
- First instinct was "use bchlib — it's the classic BCH library for fuzzy commitment." Research killed that: bchlib FAILS our liveness bar (last release 2024-08, last commit 2024-09, ~22 months stale) and is a native C extension. Wrong pick.
- Second instinct was "reedsolo, it's everywhere (2.7M downloads/month)." Also wrong: its newest artifact is 2023 and newest commit 2025-05-05 is just OUTSIDE the 12-month bar (gray zone -> `unconfirmed`), AND Reed-Solomon is symbol-based, a poor fit for a bit-level Hamming fuzzy commitment.
- Surprise: the two libraries I did NOT expect to lead — galois (2026-05) and komm (2026-07) — are the only ones that PASS liveness, and komm is numpy-only (lighter than galois's numba/llvmlite).
- Bigger surprise: the ECC library is not the real problem at all. The 192-dim -> sign-bit binarization gives a ~25% genuine bit-error rate, which no code can absorb while still carrying a key. The actual work (and learning value) is LSH bit-expansion + reliability selection, which is pure numpy. That reframes the whole task away from "pick an ECC lib" toward "hand-roll the binarizer + a simple code, no dep."

## Final recommendation (one paragraph)
For THIS offline, pure-Python, learning demo, hand-roll the construction in numpy and add NO new dependency. Implement the recognized code-offset fuzzy commitment directly: a seeded random-hyperplane LSH projection (numpy) to binarize and expand the 192-dim embedding to a few hundred bits, a per-dimension reliability mask (keep the most stable bits, stored as non-secret helper data) to pull the genuine bit-error rate down toward ~10-15%, and a simple repetition/majority-vote inner code as the ECC — all of which is a standard, citable construction and keeps the offline/pure-python/no-extra-wheel constraints trivially satisfied while making the honest demo-grade limitations (modest key entropy, tunable ACCEPT/REJECT via the correction radius) easy to explain. The ECC library is not where the difficulty or the learning lives, so a new dependency is NOT needed. IF the team wants a "recognized named BCH library" in the writeup for credibility, add exactly one dependency — komm (live 2026-07-05, numpy-only, ships a real BerlekampDecoder for BCH) as the pick, with galois (live 2026-05, cleaner BCH(n,k)/decode(errors=True) API but heavier via numba/llvmlite) as the runner-up; avoid bchlib and reedsolo as both fail the liveness bar.

## TECH-PICK (only if a named BCH dependency is warranted)

| Candidate | Live? (quoted evidence, 2026-07-23) | Fits our stack because | Cost / risk |
|---|---|---|---|
| **komm 0.31.0** (PICK) | PASS — uploaded 2026-07-05T20:20:51Z (pypi.org/pypi/komm/json) | numpy-only dep chain (numpy>=2.1.1 satisfied by our 2.2.6) + tqdm + typeguard, NO native code; provides `BCHCode` + separate `BerlekampDecoder` for real bounded-distance BCH decoding; pure-wheel offline install on Win/py3.11 | GPL-3.0 viral license (fine for private demo, flag if distributed); BCH parameterized by (mu, delta) not (n,k); lower adoption (~4.8k downloads/mo) and thinner docs than galois |
| **galois 0.4.11** (runner-up) | PASS — uploaded 2026-05-02T18:21:26Z; commit 2026-05-03T14:03:27Z (pypi + github API) | Clean `galois.BCH(n, k)` and `decode(errors=True)` returning corrected-error count (ideal for tuning the fuzzy-commitment radius); strong docs; 254,593 downloads/mo | Drags in numba + llvmlite (heavy native deps, but reliably wheeled; numba 0.66 allows numpy<2.5 so 2.2.6 is OK) — larger offline wheel set than komm |
| bchlib 2.1.3 | FAIL — last release 2024-08-06, last commit 2024-09-12 (~22mo stale) | (classic BCH choice, has Win py3.11 wheels) | Fails liveness bar; native C extension | 
| reedsolo 1.7.0 / 2.0.31b1 | FAIL/`unconfirmed` — newest artifact 2023-04, newest commit 2025-05-05 (~14.5mo, before the bar) | (huge adoption 2.77M/mo, pure-python wheel) | Fails liveness bar; Reed-Solomon is symbol-based, poor fit for bit-level Hamming fuzzy commitment |
| unireedsolomon 1.0.6 | FAIL — last release 2023-04-15, last commit 2023-05-07 (dead) | (pure-python, zero deps) | Dead; 325 downloads/mo; RS/symbol-based |
