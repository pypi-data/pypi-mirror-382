
\restrict WBtltrfyEEoF24oRSfGBapNcgKliB6xSV8AgT2uO2cKxNSkoUuc9InlJ2lBPCQx


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."cleanup_old_messages"("days_to_keep" integer DEFAULT 30) RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sales_messages 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep
    AND session_id IN (
        SELECT id FROM sales_chat_sessions WHERE status = 'archived'
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;


ALTER FUNCTION "public"."cleanup_old_messages"("days_to_keep" integer) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."end_expired_admin_conversations"() RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    ended_count INTEGER;
BEGIN
    UPDATE admin_user_conversations 
    SET status = 'completed', ended_at = NOW()
    WHERE status = 'active' AND auto_end_at < NOW();
    
    GET DIAGNOSTICS ended_count = ROW_COUNT;
    RETURN ended_count;
END;
$$;


ALTER FUNCTION "public"."end_expired_admin_conversations"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."update_updated_at_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."update_updated_at_column"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."validate_bot_id"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $_$
BEGIN
    -- Проверяем, что bot_id не пустой
    IF NEW.bot_id IS NULL OR trim(NEW.bot_id) = '' THEN
        RAISE EXCEPTION 'bot_id не может быть пустым';
    END IF;
    
    -- Проверяем формат bot_id (только латиница, цифры и дефисы)
    IF NEW.bot_id !~ '^[a-z0-9\-]+$' THEN
        RAISE EXCEPTION 'bot_id должен содержать только латинские буквы, цифры и дефисы';
    END IF;
    
    RETURN NEW;
END;
$_$;


ALTER FUNCTION "public"."validate_bot_id"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."admin_user_conversations" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "admin_id" bigint,
    "user_id" bigint,
    "session_id" "uuid",
    "status" "text" DEFAULT 'active'::"text",
    "started_at" timestamp with time zone DEFAULT "now"(),
    "ended_at" timestamp with time zone,
    "auto_end_at" timestamp with time zone DEFAULT ("now"() + '00:30:00'::interval),
    CONSTRAINT "admin_user_conversations_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'completed'::"text"])))
);


ALTER TABLE "public"."admin_user_conversations" OWNER TO "postgres";


COMMENT ON TABLE "public"."admin_user_conversations" IS 'Активные диалоги админов с пользователями';



CREATE TABLE IF NOT EXISTS "public"."session_events" (
    "id" bigint NOT NULL,
    "session_id" "uuid",
    "event_type" "text" NOT NULL,
    "event_info" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "notified_admins" bigint[] DEFAULT '{}'::bigint[]
);


ALTER TABLE "public"."session_events" OWNER TO "postgres";


COMMENT ON TABLE "public"."session_events" IS 'События из ответов ИИ для уведомлений';



CREATE OR REPLACE VIEW "public"."daily_events" AS
 SELECT "date"("created_at") AS "event_date",
    "event_type",
    "count"(*) AS "count"
   FROM "public"."session_events"
  WHERE ("created_at" > ("now"() - '30 days'::interval))
  GROUP BY ("date"("created_at")), "event_type"
  ORDER BY ("date"("created_at")) DESC, "event_type";


ALTER VIEW "public"."daily_events" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sales_chat_sessions" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" bigint NOT NULL,
    "system_prompt" "text" NOT NULL,
    "status" "text" DEFAULT 'active'::"text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "metadata" "jsonb" DEFAULT '{}'::"jsonb",
    "bot_id" "text" DEFAULT 'growthmed-october-14'::"text" NOT NULL,
    "current_stage" "text",
    "lead_quality_score" integer,
    CONSTRAINT "sales_chat_sessions_status_check" CHECK (("status" = ANY (ARRAY['active'::"text", 'completed'::"text", 'archived'::"text"])))
);


ALTER TABLE "public"."sales_chat_sessions" OWNER TO "postgres";


COMMENT ON TABLE "public"."sales_chat_sessions" IS 'Сессии диалогов с пользователями';



COMMENT ON COLUMN "public"."sales_chat_sessions"."system_prompt" IS 'Системный промпт для данной сессии';



COMMENT ON COLUMN "public"."sales_chat_sessions"."status" IS 'Статус сессии: active, completed, archived';



COMMENT ON COLUMN "public"."sales_chat_sessions"."bot_id" IS 'ID бота, обязательное поле для разделения данных между ботами';



