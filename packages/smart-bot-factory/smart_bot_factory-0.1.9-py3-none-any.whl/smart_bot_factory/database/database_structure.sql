-- Исправленная структура базы данных для чат-бота с поддержкой множественных ботов

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS sales_users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    bot_id TEXT NOT NULL,  -- 🆕 Идентификатор бота
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(telegram_id, bot_id)  -- 🆕 Уникальность по пользователю + боту
);

-- Таблица сессий чата
CREATE TABLE IF NOT EXISTS sales_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    bot_id TEXT NOT NULL,  -- 🆕 Идентификатор бота
    system_prompt TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (user_id, bot_id) REFERENCES sales_users(telegram_id, bot_id) ON DELETE CASCADE
);

-- Остальные таблицы без изменений, так как они ссылаются на сессии

-- Обновляем индексы
CREATE INDEX IF NOT EXISTS idx_sales_users_telegram_bot ON sales_users(telegram_id, bot_id);
CREATE INDEX IF NOT EXISTS idx_sales_users_bot_id ON sales_users(bot_id);
CREATE INDEX IF NOT EXISTS idx_sales_chat_sessions_bot_id ON sales_chat_sessions(bot_id);
CREATE INDEX IF NOT EXISTS idx_sales_chat_sessions_user_bot ON sales_chat_sessions(user_id, bot_id);


-- Обновляем политики RLS
DROP POLICY IF EXISTS "Users can view their own data" ON sales_users;
CREATE POLICY "Users can view their own data" ON sales_users
    FOR SELECT USING (
        telegram_id = current_setting('app.current_user_id')::bigint 
        AND bot_id = current_setting('app.current_bot_id')
    );

DROP POLICY IF EXISTS "Users can view their own sessions" ON sales_chat_sessions;
CREATE POLICY "Users can view their own sessions" ON sales_chat_sessions
    FOR SELECT USING (
        user_id = current_setting('app.current_user_id')::bigint 
        AND bot_id = current_setting('app.current_bot_id')
    );

-- Комментарии
COMMENT ON COLUMN sales_users.bot_id IS 'Идентификатор бота (имя запускалки без .py)';
COMMENT ON COLUMN sales_chat_sessions.bot_id IS 'Идентификатор бота для разделения данных между ботами';