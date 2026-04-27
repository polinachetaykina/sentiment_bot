Sentiment Analysis Telegram Bot
О проекте
Telegram бот для анализа тональности текстов, основанный на модели TF-IDF + Logistic Regression. Бот определяет, является ли сообщение пользователя позитивным или негативным, и возвращает результат с процентом уверенности.

Проект является финальной частью исследовательской работы по сравнению различных методов анализа тональности.

Исследовательская часть
Датасеты
Для обучения и тестирования моделей использовались три датасета с разными доменами:

№	Датасет	Описание
1	Sentiment Twitter	Тексты из твитов с разметкой тональности
2	Financial Sentiment	Тексты с настроениями на фондовом рынке
3	Movie Reviews	Отзывы на фильмы
Предобработка данных
1. Очистка текста от HTML-тегов и специальных символов
2. Приведение к нижнему регистру
3. Удаление пунктуации (кроме скобок, сохраняющих эмоции :), :()
4. Удаление стоп-слов и аббревиатур
5. Лемматизация с использованием NLTK

Сравниваемые методы
Метод	Тип
CountVectorizer	Bag of Words
TF-IDF	Взвешенная частота терминов
Word2Vec	Контекстные эмбеддинги (gensim)
FastText	Субсловные эмбеддинги
GloVe	Статические эмбеддинги (перенос обученных векторов)
BERT	Контекстуальные эмбеддинги (transformer)
Результаты обучения на конкатенированном датасете
Метод	F1-Score
TF-IDF	0.857 (85.7%) 
CountVectorizer	0.848
BERT	0.78
Word2Vec	0.80
FastText	0.78
GloVe	0.797
TF-IDF показал лучший результат на общем датасете.

Результаты обучения на отдельных датасетах
Датасет	TF-IDF F1-Score
💬 Твиты	0.866
🎬 Отзывы на фильмы	0.894
📈 Финансовые настроения	0.773
TF-IDF уверенно показал лучшие результаты на всех трёх доменах.

Вывод исследования
TF-IDF был выбран как основа для продакшн-решения благодаря:

1. Высокой точности предсказаний (85.7% на смешанных данных)
2. Быстрому времени инференса
3. Малому размеру модели
4. Устойчивости к шуму в текстах

Telegram Bot
Функциональность
Команда	Описание
/start	Приветственное сообщение
/help	Справка по использованию
/status	Проверка статуса бота и моделей
Примеры сообщений
Позитивные:

text
I am very happy today! 😊
This product is amazing!
Absolutely wonderful experience
Негативные:

text
I'm so disappointed
This is terrible
Worst service ever 😞
Ответ бота:

text
😊 позитивное
📊 Уверенность: 87.3%
🎯 Высокая уверенность


Компоненты
Telegram Bot API — приём сообщений от пользователей

Yandex API Gateway — маршрутизация webhook-запросов

Yandex Cloud Function — выполнение инференса

TF-IDF + Logistic Regression — модель анализа тональности

Структура проекта
text
sentiment_bot/
├── handler.py              # Основной код Cloud Function
├── requirements.txt        # Python зависимости
├── tfidf_vectorizer.pkl    # Обученный векторизатор
├── sentiment_classifier.pkl # Обученный классификатор
├── README.md               # Документация
└── notebooks.ipnb              # Jupyter Notebooks с исследованием

Развёртывание
Локальный запуск (для тестирования)
bash
# Клонирование репозитория
git clone https://github.com/yourusername/sentiment_bot.git
cd sentiment_bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота (локально для теста)
python bot.py
Деплой в Yandex Cloud
Создание ZIP архива:

bash
zip -r function.zip handler.py requirements.txt *.pkl
Настройка Cloud Function:

Среда выполнения: Python 3.12

Память: 1024 MB
Таймаут: 30 секунд
Точка входа: handler.handler
Настройка API Gateway:

yaml
openapi: 3.0.0
info:
  title: Sentiment Bot API
  version: 1.0.0
paths:
  /webhook:
    post:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: "your-function-id"
        service_account_id: "your-service-account-id"
Настройка webhook:
text
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-gateway.apigw.yandexcloud.net/webhook

Зависимости
txt
nltk==3.8.1      # Токенизация, стоп-слова, лемматизация
joblib==1.3.2    # Загрузка моделей
scikit-learn==1.6.1  # TF-IDF, логистическая регрессия
numpy==1.24.3    # Математические операции
requests==2.31.0 # HTTP запросы к Telegram API

Результаты работы бота
Метрика	Значение
Точность (Accuracy)	~85%
F1-Score	0.857
Время ответа	0.5-2 секунды
Поддерживаемые языки	Английский (с базовой поддержкой русского)

Команды бота в Telegram
Команда	Действие
/start	Начать диалог
/help	Показать справку
/status	Статус бота и моделей

Выводы по проекту
TF-IDF показал наилучшие результаты среди всех методов (F1 = 85.7%)
Качество обработки зависит от домена — лучшие результаты на отзывах к фильмам (89.4%)
Простота и скорость TF-IDF сделали его оптимальным для продакшн-решения

Контакты
Автор: Четайкина Полина
GitHub: [ссылка на репозиторий]

Telegram: 
@sentiment_mood_bot

Лицензия
MIT License
