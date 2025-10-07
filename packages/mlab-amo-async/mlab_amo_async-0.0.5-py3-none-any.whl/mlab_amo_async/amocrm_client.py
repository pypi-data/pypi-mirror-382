import os
import time
import asyncio
import aiohttp
import aiofiles
from typing import Dict, Any, List, Optional
from . import tokens
from . async_interaction import (
    AsyncLeadsInteraction, 
    AsyncContactsInteraction,
    AsyncCompaniesInteraction, 
    AsyncTasksInteraction,
    AsyncGenericInteraction
)
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Класс для работы с заметками
class AsyncNotesInteraction(AsyncGenericInteraction):
    """Класс для работы с заметками."""
    path = "notes"
    
    def __init__(self, token_manager, entity_type=None, entity_id=None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(token_manager=token_manager)
    
    def _get_path(self):
        if self.entity_type and self.entity_id:
            return f"{self.entity_type}/{self.entity_id}/notes"
        return "notes"


class AsyncAmoCRMClient:
    """Асинхронный клиент для работы с AmoCRM с поддержкой MongoDB."""
    
    def __init__(
        self, 
        client_id: str,
        client_secret: str,
        subdomain: str,
        redirect_url: str,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "medai"
    ):
        # Создаем менеджер токенов с MongoDB
        self.token_manager = tokens.TokenManager(mongo_uri=mongo_uri)
        self.token_manager(
            client_id=client_id,
            client_secret=client_secret,
            subdomain=subdomain,
            redirect_url=redirect_url
        )
        
        # Инициализируем API-клиенты для разных сущностей
        self.leads = AsyncLeadsInteraction(token_manager=self.token_manager)
        self.contacts = AsyncContactsInteraction(token_manager=self.token_manager)
        self.companies = AsyncCompaniesInteraction(token_manager=self.token_manager)
        self.tasks = AsyncTasksInteraction(token_manager=self.token_manager)
    
    async def init_token(self, auth_code: str) -> None:
        """Инициализация токена по коду авторизации."""
        await self.token_manager.init(code=auth_code, skip_error=False)
        print("✅ Токены успешно инициализированы и сохранены в MongoDB")
    
    async def get_lead(self, lead_id: int) -> Dict[str, Any]:
        """Получение сделки по ID."""
        return await self.leads.get(lead_id)
    
    async def get_contact(self, contact_id: int) -> Dict[str, Any]:
        """Получение контакта по ID."""
        return await self.contacts.get(contact_id)

    async def get_contact_from_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение контакта из сделки.
        
        :param lead_id: ID сделки
        :return: Данные первого контакта, связанного со сделкой
        """
        # Получаем сделку с включением связанных контактов
        lead = await self.leads.get(lead_id, include=["contacts"])
        
        # Проверяем есть ли у сделки связанные контакты
        if "_embedded" in lead and "contacts" in lead["_embedded"]:
            contacts = lead["_embedded"]["contacts"]
            if contacts:
                # Берем первый связанный контакт
                contact_id = contacts[0]["id"]
                # Получаем полные данные контакта
                return await self.get_contact(contact_id)
        
        return None
    
    async def get_contact_notes(self, contact_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех заметок контакта.
        
        :param contact_id: ID контакта
        :return: Список заметок
        """
        notes_client = AsyncNotesInteraction(
            token_manager=self.token_manager,
            entity_type="contacts",
            entity_id=contact_id
        )
        
        try:
            # Получаем URL запроса для отладки
            path = notes_client._get_path()
            url = await notes_client._get_url(path)
            print(f"🔍 URL запроса заметок контакта: {url}")
            
            # Получаем первую страницу заметок
            notes_response, status_code = await notes_client.request(
                "get", 
                path, 
                params={"page": 1, "limit": 100}
            )
            
            print(f"📊 Статус ответа API notes: {status_code}")
            print(f"📊 ОТЛАДКА: Ответ API notes для контакта {contact_id}: {notes_response}")
            
            if not notes_response or not isinstance(notes_response, dict):
                print(f"❌ Ответ API не содержит данных или имеет неверный формат: {notes_response}")
                return []
            
            # Извлекаем заметки из ответа
            if "_embedded" in notes_response and "notes" in notes_response["_embedded"]:
                notes = notes_response["_embedded"]["notes"]
                print(f"✅ Получено {len(notes)} заметок для контакта {contact_id}")
                
                # Выводим подробную информацию о каждой заметке
                for i, note in enumerate(notes):
                    note_type = note.get("note_type")
                    note_id = note.get("id")
                    created_at = note.get("created_at")
                    params = note.get("params", {})
                    
                    print(f"📝 Заметка #{i+1}: ID {note_id}, тип {note_type}, создана {created_at}")
                    
                return notes
            else:
                print(f"⚠️ Структура ответа API не содержит заметок: {notes_response}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка при получении заметок контакта {contact_id}: {e}")
            import traceback
            print(f"Стек-трейс: {traceback.format_exc()}")
            return []

    async def get_lead_notes(self, lead_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех заметок сделки.
        
        :param lead_id: ID сделки
        :return: Список заметок
        """
        try:
            notes_client = AsyncNotesInteraction(
                token_manager=self.token_manager,
                entity_type="leads",
                entity_id=lead_id
            )
            
            # Получаем URL запроса для отладки
            path = notes_client._get_path()
            url = await notes_client._get_url(path)
            print(f"🔍 URL запроса заметок сделки: {url}")
            
            # Получаем первую страницу заметок
            notes_response, status_code = await notes_client.request(
                "get", 
                path, 
                params={"page": 1, "limit": 100}
            )
            
            print(f"📊 Статус ответа API notes для сделки: {status_code}")
            print(f"📊 ОТЛАДКА: Ответ API notes для сделки {lead_id}: {notes_response}")
            
            if not notes_response or not isinstance(notes_response, dict):
                print(f"❌ Ответ API не содержит данных или имеет неверный формат: {notes_response}")
                return []
            
            # Извлекаем заметки из ответа
            if "_embedded" in notes_response and "notes" in notes_response["_embedded"]:
                notes = notes_response["_embedded"]["notes"]
                print(f"✅ Получено {len(notes)} заметок для сделки {lead_id}")
                
                # Выводим подробную информацию о каждой заметке
                for i, note in enumerate(notes):
                    note_type = note.get("note_type")
                    note_id = note.get("id")
                    created_at = note.get("created_at")
                    params = note.get("params", {})
                    
                    print(f"📝 Заметка #{i+1}: ID {note_id}, тип {note_type}, создана {created_at}")
                    
                return notes
            else:
                print(f"⚠️ Структура ответа API не содержит заметок: {notes_response}")
                return []
                
        except Exception as e:
            print(f"❌ Ошибка при получении заметок сделки {lead_id}: {e}")
            import traceback
            print(f"Стек-трейс: {traceback.format_exc()}")
            return []
        
    async def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение заметки по ID.
        
        :param note_id: ID заметки
        :return: Данные заметки или None, если заметка не найдена
        """
        try:
            # Пробуем прямой запрос к API
            note_path = f"notes/{note_id}"
            note_response, status_code = await self.contacts.request("get", note_path)
            
            if status_code == 200:
                print(f"✅ Заметка {note_id} найдена через прямой API-запрос")
                return note_response
            
            # Если прямой запрос не сработал, используем поиск
            print(f"⚠️ Прямой запрос заметки {note_id} вернул статус {status_code}")
            
            # Используем поиск по фильтру ID
            search_path = "notes"
            search_params = {
                "filter[id]": note_id
            }
            
            search_response, search_status = await self.contacts.request(
                "get", 
                search_path, 
                params=search_params
            )
            
            if search_status == 200 and "_embedded" in search_response and "notes" in search_response["_embedded"]:
                notes = search_response["_embedded"]["notes"]
                if notes:
                    print(f"✅ Заметка {note_id} найдена через поиск")
                    return notes[0]
            
            print(f"⚠️ Заметка {note_id} не найдена ни одним способом")
            return None
        except Exception as e:
            print(f"❌ Ошибка при получении заметки {note_id}: {e}")
            return None

    async def get_all_notes_types(self, entity_id: int, entity_type: str = "contacts") -> Dict[Any, int]:
        """
        Получает все типы заметок для сущности для отладки.
        
        :param entity_id: ID сущности
        :param entity_type: Тип сущности ("contacts" или "leads")
        :return: Словарь с типами заметок и их количеством
        """
        if entity_type == "contacts":
            notes = await self.get_contact_notes(entity_id)
        else:
            notes = await self.get_lead_notes(entity_id)
            
        note_types = {}
        
        for note in notes:
            note_type = note.get("note_type")
            if note_type in note_types:
                note_types[note_type] += 1
            else:
                note_types[note_type] = 1
                
        print(f"📊 Типы заметок для {entity_type} {entity_id}: {note_types}")
        return note_types

    async def get_call_links(self, contact_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех ссылок на записи звонков из заметок контакта.
        
        :param contact_id: ID контакта
        :return: Список словарей с note_id и call_link
        """
        try:
            notes = await self.get_contact_notes(contact_id)
            
            if not notes:
                print(f"⚠️ Заметки для контакта {contact_id} не найдены")
                return []
            
            print(f"📊 Обрабатываем {len(notes)} заметок для поиска звонков")
            
            # Получаем типы заметок для отладки
            await self.get_all_notes_types(contact_id)
            
            # Данные для аутентификации
            account_id = None
            user_id = None
            
            # Ищем account_id и user_id в заметках
            for note in notes:
                if not account_id and "account_id" in note:
                    account_id = note["account_id"]
                    print(f"📊 Найден account_id: {account_id}")
                
                if not user_id and "created_by" in note:
                    user_id = note["created_by"]
                    print(f"📊 Найден user_id: {user_id}")
                
                if account_id and user_id:
                    break
            
            # РАСШИРЯЕМ ЛОГИКУ ОПРЕДЕЛЕНИЯ ЗАМЕТОК О ЗВОНКАХ
            call_notes = []
            for note in notes:
                note_type = note.get("note_type")
                params = note.get("params", {})
                note_id = note.get("id")
                
                # Расширенная проверка типа заметки
                is_call_note = False
                
                # 1. Проверка по числовому типу
                if isinstance(note_type, int) and note_type in [10, 11, 12, 13, 14, 15]:
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по числовому типу {note_type}")
                
                # 2. Проверка по строковому типу
                elif isinstance(note_type, str) and any(keyword in note_type.lower() for keyword in ["call", "звонок", "запись", "аудио", "voice", "телефон"]):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по строковому типу {note_type}")
                
                # 3. Проверка параметров заметки
                elif params and (
                    "link" in params or 
                    "duration" in params or 
                    "phone" in params or
                    "call" in str(params).lower() or
                    "запись" in str(params).lower() or
                    "mango" in str(params).lower()
                ):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по параметрам")
                
                # 4. Проверка содержимого текста заметки
                elif "text" in note and note["text"] and any(keyword in note["text"].lower() for keyword in ["звонок", "позвонил", "call", "телефон", "запись"]):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по тексту")
                    
                # Дополнительная проверка - любая заметка с mango в параметрах
                elif "mango" in str(note).lower():
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок из-за упоминания mango")
                
                # Если заметка определена как звонок, добавляем в список
                if is_call_note:
                    call_notes.append(note)
                else:
                    print(f"🔍 Заметка {note_id} не является звонком, тип: {note_type}")
            
            # Если не нашли ни одной заметки о звонке
            if not call_notes:
                print(f"⚠️ Заметки о звонках для контакта {contact_id} не обнаружены")
                return []
            
            # Сортируем заметки по дате создания (убывание - сначала новые)
            call_notes.sort(key=lambda note: note.get("created_at", 0), reverse=True)
            
            print(f"📊 Найдено {len(call_notes)} заметок о звонках, отсортированных по дате")
            
            # Получаем ссылки из всех заметок о звонках
            call_links = []
            for i, note in enumerate(call_notes):
                print(f"📊 Проверяем заметку о звонке #{i+1}/{len(call_notes)}: ID {note.get('id')}, создана {note.get('created_at')}")
                
                note_id = note.get('id')
                params = note.get("params", {})
                
                # РАСШИРЕННЫЕ МЕТОДЫ ПОИСКА ССЫЛКИ
                
                # 1. Прямая проверка наличия ссылки в параметрах
                call_link = None
                if params and "link" in params and params["link"]:
                    call_link = params["link"]
                    print(f"✅ Найдена ссылка на запись звонка в заметке {note_id}: {call_link}")
                
                # 2. Поиск ссылки в других полях
                if not call_link and isinstance(params, dict):
                    call_link = self._find_link_in_dict(params)
                    if call_link:
                        print(f"✅ Найдена ссылка в других полях заметки {note_id}: {call_link}")
                
                # 3. Поиск ссылки в тексте заметки
                if not call_link and "text" in note and note["text"]:
                    import re
                    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    urls = re.findall(url_pattern, note["text"])
                    for url in urls:
                        if "mango" in url or "call" in url or "record" in url or "audio" in url:
                            call_link = url
                            print(f"✅ Найдена ссылка в тексте заметки {note_id}: {call_link}")
                            break
                
                # 4. Поиск по всей структуре заметки
                if not call_link:
                    call_link = self._find_link_in_dict(note, max_depth=5, current_depth=0)
                    if call_link:
                        print(f"✅ Найдена ссылка в структуре заметки {note_id}: {call_link}")
                
                # 5. Проверка наличия URL в строковом представлении заметки
                if not call_link:
                    str_note = str(note)
                    import re
                    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    urls = re.findall(url_pattern, str_note)
                    for url in urls:
                        # ВАЖНО: Пропускаем API эндпоинты заметок AmoCRM (не аудио)
                        if "/api/v4/contacts/" in url and "/notes/" in url:
                            print(f"⚠️ Пропускаем API эндпоинт заметки (не аудио): {url[:80]}")
                            continue
                        
                        if "mango" in url or "amocrm" in url or ".mp3" in url:
                            call_link = url
                            print(f"✅ Найдена ссылка в строковом представлении заметки {note_id}: {call_link}")
                            break
                
                # 6. Последняя попытка - извлечь ссылку из заметки mangocall
                if not call_link and "service" in note and note["service"] in ["mangocall", "mango", "mangooffice"]:
                    # Попытка воссоздать ссылку на основе данных заметки
                    if account_id and "id" in note and "created_at" in note:
                        note_id_str = str(note["id"])
                        created_at_str = str(note["created_at"])
                        # Формируем примерную ссылку в формате mango
                        call_link = f"https://amocrm.mango-office.ru/download/{account_id}/{note_id_str}_{created_at_str}/call.mp3"
                        print(f"🔧 Создана ссылка на запись звонка для заметки {note_id}: {call_link}")
                
                # Если нашли ссылку на запись
                if call_link:
                    # Добавляем параметры аутентификации, если их нет
                    if account_id and user_id and "userId" not in call_link:
                        if "?" in call_link:
                            call_link += f"&userId={user_id}&accountId={account_id}"
                        else:
                            call_link += f"?userId={user_id}&accountId={account_id}"
                        print(f"✅ Добавлены параметры аутентификации к ссылке: {call_link}")
                    
                    # Добавляем параметр загрузки
                    if "download=" not in call_link:
                        call_link += "&download=true" if "?" in call_link else "?download=true"
                    
                    call_links.append({
                        "note_id": note_id,
                        "call_link": call_link,
                        "created_at": note.get("created_at"),
                        "note": note  # Включаем полную заметку для дополнительной информации
                    })
            
            print(f"📊 Всего найдено ссылок на записи звонков: {len(call_links)}")
            return call_links
                
        except Exception as e:
            print(f"❌ Ошибка при поиске ссылок на записи звонков: {e}")
            import traceback
            print(f"Стек-трейс: {traceback.format_exc()}")
            return []

    async def get_call_links_from_lead(self, lead_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех ссылок на записи звонков из заметок сделки.
        
        :param lead_id: ID сделки
        :return: Список словарей с note_id и call_link
        """
        try:
            notes = await self.get_lead_notes(lead_id)
            
            if not notes:
                print(f"⚠️ Заметки для сделки {lead_id} не найдены")
                return []
            
            print(f"📊 Обрабатываем {len(notes)} заметок сделки для поиска звонков")
            
            # Получаем типы заметок для отладки
            await self.get_all_notes_types(lead_id, "leads")
            
            # Данные для аутентификации
            account_id = None
            user_id = None
            
            # Ищем account_id и user_id в заметках
            for note in notes:
                if not account_id and "account_id" in note:
                    account_id = note["account_id"]
                    print(f"📊 Найден account_id: {account_id}")
                
                if not user_id and "created_by" in note:
                    user_id = note["created_by"]
                    print(f"📊 Найден user_id: {user_id}")
                
                if account_id and user_id:
                    break
            
            # РАСШИРЯЕМ ЛОГИКУ ОПРЕДЕЛЕНИЯ ЗАМЕТОК О ЗВОНКАХ
            call_notes = []
            for note in notes:
                note_type = note.get("note_type")
                params = note.get("params", {})
                note_id = note.get("id")
                
                # Расширенная проверка типа заметки
                is_call_note = False
                
                # 1. Проверка по числовому типу
                if isinstance(note_type, int) and note_type in [10, 11, 12, 13, 14, 15]:
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по числовому типу {note_type}")
                
                # 2. Проверка по строковому типу
                elif isinstance(note_type, str) and any(keyword in note_type.lower() for keyword in ["call", "звонок", "запись", "аудио", "voice", "телефон"]):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по строковому типу {note_type}")
                
                # 3. Проверка параметров заметки
                elif params and (
                    "link" in params or 
                    "duration" in params or 
                    "phone" in params or
                    "call" in str(params).lower() or
                    "запись" in str(params).lower() or
                    "mango" in str(params).lower()
                ):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по параметрам")
                
                # 4. Проверка содержимого текста заметки
                elif "text" in note and note["text"] and any(keyword in note["text"].lower() for keyword in ["звонок", "позвонил", "call", "телефон", "запись"]):
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок по тексту")
                    
                # Дополнительная проверка - любая заметка с mango в параметрах
                elif "mango" in str(note).lower():
                    is_call_note = True
                    print(f"📞 Заметка {note_id} определена как звонок из-за упоминания mango")
                
                # Если заметка определена как звонок, добавляем в список
                if is_call_note:
                    call_notes.append(note)
                else:
                    print(f"🔍 Заметка {note_id} не является звонком, тип: {note_type}")
            
            # Если не нашли ни одной заметки о звонке
            if not call_notes:
                print(f"⚠️ Заметки о звонках для сделки {lead_id} не обнаружены")
                return []
            
            # Сортируем заметки по дате создания (убывание - сначала новые)
            call_notes.sort(key=lambda note: note.get("created_at", 0), reverse=True)
            
            print(f"📊 Найдено {len(call_notes)} заметок о звонках, отсортированных по дате")
            
            # Получаем ссылки из всех заметок о звонках
            call_links = []
            for i, note in enumerate(call_notes):
                print(f"📊 Проверяем заметку о звонке #{i+1}/{len(call_notes)}: ID {note.get('id')}, создана {note.get('created_at')}")
                
                note_id = note.get('id')
                params = note.get("params", {})
                
                # РАСШИРЕННЫЕ МЕТОДЫ ПОИСКА ССЫЛКИ
                
                # 1. Прямая проверка наличия ссылки в параметрах
                call_link = None
                if params and "link" in params and params["link"]:
                    call_link = params["link"]
                    print(f"✅ Найдена ссылка на запись звонка в заметке {note_id}: {call_link}")
                
                # 2. Поиск ссылки в других полях
                if not call_link and isinstance(params, dict):
                    call_link = self._find_link_in_dict(params)
                    if call_link:
                        print(f"✅ Найдена ссылка в других полях заметки {note_id}: {call_link}")
                
                # 3. Поиск ссылки в тексте заметки
                if not call_link and "text" in note and note["text"]:
                    import re
                    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    urls = re.findall(url_pattern, note["text"])
                    for url in urls:
                        if "mango" in url or "call" in url or "record" in url or "audio" in url:
                            call_link = url
                            print(f"✅ Найдена ссылка в тексте заметки {note_id}: {call_link}")
                            break
                
                # 4. Поиск по всей структуре заметки
                if not call_link:
                    call_link = self._find_link_in_dict(note, max_depth=5, current_depth=0)
                    if call_link:
                        print(f"✅ Найдена ссылка в структуре заметки {note_id}: {call_link}")
                
                # 5. Проверка наличия URL в строковом представлении заметки
                if not call_link:
                    str_note = str(note)
                    import re
                    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
                    urls = re.findall(url_pattern, str_note)
                    for url in urls:
                        # ВАЖНО: Пропускаем API эндпоинты заметок AmoCRM (не аудио)
                        if "/api/v4/contacts/" in url and "/notes/" in url:
                            print(f"⚠️ Пропускаем API эндпоинт заметки (не аудио): {url[:80]}")
                            continue
                        
                        if "mango" in url or "amocrm" in url or ".mp3" in url:
                            call_link = url
                            print(f"✅ Найдена ссылка в строковом представлении заметки {note_id}: {call_link}")
                            break
                
                # 6. Последняя попытка - извлечь ссылку из заметки mangocall
                if not call_link and "service" in note and note["service"] in ["mangocall", "mango", "mangooffice"]:
                    # Попытка воссоздать ссылку на основе данных заметки
                    if account_id and "id" in note and "created_at" in note:
                        note_id_str = str(note["id"])
                        created_at_str = str(note["created_at"])
                        # Формируем примерную ссылку в формате mango
                        call_link = f"https://amocrm.mango-office.ru/download/{account_id}/{note_id_str}_{created_at_str}/call.mp3"
                        print(f"🔧 Создана ссылка на запись звонка для заметки {note_id}: {call_link}")
                
                # Если нашли ссылку на запись
                if call_link:
                    # Добавляем параметры аутентификации, если их нет
                    if account_id and user_id and "userId" not in call_link:
                        if "?" in call_link:
                            call_link += f"&userId={user_id}&accountId={account_id}"
                        else:
                            call_link += f"?userId={user_id}&accountId={account_id}"
                        print(f"✅ Добавлены параметры аутентификации к ссылке: {call_link}")
                    
                    # Добавляем параметр загрузки
                    if "download=" not in call_link:
                        call_link += "&download=true" if "?" in call_link else "?download=true"
                    
                    call_links.append({
                        "note_id": note_id,
                        "call_link": call_link,
                        "created_at": note.get("created_at"),
                        "note": note  # Включаем полную заметку для дополнительной информации
                    })
            
            print(f"📊 Всего найдено ссылок на записи звонков: {len(call_links)}")
            return call_links
                
        except Exception as e:
            print(f"❌ Ошибка при поиске ссылок на записи звонков: {e}")
            import traceback
            print(f"Стек-трейс: {traceback.format_exc()}")
            return []
        
    def _find_link_in_dict(self, data: Dict[str, Any], max_depth: int = 3, current_depth: int = 0) -> Optional[str]:
        """
        Рекурсивно ищет поля, содержащие ссылку на запись звонка.
        
        :param data: Словарь для поиска
        :param max_depth: Максимальная глубина рекурсии
        :param current_depth: Текущая глубина рекурсии
        :return: Ссылка на запись звонка или None
        """
        if current_depth > max_depth or not isinstance(data, dict):
            return None
        
        # Расширенный список возможных имен полей, содержащих ссылку
        link_field_names = [
            "link", "recording_url", "url", "file", "audio", "record", "href", 
            "src", "source", "mp3", "wav", "recording", "запись", "voice", "sound",
            "download", "media", "call", "звонок", "телефон", "phone"
        ]
        
        for key, value in data.items():
            # Проверяем, есть ли ключ с названием связанным со ссылкой
            if (key == 'link' or 
                key == 'url' or 
                key == 'href' or 
                key == 'src' or
                key == 'download_url') and value is not None:
                if isinstance(value, str) and value.strip() != "" and ("http" in value or value.endswith(".mp3")):
                    print(f"📊 Найдена ссылка в поле '{key}': {value}")
                    return value
                    
            # Проверяем, содержит ли ключ одно из искомых слов
            if any(link_name in key.lower() for link_name in link_field_names):
                if isinstance(value, str) and value.strip() != "" and ("http" in value or value.endswith(".mp3")):
                    print(f"📊 Найдена ссылка в поле '{key}': {value}")
                    return value
            
            # Проверка на наличие URL в строковом значении
            if isinstance(value, str) and "http" in value and (".mp3" in value or "mango" in value or "amocrm" in value):
                print(f"📊 Найден URL в значении поля '{key}': {value}")
                return value
            
            # Рекурсивно проверяем вложенные словари
            if isinstance(value, dict):
                link = self._find_link_in_dict(value, max_depth, current_depth + 1)
                if link:
                    return link
                    
            # Также проверяем элементы списка
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        link = self._find_link_in_dict(item, max_depth, current_depth + 1)
                        if link:
                            return link
                    # Проверяем строковые элементы списка
                    elif isinstance(item, str) and "http" in item and (".mp3" in item or "mango" in item or "amocrm" in item):
                        print(f"📊 Найден URL в элементе списка для поля '{key}': {item}")
                        return item
        
        return None

    def _is_valid_audio_file(self, data: bytes, content_type: str) -> bool:
        """
        Проверка, является ли данные аудиофайлом.
        
        :param data: Данные файла
        :param content_type: Тип контента из заголовка
        :return: True, если данные похожи на аудиофайл
        """
        # Если это определенно аудиофайл по типу контента
        if content_type and any(mime in content_type.lower() for mime in [
            'audio/', 'application/octet-stream', 'application/binary'
        ]):
            # Проверяем минимальный размер (чтобы отфильтровать пустые файлы)
            if len(data) > 1000:
                return True
        
        # Проверяем на HTML-контент (что указывало бы на ошибку)
        if (data.startswith(b'<!DOCTYPE') or 
            data.startswith(b'<html') or 
            content_type.startswith('text/html')):
            return False
        
        # Проверяем на распространенные сигнатуры аудиофайлов
        # MP3 сигнатура: 'ID3' или 0xFF 0xFB
        if (data.startswith(b'ID3') or 
            (len(data) > 2 and data[0] == 0xFF and (data[1] == 0xFB or data[1] == 0xFA))):
            return True
        
        # WAV сигнатура: 'RIFF'
        if data.startswith(b'RIFF'):
            return True
        
        # Если файл достаточно большой и не похож на HTML
        if len(data) > 10000 and not data.startswith(b'<!DOCTYPE') and not data.startswith(b'<html'):
            return True
        
        return False

    async def download_call_recording(self, contact_id: int, save_dir: str = "audio", note_id: Optional[int] = None, max_retries: int = 3) -> Optional[str]:
        """
        Скачивание записи звонка и сохранение в файл.
        
        :param contact_id: ID контакта
        :param save_dir: Директория для сохранения файла
        :param note_id: ID конкретной заметки для скачивания (опционально)
        :param max_retries: Максимальное количество попыток
        :return: Путь к сохраненному файлу или None в случае ошибки
        """
        # Создаем директорию, если она не существует
        os.makedirs(save_dir, exist_ok=True)
        
        # Получаем все ссылки на звонки
        call_links = await self.get_call_links(contact_id)
        
        if not call_links:
            print(f"⚠️ Ссылки на записи звонков для контакта {contact_id} не найдены")
            return None
        
        # Если указан ID заметки, фильтруем только эту заметку
        if note_id:
            call_links = [link for link in call_links if link.get("note_id") == note_id]
            if not call_links:
                print(f"⚠️ Ссылка на запись звонка для заметки {note_id} не найдена")
                return None
        
        # Пробуем каждую ссылку, пока одна не сработает
        print(f"🔄 Пытаемся скачать {len(call_links)} записей звонков")
        
        for link_info in call_links:
            call_link = link_info["call_link"]
            current_note_id = link_info["note_id"]
            
            # Генерируем уникальное имя файла
            filename = f"{contact_id}_{current_note_id}_call.mp3"
            save_path = os.path.join(save_dir, filename)
            
            print(f"🔄 Скачиваем звонок из заметки {current_note_id} в {save_path}")
            
            # Пробуем несколько раз в случае случайных ошибок
            for attempt in range(max_retries):
                try:
                    # Создаем SSL-контекст с отключенной проверкой сертификата
                    import ssl
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    # Заголовки для имитации браузера
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
                        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Referer": "https://amocrm.mango-office.ru/",
                        "Origin": "https://amocrm.mango-office.ru",
                        "Sec-Fetch-Dest": "audio",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-origin"
                    }
                    
                    # Добавляем параметр download, если его нет
                    if "download=" not in call_link:
                        separator = "&" if "?" in call_link else "?"
                        call_link += f"{separator}download=true"
                    
                    # Добавляем временную метку для предотвращения кеширования
                    call_link += f"&_ts={int(time.time())}"
                    
                    print(f"🔄 Попытка {attempt+1}/{max_retries} - Скачиваем по ссылке: {call_link}")
                    
                    # Используем ClientSession с cookies
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    async with aiohttp.ClientSession(
                        connector=connector, 
                        headers=headers,
                        cookie_jar=aiohttp.CookieJar()
                    ) as session:
                        # Первый запрос для получения cookies
                        async with session.get("https://amocrm.mango-office.ru/") as init_response:
                            print(f"📡 Инициализация сессии: HTTP {init_response.status}")
                        
                        # Теперь скачиваем файл
                        async with session.get(call_link, allow_redirects=True) as response:
                            status = response.status
                            content_type = response.headers.get("Content-Type", "")
                            content_length = response.headers.get("Content-Length", "неизвестно")
                            
                            print(f"📡 Статус ответа: {status}")
                            print(f"📡 Тип контента: {content_type}")
                            print(f"📡 Размер контента: {content_length}")
                            
                            # Обрабатываем редиректы
                            if status in (301, 302, 303, 307, 308):
                                redirect_url = response.headers.get("Location")
                                print(f"📡 Редирект на: {redirect_url}")
                                
                                if redirect_url:
                                    async with session.get(redirect_url, allow_redirects=True) as redirect_response:
                                        data = await redirect_response.read()
                                        print(f"📦 Получено {len(data)} байт данных после редиректа")
                                        
                                        # Валидируем контент
                                        if self._is_valid_audio_file(data, content_type):
                                            async with aiofiles.open(save_path, 'wb') as f:
                                                await f.write(data)
                                            
                                            print(f"✅ Запись звонка сохранена после редиректа: {save_path}")
                                            return save_path
                                        else:
                                            print(f"⚠️ Получен некорректный аудиоконтент после редиректа")
                            
                            # Обрабатываем успешный ответ
                            if status == 200:
                                data = await response.read()
                                content_size = len(data)
                                print(f"📦 Получено {content_size} байт данных")
                                
                                # Валидируем контент
                                if self._is_valid_audio_file(data, content_type):
                                    async with aiofiles.open(save_path, 'wb') as f:
                                        await f.write(data)
                                    
                                    print(f"✅ Запись звонка сохранена: {save_path}")
                                    return save_path
                                else:
                                    print(f"⚠️ Получен HTML или некорректный контент вместо аудио")
                                    
                                    # Сохраняем ответ для отладки
                                    debug_path = os.path.join(save_dir, f"{contact_id}_{current_note_id}_error_{attempt}.html")
                                    async with aiofiles.open(debug_path, 'wb') as f:
                                        await f.write(data)
                                    
                                    print(f"⚠️ Отладочный ответ сохранен в: {debug_path}")
                            else:
                                print(f"⚠️ Не удалось скачать файл: HTTP {status}")
                    
                    # Если мы здесь, то попытка скачивания не удалась
                    print(f"⚠️ Попытка {attempt+1}/{max_retries} не удалась для заметки {current_note_id}")
                    
                    # Ждем перед повторной попыткой
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка
                
                except Exception as e:
                    print(f"❌ Ошибка при скачивании файла из заметки {current_note_id}: {e}")
                    import traceback
                    print(f"Стек-трейс: {traceback.format_exc()}")
                    
                    # Ждем перед повторной попыткой
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка
        
        # Если мы перепробовали все ссылки и все попытки не удались
        print(f"❌ Все попытки скачивания не удались для контакта {contact_id}")
        return None

    async def download_call_recording_from_lead(self, lead_id: int, save_dir: str = "audio", note_id: Optional[int] = None, max_retries: int = 3) -> Optional[str]:
        """
        Скачивание записи звонка из сделки и сохранение в файл.
        
        :param lead_id: ID сделки
        :param save_dir: Директория для сохранения файла
        :param note_id: ID конкретной заметки для скачивания (опционально)
        :param max_retries: Максимальное количество попыток
        :return: Путь к сохраненному файлу или None в случае ошибки
        """
        # Создаем директорию, если она не существует
        os.makedirs(save_dir, exist_ok=True)
        
        # Получаем все ссылки на звонки
        call_links = await self.get_call_links_from_lead(lead_id)
        
        if not call_links:
            print(f"⚠️ Ссылки на записи звонков для сделки {lead_id} не найдены")
            return None
        
        # Если указан ID заметки, фильтруем только эту заметку
        if note_id:
            call_links = [link for link in call_links if link.get("note_id") == note_id]
            if not call_links:
                print(f"⚠️ Ссылка на запись звонка для заметки {note_id} не найдена")
                return None
        
        # Пробуем каждую ссылку, пока одна не сработает
        print(f"🔄 Пытаемся скачать {len(call_links)} записей звонков")
        
        for link_info in call_links:
            call_link = link_info["call_link"]
            current_note_id = link_info["note_id"]
            
            # Генерируем уникальное имя файла
            filename = f"lead_{lead_id}_note_{current_note_id}_call.mp3"
            save_path = os.path.join(save_dir, filename)
            
            print(f"🔄 Скачиваем звонок из заметки {current_note_id} в {save_path}")
            
            # Пробуем несколько раз в случае случайных ошибок
            for attempt in range(max_retries):
                try:
                    # Создаем SSL-контекст с отключенной проверкой сертификата
                    import ssl
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
                    # Заголовки для имитации браузера
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
                        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Referer": "https://amocrm.mango-office.ru/",
                        "Origin": "https://amocrm.mango-office.ru",
                        "Sec-Fetch-Dest": "audio",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Site": "same-origin"
                    }
                    
                    # Добавляем параметр download, если его нет
                    if "download=" not in call_link:
                        separator = "&" if "?" in call_link else "?"
                        call_link += f"{separator}download=true"
                    
                    # Добавляем временную метку для предотвращения кеширования
                    call_link += f"&_ts={int(time.time())}"
                    
                    print(f"🔄 Попытка {attempt+1}/{max_retries} - Скачиваем по ссылке: {call_link}")
                    
                    # Используем ClientSession с cookies
                    connector = aiohttp.TCPConnector(ssl=ssl_context)
                    async with aiohttp.ClientSession(
                        connector=connector, 
                        headers=headers,
                        cookie_jar=aiohttp.CookieJar()
                    ) as session:
                        # Первый запрос для получения cookies
                        async with session.get("https://amocrm.mango-office.ru/") as init_response:
                            print(f"📡 Инициализация сессии: HTTP {init_response.status}")
                        
                        # Теперь скачиваем файл
                        async with session.get(call_link, allow_redirects=True) as response:
                            status = response.status
                            content_type = response.headers.get("Content-Type", "")
                            content_length = response.headers.get("Content-Length", "неизвестно")
                            
                            print(f"📡 Статус ответа: {status}")
                            print(f"📡 Тип контента: {content_type}")
                            print(f"📡 Размер контента: {content_length}")
                            
                            # Обрабатываем редиректы
                            if status in (301, 302, 303, 307, 308):
                                redirect_url = response.headers.get("Location")
                                print(f"📡 Редирект на: {redirect_url}")
                                
                                if redirect_url:
                                    async with session.get(redirect_url, allow_redirects=True) as redirect_response:
                                        data = await redirect_response.read()
                                        print(f"📦 Получено {len(data)} байт данных после редиректа")
                                        
                                        # Валидируем контент
                                        if self._is_valid_audio_file(data, content_type):
                                            async with aiofiles.open(save_path, 'wb') as f:
                                                await f.write(data)
                                            
                                            print(f"✅ Запись звонка сохранена после редиректа: {save_path}")
                                            return save_path
                                        else:
                                            print(f"⚠️ Получен некорректный аудиоконтент после редиректа")
                            
                            # Обрабатываем успешный ответ
                            if status == 200:
                                data = await response.read()
                                content_size = len(data)
                                print(f"📦 Получено {content_size} байт данных")
                                
                                # Валидируем контент
                                if self._is_valid_audio_file(data, content_type):
                                    async with aiofiles.open(save_path, 'wb') as f:
                                        await f.write(data)
                                    
                                    print(f"✅ Запись звонка сохранена: {save_path}")
                                    return save_path
                                else:
                                    print(f"⚠️ Получен HTML или некорректный контент вместо аудио")
                                    
                                    # Сохраняем ответ для отладки
                                    debug_path = os.path.join(save_dir, f"lead_{lead_id}_note_{current_note_id}_error_{attempt}.html")
                                    async with aiofiles.open(debug_path, 'wb') as f:
                                        await f.write(data)
                                    
                                    print(f"⚠️ Отладочный ответ сохранен в: {debug_path}")
                            else:
                                print(f"⚠️ Не удалось скачать файл: HTTP {status}")
                    
                    # Если мы здесь, то попытка скачивания не удалась
                    print(f"⚠️ Попытка {attempt+1}/{max_retries} не удалась для заметки {current_note_id}")
                    
                    # Ждем перед повторной попыткой
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка
                
                except Exception as e:
                    print(f"❌ Ошибка при скачивании файла из заметки {current_note_id}: {e}")
                    import traceback
                    print(f"Стек-трейс: {traceback.format_exc()}")
                    
                    # Ждем перед повторной попыткой
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка
        
        # Если мы перепробовали все ссылки и все попытки не удались
        print(f"❌ Все попытки скачивания не удались для сделки {lead_id}")
        return None
        
    async def get_call_link(self, contact_id: int) -> Optional[str]:
        """
        Устаревший метод - получение самой свежей ссылки на запись звонка из заметок контакта.
        Для обратной совместимости.
        
        :param contact_id: ID контакта
        :return: Ссылка на запись звонка или None
        """
        call_links = await self.get_call_links(contact_id)
        if call_links:
            return call_links[0]["call_link"]
        return None
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание новой сделки."""
        return await self.leads.create(lead_data)
    
    async def update_lead(self, lead_id: int, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление сделки."""
        return await self.leads.update(lead_id, lead_data)
    
    async def close(self):
        """Закрыть соединения."""
        # При необходимости добавьте закрытие соединений
        pass