# ai-wildberries-review-responder

AI-powered auto-responder for Wildberries marketplace customer reviews. Periodically fetches unanswered reviews via Wildberries Feedbacks API, generates replies through an LLM (YandexGPT, OpenAI, or any OpenAI-compatible endpoint such as a local Ollama), and publishes them back.

This chart deploys the responder as a Kubernetes `CronJob` running `src.entrypoints.docker_once` on each tick. It is the K8s-native alternative to the in-container APScheduler mode used by the bare Docker image.

- Source: https://github.com/eslazarev/ai-wildberries-review-responder
- Image: `docker.io/eslazarev/ai-wildberries-review-responder`
- License: MIT

## TL;DR

```bash
helm install wb-responder ./charts/ai-wildberries-review-responder \
  --set secrets.wildberriesApiToken=$WILDBERRIES_API_TOKEN \
  --set secrets.llmApiKey=$LLM_API_KEY
```

## Prerequisites

- Kubernetes 1.21+
- A Wildberries seller API token with access to Feedbacks
- An LLM endpoint reachable from the cluster (OpenAI, YandexGPT via REST, Ollama, etc.)

## Install

```bash
helm install wb-responder oci://ghcr.io/eslazarev/charts/ai-wildberries-review-responder \
  --version 0.1.0 \
  --set secrets.wildberriesApiToken=YOUR_WB_TOKEN \
  --set secrets.llmApiKey=YOUR_LLM_KEY
```

Or from a cloned repo:

```bash
git clone https://github.com/eslazarev/ai-wildberries-review-responder
cd ai-wildberries-review-responder
helm install wb-responder ./charts/ai-wildberries-review-responder \
  --set secrets.wildberriesApiToken=YOUR_WB_TOKEN \
  --set secrets.llmApiKey=YOUR_LLM_KEY
```

## Uninstall

```bash
helm uninstall wb-responder
```

## Values

| Key | Type | Default | Description |
|---|---|---|---|
| `image.repository` | string | `eslazarev/ai-wildberries-review-responder` | Container image repository |
| `image.tag` | string | `""` (uses `Chart.appVersion`) | Image tag |
| `image.pullPolicy` | string | `IfNotPresent` | Pull policy |
| `cronjob.schedule` | string | `*/30 * * * *` | Cron schedule |
| `cronjob.concurrencyPolicy` | string | `Forbid` | Whether overlapping runs are allowed |
| `cronjob.activeDeadlineSeconds` | int | `300` | Per-job deadline |
| `cronjob.ttlSecondsAfterFinished` | int | `3600` | Pod cleanup TTL |
| `command` | list | runs `docker_once` | Container command override |
| `secrets.create` | bool | `true` | Create the API tokens Secret |
| `secrets.existingSecret` | string | `""` | Use a pre-existing Secret instead |
| `secrets.wildberriesApiToken` | string | `""` | **Required** unless `existingSecret` is set |
| `secrets.llmApiKey` | string | `""` | LLM API key; leave empty to skip (e.g. when YC IAM is used) |
| `settings.create` | bool | `true` | Render `settings.yaml` into a ConfigMap |
| `settings.existingConfigMap` | string | `""` | Use a pre-existing ConfigMap with `settings.yaml` key |
| `settings.content` | object | see `values.yaml` | YAML content for `settings.yaml` |
| `extraEnv` | list | `[]` | Additional env vars |
| `extraEnvFrom` | list | `[]` | Additional `envFrom` entries |
| `resources` | object | minimal requests/limits | Pod resource requests/limits |
| `serviceAccount.create` | bool | `true` | Create a ServiceAccount |
| `podSecurityContext` / `securityContext` | object | hardened defaults | Run as non-root, read-only rootfs, no capabilities |

See `values.yaml` for the full list and defaults.

## Configuration patterns

### Use an existing Secret

```yaml
secrets:
  create: false
  existingSecret: my-wb-tokens
```

The Secret must contain at least `WILDBERRIES__API_TOKEN` (and optionally `LLM__API_KEY`) — the keys are loaded via `envFrom`.

### Override settings.yaml

```yaml
settings:
  content:
    wildberries:
      base_url: "https://feedbacks-api.wildberries.ru"
      batch_size: 25
      check_every_minutes: 15
    llm:
      model: "gpt-4o-mini"
      base_url: "https://api.openai.com/v1"
      temperature: 0.2
      max_tokens: 600
      timeout: 15
      instructions: |
        Ты — вежливый сотрудник поддержки реселлера.
      prompt_template: |
        Отвечай на отзыв на том же языке. Тон дружелюбный.
```

### Use Ollama running in-cluster

```yaml
extraEnv:
  - name: LLM__BASE_URL
    value: http://ollama.ollama.svc.cluster.local:11434/v1
  - name: LLM__MODEL
    value: gemma3:4b
  - name: LLM__API_KEY
    value: ollama
```

## Trigger a manual run

```bash
kubectl create job --from=cronjob/wb-responder wb-responder-manual
kubectl logs -l app.kubernetes.io/instance=wb-responder --tail=200 -f
```
