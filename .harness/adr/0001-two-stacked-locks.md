# Two stacked locks (Approach B)

Learning demo needs passphrase and voice to each fail independently and visibly.
We seal the profile vault with an outer passphrase-derived lock and an inner
voice-derived lock (fuzzy-reconciled codeword), instead of using voice only as a
pre-decrypt gate or mixing both into one key. Gate-only would not truly bind voice
to the ciphertext; a combined key would blur which factor failed.
