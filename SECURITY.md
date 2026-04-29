# Security Policy

## Reporting a vulnerability

Please **do not open a public GitHub issue** for security problems.

Use GitHub's [private vulnerability reporting](https://github.com/eslazarev/ai-wildberries-review-responder/security/advisories/new) form to send the report. As a fallback, email the maintainer at **elazarev@gmail.com** with subject `SECURITY: ai-wildberries-review-responder`.

When reporting, please include:

- A description of the issue and its impact
- Steps to reproduce (a minimal proof-of-concept is appreciated)
- Affected versions (chart version, Docker image tag, or commit SHA)
- Your suggested mitigation, if you have one

A public disclosure timeline will be agreed jointly. By default a fix is expected to land within 30 days; severe issues are prioritised.

## Supported versions

Only the latest published versions receive security fixes:

| Component | Supported version |
|---|---|
| Docker image `eslazarev/ai-wildberries-review-responder` | `latest` tag |
| Helm chart `ai-wildberries-review-responder` | latest in [GitHub Pages repo](https://eslazarev.github.io/ai-wildberries-review-responder) / [Artifact Hub](https://artifacthub.io/packages/helm/ai-wildberries-review-responder/ai-wildberries-review-responder) |
| Source code | `main` branch |

Older releases are best-effort only.

## Scope

In scope:

- The application code under `src/`
- The Helm chart under `charts/ai-wildberries-review-responder/`
- The published Docker image
- CI/CD workflows under `.github/workflows/`

Out of scope:

- Vulnerabilities in upstream dependencies (please report those to the dependency's maintainer; we track them via Dependabot and apply fixes on a regular cadence)
- Wildberries Feedbacks API and YandexGPT/OpenAI provider issues
- Self-hosted deployments where the operator has changed defaults that weaken security (e.g. running as root, mounting writable rootfs, disabling network policies)

## Hardening defaults

The Helm chart ships with hardened defaults — please file an issue (or, if it is exploitable, a security report) if any of these regress:

- Pod runs as `runAsNonRoot: true`, `runAsUser: 65532`, `fsGroup: 65532`
- Container `readOnlyRootFilesystem: true`, all Linux capabilities dropped, `allowPrivilegeEscalation: false`, `seccompProfile: RuntimeDefault`
- Secrets are loaded from a Kubernetes `Secret` via `envFrom`; tokens are never baked into the image
- The chart never logs the API token; the application's structured logger does not include credentials
