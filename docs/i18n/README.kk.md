# Wildberries-те сатып алушылардың пікірлеріне жасанды интеллектпен автоматты жауап беру қызметі

🌐 [Русский](../../README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md) · [Türkçe](README.tr.md) · **Қазақша** · [Oʻzbekcha](README.uz.md)

<img src="https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/main/.github/images/wildberries-ai-review-service.gif">

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/ai-wildberries-review-responder)](https://artifacthub.io/packages/search?repo=ai-wildberries-review-responder)
[![Docker Pulls](https://img.shields.io/docker/pulls/eslazarev/ai-wildberries-review-responder)](https://hub.docker.com/r/eslazarev/ai-wildberries-review-responder)
![License](https://img.shields.io/badge/license-MIT-blue)

Бұл қызмет Wildberries сатушы кабинетінен жаңа пікірлерді автоматты түрде алады, LLM арқылы жауап жасайды және оны қайтадан жариялайды. Yandex Cloud Functions, Docker, жергілікті ортада немесе Helm chart арқылы Kubernetes кластерінде іске қосылады.

## Негізгі мүмкіндіктер
- **Wildberries API токенін толық бақылау — үшінші тараптарға бермейсіз.**
- Yandex Cloud Functions-қа Serverless Framework арқылы оңай орналастыру.
- Промптарды қалауыңызша өзгертуге болады.
- Жаңа пікірлерді тұрақты түрде өңдеу — серверді үнемі іске қосудың қажеті жоқ.
- YandexGPT және OpenAI-мен үйлесімді кез келген API қолдау табылады (OpenAI, Ollama, vLLM).
- YAML файл және орта айнымалылары арқылы икемді конфигурация.
- Бірнеше іске қосу режимі: Yandex Cloud Functions, Docker, Kubernetes (Helm), жергілікті.

## Жұмыс істеу принципі
1. Жоспарланған кестемен функция Wildberries-тен жауап берілмеген пікірлер тізімін алады.
2. Әр пікір үшін жеке промпт жасалынады (фото немесе бейне бар-жоғын қоса).
3. LLM сәйкес тонда және тілде жауап жасайды.
4. Жауап Wildberries Feedbacks API арқылы жіберіледі.

## Шығындар
- Код тегін және ашық бастапқы кодты.
- Шығын бұлт қызметіне, модельге және пікірлер санына байланысты.
- Yandex Cloud Functions: орындау уақыты мен жадыға бағаланады.
- YandexGPT немесе OpenAI: токен бойынша бағаланады.
- Wildberries Feedbacks API: сатушы кабинеті лимиттері аясында тегін.

Өндірістік өлшеулер шамамен **бір пікірге 0,25 ₽** көрсетеді.

![Yandex Cloud шығын мысалы](../../.github/images/yandex_cloud_cost.png)

## Жылдам бастау

```bash
npm install
WILDBERRIES__API_TOKEN='сіздің_wb_token' serverless deploy
```

Қосымша параметрлер:

```bash
LLM__API_KEY='сіздің_llm_api_key' WILDBERRIES__API_TOKEN='сіздің_wb_token' serverless deploy
WILDBERRIES__CHECK_EVERY_MINUTES='15' WILDBERRIES__API_TOKEN='сіздің_wb_token' serverless deploy
```

## Талаптар

- Python 3.12+ және `pip`.
- Node.js 18+ және `npm` (Serverless Framework).
- `yc` CLI (Yandex Cloud).

### Wildberries API токенін алу
1. Сатушы кабинетіне кіріп: *Профиль → Параметрлер → API қолжетімдігі → Пікірлер мен сұрақтар*.
2. Жаңа кілт жасап `WILDBERRIES__API_TOKEN` арқылы беріңіз.

## Жергілікті іске қосу

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

export WILDBERRIES__API_TOKEN='сіздің_wb_token'
export LLM__API_KEY='сіздің_llm_api_key'
python -m src.entrypoints.docker_once
```

Cron режимі:
```bash
python -m src.entrypoints.docker_cron
```

## Docker

```bash
docker pull eslazarev/ai-wildberries-review-responder:latest

docker run --rm \
  -e WILDBERRIES__API_TOKEN='сіздің_wb_token' \
  -e LLM__API_KEY='сіздің_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest src.entrypoints.docker_once
```

## Kubernetes (Helm chart)

```bash
helm repo add wb-responder https://eslazarev.github.io/ai-wildberries-review-responder
helm repo update
helm install wb-responder wb-responder/ai-wildberries-review-responder \
  --namespace wb-responder --create-namespace \
  --set secrets.wildberriesApiToken=$WILDBERRIES_API_TOKEN \
  --set secrets.llmApiKey=$LLM_API_KEY
```

Chart [Artifact Hub](https://artifacthub.io/packages/helm/ai-wildberries-review-responder/ai-wildberries-review-responder)-та жарияланған.

## Қосымша құжаттама

Толық техникалық сипаттамалар, конфигурация мысалдары, архитектура және FAQ үшін **орыс тіліндегі негізгі құжатты** қараңыз: [README.md](../../README.md).

## Лицензия

MIT — [`LICENSE`](../../LICENSE) файлынан қараңыз.
