# Security

## Secrets & config
- Store secrets only in `.env` (never commit). Follow 12-factor config where possible.
- `chmod 600 .env` on the server.

## OS/Network
- SSH keys only; consider disabling root SSH; `ufw` restrictive defaults.
- Least privilege: run as `bot` user; restrict filesystem rights.

## Exchange keys
- Use the **minimum** API scopes; add **IP whitelists** where possible.
- Start in DRY-RUN; only enable live trading after a clean 48h dry-run window.

## Logging
- No PII/secret values in logs; prefer IDs over raw payloads.
