# Обновленный supabase_client.py с поддержкой bot_id и обратной совместимостью

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Клиент для работы с Supabase с поддержкой bot_id для мультиботовой архитектуры"""
    
    def __init__(self, url: str, key: str, bot_id: str = None):
        """
        Инициализация клиента Supabase
        
        Args:
            url: URL Supabase проекта
            key: API ключ Supabase
            bot_id: Идентификатор бота для изоляции данных (опционально для обратной совместимости)
        """
        self.url = url
        self.key = key
        self.bot_id = bot_id  # 🆕 Теперь опционально!
        self.client: Optional[Client] = None
        
        if self.bot_id:
            logger.info(f"Инициализация SupabaseClient для bot_id: {self.bot_id}")
        else:
            logger.warning("SupabaseClient инициализирован БЕЗ bot_id - мультиботовая изоляция отключена")
    
    async def initialize(self):
        """Инициализация клиента Supabase"""
        try:
            self.client = create_client(self.url, self.key)
            logger.info(f"Supabase client инициализирован{f' для bot_id: {self.bot_id}' if self.bot_id else ''}")
        except Exception as e:
            logger.error(f"Ошибка инициализации Supabase client: {e}")
            raise
    
    async def create_or_get_user(self, user_data: Dict[str, Any]) -> int:
        """Создает или получает пользователя с учетом bot_id (если указан)"""
        try:
            # 🆕 Если bot_id указан, фильтруем по нему
            query = self.client.table('sales_users').select('telegram_id').eq(
                'telegram_id', user_data['telegram_id']
            )
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            response = query.execute()
            
            if response.data:
                # Обновляем данные существующего пользователя
                update_query = self.client.table('sales_users').update({
                    'username': user_data.get('username'),
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'language_code': user_data.get('language_code'),
                    'updated_at': datetime.now().isoformat(),
                    'is_active': True
                }).eq('telegram_id', user_data['telegram_id'])
                
                if self.bot_id:
                    update_query = update_query.eq('bot_id', self.bot_id)
                
                update_query.execute()
                
                logger.info(f"Обновлен пользователь {user_data['telegram_id']}{f' для bot_id {self.bot_id}' if self.bot_id else ''}")
                return user_data['telegram_id']
            else:
                # 🆕 Создаем нового пользователя с bot_id (если указан)
                user_insert_data = {
                    'telegram_id': user_data['telegram_id'],
                    'username': user_data.get('username'),
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'language_code': user_data.get('language_code'),
                    'is_active': True,
                    'source': user_data.get('source'),
                    'medium': user_data.get('medium'),
                    'campaign': user_data.get('campaign'),
                    'content': user_data.get('content'),
                    'term': user_data.get('term'),
                }
                if self.bot_id:
                    user_insert_data['bot_id'] = self.bot_id
                
                response = self.client.table('sales_users').insert(user_insert_data).execute()
                
                logger.info(f"Создан новый пользователь {user_data['telegram_id']}{f' для bot_id {self.bot_id}' if self.bot_id else ''}")
                return user_data['telegram_id']
                
        except APIError as e:
            logger.error(f"Ошибка при работе с пользователем: {e}")
            raise
    
    async def create_chat_session(self, user_data: Dict[str, Any], system_prompt: str) -> str:
        """Создает новую сессию чата с учетом bot_id (если указан)"""
        try:
            # Создаем или обновляем пользователя
            user_id = await self.create_or_get_user(user_data)
            
            # 🆕 Завершаем активные сессии пользователя (с учетом bot_id)
            await self.close_active_sessions(user_id)
            
            # 🆕 Создаем новую сессию с bot_id (если указан)
            session_data = {
                'user_id': user_id,
                'system_prompt': system_prompt,
                'status': 'active',
                'current_stage': 'introduction',
                'lead_quality_score': 5,
                'metadata': {
                    'user_agent': user_data.get('user_agent', ''),
                    'start_timestamp': datetime.now().isoformat()
                }
            }
            if self.bot_id:
                session_data['bot_id'] = self.bot_id
                session_data['metadata']['bot_id'] = self.bot_id
            
            response = self.client.table('sales_chat_sessions').insert(session_data).execute()
            
            session_id = response.data[0]['id']
            
            # Создаем запись аналитики
            await self.create_session_analytics(session_id)
            
            logger.info(f"Создана новая сессия {session_id} для пользователя {user_id}{f', bot_id {self.bot_id}' if self.bot_id else ''}")
            return session_id
            
        except APIError as e:
            logger.error(f"Ошибка при создании сессии: {e}")
            raise
    
    async def close_active_sessions(self, user_id: int):
        """Закрывает активные сессии пользователя с учетом bot_id (если указан)"""
        try:
            # 🆕 Закрываем только сессии этого бота (если bot_id указан)
            query = self.client.table('sales_chat_sessions').update({
                'status': 'completed',
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('status', 'active')
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            query.execute()
            
            logger.info(f"Закрыты активные сессии для пользователя {user_id}{f', bot_id {self.bot_id}' if self.bot_id else ''}")
            
        except APIError as e:
            logger.error(f"Ошибка при закрытии сессий: {e}")
            raise
            
    async def get_active_session(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получает активную сессию пользователя с учетом bot_id (если указан)"""
        try:
            # 🆕 Ищем активную сессию с учетом bot_id (если указан)
            query = self.client.table('sales_chat_sessions').select(
                'id', 'system_prompt', 'created_at', 'current_stage', 'lead_quality_score'
            ).eq('user_id', telegram_id).eq('status', 'active')
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            response = query.execute()
            
            if response.data:
                session_info = response.data[0]
                logger.info(f"Найдена активная сессия {session_info['id']} для пользователя {telegram_id}{f', bot_id {self.bot_id}' if self.bot_id else ''}")
                return session_info
            
            return None
            
        except APIError as e:
            logger.error(f"Ошибка при поиске активной сессии: {e}")
            return None

    async def create_session_analytics(self, session_id: str):
        """Создает запись аналитики для сессии"""
        try:
            self.client.table('sales_session_analytics').insert({
                'session_id': session_id,
                'total_messages': 0,
                'total_tokens': 0,
                'average_response_time_ms': 0,
                'conversion_stage': 'initial',
                'lead_quality_score': 5
            }).execute()
            
            logger.debug(f"Создана аналитика для сессии {session_id}")
            
        except APIError as e:
            logger.error(f"Ошибка при создании аналитики: {e}")
            raise
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        message_type: str = 'text',
        tokens_used: int = 0,
        processing_time_ms: int = 0,
        metadata: Dict[str, Any] = None,
        ai_metadata: Dict[str, Any] = None
    ) -> int:
        """Добавляет сообщение в базу данных"""
        try:
            response = self.client.table('sales_messages').insert({
                'session_id': session_id,
                'role': role,
                'content': content,
                'message_type': message_type,
                'tokens_used': tokens_used,
                'processing_time_ms': processing_time_ms,
                'metadata': metadata or {},
                'ai_metadata': ai_metadata or {}
            }).execute()
            
            message_id = response.data[0]['id']
            
            # Обновляем аналитику сессии
            await self.update_session_analytics(session_id, tokens_used, processing_time_ms)
            
            logger.debug(f"Добавлено сообщение {message_id} в сессию {session_id}")
            return message_id
            
        except APIError as e:
            logger.error(f"Ошибка при добавлении сообщения: {e}")
            raise
    
    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получает историю сообщений для сессии"""
        try:
            response = self.client.table('sales_messages').select(
                'id', 'role', 'content', 'message_type', 'created_at', 'metadata', 'ai_metadata'
            ).eq('session_id', session_id).order('created_at', desc=True).limit(limit).execute()
            
            # Фильтруем системные сообщения из истории
            messages = [msg for msg in response.data if msg['role'] != 'system']
            
            # Переворачиваем в хронологический порядок (старые -> новые)
            messages.reverse()
            
            logger.debug(f"Получено {len(messages)} сообщений для сессии {session_id}")
            return messages
            
        except APIError as e:
            logger.error(f"Ошибка при получении истории: {e}")
            raise
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о сессии с проверкой bot_id (если указан)"""
        try:
            response = self.client.table('sales_chat_sessions').select(
                'id', 'user_id', 'bot_id', 'system_prompt', 'status', 'created_at', 
                'metadata', 'current_stage', 'lead_quality_score'
            ).eq('id', session_id).execute()
            
            if response.data:
                session = response.data[0]
                # 🆕 Дополнительная проверка bot_id для безопасности (если указан)
                if self.bot_id and session.get('bot_id') != self.bot_id:
                    logger.warning(f"Попытка доступа к сессии {session_id} другого бота: {session.get('bot_id')} != {self.bot_id}")
                    return None
                return session
            return None
            
        except APIError as e:
            logger.error(f"Ошибка при получении информации о сессии: {e}")
            raise
    
    async def update_session_stage(self, session_id: str, stage: str = None, quality_score: int = None):
        """Обновляет этап сессии и качество лида"""
        try:
            update_data = {'updated_at': datetime.now().isoformat()}
            
            if stage:
                update_data['current_stage'] = stage
            if quality_score is not None:
                update_data['lead_quality_score'] = quality_score
            
            # 🆕 Дополнительная проверка bot_id при обновлении (если указан)
            if self.bot_id:
                response = self.client.table('sales_chat_sessions').select('bot_id').eq('id', session_id).execute()
                if response.data and response.data[0].get('bot_id') != self.bot_id:
                    logger.warning(f"Попытка обновления сессии {session_id} другого бота")
                    return
                
            self.client.table('sales_chat_sessions').update(update_data).eq(
                'id', session_id
            ).execute()
            
            logger.debug(f"Обновлен этап сессии {session_id}: stage={stage}, quality={quality_score}")
            
        except APIError as e:
            logger.error(f"Ошибка при обновлении этапа сессии: {e}")
            raise
    
    async def get_user_sessions(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получает все сессии пользователя с учетом bot_id (если указан)"""
        try:
            # 🆕 Получаем только сессии этого бота (если bot_id указан)
            query = self.client.table('sales_chat_sessions').select(
                'id', 'status', 'created_at', 'updated_at', 'current_stage', 'lead_quality_score'
            ).eq('user_id', telegram_id).order('created_at', desc=True)
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            response = query.execute()
            return response.data
            
        except APIError as e:
            logger.error(f"Ошибка при получении сессий пользователя: {e}")
            raise
    
    # 🆕 Новые методы для админской системы с поддержкой bot_id
    
    async def add_session_event(self, session_id: str, event_type: str, event_info: str) -> int:
        """Добавляет событие в сессию"""
        try:
            response = self.client.table('session_events').insert({
                'session_id': session_id,
                'event_type': event_type,
                'event_info': event_info,
                'notified_admins': []
            }).execute()
            
            event_id = response.data[0]['id']
            logger.info(f"Добавлено событие {event_type} для сессии {session_id}")
            return event_id
            
        except APIError as e:
            logger.error(f"Ошибка при добавлении события: {e}")
            raise
    
    async def sync_admin(self, admin_data: Dict[str, Any]):
        """Синхронизирует админа в БД (админы общие для всех ботов)"""
        try:
            # Проверяем существует ли админ
            response = self.client.table('sales_admins').select('telegram_id').eq(
                'telegram_id', admin_data['telegram_id']
            ).execute()
            
            if response.data:
                # Обновляем существующего
                self.client.table('sales_admins').update({
                    'username': admin_data.get('username'),
                    'first_name': admin_data.get('first_name'),
                    'last_name': admin_data.get('last_name'),
                    'is_active': True
                }).eq('telegram_id', admin_data['telegram_id']).execute()
                
                logger.debug(f"Обновлен админ {admin_data['telegram_id']}")
            else:
                # Создаем нового
                self.client.table('sales_admins').insert({
                    'telegram_id': admin_data['telegram_id'],
                    'username': admin_data.get('username'),
                    'first_name': admin_data.get('first_name'),
                    'last_name': admin_data.get('last_name'),
                    'role': 'admin',
                    'is_active': True
                }).execute()
                
                logger.info(f"Создан новый админ {admin_data['telegram_id']}")
                
        except APIError as e:
            logger.error(f"Ошибка при синхронизации админа: {e}")
            raise
    
    async def start_admin_conversation(self, admin_id: int, user_id: int, session_id: str) -> int:
        """Начинает диалог между админом и пользователем"""
        try:
            # Завершаем активные диалоги этого админа
            await self.end_admin_conversations(admin_id)
            
            response = self.client.table('admin_user_conversations').insert({
                'admin_id': admin_id,
                'user_id': user_id,
                'session_id': session_id,
                'status': 'active',
                'auto_end_at': (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            }).execute()
            
            conversation_id = response.data[0]['id']
            logger.info(f"Начат диалог {conversation_id}: админ {admin_id} с пользователем {user_id}")
            return conversation_id
            
        except APIError as e:
            logger.error(f"Ошибка при начале диалога: {e}")
            raise
    
    async def end_admin_conversations(self, admin_id: int = None, user_id: int = None) -> int:
        """Завершает активные диалоги админа или пользователя"""
        try:
            query = self.client.table('admin_user_conversations').update({
                'status': 'ended',
                'ended_at': datetime.now(timezone.utc).isoformat()
            }).eq('status', 'active')
            
            if admin_id:
                query = query.eq('admin_id', admin_id)
            if user_id:
                query = query.eq('user_id', user_id)
                
            response = query.execute()
            ended_count = len(response.data)
            
            if ended_count > 0:
                logger.info(f"Завершено {ended_count} активных диалогов")
                
            return ended_count
            
        except APIError as e:
            logger.error(f"Ошибка при завершении диалогов: {e}")
            return 0
    
    async def get_admin_active_conversation(self, admin_id: int) -> Optional[Dict[str, Any]]:
        """Получает активный диалог админа"""
        try:
            response = self.client.table('admin_user_conversations').select(
                'id', 'user_id', 'session_id', 'started_at', 'auto_end_at'
            ).eq('admin_id', admin_id).eq('status', 'active').execute()
            
            return response.data[0] if response.data else None
            
        except APIError as e:
            logger.error(f"Ошибка при получении диалога админа: {e}")
            return None
    
    async def get_user_conversation(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает активный диалог пользователя"""
        try:
            response = self.client.table('admin_user_conversations').select(
                'id', 'admin_id', 'session_id', 'started_at', 'auto_end_at'
            ).eq('user_id', user_id).eq('status', 'active').execute()
            
            return response.data[0] if response.data else None
            
        except APIError as e:
            logger.error(f"Ошибка при получении диалога пользователя: {e}")
            return None
    
    # 🆕 Методы совместимости - добавляем недостающие методы из старого кода
    
    async def cleanup_expired_conversations(self) -> int:
        """Завершает просроченные диалоги админов"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            response = self.client.table('admin_user_conversations').update({
                'status': 'expired',
                'ended_at': now
            }).eq('status', 'active').lt('auto_end_at', now).execute()
            
            ended_count = len(response.data)
            if ended_count > 0:
                logger.info(f"Автоматически завершено {ended_count} просроченных диалогов")
                
            return ended_count
            
        except APIError as e:
            logger.error(f"Ошибка при завершении просроченных диалогов: {e}")
            return 0
    
    async def end_expired_conversations(self) -> int:
        """Алиас для cleanup_expired_conversations для обратной совместимости"""
        return await self.cleanup_expired_conversations()
    
    async def get_user_admin_conversation(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Проверяет, ведется ли диалог с пользователем (для совместимости)"""
        return await self.get_user_conversation(user_id)
    
    # 🆕 Методы аналитики с фильтрацией по bot_id
    
    async def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Получает сводку аналитики за последние дни с учетом bot_id (если указан)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 🆕 Получаем сессии с учетом bot_id (если указан)
            query = self.client.table('sales_chat_sessions').select(
                'id', 'current_stage', 'lead_quality_score', 'created_at'
            ).gte('created_at', cutoff_date.isoformat())
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            sessions_response = query.execute()
            
            sessions = sessions_response.data
            total_sessions = len(sessions)
            
            # Группировка по этапам
            stages = {}
            quality_scores = []
            
            for session in sessions:
                stage = session.get('current_stage', 'unknown')
                stages[stage] = stages.get(stage, 0) + 1
                
                score = session.get('lead_quality_score', 5)
                if score:
                    quality_scores.append(score)
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 5
            
            return {
                'bot_id': self.bot_id,
                'period_days': days,
                'total_sessions': total_sessions,
                'stages': stages,
                'average_lead_quality': round(avg_quality, 1),
                'generated_at': datetime.now().isoformat()
            }
            
        except APIError as e:
            logger.error(f"Ошибка при получении аналитики: {e}")
            return {
                'bot_id': self.bot_id,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    async def update_session_analytics(
        self, 
        session_id: str, 
        tokens_used: int = 0, 
        processing_time_ms: int = 0
    ):
        """Обновляет аналитику сессии"""
        try:
            # Получаем текущую аналитику
            response = self.client.table('sales_session_analytics').select(
                'total_messages', 'total_tokens', 'average_response_time_ms'
            ).eq('session_id', session_id).execute()
            
            if response.data:
                current = response.data[0]
                new_total_messages = current['total_messages'] + 1
                new_total_tokens = current['total_tokens'] + tokens_used
                
                # Вычисляем среднее время ответа
                if processing_time_ms > 0:
                    current_avg = current['average_response_time_ms']
                    new_avg = ((current_avg * (new_total_messages - 1)) + processing_time_ms) / new_total_messages
                else:
                    new_avg = current['average_response_time_ms']
                
                # Обновляем аналитику
                self.client.table('sales_session_analytics').update({
                    'total_messages': new_total_messages,
                    'total_tokens': new_total_tokens,
                    'average_response_time_ms': int(new_avg),
                    'updated_at': datetime.now().isoformat()
                }).eq('session_id', session_id).execute()
                
        except APIError as e:
            logger.error(f"Ошибка при обновлении аналитики: {e}")
            # Не прерываем выполнение, аналитика не критична
    
    # Методы совместимости
    async def update_conversion_stage(self, session_id: str, stage: str, quality_score: int = None):
        """Обновляет этап конверсии и качество лида (для совместимости)"""
        await self.update_session_stage(session_id, stage, quality_score)
    
    async def archive_old_sessions(self, days: int = 7):
        """Архивирует старые завершенные сессии с учетом bot_id (если указан)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 🆕 Архивируем только сессии этого бота (если bot_id указан)
            query = self.client.table('sales_chat_sessions').update({
                'status': 'archived'
            }).eq('status', 'completed').lt('updated_at', cutoff_date.isoformat())
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            query.execute()
            
            logger.info(f"Архивированы сессии старше {days} дней{f' для bot_id {self.bot_id}' if self.bot_id else ''}")
            
        except APIError as e:
            logger.error(f"Ошибка при архивировании сессий: {e}")
            raise
    
    async def get_sent_files(self, user_id: int) -> List[str]:
        """Получает список отправленных файлов для пользователя
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            List[str]: Список имен файлов, разделенных запятой
        """
        try:
            query = self.client.table('sales_users').select('files').eq('telegram_id', user_id)
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            response = query.execute()
            
            if response.data and response.data[0].get('files'):
                files_str = response.data[0]['files']
                return [f.strip() for f in files_str.split(',') if f.strip()]
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения отправленных файлов для пользователя {user_id}: {e}")
            return []
    
    async def get_sent_directories(self, user_id: int) -> List[str]:
        """Получает список отправленных каталогов для пользователя
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            List[str]: Список путей каталогов, разделенных запятой
        """
        try:
            query = self.client.table('sales_users').select('directories').eq('telegram_id', user_id)
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
            
            response = query.execute()
            
            if response.data and response.data[0].get('directories'):
                dirs_str = response.data[0]['directories']
                return [d.strip() for d in dirs_str.split(',') if d.strip()]
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка получения отправленных каталогов для пользователя {user_id}: {e}")
            return []
    
    async def add_sent_files(self, user_id: int, files_list: List[str]):
        """Добавляет файлы в список отправленных для пользователя
        
        Args:
            user_id: Telegram ID пользователя
            files_list: Список имен файлов для добавления
        """
        try:
            logger.info(f"Добавление файлов для пользователя {user_id}: {files_list}")
            
            # Получаем текущий список
            current_files = await self.get_sent_files(user_id)
            logger.info(f"Текущие файлы в БД: {current_files}")
            
            # Объединяем с новыми файлами (без дубликатов)
            all_files = list(set(current_files + files_list))
            logger.info(f"Объединенный список файлов: {all_files}")
            
            # Сохраняем обратно
            files_str = ', '.join(all_files)
            logger.info(f"Сохраняем строку: {files_str}")
            
            query = self.client.table('sales_users').update({
                'files': files_str
            }).eq('telegram_id', user_id)
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
                logger.info(f"Фильтр по bot_id: {self.bot_id}")
            
            response = query.execute()
            logger.info(f"Ответ от БД: {response.data}")
            
            logger.info(f"✅ Добавлено {len(files_list)} файлов для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления отправленных файлов для пользователя {user_id}: {e}")
            logger.exception("Полный стек ошибки:")
    
    async def add_sent_directories(self, user_id: int, dirs_list: List[str]):
        """Добавляет каталоги в список отправленных для пользователя
        
        Args:
            user_id: Telegram ID пользователя
            dirs_list: Список путей каталогов для добавления
        """
        try:
            logger.info(f"Добавление каталогов для пользователя {user_id}: {dirs_list}")
            
            # Получаем текущий список
            current_dirs = await self.get_sent_directories(user_id)
            logger.info(f"Текущие каталоги в БД: {current_dirs}")
            
            # Объединяем с новыми каталогами (без дубликатов)
            all_dirs = list(set(current_dirs + dirs_list))
            logger.info(f"Объединенный список каталогов: {all_dirs}")
            
            # Сохраняем обратно
            dirs_str = ', '.join(all_dirs)
            logger.info(f"Сохраняем строку: {dirs_str}")
            
            query = self.client.table('sales_users').update({
                'directories': dirs_str
            }).eq('telegram_id', user_id)
            
            if self.bot_id:
                query = query.eq('bot_id', self.bot_id)
                logger.info(f"Фильтр по bot_id: {self.bot_id}")
            
            response = query.execute()
            logger.info(f"Ответ от БД: {response.data}")
            
            logger.info(f"✅ Добавлено {len(dirs_list)} каталогов для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления отправленных каталогов для пользователя {user_id}: {e}")
            logger.exception("Полный стек ошибки:")

    # =============================================================================
    # МЕТОДЫ ДЛЯ АНАЛИТИКИ
    # =============================================================================
    
    async def get_funnel_stats(self, days: int = 7) -> Dict[str, Any]:
        """Получает статистику воронки продаж"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Общее количество сессий
            sessions_response = self.client.table('sales_chat_sessions').select('id').gte(
                'created_at', cutoff_date.isoformat()
            )
            if self.bot_id:
                sessions_response = sessions_response.eq('bot_id', self.bot_id)
            
            total_sessions = len(sessions_response.execute().data)
            
            # Статистика по этапам
            stages_response = self.client.table('sales_chat_sessions').select(
                'current_stage', 'quality_score'
            ).gte('created_at', cutoff_date.isoformat())
            
            if self.bot_id:
                stages_response = stages_response.eq('bot_id', self.bot_id)
            
            sessions_data = stages_response.execute().data
            
            stages = {}
            quality_scores = []
            
            for session in sessions_data:
                stage = session.get('current_stage', 'unknown')
                stages[stage] = stages.get(stage, 0) + 1
                
                if session.get('quality_score'):
                    quality_scores.append(session['quality_score'])
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                'total_sessions': total_sessions,
                'stages': stages,
                'avg_quality': round(avg_quality, 2),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики воронки: {e}")
            return {
                'total_sessions': 0,
                'stages': {},
                'avg_quality': 0,
                'period_days': days
            }
    
    async def get_events_stats(self, days: int = 7) -> Dict[str, int]:
        """Получает статистику событий"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            response = self.client.table('scheduled_events').select(
                'event_type', 'status'
            ).gte('created_at', cutoff_date.isoformat())
            
            events_data = response.execute().data
            
            stats = {}
            for event in events_data:
                event_type = event.get('event_type', 'unknown')
                status = event.get('status', 'unknown')
                
                key = f"{event_type}_{status}"
                stats[key] = stats.get(key, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики событий: {e}")
            return {}

    async def get_user_last_message_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о последней активности пользователя из сессии"""
        try:
            # Получаем последнюю сессию пользователя
            response = self.client.table('sales_chat_sessions').select(
                'id', 'current_stage', 'created_at', 'updated_at'
            ).eq('user_id', user_id).order('updated_at', desc=True).limit(1).execute()
            
            if not response.data:
                return None
            
            session = response.data[0]
            
            return {
                'last_message_at': session['updated_at'],
                'session_id': session['id'],
                'current_stage': session['current_stage'],
                'session_updated_at': session['updated_at']
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о последнем сообщении пользователя {user_id}: {e}")
            return None

    async def check_user_stage_changed(self, user_id: int, original_session_id: str) -> bool:
        """Проверяет, изменился ли этап пользователя с момента планирования события"""
        try:
            # Получаем текущую информацию о сессии
            current_response = self.client.table('sales_chat_sessions').select(
                'id', 'current_stage'
            ).eq('user_telegram_id', user_id).order('created_at', desc=True).limit(1).execute()
            
            if not current_response.data:
                return False
            
            current_session = current_response.data[0]
            
            # Если сессия изменилась - этап точно изменился
            if current_session['id'] != original_session_id:
                return True
            
            # Если сессия та же, получаем оригинальный этап из scheduled_events
            # и сравниваем с текущим
            original_response = self.client.table('sales_chat_sessions').select(
                'current_stage'
            ).eq('id', original_session_id).execute()
            
            if not original_response.data:
                # Если не нашли оригинальную сессию, считаем что этап не изменился
                return False
            
            original_stage = original_response.data[0]['current_stage']
            current_stage = current_session['current_stage']
            
            # Проверяем, изменился ли этап внутри той же сессии
            if original_stage != current_stage:
                logger.info(f"🔄 Этап изменился: {original_stage} -> {current_stage} (сессия {original_session_id})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки изменения этапа пользователя {user_id}: {e}")
            return False

    async def get_last_event_info_by_user_and_type(self, user_id: int, event_type: str) -> Optional[str]:
        """
        Получает event_info последнего события определенного типа для пользователя
        
        Args:
            user_id: Telegram ID пользователя
            event_type: Тип события для поиска
            
        Returns:
            str: event_info последнего найденного события или None если не найдено
        """
        try:
            # 1. Получаем последнюю сессию пользователя
            sessions_query = self.client.table('sales_chat_sessions').select(
                'id'
            ).eq('user_id', user_id).order('created_at', desc=True).limit(1)
            
            # Фильтруем по bot_id если указан
            if self.bot_id:
                sessions_query = sessions_query.eq('bot_id', self.bot_id)
            
            sessions_response = sessions_query.execute()
            
            if not sessions_response.data:
                logger.info(f"Пользователь {user_id} не найден в сессиях")
                return None
            
            session_id = sessions_response.data[0]['id']
            logger.info(f"Найдена последняя сессия {session_id} для пользователя {user_id}")
            
            # 2. Ищем последнее событие с этим session_id и event_type
            events_response = self.client.table('session_events').select(
                'event_info', 'created_at'
            ).eq('session_id', session_id).eq('event_type', event_type).order(
                'created_at', desc=True
            ).limit(1).execute()
            
            if not events_response.data:
                logger.info(f"События типа '{event_type}' не найдены для сессии {session_id}")
                return None
            
            event_info = events_response.data[0]['event_info']
            created_at = events_response.data[0]['created_at']
            
            logger.info(f"Найдено последнее событие '{event_type}' для пользователя {user_id}: {event_info[:50]}... (создано: {created_at})")
            
            return event_info
            
        except Exception as e:
            logger.error(f"Ошибка получения последнего события для пользователя {user_id}, тип '{event_type}': {e}")
            return None