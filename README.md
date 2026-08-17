# Discord Ticket Bot — деплой на Railway

## 1. Загрузка на GitHub

```
git init
git add .
git commit -m "Ticket bot"
git branch -M main
git remote add origin https://github.com/ВАШ_НИК/ВАШ_РЕПО.git
git push -u origin main
```

Файл `.gitignore` уже настроен, чтобы `.env` не попал в репозиторий — токен туда не уйдёт.

## 2. Деплой на Railway

1. Зайдите на railway.app → **New Project** → **Deploy from GitHub repo** → выберите ваш репозиторий.
2. Railway сам определит `Procfile` и `requirements.txt` и запустит `worker: python bot.py`.
3. Перейдите во вкладку **Variables** проекта и добавьте переменные (без кавычек, только значения):

   | Переменная | Значение |
   |---|---|
   | `DISCORD_TOKEN` | токен вашего бота из Developer Portal |
   | `GUILD_ID` | ID вашего сервера |
   | `LEADER_ROLE_ID` | ID роли "Лидер" |
   | `ADMIN_ROLE_ID` | ID роли "Админ" (необязательно) |
   | `TICKET_CATEGORY_ID` | ID категории для тикетов |

4. После сохранения переменных Railway автоматически передеплоит бота.
5. Во вкладке **Deployments → View Logs** проверьте, что появилась строка `Бот запущен как ...`.

## 3. Если меняете код

Просто:
```
git add .
git commit -m "update"
git push
```
Railway задеплоит новую версию автоматически.

## Важно про токен

Токен, который вы прислали ранее в чат, нужно считать скомпрометированным —
зайдите в Discord Developer Portal → ваше приложение → **Bot** → **Reset Token**,
получите новый и впишите его **только** в Railway Variables, никогда в код или в git.
