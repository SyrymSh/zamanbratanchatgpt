from flask import Flask, request, jsonify, render_template
import requests
import json
from datetime import datetime
import os
import tempfile
from flask import send_file
import base64
from db.users import get_user_by_id

app = Flask(__name__)

# Конфигурация API
API_URL = "https://openai-hub.neuraldeep.tech/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer sk-roG3OusRr0TLCHAADks6lw",
    "Content-Type": "application/json"
}
user_id = 1
# Данные о продуктах банка
products_data = {
    "retail": [
        {
            "name": "BNPL (рассрочка)",
            "type": "финансирование",
            "min_amount": 10000,
            "max_amount": 300000,
            "min_term": 1,
            "max_term": 12,
            "fee": "от 300 тенге",
            "income": None,
            "min_age": 18,
            "max_age": 63
        },
        {
            "name": "Исламское финансирование",
            "type": "финансирование",
            "min_amount": 100000,
            "max_amount": 5000000,
            "min_term": 3,
            "max_term": 60,
            "fee": "от 6000 тенге",
            "income": None,
            "min_age": 18,
            "max_age": 60
        },
        {
            "name": "Исламская ипотека",
            "type": "финансирование",
            "min_amount": 3000000,
            "max_amount": 75000000,
            "min_term": 12,
            "max_term": 240,
            "fee": "от 200000 тенге",
            "income": None,
            "min_age": 25,
            "max_age": 60
        },
        {
            "name": "Копилка",
            "type": "Инвестиционный",
            "min_amount": 1000,
            "max_amount": 20000000,
            "min_term": 1,
            "max_term": 12,
            "fee": None,
            "income": "до 18%",
            "min_age": 18,
            "max_age": None
        },
        {
            "name": "Вакала",
            "type": "Инвестиционный",
            "min_amount": 50000,
            "max_amount": None,
            "min_term": 3,
            "max_term": 36,
            "fee": None,
            "income": "до 20%",
            "min_age": 18,
            "max_age": None
        }
    ]
}

# Данные пользователя
user_data = get_user_by_id(user_id)


def analyze_expenses(user_data):
    """Анализ расходов пользователя"""
    total_expenses = sum(user_data["expenses"].values())
    income = user_data["income"]
    savings_rate = (income - total_expenses) / income * 100

    analysis = {
        "total_expenses": total_expenses,
        "savings_rate": savings_rate,
        "expense_categories": user_data["expenses"],
        "recommendations": []
    }

    # Рекомендации по оптимизации
    if user_data["expenses"]["shopping"] > 50000:
        analysis["recommendations"].append("Рассмотрите возможность сокращения расходов на шоппинг")
    if savings_rate < 20:
        analysis["recommendations"].append("Рекомендуем увеличить норму сбережений до 20%")
    if user_data["expenses"]["entertainment"] > 40000:
        analysis["recommendations"].append("Можно оптимизировать расходы на развлечения")

    return analysis


def recommend_products(user_data, goal_type=None):
    """Рекомендация продуктов на основе профиля пользователя"""
    suitable_products = []

    for product in products_data["retail"]:
        # Проверка возраста
        age_ok = True
        if product.get("min_age") and user_data["age"] < product["min_age"]:
            age_ok = False
        if product.get("max_age") and user_data["age"] > product["max_age"]:
            age_ok = False

        # Проверка суммы
        amount_ok = True
        if product["min_amount"] and user_data["savings"] < product["min_amount"]:
            amount_ok = False

        if age_ok and amount_ok:
            if goal_type == "investment" and product["type"] == "Инвестиционный":
                suitable_products.append(product)
            elif goal_type == "finance" and product["type"] == "финансирование":
                suitable_products.append(product)
            elif goal_type is None:
                suitable_products.append(product)

    return suitable_products


def get_ai_response(message, context):
    """Получение ответа от GPT с контекстом пользователя"""
    try:
        # Подготовка системного промпта
        system_prompt = f"""
        Ты - AI-ассистент банка Zaman. Ты помогаешь клиентам с финансовыми целями, 
        анализом расходов и подбором продуктов. Будь дружелюбным, человечным и полезным.

        Информация о пользователе:
        - Возраст: {context['age']}
        - Доход: {context['income']} тенге/месяц
        - Сбережения: {context['savings']} тенге
        - Финансовые цели: {[goal['name'] for goal in context['goals']]}

        Доступные продукты банка: {json.dumps(products_data['retail'], ensure_ascii=False)}

        Анализ расходов пользователя:
        - Общие расходы: {context['expense_analysis']['total_expenses']} тенге/месяц
        - Норма сбережений: {context['expense_analysis']['savings_rate']:.1f}%
        - Рекомендации: {context['expense_analysis']['recommendations']}

        Отвечай на русском языке, будь empathetic и давай практические советы.
        Предлагай конкретные банковские продукты когда это уместно.
        Помогай бороться со стрессом через полезные привычки, а не через покупки.
        """

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"GPT API error: {response.status_code} - {response.text}")
            return "Извините, произошла ошибка при обращении к AI. Пожалуйста, попробуйте еще раз."

    except Exception as e:
        print(f"Error in AI response: {e}")
        return "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз."


@app.route('/')
def index():
    return render_template('index.html')


@app.after_request
def after_request(response):
    """Добавляем CORS headers"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Обработка текстовых сообщений"""
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    message = data.get('message', '').lower()

    # Анализ текущих расходов
    expense_analysis = analyze_expenses(user_data)

    context = {
        **user_data,
        "expense_analysis": expense_analysis
    }

    response = get_ai_response(message, context)

    # Показываем анализ только если запрос связан с финансами
    finance_keywords = ['расход', 'доход', 'сбережен', 'бюджет', 'трат', 'финанс', 'деньг', 'экономи', 'копить']
    show_analysis = any(keyword in message for keyword in finance_keywords)

    # Генерируем аудио ответ
    audio_file_path = text_to_speech(response)
    audio_filename = None
    if audio_file_path:
        audio_filename = os.path.basename(audio_file_path)

    return jsonify({
        "response": response,
        "expense_analysis": expense_analysis if show_analysis else None,
        "audio_filename": audio_filename
    })


