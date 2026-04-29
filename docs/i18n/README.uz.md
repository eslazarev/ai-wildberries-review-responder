# Wildberries xaridorlarining sharhlariga sun'iy intellekt yordamida avtomatik javob xizmati

🌐 [Русский](../../README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md) · [Türkçe](README.tr.md) · [Қазақша](README.kk.md) · **Oʻzbekcha**

<img src="https://raw.githubusercontent.com/eslazarev/ai-wildberries-review-responder/main/.github/images/wildberries-ai-review-service.gif">

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/ai-wildberries-review-responder)](https://artifacthub.io/packages/search?repo=ai-wildberries-review-responder)
[![Docker Pulls](https://img.shields.io/docker/pulls/eslazarev/ai-wildberries-review-responder)](https://hub.docker.com/r/eslazarev/ai-wildberries-review-responder)
![License](https://img.shields.io/badge/license-MIT-blue)

Bu xizmat Wildberries sotuvchi kabinetidan yangi sharhlarni avtomatik tarzda oladi, LLM orqali javob yaratadi va uni qaytadan joylashtiradi. Yandex Cloud Functions, Docker, mahalliy muhitda yoki Helm chart orqali har qanday Kubernetes klasterida ishga tushirish mumkin.

## Asosiy imkoniyatlar
- **Wildberries API tokeni ustidan to'liq nazorat — uchinchi tomonlar bilan ulashish shart emas.**
- Serverless Framework yordamida Yandex Cloud Functions'ga oson joylashtirish.
- Promptlarni o'zingizga moslashtirish imkoniyati.
- Yangi sharhlarni doimiy ravishda qayta ishlash — server doimo ishlab turishi shart emas.
- YandexGPT va OpenAI mos keladigan har qanday API qo'llab-quvvatlanadi (OpenAI, Ollama, vLLM).
- YAML fayli va atrof-muhit o'zgaruvchilari orqali moslashuvchan konfiguratsiya.
- Bir nechta ishga tushirish rejimlari: Yandex Cloud Functions, Docker, Kubernetes (Helm), mahalliy.

## Qanday ishlaydi
1. Belgilangan jadval bo'yicha funksiya Wildberries'dan javob berilmagan sharhlar ro'yxatini oladi.
2. Har bir sharh uchun alohida prompt yaratiladi (foto/video bor-yo'qligi bilan).
3. LLM mos ohang va tilda javob yaratadi.
4. Javob Wildberries Feedbacks API orqali yuboriladi.

## Xarajatlar
- Kod bepul va ochiq manbali.
- Xarajat bulut, model va sharhlar hajmiga bog'liq.
- Yandex Cloud Functions: bajarilish vaqti va xotiraga to'lov.
- YandexGPT yoki OpenAI: token bo'yicha to'lov.
- Wildberries Feedbacks API: sotuvchi hisobi limitlari doirasida bepul.

Ishlab chiqarish o'lchovlari taxminan **bir sharh uchun 0,25 ₽** ko'rsatadi.

![Yandex Cloud xarajat misoli](../../.github/images/yandex_cloud_cost.png)

## Tezkor boshlash

```bash
npm install
WILDBERRIES__API_TOKEN='sizning_wb_token' serverless deploy
```

Qo'shimcha parametrlar:

```bash
LLM__API_KEY='sizning_llm_api_key' WILDBERRIES__API_TOKEN='sizning_wb_token' serverless deploy
WILDBERRIES__CHECK_EVERY_MINUTES='15' WILDBERRIES__API_TOKEN='sizning_wb_token' serverless deploy
```

## Talablar

- Python 3.12+ va `pip`.
- Node.js 18+ va `npm` (Serverless Framework).
- `yc` CLI (Yandex Cloud).

### Wildberries API tokeni
1. Sotuvchi kabinetida: *Profil → Sozlamalar → API kirish → Sharhlar va savollar*.
2. Yangi kalit yarating va `WILDBERRIES__API_TOKEN` orqali bering.

## Mahalliy ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

export WILDBERRIES__API_TOKEN='sizning_wb_token'
export LLM__API_KEY='sizning_llm_api_key'
python -m src.entrypoints.docker_once
```

Cron rejimi:
```bash
python -m src.entrypoints.docker_cron
```

## Docker

```bash
docker pull eslazarev/ai-wildberries-review-responder:latest

docker run --rm \
  -e WILDBERRIES__API_TOKEN='sizning_wb_token' \
  -e LLM__API_KEY='sizning_llm_api_key' \
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

Chart [Artifact Hub](https://artifacthub.io/packages/helm/ai-wildberries-review-responder/ai-wildberries-review-responder)'da nashr etilgan.

## Qo'shimcha hujjatlar

To'liq texnik tavsif, konfiguratsiya namunalari, arxitektura va FAQ uchun **rus tilidagi asosiy hujjatni** ko'ring: [README.md](../../README.md).

## Litsenziya

MIT — [`LICENSE`](../../LICENSE) faylida ko'ring.
