# Описание проекта
**GPUniq**
![PyPI Version](https://img.shields.io/pypi/v/GPUniq) ![License](https://img.shields.io/badge/license-MIT-blue)

**GPUniq** — Python-клиент для доступа к GPUniq LLM API.
Обеспечивает простое и удобное взаимодействие с различными языковыми моделями через единый интерфейс.

📌 **Официальный сайт:** [gpuniq.ru](https://gpuniq.ru)

---

## 🚀 Возможности

🤖 **Множество LLM-моделей** — доступ к OpenAI, GLM и другим моделям через единый API.
💬 **Простой интерфейс** — всего пара строк кода для отправки запросов.
⚡ **Быстрые запросы** — обработка запросов с настройкой таймаутов.
🔐 **Безопасность** — аутентификация через API-ключи.
📊 **Мониторинг токенов** — отслеживание использованных и оставшихся токенов.

---

## 📚 Установка

Установите библиотеку через PyPI:

```bash
pip install GPUniq
```

---

## 🛠️ Начало работы

### 1️⃣ Инициализация клиента

Подключите GPUniq к вашему проекту:

```python
import gpuniq

# Инициализация клиента с API-ключом
client = gpuniq.init("gpuniq_your_api_key_here")
```

### 2️⃣ Простой запрос к LLM

Отправьте сообщение в языковую модель:

```python
response = client.request(
    "openai/gpt-oss-120b",
    "Привет, как дела?"
)
print(response)
```

### 3️⃣ Обработка ошибок

Обрабатывайте ошибки API:

```python
from gpuniq import GPUniqError

try:
    response = client.request("openai/gpt-oss-120b", "Hello!")
    print(response)
except GPUniqError as e:
    print(f"Ошибка: {e.message}")
    print(f"Код ошибки: {e.error_code}")
    print(f"HTTP статус: {e.http_status}")
```

---

## 🛠️ API Методы

| Метод | Описание |
|-------|----------|
| `init(api_key)` | Инициализирует клиент с API-ключом |
| `request(model, message)` | Отправляет запрос к LLM |

### Детальное описание методов

#### `gpuniq.init(api_key: str) -> GPUniqClient`
Инициализирует и возвращает клиент GPUniq.

**Параметры:**
- `api_key` (str): Ваш API-ключ GPUniq (начинается с 'gpuniq_')

**Возвращает:**
- `GPUniqClient`: Экземпляр клиента

---

#### `GPUniqClient.request(model: str, message: str, role: str = "user", timeout: int = 30) -> str`
Отправляет простой запрос к языковой модели.

**Параметры:**
- `model` (str): Идентификатор модели (например, 'openai/gpt-oss-120b')
- `message` (str): Текст сообщения
- `role` (str, опционально): Роль сообщения (по умолчанию: 'user')
- `timeout` (int, опционально): Таймаут запроса в секундах (по умолчанию: 30)

**Возвращает:**
- `str`: Ответ от языковой модели

---

## 🎯 Доступные модели

- `openai/gpt-oss-120b`
- `zai-org/GLM-4.6`
- И другие...

---

## 📝 Лицензия

Этот проект распространяется под лицензией **MIT**.

📌 **Официальный сайт:** [gpuniq.ru](https://gpuniq.ru)
📌 **PyPI:** [GPUniq на PyPI](https://pypi.org/project/GPUniq/)
📌 **GitHub:** [GPUniq на GitHub](https://github.com/GPUniq/GPUniq)
