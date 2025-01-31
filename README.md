# ITMO Bot API

Это Flask-приложение, которое использует модель Hugging Face для генерации ответов, а также интегрируется с Википедией и RSS-лентой новостей ИТМО.

## Требования

- Docker
- Docker Compose

## Запуск с помощью Docker Compose

1. Убедитесь, что у вас установлены Docker и Docker Compose.
2. Клонируйте репозиторий:

   ```bash
   git clone <ваш-репозиторий>
   cd <ваш-репозиторий>

3. Запустите приложение:

   ```bash
   docker-compose up --build
   
4. Приложение будет доступно по адресу: http://localhost:8000.

##API Endpoints
####GET /: Проверка работоспособности сервера.

#####POST /api/request: Основной endpoint для обработки запросов.

5. Пример запроса:
   ```bash
   {
   "query": "Какие новости в ИТМО?",
   "id": 1
   }

#Остановка приложения

```bash
   docker-compose down