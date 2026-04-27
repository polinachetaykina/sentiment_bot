import json
import logging
import os
import re
import sys
import joblib
import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

vectorizer = None
classifier = None
nltk_initialized = False

def init_nltk():
    global nltk_initialized
    if nltk_initialized:
        return True
    
    try:
        import nltk
        
        # Папка для NLTK данных
        nltk_data_path = '/tmp/nltk_data'
        os.makedirs(nltk_data_path, exist_ok=True)
        nltk.data.path.insert(0, nltk_data_path)
        
        # Скачиваем необходимые данные
        nltk.download('punkt', download_dir=nltk_data_path, quiet=True)
        nltk.download('punkt_tab', download_dir=nltk_data_path, quiet=True)
        nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)
        nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
        nltk.download('omw-1.4', download_dir=nltk_data_path, quiet=True)
        
        logger.info("NLTK данные успешно загружены")
        nltk_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Ошибка инициализации NLTK: {e}")
        return False

def init_models():
    global vectorizer, classifier
    
    if vectorizer is not None and classifier is not None:
        return True
    
    try:
        code_dir = os.path.dirname(os.path.abspath(__file__))
        v_path = os.path.join(code_dir, 'tfidf_vectorizer.pkl')
        c_path = os.path.join(code_dir, 'sentiment_classifier.pkl')
        
        logger.info(f"Загрузка моделей из {code_dir}")
        
        if not os.path.exists(v_path):
            logger.error(f"Файл векторизатора не найден: {v_path}")
            return False
        
        if not os.path.exists(c_path):
            logger.error(f"Файл классификатора не найден: {c_path}")
            return False
        
        vectorizer = joblib.load(v_path)
        classifier = joblib.load(c_path)
        
        logger.info("Модели успешно загружены")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка загрузки моделей: {e}")
        return False

def clean_text(text):
    """Полная очистка текста: нижний регистр, пунктуация, стоп-слова, лемматизация"""
    
    if not init_nltk():
        text = text.lower()
        text = re.sub(r'[^a-zA-Zа-яА-Я\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    try:
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        punctuation_wout_brackets = '!"#$%&\'*+,-./:;<=>?@[\\]^_`{|}~'
        stop_words = set(stopwords.words('english'))
        abbreviations = ['v', 'u', 'ur', 'r', 'b', 'n', 'y', 'c']
        stop_words.update(abbreviations)
        lemmatizer = WordNetLemmatizer()
        
        # 1. Удаляем HTML-теги
        text = re.sub(r"<[^>]+>", "", text)
        
        # 2. Удаляем пунктуацию (кроме скобок)
        text = re.sub('[' + re.escape(punctuation_wout_brackets) + ']', ' ', text)
        
        # 3. Токенизация
        words = word_tokenize(text)
        
        # 4. Нижний регистр
        words = [word.lower() for word in words]
        
        # 5. Лемматизация
        words = [lemmatizer.lemmatize(word) for word in words]
        
        # 6. Удаление стоп-слов
        words = [word for word in words if word not in stop_words]
        
        # 7. Собираем обратно
        result = " ".join(words)
        
        logger.info(f"Очистка текста: '{text[:50]}...' -> '{result[:50]}...'")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка в clean_text: {e}")
        # Fallback
        text = text.lower()
        text = re.sub(r'[^a-zA-Zа-яА-Я\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

def predict_sentiment(text):
    """Предсказание тональности текста"""
    
    try:
        if not init_models():
            return "ошибка", 0.0, "❌"
        
        # Очистка текста
        cleaned = clean_text(text)
        
        if not cleaned.strip():
            return "неопределённое", 0.0, "🤔"
        
        # Векторизация
        text_vectorized = vectorizer.transform([cleaned])
        
        # Предсказание
        prediction = classifier.predict(text_vectorized)[0]
        probabilities = classifier.predict_proba(text_vectorized)[0]
        confidence = max(probabilities) * 100
        
        # Преобразуем в читаемый формат
        if prediction in [1, '1', 'positive', 'pos', 'Positive']:
            sentiment = "позитивное"
            emoji = "😊"
        else:
            sentiment = "негативное"
            emoji = "😞"
        
        logger.info(f"Предсказание: {sentiment} (уверенность: {confidence:.1f}%)")
        return sentiment, confidence, emoji
        
    except Exception as e:
        logger.error(f"Ошибка предсказания: {e}")
        return "ошибка", 0.0, "❌"

def handler(event, context):
    """Основной обработчик Cloud Function"""
    
    logger.info("=== НОВЫЙ ЗАПРОС ===")
    
    try:
        # Парсим тело запроса
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        # Проверяем, что это сообщение от Telegram
        if 'message' not in body:
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'ok'})
            }
        
        # Извлекаем данные
        message = body['message']
        chat_id = message['chat']['id']
        message_text = message.get('text', '')
        first_name = message['chat'].get('first_name', 'Пользователь')
        
        logger.info(f"Сообщение от {first_name}: {message_text}")
        
        if message_text == '/start':
            response_text = (
                f"🤖 Привет, {first_name}! 👋\n\n"
                f"Я бот для анализа тональности текста.\n\n"
                f"📝 Отправь мне любое сообщение, и я скажу,\n"
                f"позитивное оно или негативное.\n\n"
                f"🔧 Команды:\n"
                f"/start - начать\n"
                f"/help - помощь\n"
                f"/status - статус бота"
            )
        
        elif message_text == '/help':
            response_text = (
                f"📖 Как пользоваться ботом:\n\n"
                f"1️⃣ Отправь любой текст на русском или английском\n"
                f"2️⃣ Бот очистит текст, удалит стоп-слова\n"
                f"3️⃣ Проведёт лемматизацию\n"
                f"4️⃣ Проанализирует с помощью обученной модели\n"
                f"5️⃣ Выдаст результат с процентом уверенности\n\n"
                f"✨ Примеры:\n"
                f"• 'Сегодня отличный день!'\n"
                f"• 'I am very sad today'\n"
                f"• 'This is amazing! 😊'"
            )
        
        elif message_text == '/status':
            # Проверяем доступность моделей и NLTK
            models_ok = init_models()
            nltk_ok = init_nltk()
            
            status_text = "✅ Бот работает\n\n"
            status_text += f"Модели: {'✅ загружены' if models_ok else '❌ не загружены'}\n"
            status_text += f"NLTK: {'✅ инициализирован' if nltk_ok else '❌ не инициализирован'}\n\n"
            status_text += f"Версия: 1.0\n"
            status_text += f"Готов к работе: {'✅ да' if models_ok and nltk_ok else '❌ нет'}"
            
            response_text = status_text
        
        else:
            # Анализ тональности
            sentiment, confidence, emoji = predict_sentiment(message_text)
            
            if confidence > 80:
                confidence_text = "🎯 Высокая уверенность"
            elif confidence > 60:
                confidence_text = "👍 Средняя уверенность"
            else:
                confidence_text = "🤔 Низкая уверенность"
            
            response_text = (
                f"{emoji} *Тональность:* {sentiment}\n\n"
                f"📊 *Уверенность:* {confidence:.1f}%\n"
                f"{confidence_text}"
            )
        
        # Формируем ответ для API Gateway
        telegram_response = {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": response_text,
            "parse_mode": "Markdown"
        }
        
        logger.info(f"✅ Ответ отправлен пользователю {chat_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(telegram_response, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        return {
            'statusCode': 200,
            'body': json.dumps({
                "method": "sendMessage",
                "chat_id": chat_id if 'chat_id' in locals() else 123456,
                "text": f"❌ Произошла ошибка. Пожалуйста, попробуйте позже."
            })
        }