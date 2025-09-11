# 🚀 Quick Start Guide - Автосервиз

## ⚡ Бърз старт за утре

### 1. Стартиране на проекта
```bash
cd /private/var/www/deyanski/Programa
docker compose up -d
```

### 2. Достъп до приложението
- **Главно табло:** http://localhost:8000
- **Клиенти:** http://localhost:8000/klienti/

### 3. Спиране на проекта
```bash
docker compose down
```

---

## 📋 Какво е готово

✅ **Docker инфраструктура** - работи  
✅ **Главно табло** - 6 кутии + календар  
✅ **Customer система** - пълна CRUD функционалност  
✅ **Български интерфейс** - готов за механиците  

---

## 🎯 Следващи стъпки

1. **Фактури модул** - създаване и управление на фактури
2. **Поръчки модул** - нови поръчки за ремонт  
3. **Служители модул** - управление на персонал
4. **Склад модул** - части и материали

---

## 📁 Ключови файлове

- `PROJECT_DOCUMENTATION.md` - пълна документация
- `docker-compose.yml` - Docker конфигурация
- `dashboard/models.py` - Customer model
- `dashboard/views.py` - Контролери
- `templates/dashboard/` - HTML шаблони

---

## 🔧 Полезни команди

```bash
# Проверка на логове
docker logs car_service_web

# Създаване на миграции
docker exec car_service_web python manage.py makemigrations

# Прилагане на миграции
docker exec car_service_web python manage.py migrate

# Създаване на superuser
docker exec car_service_web python manage.py createsuperuser
```

**Готово за продължаване! 🎉**
