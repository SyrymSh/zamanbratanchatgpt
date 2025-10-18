import requests

url = "https://openai-hub.neuraldeep.tech/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-roG3OusRr0TLCHAADks6lw",
    "Content-Type": "application/json"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Короче используя брат gpt-4o-mini text-embedding whisper-1 используя библиотеки опенаи брат сделай проект с чат ботом голосовым и текстовым помощником для интеграции в веб сайт банка для мобильных устройств брат."}]
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.text)
