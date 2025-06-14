# Subscriptions API

REST API для управления платными подписками. Поддерживает кэширование, асинхронную обработку задач и покрыт автотестами.

# Функциональность
- Система подписок
- Вычисления сколько стоят все подписки
- Кеширования основных страниц
- тесты покрывающее cache api и serializers
- Оптимизация запросов и отстуствия ошибки n+1

# Стек технологий
ф
-Python + Django
-Django REST Framework
-Celery + Redis + Flower
-Celery Singleton
-Django Redis Cache
-dj-rest-auth (авторизация)

# Установка и запуск

- git clone https://github.com/MrExalight123/API_Subscription-Store.git
- Запуск докера
в консоль вписаваем:
cd (В директорию проекта)
docker compose build

docker compose run --rm  wep-app sh -c  "python manage.py migrate"

docker compose run --rm  wep-app sh -c  "python manage.py test"

docker compose up

# Структура моделей

### Clients
- user(Пользватель)
- company_name(Названия компании пресдавляющие подписку)
- full_address(Адрес компании)

### Service
- name(Названия сервиса)
- full_price(Сколько он стоит без скидок)

### Plan
- play_type(Вариции скидок при оформления подписки)
- discount_percent(Сколько будет сама скидка)

### Subsription
- client(ссылка на клиента, оформившего подписку)
- service(ссылка на подписываемую услугу)
- plan(тарифный план)
- price - стоимость подписки, после скидки (может вычисляться автоматически)
- comment(дополнительный комментарий)

**Бизнес-логика:**
- При создании новой подписки вызывается фоновая задача `set_price` через Celery, которая рассчитывает стоимость.
- Это позволяет вынести логику вычислений за пределы основного запроса и избежать блокировки.
