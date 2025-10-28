# Signing & Verification (Ed25519 + SHA-256)

- Use Ed25519 keys (OpenSSH or minisign) to sign releases.
- Hash artifacts with SHA-256 and surface sig8 (first 8 hex).
- Only signed releases are "official". See KEY_POLICY.md.
