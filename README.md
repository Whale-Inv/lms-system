# LMS System (Learning Management System)
**Платформа для онлайн-обучения**, на которой авторы могут создавать и публиковать курсы, 
уроки и другие образовательные материалы.

> Проект представляет собой **бэкенд-сервер** на Django REST Framework. 
> API возвращает клиентскому SPA-приложению структурированные JSON-данные.

## Технологии

| Компонент | Технология |
|-----------|-----------|
| Backend | Django 6.0 + DRF |
| База данных | PostgreSQL 16 |
| Кэш / Брокер | Redis 7 |
| Фоновые задачи | Celery + Celery Beat |
| Web-сервер | Nginx + Gunicorn |
| Контейнеризация | Docker + Docker Compose |
| CI/CD | GitHub Actions + Docker Hub |
| Сервер | Ubuntu 24.04 (Yandex Cloud VM) |

---

## Локальный запуск

### Требования

- Docker Desktop
- Poetry (опционально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/Whale-Inv/lms-system.git
cd lms-system
```

### 2. Настройка переменных окружения
`cp .env.template .env`  
Заполните .env:
```
POSTGRES_DB=lms_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
### 3. Запуск через Docker
`docker compose up -d --build`
### 4. Создание суперпользователя
`docker exec -it lms-app python manage.py createsuperuser`
### 5. Проверка
```
http://localhost
http://localhost/admin
```
### Остановка
`docker compose down`

## Настройка удаленного сервера
### 1. Подготовка сервера (Ubuntu 24.04)
```
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Настройка firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```
### 2. Настройка SSH-ключей
```
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
ssh-copy-id -i ~/.ssh/id_ed25519.pub test@IP_СЕРВЕРА
```
### 3. Деплой проекта
```
git clone -b develop https://github.com/exzently/lms-system.git ~/lms-system
cd ~/lms-system
cp .env.template .env
nano .env
```  
Обязательные переменные в .env на сервере:
```commandline
POSTGRES_DB=lms_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=IP_СЕРВЕРА,localhost
DOCKER_USERNAME=exzently
```
### 4. Запуск контейнеров
```commandline
sudo docker compose up -d --build
```
### 5. Создание суперпользователя
```commandline
sudo docker exec -it lms-app python manage.py createsuperuser
```
### 6. Проверка
```commandline
http://IP_СЕРВЕРА/admin
```
## CI/CD GitHub Actions
### Как это работает
При каждом push в ветку `develop` автоматически запускается:  

| Шаг | Действие |
|-----|----------|
| 1 | Линтер (flake8) — проверка стиля кода |
| 2 | Тесты (Django) — запуск всех тестов |
| 3 | Сборка Docker образа — push в Docker Hub |
| 4 | Деплой на сервер — обновление контейнеров |

### Настройка GitHub Secrets

В репозитории: **Settings → Secrets and variables → Actions**

| Secret | Описание |
|--------|----------|
| `DOCKER_USERNAME` | Имя пользователя Docker Hub |
| `DOCKER_PASSWORD` | Токен доступа Docker Hub |
| `SERVER_HOST` | IP адрес сервера |
| `SERVER_USER` | Имя пользователя на сервере |
| `SSH_PRIVATE_KEY` | Приватный SSH ключ |

### Запуск вручную
Workflow запускается автоматически при push. Статус можно посмотреть в:
```commandline
GitHub → Actions → CI/CD Pipeline
```
---
## Автор
**Nikita Dorozhko**  
* GitHub: [@Whale-Inv](https://github.com/Whale-Inv)
* Docker Hub: [@exzently](https://hub.docker.com/u/exzently)
---
## Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)