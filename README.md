![CI](https://github.com/eslazarev/ai-wildberries-review-responder/actions/workflows/ci.yml/badge.svg)
![Mypy](https://img.shields.io/badge/type%20checked-mypy-039dfc)
![Pylint](https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/refs/heads/main/.github/badges/pylint.svg)
![Coverage](https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/refs/heads/main/.github/badges/coverage.svg)
![Maintainability](https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/refs/heads/main/.github/badges/radon.svg)
![CodeQL](https://github.com/eslazarev/ai-wildberries-review-responder/actions/workflows/codeql.yml/badge.svg)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
![Dependabot](https://img.shields.io/badge/dependabot-enabled-brightgreen.svg)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Docker Pulls](https://img.shields.io/docker/pulls/eslazarev/ai-wildberries-review-responder?style=flat-square)

# Сервис-автоответчик на отзывы Wildberries с YandexGPT или OpenAI

Автоответчик, который регулярно подхватывает свежие отзывы из личного кабинета продавца Wildberries, прогоняет их через LLM (по умолчанию YandexGPT) и отправляет готовые ответы обратно через Feedbacks API. 
Проект рассчитан на запуск внутри Yandex Cloud Functions по расписанию, так что выделять и поддерживать собственный сервер не нужно.

## Кратко как всё устроено
- каждые 30 минут (по умолчанию, настраивается) Cloud Function просыпается по cron-триггеру, забирает пачку необработанных отзывов через `wildberries/api/v1/feedbacks/list`;
- `PromptBuilder` собирает промпт с отзывом целиком, LLM выдаёт дружелюбный ответ в нужном языке;
- готовый текст публикуется через `wildberries/api/v1/feedbacks/answer`.

## Сколько это стоит?
- Сам код открыт и бесплатен!
- Вы плачиваете только за использование Yandex Cloud и YandexGPT (или OpenAI) и среды выполнения.
- Yandex Cloud Functions тарифицируется по времени выполнения и объёму памяти. 
- YandexGPT тарифицируется по количеству обработанных токенов (входящих + выходящих).
- Wildberries Feedbacks API бесплатен в рамках лимитов личного кабинета продавца.
- На небольшой магазин с десятком отзывов в день, расходы будут минимальны ~ **100-200 рублей в месяц.**

## Что понадобится заранее
- Python 3.12+ и `pip` для локальных проверок;
- Node.js 18+ и `npm` — Serverless Framework подтягивается через `package.json`;
- установленный CLI `yc` с доступом к облаку и каталогу Yandex Cloud;
- токен Feedbacks API для вашего кабинета WB;
- папка в Яндекс Облаке с включённым доступом к YandexGPT (`ai.languageModels.user` на сервисный аккаунт выдаёт `serverless.yml`).

## Токен Wildberries
1. В личном кабинете продавца откройте Wildberries «Профиль → Настройки → Доступ к API → Отзывы и вопросы».
2. Создайте новый ключ и передайте его в функцию через переменную окружения `WB_API_TOKEN` (Serverless прокинет её в `WILDBERRIES__API_TOKEN`):

```yaml
wildberries:
  base_url: "https://feedbacks-api.wildberries.ru"
  request_timeout: 10
  batch_size: 10
  check_every_minutes: 30
```

`batch_size` задаёт сколько отзывов обрабатываем за вызов, `check_every_minutes` — период запуска (в минутах).

## Настройка Yandex Cloud и YandexGPT
### Установка и авторизация `yc`
```bash
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
yc init  # выбираем облако, каталог и авторизуемся по OAuth
```

Внутри Cloud Functions ключ не нужен: функция возьмёт IAM-токен из `context.token["access_token"]` и подставит `folder_id` в модель (заменит `{FOLDER_ID}`).

## npm-скрипты: установка, деплой и удаление
1. Установите JS-зависимости разом:
   ```bash
   npm install
   ```
   Здесь подтянется `serverless` и `@yandex-cloud/serverless-plugin`.
2. Сборка и деплой:
   ```bash
   WB_API_TOKEN='your_wb_token' serverless deploy
   # (опционально) если LLM требует ключ:
   # LLM_API_KEY='your_llm_api_key' WB_API_TOKEN='your_wb_token' serverless deploy
   # (опционально) изменить период запуска (в минутах):
   # WB_CHECK_EVERY_MINUTES='15' WB_API_TOKEN='your_wb_token' serverless deploy
   ```
   Или в две команды:
   ```bash
   export WB_API_TOKEN='your_wb_token'
   serverless deploy
   ```
   Скрипт упакует `src/`, `requirements.txt` и `settings.yaml`, загрузит архив в Yandex Cloud и создаст Cloud Function `wb-responder-function` вместе с cron-триггером `*/30 * * * ? *`, который запускает обработку каждые 30 минут.
3. Удаление всех созданных ресурсов:
   ```bash
   serverless remove
   ```
   Команда снесёт функцию, сервисные аккаунты и триггер — полезно, если нужно быстро освободить лимиты.

## Docker (локально или сервер)
### Скачать готовый образ
```bash
docker pull eslazarev/ai-wildberries-review-responder:latest
```

### Разовый запуск (одна обработка пачки отзывов)
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='your_wb_token' \
  -e LLM__API_KEY='your_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest
```

### Запуск по расписанию (cron внутри контейнера)
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='your_wb_token' \
  -e LLM__API_KEY='your_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest src.entrypoints.docker_cron
```
По умолчанию контейнер берёт период запуска из `wildberries.check_every_minutes` (30 минут). При необходимости можно переопределить:
```bash
docker run --rm \
  -e WILDBERRIES__API_TOKEN='your_wb_token' \
  -e WILDBERRIES__CHECK_EVERY_MINUTES='15' \
  -e LLM__API_KEY='your_llm_api_key' \
  eslazarev/ai-wildberries-review-responder:latest src.entrypoints.docker_cron
```

## Конфигурация LLM
- Делайте правки через `settings.yaml`. Любую настройку можно перекрыть переменными окружения (Pydantic Settings позаботится об этом).
- Чтобы использовать другой OpenAI-совместимый сервер, задайте `llm.base_url`, `llm.model` и при необходимости `llm.api_key`.
- Температуру, верхний лимит токенов, инструкции и шаблон промпта (`llm.prompt_template`) правим там же.

## Почему Cloud Functions (и почему без серверов)
Это по-настоящему serverless: функция холодно стартует по расписанию, берет IAM-токен из метаданных, вызывает YandexGPT и завершает работу. Никаких VM, Docker и обновлений ОС, только контейнер, который платно существует ровно столько, сколько длится обработка очередной пачки отзывов. Хотите чаще — подкручиваете cron, хотите реже — прописываете своё выражение вместо `*/30 * * * ? *`. А если вдруг нужно временно выключить автоматику, достаточно удалить или остановить триггер, функция останется в каталоге без расходов.

## Ещё немного полезного
- В `src/application/respond_on_reviews.py` всего одна оркестрация, так что при необходимости можно быстро подключить логирование метрик или ретраи.
- `tests/test_architecture.py` проверяет, что домен не зависит от инфраструктурных слоёв — удобно для быстрой регрессии.
- Любой кастомный промпт переносится через `settings.llm.prompt_template`. Если в нём требуется дополнительный контекст, добавьте это прямо в шаблон и перезапустите функцию.

### Понравился проект? Звёздочка на GitHub и фидбек в issues будут очень кстати!
