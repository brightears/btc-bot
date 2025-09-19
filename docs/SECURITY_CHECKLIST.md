# Security Checklist

## API Keys
- [ ] Never commit API keys
- [ ] Use read-only keys for monitoring
- [ ] Limit IP whitelist on exchange
- [ ] Enable 2FA on exchange account

## Code Security
- [ ] .env in .gitignore
- [ ] No secrets in logs
- [ ] No secrets in state files
- [ ] Validate all user inputs

## Runtime Security
- [ ] Run with minimal privileges
- [ ] Use systemd security features
- [ ] Regular security updates
- [ ] Monitor for anomalies

## Emergency Procedures
- [ ] Kill switch tested
- [ ] API key revocation plan
- [ ] Incident response contacts
- [ ] Backup access methods