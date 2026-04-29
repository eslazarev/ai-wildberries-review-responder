# Wildberries 客户评价 AI 自动回复服务

🌐 [Русский](../../README.md) · [English](README.en.md) · **简体中文** · [Türkçe](README.tr.md) · [Қазақша](README.kk.md) · [Oʻzbekcha](README.uz.md)

<img src="https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/main/.github/images/wildberries-ai-review-service.gif">

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/ai-wildberries-review-responder)](https://artifacthub.io/packages/search?repo=ai-wildberries-review-responder)
[![Docker Pulls](https://img.shields.io/docker/pulls/eslazarev/ai-wildberries-review-responder)](https://hub.docker.com/r/eslazarev/ai-wildberries-review-responder)
![License](https://img.shields.io/badge/license-MIT-blue)

本服务自动从 Wildberries 卖家后台拉取新评价,通过大模型生成回复,并将其发回。默认在 Yandex Cloud Functions 上运行,也支持本地、Docker 以及通过官方 Helm chart 部署到任意 Kubernetes 集群。

> 面向跨境/中俄电商卖家:很多在 Wildberries 销售的商家来自中国。本服务帮你自动用俄语回复俄语买家,无需逐条手动翻译。

## 主要功能
- **完全掌控 Wildberries API token,绝不与第三方共享。**
- 一行命令即可部署到 Yandex Cloud Functions(基于 Serverless Framework)。
- 提示词(prompt)可自定义 — 完全控制模型语气和风格。
- 定期自动处理新评价,无需常驻服务器。
- 支持 YandexGPT 与任何 OpenAI 兼容 API(OpenAI、Ollama、vLLM 等)。
- 通过 YAML 文件和环境变量灵活配置。
- 多种部署方式:Yandex Cloud Functions、Docker、Kubernetes (Helm)、本地。

## 工作原理
1. 按计划从 Wildberries 拉取所有未回复的评价。
2. 每条评价生成独立的提示词,包含详情及是否含图片/视频。
3. 大模型生成符合语气和语种的回复。
4. 通过 Wildberries Feedbacks API 发送回复。

## 成本
- 代码免费且开源。
- 实际开销取决于云服务、模型和评价数量。
- Yandex Cloud Functions:按执行时间和内存计费。
- YandexGPT 或 OpenAI:按 token 计费。
- Wildberries Feedbacks API:在卖家账户限额内免费。

实测约 **0.25 卢布/条评价**(下图为两天内回复约 100 条评价的支出):

![Yandex Cloud 费用示例](../../.github/images/yandex_cloud_cost.png)

## 快速开始

如果环境已配置完毕(YC、权限、token),只需:

```bash
npm install
WILDBERRIES__API_TOKEN='你的_wb_token' serverless deploy
```

会构建函数并部署到 Yandex Cloud Functions,同时设置定时触发器。

可选参数:

```bash
LLM__API_KEY='你的_llm_api_key' WILDBERRIES__API_TOKEN='你的_wb_token' serverless deploy
WILDBERRIES__CHECK_EVERY_MINUTES='15' WILDBERRIES__API_TOKEN='你的_wb_token' serverless deploy
```

## 前置条件

### 工具
- Python 3.12+ 和 `pip`(本地运行和测试)。
- Node.js 18+ 和 `npm`(Serverless Framework)。
- `yc` CLI(Yandex Cloud 操作)。

### 获取 Wildberries API token
1. 卖家后台 → 资料 → 设置 → API 接入 → 评价与问答。
2. 创建新 key,通过 `WILDBERRIES__API_TOKEN` 注入。
3. 文档:<https://dev.wildberries.ru/openapi/api-information>

### YandexGPT 或 OpenAI 接入
- YandexGPT(YC Functions 内):需要 `ai.languageModels.user` 角色的服务账号(在 `serverless.yml` 中已定义)。
- 在 Cloud Functions 内可不设置 `LLM__API_KEY`,函数将自动使用 `context.token` 中的 IAM token。
- OpenAI 或其它 OpenAI 兼容 API:配置 `LLM__API_KEY`、`LLM__MODEL`、`LLM__BASE_URL`。

### 通过 Ollama 使用本地模型
[Ollama](https://ollama.com) 在 `http://localhost:11434/v1` 暴露 OpenAI 兼容接口:

```yaml
llm:
  base_url: "http://localhost:11434/v1"
  model: "gemma3:4b"
  api_key: "ollama"
```

## 配置

### `settings.yaml`
默认配置来源,环境变量优先级更高。

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

`{FOLDER_ID}` 在 Yandex Cloud Functions 中自动替换。

### 环境变量
嵌套字段以 `__` 分隔:

- `WILDBERRIES__API_TOKEN` — 必填。
- `WILDBERRIES__BASE_URL`、`WILDBERRIES__REQUEST_TIMEOUT`、`WILDBERRIES__BATCH_SIZE`、`WILDBERRIES__CHECK_EVERY_MINUTES`。
- `LLM__API_KEY` — YC Functions 内可留空以使用 IAM token。
- `LLM__MODEL`、`LLM__BASE_URL`、`LLM__TEMPERATURE`、`LLM__MAX_TOKENS`、`LLM__INSTRUCTIONS`、`LLM__PROMPT_TEMPLATE`、`LLM__TIMEOUT`。

### 优先级
环境变量 → `.env` → 文件 secret → `settings.yaml`。YAML 提供安全默认值,环境变量始终覆盖。

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

export WILDBERRIES__API_TOKEN='你的_wb_token'
export LLM__API_KEY='你的_llm_api_key'
python -m src.entrypoints.docker_once
```

定时本地模式:
```bash
python -m src.entrypoints.docker_cron
```

## Yandex Cloud Functions(Serverless)

```bash
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
yc init

npm install
WILDBERRIES__API_TOKEN='你的_wb_token' serverless deploy
```

清理资源:
```bash
serverless remove
```

## Docker

```bash
docker pull eslazarev/ai-wildberries-review-responder:latest
```

单次执行:
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='你的_wb_token' \
  -e LLM__API_KEY='你的_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest src.entrypoints.docker_once
```

容器内定时执行:
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='你的_wb_token' \
  -e WILDBERRIES__CHECK_EVERY_MINUTES='15' \
  -e LLM__API_KEY='你的_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest
```

## Kubernetes (Helm chart)

Helm chart 在每次触发时启动 K8s 原生 `CronJob` 执行 `docker_once`,并自动创建 `ConfigMap`(settings.yaml)和 `Secret`(API tokens)。已发布到 [Artifact Hub](https://artifacthub.io/packages/helm/ai-wildberries-review-responder/ai-wildberries-review-responder)。

```bash
helm repo add wb-responder https://eslazarev.github.io/ai-wildberries-review-responder
helm repo update
helm install wb-responder wb-responder/ai-wildberries-review-responder \
  --namespace wb-responder --create-namespace \
  --set secrets.wildberriesApiToken=$WILDBERRIES_API_TOKEN \
  --set secrets.llmApiKey=$LLM_API_KEY
```

手动执行:
```bash
kubectl create job --from=cronjob/wb-responder-ai-wildberries-review-responder manual -n wb-responder
kubectl logs -n wb-responder -l app.kubernetes.io/instance=wb-responder --tail=200 -f
```

主要参数(完整说明见 [`charts/ai-wildberries-review-responder/README.md`](../../charts/ai-wildberries-review-responder/README.md)):
- `cronjob.schedule` — cron 表达式,默认 `*/30 * * * *`。
- `secrets.existingSecret` — 使用预先存在的 `Secret`,不要本 chart 自动生成。
- `settings.content` — 完整的 `settings.yaml` 内容,挂载到 Pod 中。
- `extraEnv` / `extraEnvFrom` — 额外环境变量(例如指向集群内 Ollama 的 `LLM__BASE_URL`)。

Pod 默认非 root 运行,只读根文件系统,删除全部 capabilities。

## 架构

- **Domain** (`src/domain`) — 纯实体,不依赖任何外部基础设施。
- **Application** (`src/application`) — 用例编排与端口(ports)。
- **Infrastructure** (`src/infra`) — API 客户端、日志、外部集成。
- **Entrypoints** (`src/entrypoints`) — YC 处理函数、一次性、cron。

`respond_on_reviews`(`src/application/respond_on_reviews.py`)驱动主流程:抓取 → 生成回复 → 发布。具体实现通过 port 接入。层次边界由 `tests/test_architecture.py` 自动验证。

## 测试与质量

```bash
pytest -m architecture
make lint
make test
make ci
```

## 自定义

### 提示词
直接编辑 `settings.yaml` 中的 `llm.prompt_template` 和 `llm.instructions`。快速实验可使用 `LLM__PROMPT_TEMPLATE` / `LLM__INSTRUCTIONS` 环境变量。

### 切换 LLM 提供商
本服务使用 OpenAI 兼容客户端:

```bash
export LLM__BASE_URL='https://api.openai.com/v1'
export LLM__MODEL='gpt-4o-mini'
export LLM__API_KEY='你的_key'
```

## 常见问题

**Yandex Cloud Functions 内必须设 `LLM__API_KEY` 吗?**
不必。使用 YandexGPT 时,IAM token 会从函数上下文自动注入。

**如何调整运行频率?**
修改 `wildberries.check_every_minutes` 后重新部署,或在部署时传 `WILDBERRIES__CHECK_EVERY_MINUTES`。

**可以只回复部分评价吗?**
当前按 `wildberries.batch_size` 批量处理未回复评价,尚未支持自定义过滤规则。

## 已知限制

- 回复串行发送,暂无并行与重试。
- 无内置长度上限,长度由提示词和模型参数控制。
- 不存储已处理的评价,依赖 WB API 的 `isAnswered` 字段。
- Docker 模式通过 APScheduler 实现定时;YC 通过 serverless 触发器。

## 反馈与贡献

欢迎在 Issues 提交 bug 和想法,欢迎 PR(尽量附带测试与简要说明)。

## 许可证

MIT — 详见 [`LICENSE`](../../LICENSE)。