CREATE OR REPLACE VIEW "public"."funnel_stats" AS
 SELECT "current_stage",
    "count"(*) AS "count",
    "avg"("lead_quality_score") AS "avg_quality",
    "round"(((("count"(*))::numeric * 100.0) / NULLIF("sum"("count"(*)) OVER (), (0)::numeric)), 1) AS "percentage"
   FROM "public"."sales_chat_sessions"
  WHERE (("created_at" > ("now"() - '7 days'::interval)) AND ("current_stage" IS NOT NULL))
  GROUP BY "current_stage";


ALTER VIEW "public"."funnel_stats" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."sales_admins" (
    "id" bigint NOT NULL,
    "telegram_id" bigint NOT NULL,
    "username" "text",
    "first_name" "text",
    "last_name" "text",
    "role" "text" DEFAULT 'admin'::"text",
    "is_active" boolean DEFAULT true,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."sales_admins" OWNER TO "postgres";


COMMENT ON TABLE "public"."sales_admins" IS 'Администраторы бота';



CREATE SEQUENCE IF NOT EXISTS "public"."sales_admins_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sales_admins_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sales_admins_id_seq" OWNED BY "public"."sales_admins"."id";



CREATE TABLE IF NOT EXISTS "public"."sales_messages" (
    "id" bigint NOT NULL,
    "session_id" "uuid" NOT NULL,
    "role" "text" NOT NULL,
    "content" "text" NOT NULL,
    "message_type" "text" DEFAULT 'text'::"text",
    "tokens_used" integer DEFAULT 0,
    "processing_time_ms" integer DEFAULT 0,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "metadata" "jsonb" DEFAULT '{}'::"jsonb",
    "ai_metadata" "jsonb" DEFAULT '{}'::"jsonb",
    CONSTRAINT "sales_messages_message_type_check" CHECK (("message_type" = ANY (ARRAY['text'::"text", 'image'::"text", 'document'::"text", 'audio'::"text"]))),
    CONSTRAINT "sales_messages_role_check" CHECK (("role" = ANY (ARRAY['system'::"text", 'user'::"text", 'assistant'::"text"])))
);


ALTER TABLE "public"."sales_messages" OWNER TO "postgres";


COMMENT ON TABLE "public"."sales_messages" IS 'Сообщения в диалогах';



COMMENT ON COLUMN "public"."sales_messages"."role" IS 'Роль отправителя: system, user, assistant';



COMMENT ON COLUMN "public"."sales_messages"."tokens_used" IS 'Количество токенов использованных для обработки сообщения';



CREATE SEQUENCE IF NOT EXISTS "public"."sales_messages_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sales_messages_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sales_messages_id_seq" OWNED BY "public"."sales_messages"."id";



CREATE TABLE IF NOT EXISTS "public"."sales_session_analytics" (
    "id" bigint NOT NULL,
    "session_id" "uuid" NOT NULL,
    "total_messages" integer DEFAULT 0,
    "total_tokens" integer DEFAULT 0,
    "average_response_time_ms" integer DEFAULT 0,
    "conversion_stage" "text",
    "lead_quality_score" integer,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "sales_session_analytics_lead_quality_score_check" CHECK ((("lead_quality_score" >= 1) AND ("lead_quality_score" <= 10)))
);


ALTER TABLE "public"."sales_session_analytics" OWNER TO "postgres";


COMMENT ON TABLE "public"."sales_session_analytics" IS 'Аналитика по сессиям для оценки качества лидов';



COMMENT ON COLUMN "public"."sales_session_analytics"."conversion_stage" IS 'Этап воронки продаж';



COMMENT ON COLUMN "public"."sales_session_analytics"."lead_quality_score" IS 'Оценка качества лида от 1 до 10';



CREATE SEQUENCE IF NOT EXISTS "public"."sales_session_analytics_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sales_session_analytics_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sales_session_analytics_id_seq" OWNED BY "public"."sales_session_analytics"."id";



CREATE TABLE IF NOT EXISTS "public"."sales_users" (
    "id" bigint NOT NULL,
    "telegram_id" bigint NOT NULL,
    "username" "text",
    "first_name" "text",
    "last_name" "text",
    "language_code" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "is_active" boolean DEFAULT true,
    "bot_id" "text" DEFAULT 'growthmed-october-14'::"text" NOT NULL
);


ALTER TABLE "public"."sales_users" OWNER TO "postgres";


COMMENT ON TABLE "public"."sales_users" IS 'Информация о пользователях Telegram';



COMMENT ON COLUMN "public"."sales_users"."telegram_id" IS 'Уникальный ID пользователя в Telegram';



COMMENT ON COLUMN "public"."sales_users"."bot_id" IS 'ID бота, обязательное поле для разделения данных между ботами';



CREATE SEQUENCE IF NOT EXISTS "public"."sales_users_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."sales_users_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."sales_users_id_seq" OWNED BY "public"."sales_users"."id";



CREATE SEQUENCE IF NOT EXISTS "public"."session_events_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."session_events_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."session_events_id_seq" OWNED BY "public"."session_events"."id";



CREATE TABLE IF NOT EXISTS "public"."user_profiles" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" "text" NOT NULL,
    "role" "text" NOT NULL,
    "company" "text" NOT NULL,
    "geo" "text",
    "goals" "text" NOT NULL,
    "telegram_id" "text" NOT NULL,
    "username" "text",
    "company_business" "text",
    "company_type" smallint NOT NULL
);


