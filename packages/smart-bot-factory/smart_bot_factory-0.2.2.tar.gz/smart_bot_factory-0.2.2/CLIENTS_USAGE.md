# Использование клиентов в Smart Bot Factory

## Простой импорт клиентов

```python
from smart_bot_factory.clients import supabase_client, openai_client
```

## Автозаполнение работает!

После импорта IDE знает типы и предлагает:

### Supabase Client
```python
# IDE предлагает методы SupabaseClient
users = supabase_client.client.table('users').select('*').execute()
user = supabase_client.create_or_get_user(user_data)
session = supabase_client.create_chat_session(user_data, system_prompt)
```

### OpenAI Client  
```python
# IDE предлагает методы OpenAIClient
response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Пример глобального обработчика

```python
from smart_bot_factory.core import global_handler
from smart_bot_factory.clients import supabase_client

@global_handler("mass_notification", notify=True)
async def send_mass_notification(message_text: str):
    """Отправляет сообщение всем пользователям"""
    
    # Проверяем доступность
    if not supabase_client:
        return {"status": "error", "message": "Supabase клиент не найден"}
    
    try:
        # Получаем всех пользователей - автозаполнение работает!
        users = supabase_client.client.table('users').select('telegram_id').execute()
        
        sent_count = 0
        for user in users.data:
            # Отправляем сообщение каждому пользователю
            # ... логика отправки ...
            sent_count += 1
        
        return {
            "status": "completed",
            "sent_count": sent_count,
            "message": f"Отправлено {sent_count} сообщений"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## Доступные клиенты

- `supabase_client` - клиент для работы с Supabase
- `openai_client` - клиент для работы с OpenAI

## Важно

- Клиенты доступны только после запуска бота через `BotBuilder`
- Все клиенты типизированы для полной поддержки автозаполнения
- Остальные глобальные переменные (config, admin_manager и т.д.) недоступны пользователю

