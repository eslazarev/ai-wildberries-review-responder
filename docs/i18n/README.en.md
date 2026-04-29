# AI-powered customer review responder for Wildberries

🌐 [Русский](../../README.md) · **English** · [简体中文](README.zh-CN.md) · [Türkçe](README.tr.md) · [Қазақша](README.kk.md) · [Oʻzbekcha](README.uz.md)

<img src="https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/main/.github/images/wildberries-ai-review-service.gif">

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/ai-wildberries-review-responder)](https://artifacthub.io/packages/search?repo=ai-wildberries-review-responder)
[![Docker Pulls](https://img.shields.io/docker/pulls/eslazarev/ai-wildberries-review-responder)](https://hub.docker.com/r/eslazarev/ai-wildberries-review-responder)
![License](https://img.shields.io/badge/license-MIT-blue)

This service automatically picks up new reviews from your Wildberries seller dashboard, generates a reply through an LLM, and posts it back. It is designed for Yandex Cloud Functions but also runs locally or in Docker, and can be deployed to any Kubernetes cluster via the published Helm chart.

## Key features
- **Full control over your Wildberries API token — no token sharing with third parties.**
- Trivial setup and deployment to Yandex Cloud Functions through the Serverless Framework.
- Customisable prompts — fully control how the model phrases its replies.
- Periodic processing of new reviews without a long-running server.
- Works with YandexGPT and any OpenAI-compatible API (OpenAI, Ollama, vLLM, etc.).
- Configuration via YAML and environment variables.
- Multiple deployment modes: Yandex Cloud Functions, Docker, Kubernetes (Helm), local.

## How it works
1. On a schedule, the function fetches the list of unanswered reviews from Wildberries.
2. Each review is rendered into an individual prompt for the LLM, including review details and presence of attached photos/videos.
3. The LLM generates a reply in the right tone and language.
4. The reply is posted back via the Wildberries Feedbacks API.

## Cost
- The code is free and open source.
- Operational cost depends on cloud, model, and review volume.
- Yandex Cloud Functions: billed per execution time and memory.
- YandexGPT or OpenAI: billed per token.
- Wildberries Feedbacks API: free within seller-account limits.

Production measurements show ≈ **0.25 RUB per review**. The screenshot below shows two days during which ≈100 reviews were answered.

![Yandex Cloud cost example](../../.github/images/yandex_cloud_cost.png)

## Quick start

If you already have everything set up (YC, access, tokens), just run:

```bash
npm install
WILDBERRIES__API_TOKEN='your_wb_token' serverless deploy
```

This builds and deploys the function to Yandex Cloud Functions and configures the cron trigger.

Optionally pass an LLM key or change the schedule:

```bash
LLM__API_KEY='your_llm_api_key' WILDBERRIES__API_TOKEN='your_wb_token' serverless deploy
WILDBERRIES__CHECK_EVERY_MINUTES='15' WILDBERRIES__API_TOKEN='your_wb_token' serverless deploy
```

## Prerequisites

### Tools
- Python 3.12+ and `pip` for local runs and tests.
- Node.js 18+ and `npm` for the Serverless Framework.
- The `yc` CLI for Yandex Cloud.

### Wildberries API token
1. In your seller dashboard open *Profile → Settings → API access → Reviews and Q&A*.
2. Create a new key and pass it as `WILDBERRIES__API_TOKEN`.
3. Token docs: <https://dev.wildberries.ru/openapi/api-information>

### Access to YandexGPT or OpenAI
- For YandexGPT inside Yandex Cloud Functions you need a service account with the `ai.languageModels.user` role (defined in `serverless.yml`).
- Inside Cloud Functions you can leave `LLM__API_KEY` unset — the function picks up the IAM token from `context.token` if the key is empty or `null`.
- For OpenAI or any OpenAI-compatible API set `LLM__API_KEY`, `LLM__MODEL`, and `LLM__BASE_URL`.

### Local model via Ollama
Free local models work out of the box through [Ollama](https://ollama.com), which exposes an OpenAI-compatible API at `http://localhost:11434/v1`.

```yaml
llm:
  base_url: "http://localhost:11434/v1"
  model: "gemma3:4b"
  api_key: "ollama"
```

## Configuration

### `settings.yaml`
This file is the source of truth unless overridden by environment variables.

```yaml
wildberries:
  base_url: "https://feedbacks-api.wildberries.ru"
  request_timeout: 10
  batch_size: 10
  check_every_minutes: 30

llm:
  model: "gpt://{FOLDER_ID}/aliceai-llm/latest"
  base_url: "https://rest-assistant.api.cloud.yandex.net/v1"
  temperature: 0.3
  max_tokens: 600
  instructions: "..."
  prompt_template: "..."
  timeout: 10
```

`{FOLDER_ID}` is auto-substituted in Yandex Cloud Functions.

### Environment variables
Variables follow the nested-key convention with `__` as separator:

- `WILDBERRIES__API_TOKEN` — required.
- `WILDBERRIES__BASE_URL`, `WILDBERRIES__REQUEST_TIMEOUT`, `WILDBERRIES__BATCH_SIZE`, `WILDBERRIES__CHECK_EVERY_MINUTES`.
- `LLM__API_KEY` — leave empty in YC Functions to use the IAM token.
- `LLM__MODEL`, `LLM__BASE_URL`, `LLM__TEMPERATURE`, `LLM__MAX_TOKENS`, `LLM__INSTRUCTIONS`, `LLM__PROMPT_TEMPLATE`, `LLM__TIMEOUT`.

### Source priority
Env vars → `.env` → file secrets → `settings.yaml`. YAML provides safe defaults; env always wins.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

One-shot iteration:
```bash
export WILDBERRIES__API_TOKEN='your_wb_token'
export LLM__API_KEY='your_llm_api_key'
python -m src.entrypoints.docker_once
```

Local cron mode:
```bash
export WILDBERRIES__API_TOKEN='your_wb_token'
python -m src.entrypoints.docker_cron
```

The interval is taken from `wildberries.check_every_minutes`.

## Yandex Cloud Functions (Serverless)

Install Yandex CLI: <https://cloud.yandex.com/docs/cli/quickstart>

```bash
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
yc init
```

Build & deploy:
```bash
npm install
WILDBERRIES__API_TOKEN='your_wb_token' serverless deploy
```

Remove all resources:
```bash
serverless remove
```

## Docker

```bash
docker pull eslazarev/ai-wildberries-review-responder:latest
```

One-shot run:
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='your_wb_token' \
  -e LLM__API_KEY='your_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest src.entrypoints.docker_once
```

Scheduled run inside the container:
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='your_wb_token' \
  -e WILDBERRIES__CHECK_EVERY_MINUTES='15' \
  -e LLM__API_KEY='your_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest
```

## Kubernetes (Helm chart)

The chart provisions a Kubernetes-native `CronJob` running `docker_once` on each tick, plus a `ConfigMap` with `settings.yaml` and a `Secret` with the API tokens. Published to [Artifact Hub](https://artifacthub.io/packages/helm/ai-wildberries-review-responder/ai-wildberries-review-responder).

```bash
helm repo add wb-responder https://eslazarev.github.io/ai-wildberries-review-responder
helm repo update
helm install wb-responder wb-responder/ai-wildberries-review-responder \
  --namespace wb-responder --create-namespace \
  --set secrets.wildberriesApiToken=$WILDBERRIES_API_TOKEN \
  --set secrets.llmApiKey=$LLM_API_KEY
```

Manual run:
```bash
kubectl create job --from=cronjob/wb-responder-ai-wildberries-review-responder manual -n wb-responder
kubectl logs -n wb-responder -l app.kubernetes.io/instance=wb-responder --tail=200 -f
```

Common values:
- `cronjob.schedule` — cron expression, default `*/30 * * * *`.
- `secrets.existingSecret` — point to a pre-existing `Secret` instead of generating one.
- `settings.content` — full `settings.yaml` mounted into the pod; tune prompts and timeouts from the release.
- `extraEnv` / `extraEnvFrom` — extra env vars (e.g. `LLM__BASE_URL` for in-cluster Ollama).
- `resources`, `nodeSelector`, `tolerations`, `affinity`, `podSecurityContext` — pod tuning.

Full reference: [`charts/ai-wildberries-review-responder/README.md`](../../charts/ai-wildberries-review-responder/README.md). The pod runs as non-root with a read-only rootfs and dropped capabilities by default.

## Architecture

- **Domain** (`src/domain`) — pure entities; no infra dependencies.
- **Application** (`src/application`) — orchestration and ports.
- **Infrastructure** (`src/infra`) — API clients, logging, integrations.
- **Entrypoints** (`src/entrypoints`) — YC handler, one-shot, cron.

`respond_on_reviews` (`src/application/respond_on_reviews.py`) drives the flow: fetch reviews → generate replies → publish replies. Concrete adapters are wired through ports. Layer boundaries are checked by `tests/test_architecture.py`.

## Testing

```bash
pytest -m architecture
make lint
make test
make ci
```

## Customisation

### Prompts
Edit `llm.prompt_template` and `llm.instructions` in `settings.yaml`. For quick experiments use the `LLM__PROMPT_TEMPLATE` and `LLM__INSTRUCTIONS` env vars.

### Other LLM provider
The service uses an OpenAI-compatible client:

```bash
export LLM__BASE_URL='https://api.openai.com/v1'
export LLM__MODEL='gpt-4o-mini'
export LLM__API_KEY='your_key'
```

## FAQ

**Do I need `LLM__API_KEY` in Yandex Cloud Functions?**
No — when using YandexGPT inside Cloud Functions the IAM token is taken from the request context.

**How do I change the run frequency?**
Update `wildberries.check_every_minutes` in `settings.yaml` or pass `WILDBERRIES__CHECK_EVERY_MINUTES` and redeploy.

**Can I respond to only some reviews?**
The service processes a batch sized by `wildberries.batch_size`. Custom filtering is not implemented yet.

## Limitations

- Replies are sent sequentially — no parallelism, no retries yet.
- No built-in length cap; controlled by prompt and model settings.
- No reply-history storage; relies on the `isAnswered` flag from the WB API.
- In Docker mode the schedule runs via in-process APScheduler; in YC, via the serverless trigger.

## Contributing

Open issues for bugs, ideas, and feature requests. PRs are welcome — please add tests and a short description of the change.

## License

MIT — see [`LICENSE`](../../LICENSE).