ALTER TABLE "public"."user_profiles" OWNER TO "postgres";


ALTER TABLE "public"."user_profiles" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."user_profiles_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



ALTER TABLE ONLY "public"."sales_admins" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sales_admins_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."sales_messages" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sales_messages_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."sales_session_analytics" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sales_session_analytics_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."sales_users" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."sales_users_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."session_events" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."session_events_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."admin_user_conversations"
    ADD CONSTRAINT "admin_user_conversations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_admins"
    ADD CONSTRAINT "sales_admins_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_admins"
    ADD CONSTRAINT "sales_admins_telegram_id_key" UNIQUE ("telegram_id");



ALTER TABLE ONLY "public"."sales_chat_sessions"
    ADD CONSTRAINT "sales_chat_sessions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_messages"
    ADD CONSTRAINT "sales_messages_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_session_analytics"
    ADD CONSTRAINT "sales_session_analytics_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_users"
    ADD CONSTRAINT "sales_users_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."sales_users"
    ADD CONSTRAINT "sales_users_telegram_id_bot_id_key" UNIQUE ("telegram_id", "bot_id");



ALTER TABLE ONLY "public"."sales_users"
    ADD CONSTRAINT "sales_users_telegram_id_unique" UNIQUE ("telegram_id");



ALTER TABLE ONLY "public"."session_events"
    ADD CONSTRAINT "session_events_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_profiles"
    ADD CONSTRAINT "user_profiles_pkey" PRIMARY KEY ("telegram_id");



ALTER TABLE ONLY "public"."user_profiles"
    ADD CONSTRAINT "user_profiles_telegram_id_key" UNIQUE ("telegram_id");



CREATE INDEX "idx_admin_conversations_admin" ON "public"."admin_user_conversations" USING "btree" ("admin_id");



CREATE INDEX "idx_admin_conversations_status" ON "public"."admin_user_conversations" USING "btree" ("status");



CREATE INDEX "idx_admin_conversations_user" ON "public"."admin_user_conversations" USING "btree" ("user_id");



CREATE INDEX "idx_sales_admins_telegram_id" ON "public"."sales_admins" USING "btree" ("telegram_id");



CREATE INDEX "idx_sales_chat_sessions_bot_id" ON "public"."sales_chat_sessions" USING "btree" ("bot_id");



CREATE INDEX "idx_sales_chat_sessions_bot_status" ON "public"."sales_chat_sessions" USING "btree" ("bot_id", "status");



CREATE INDEX "idx_sales_chat_sessions_stage" ON "public"."sales_chat_sessions" USING "btree" ("current_stage");



CREATE INDEX "idx_sales_chat_sessions_status" ON "public"."sales_chat_sessions" USING "btree" ("status");



CREATE INDEX "idx_sales_chat_sessions_user_bot" ON "public"."sales_chat_sessions" USING "btree" ("user_id", "bot_id");



CREATE INDEX "idx_sales_chat_sessions_user_id" ON "public"."sales_chat_sessions" USING "btree" ("user_id");



CREATE INDEX "idx_sales_messages_created_at" ON "public"."sales_messages" USING "btree" ("created_at");



CREATE INDEX "idx_sales_messages_metadata" ON "public"."sales_messages" USING "gin" ("ai_metadata");



CREATE INDEX "idx_sales_messages_role" ON "public"."sales_messages" USING "btree" ("role");



CREATE INDEX "idx_sales_messages_session_id" ON "public"."sales_messages" USING "btree" ("session_id");



CREATE INDEX "idx_sales_session_analytics_session_id" ON "public"."sales_session_analytics" USING "btree" ("session_id");



