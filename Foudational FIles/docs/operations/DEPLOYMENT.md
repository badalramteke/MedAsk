# Deployment

Purpose: Defines MediKiosk deployment environments and non-negotiable deployment controls; read before provisioning or releasing an environment.

## Approved environment pattern

| Environment | Purpose | Expected services |
| --- | --- | --- |
| Development | Local implementation and automated tests | Docker/Docker Compose, local/mock providers, synthetic data |
| SIH hackathon demo | Reproducible demonstration under variable connectivity | Local/Colab model path and/or configured online demo APIs; mock integrations where required |
| Hospital production/pilot | Hospital-controlled patient-care deployment | Approved on-prem/edge services, self-hosted Supabase where selected, Redis, encrypted storage, approved providers/integrations |

## Deployment rules

- Use the same core contracts/workflow across environments; configuration selects providers, integration adapters, credentials, and feature availability.
- Use Docker and Docker Compose for development and edge deployment as the approved baseline.
- Keep configuration and secrets outside images/source control; validate required configuration at startup.
- Deploy only versioned, tested artifacts with documented rollback path.
- Health endpoints and logs must not disclose patient data or secrets.
- Never treat a demo mock adapter as a production HIS/ABDM integration.

## Production responsibilities

- A hospital-controlled/self-hosted platform transfers responsibility for security hardening, backup, recovery, monitoring, maintenance, and capacity management to the operator.
- Managed demo services are permitted only where approved; their data handling must be reviewed before use with any patient data.

## Sources

- [Supabase self-hosting guidance](https://supabase.com/docs/guides/self-hosting) notes that self-hosted operators own security, maintenance, backups, disaster recovery, monitoring, and availability.
- [CERT-In secure application guidelines](https://www.cert-in.org.in/PDF/Application_Security_Guidelines.pdf) support security through design, development, audit, deployment, and operations.

→ For recovery, see `docs/operations/INCIDENT_RECOVERY.md`.

## Open Questions

- Production hardware/network, domain/TLS setup, CI/CD, container registry, model-serving capacity, backup tooling, monitoring platform, and rollout/rollback procedure are pending.