def speech_to_text(audio_file):
    """Конвертация речи в текст используя Whisper"""
    try:
        url = "https://openai-hub.neuraldeep.tech/v1/audio/transcriptions"
        headers = {
            "Authorization": "Bearer sk-roG3OusRr0TLCHAADks6lw"
        }

        # Простая обработка без временных файлов
        audio_data = audio_file.read()
        if not audio_data:
            print("Audio file is empty")
            return None

        files = {
            'file': ('audio.webm', audio_data, 'audio/webm'),
            'model': (None, 'whisper-1')
        }

        print(f"Sending audio to Whisper API, size: {len(audio_data)} bytes")
        response = requests.post(url, headers=headers, files=files, timeout=30)

        print(f"Whisper API response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            text = result.get("text", "").strip()
            print(f"Transcribed text: '{text}'")
            return text if text else None
        else:
            print(f"Whisper API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error in speech-to-text: {str(e)}")
        return None


@app.route('/api/voice-chat', methods=['POST', 'OPTIONS'])
def voice_chat():
    """Обработка голосовых сообщений"""
    if request.method == 'OPTIONS':
        return '', 200

    if 'audio' not in request.files:
        print("No audio file in request")
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files['audio']
    print(f"Received audio file: {audio_file.filename}, content_type: {audio_file.content_type}")

    # Проверяем что файл не пустой
    if audio_file.filename == '':
        print("Empty filename")
        return jsonify({"error": "No selected file"}), 400

    # Конвертация речи в текст
    text_message = speech_to_text(audio_file)

    if not text_message:
        print("No text transcribed from audio")
        return jsonify({"error": "Could not process audio or no speech detected"}), 400

    print(f"Successfully transcribed: {text_message}")

    # Анализ расходов
    expense_analysis = analyze_expenses(user_data)

    context = {
        **user_data,
        "expense_analysis": expense_analysis
    }

    # Получение ответа от AI
    response_text = get_ai_response(text_message, context)

    # Показываем анализ только если запрос связан с финансами
    finance_keywords = ['расход', 'доход', 'сбережен', 'бюджет', 'трат', 'финанс', 'деньг', 'экономи', 'копить']
    show_analysis = any(keyword in text_message.lower() for keyword in finance_keywords)

    # Генерируем аудио ответ
    audio_file_path = text_to_speech(response_text)
    audio_filename = None
    if audio_file_path:
        audio_filename = os.path.basename(audio_file_path)

    return jsonify({
        "transcribed_text": text_message,
        "response": response_text,
        "expense_analysis": expense_analysis if show_analysis else None,
        "audio_filename": audio_filename
    })

def text_to_speech_openai(text):
    """Конвертация текста в речь используя OpenAI TTS API"""
    try:
        url = "https://openai-hub.neuraldeep.tech/v1/audio/speech"
        headers = {
            "Authorization": "Bearer sk-roG3OusRr0TLCHAADks6lw",
            "Content-Type": "application/json"
        }

        data = {
            "model": "tts-1",
            "input": text[:4096],  # Ограничиваем длину текста
            "voice": "alloy",
            "response_format": "mp3"
        }

        print(f"Sending TTS request for text: {text[:100]}...")
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                print(f"TTS audio saved to: {tmp_file.name}")
                return tmp_file.name
        else:
            print(f"TTS API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error in OpenAI TTS: {e}")
        return None


def text_to_speech(text):
    """Конвертация текста в речь (используем OpenAI TTS)"""
    return text_to_speech_openai(text)

@app.route('/api/audio/<filename>')
def serve_audio(filename):
    """Отдача аудио файлов"""
    try:
        audio_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, as_attachment=False, mimetype='audio/mp3')
        else:
            return "Audio not found", 404
    except Exception as e:
        print(f"Error serving audio: {e}")
        return "Error", 500


@app.route('/api/analyze-expenses', methods=['GET'])
def get_expense_analysis():
    """Получение анализа расходов"""
    analysis = analyze_expenses(user_data)
    return jsonify(analysis)


@app.route('/api/recommend-products', methods=['POST', 'OPTIONS'])
def recommend_products_route():
    """Рекомендация продуктов по цели"""
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    goal_type = data.get('goal_type')

    recommendations = recommend_products(user_data, goal_type)
    return jsonify({"products": recommendations})


@app.route('/api/transfer', methods=['POST', 'OPTIONS'])
def simulate_transfer():
    """Симуляция перевода денег"""
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    amount = data.get('amount')
    recipient = data.get('recipient')

    return jsonify({
        "status": "success",
        "message": f"Перевод {amount} тенге для {recipient} выполнен успешно",
        "transaction_id": f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
    })


@app.route('/api/test-api', methods=['GET'])
def test_api():
    """Тестирование подключения к API"""
    try:
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Привет! Ответь коротко 'Тест пройден'."}],
            "max_tokens": 50
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)

        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "API подключено успешно",
                "response": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Ошибка API: {response.status_code}",
                "details": response.text
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Исключение: {str(e)}"
        }), 500


if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')

    print("Запуск Zaman Bank AI Assistant...")
    print("Откройте: http://localhost:5000")
    print("Тест API: http://localhost:5000/api/test-api")
    app.run(debug=True, port=5000, host='0.0.0.0')