CREATE INDEX "idx_sales_users_bot_id" ON "public"."sales_users" USING "btree" ("bot_id");



CREATE INDEX "idx_sales_users_telegram_bot" ON "public"."sales_users" USING "btree" ("telegram_id", "bot_id");



CREATE INDEX "idx_session_events_session" ON "public"."session_events" USING "btree" ("session_id");



CREATE INDEX "idx_session_events_type" ON "public"."session_events" USING "btree" ("event_type");



CREATE OR REPLACE TRIGGER "update_sales_admins_updated_at" BEFORE UPDATE ON "public"."sales_admins" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_sales_chat_sessions_updated_at" BEFORE UPDATE ON "public"."sales_chat_sessions" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_sales_session_analytics_updated_at" BEFORE UPDATE ON "public"."sales_session_analytics" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "update_sales_users_updated_at" BEFORE UPDATE ON "public"."sales_users" FOR EACH ROW EXECUTE FUNCTION "public"."update_updated_at_column"();



CREATE OR REPLACE TRIGGER "validate_sessions_bot_id" BEFORE INSERT OR UPDATE ON "public"."sales_chat_sessions" FOR EACH ROW EXECUTE FUNCTION "public"."validate_bot_id"();



CREATE OR REPLACE TRIGGER "validate_users_bot_id" BEFORE INSERT OR UPDATE ON "public"."sales_users" FOR EACH ROW EXECUTE FUNCTION "public"."validate_bot_id"();



ALTER TABLE ONLY "public"."admin_user_conversations"
    ADD CONSTRAINT "admin_user_conversations_admin_id_fkey" FOREIGN KEY ("admin_id") REFERENCES "public"."sales_admins"("telegram_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."admin_user_conversations"
    ADD CONSTRAINT "admin_user_conversations_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."sales_chat_sessions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."admin_user_conversations"
    ADD CONSTRAINT "admin_user_conversations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."sales_users"("telegram_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sales_messages"
    ADD CONSTRAINT "sales_messages_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."sales_chat_sessions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."sales_session_analytics"
    ADD CONSTRAINT "sales_session_analytics_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."sales_chat_sessions"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."session_events"
    ADD CONSTRAINT "session_events_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "public"."sales_chat_sessions"("id") ON DELETE CASCADE;



CREATE POLICY "Enable insert for authenticated users only" ON "public"."user_profiles" FOR INSERT TO "authenticated" WITH CHECK (true);



CREATE POLICY "Enable users to view their own data only" ON "public"."sales_users" FOR SELECT TO "authenticated" USING (("telegram_id" = ("current_setting"('app.current_user_id'::"text"))::bigint));



CREATE POLICY "Service role can manage all admins" ON "public"."sales_admins" USING (("current_setting"('role'::"text") = 'service_role'::"text"));



CREATE POLICY "Service role can manage all analytics" ON "public"."sales_session_analytics" USING (("current_setting"('role'::"text", true) = 'service_role'::"text"));



CREATE POLICY "Service role can manage all conversations" ON "public"."admin_user_conversations" USING (("current_setting"('role'::"text") = 'service_role'::"text"));



CREATE POLICY "Service role can manage all events" ON "public"."session_events" USING (("current_setting"('role'::"text") = 'service_role'::"text"));



CREATE POLICY "Service role can manage all messages" ON "public"."sales_messages" USING (("current_setting"('role'::"text", true) = 'service_role'::"text"));



CREATE POLICY "Service role can manage all sessions" ON "public"."sales_chat_sessions" USING (("current_setting"('role'::"text") = 'service_role'::"text"));



CREATE POLICY "Service role can manage all users" ON "public"."sales_users" USING (("current_setting"('role'::"text") = 'service_role'::"text"));



CREATE POLICY "Users can view analytics for their sessions" ON "public"."sales_session_analytics" FOR SELECT USING (("session_id" IN ( SELECT "sales_chat_sessions"."id"
   FROM "public"."sales_chat_sessions"
  WHERE (("sales_chat_sessions"."user_id" = ("current_setting"('app.current_user_id'::"text", true))::bigint) AND ("sales_chat_sessions"."bot_id" = "current_setting"('app.current_bot_id'::"text", true))))));



CREATE POLICY "Users can view messages from their sessions" ON "public"."sales_messages" FOR SELECT USING (("session_id" IN ( SELECT "sales_chat_sessions"."id"
   FROM "public"."sales_chat_sessions"
  WHERE (("sales_chat_sessions"."user_id" = ("current_setting"('app.current_user_id'::"text"))::bigint) AND ("sales_chat_sessions"."bot_id" = "current_setting"('app.current_bot_id'::"text", true))))));



CREATE POLICY "Users can view their own data" ON "public"."sales_users" FOR SELECT USING ((("telegram_id" = ("current_setting"('app.current_user_id'::"text"))::bigint) AND ("bot_id" = "current_setting"('app.current_bot_id'::"text", true))));



CREATE POLICY "Users can view their own sessions" ON "public"."sales_chat_sessions" FOR SELECT USING ((("user_id" = ("current_setting"('app.current_user_id'::"text"))::bigint) AND ("bot_id" = "current_setting"('app.current_bot_id'::"text", true))));



ALTER TABLE "public"."admin_user_conversations" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."sales_admins" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."sales_chat_sessions" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."sales_messages" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."sales_session_analytics" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."sales_users" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."session_events" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."user_profiles" ENABLE ROW LEVEL SECURITY;




ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

























































































































































GRANT ALL ON FUNCTION "public"."cleanup_old_messages"("days_to_keep" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."cleanup_old_messages"("days_to_keep" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."cleanup_old_messages"("days_to_keep" integer) TO "service_role";



GRANT ALL ON FUNCTION "public"."end_expired_admin_conversations"() TO "anon";
GRANT ALL ON FUNCTION "public"."end_expired_admin_conversations"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."end_expired_admin_conversations"() TO "service_role";



GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "anon";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."update_updated_at_column"() TO "service_role";



GRANT ALL ON FUNCTION "public"."validate_bot_id"() TO "anon";
GRANT ALL ON FUNCTION "public"."validate_bot_id"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."validate_bot_id"() TO "service_role";


















GRANT ALL ON TABLE "public"."admin_user_conversations" TO "anon";
GRANT ALL ON TABLE "public"."admin_user_conversations" TO "authenticated";
GRANT ALL ON TABLE "public"."admin_user_conversations" TO "service_role";



GRANT ALL ON TABLE "public"."session_events" TO "anon";
GRANT ALL ON TABLE "public"."session_events" TO "authenticated";
GRANT ALL ON TABLE "public"."session_events" TO "service_role";



GRANT ALL ON TABLE "public"."daily_events" TO "anon";
GRANT ALL ON TABLE "public"."daily_events" TO "authenticated";
GRANT ALL ON TABLE "public"."daily_events" TO "service_role";



GRANT ALL ON TABLE "public"."sales_chat_sessions" TO "anon";
GRANT ALL ON TABLE "public"."sales_chat_sessions" TO "authenticated";
GRANT ALL ON TABLE "public"."sales_chat_sessions" TO "service_role";



GRANT ALL ON TABLE "public"."funnel_stats" TO "anon";
GRANT ALL ON TABLE "public"."funnel_stats" TO "authenticated";
GRANT ALL ON TABLE "public"."funnel_stats" TO "service_role";



GRANT ALL ON TABLE "public"."sales_admins" TO "anon";
GRANT ALL ON TABLE "public"."sales_admins" TO "authenticated";
GRANT ALL ON TABLE "public"."sales_admins" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sales_admins_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sales_admins_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sales_admins_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sales_messages" TO "anon";
GRANT ALL ON TABLE "public"."sales_messages" TO "authenticated";
GRANT ALL ON TABLE "public"."sales_messages" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sales_messages_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sales_messages_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sales_messages_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sales_session_analytics" TO "anon";
GRANT ALL ON TABLE "public"."sales_session_analytics" TO "authenticated";
GRANT ALL ON TABLE "public"."sales_session_analytics" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sales_session_analytics_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sales_session_analytics_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sales_session_analytics_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."sales_users" TO "anon";
GRANT ALL ON TABLE "public"."sales_users" TO "authenticated";
GRANT ALL ON TABLE "public"."sales_users" TO "service_role";



GRANT ALL ON SEQUENCE "public"."sales_users_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."sales_users_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."sales_users_id_seq" TO "service_role";



GRANT ALL ON SEQUENCE "public"."session_events_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."session_events_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."session_events_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."user_profiles" TO "anon";
GRANT ALL ON TABLE "public"."user_profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."user_profiles" TO "service_role";



GRANT ALL ON SEQUENCE "public"."user_profiles_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_profiles_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_profiles_id_seq" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";






























\unrestrict WBtltrfyEEoF24oRSfGBapNcgKliB6xSV8AgT2uO2cKxNSkoUuc9InlJ2lBPCQx

RESET ALL;
