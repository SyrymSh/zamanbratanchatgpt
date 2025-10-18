# База пользователей Zaman Bank
users_database = {
    "user1": {
        "user_id": 1,
        "name": "Айдар",
        "age": 28,
        "income": 450000,
        "expenses": {
            "food": 70000,
            "transport": 20000,
            "entertainment": 50000,
            "shopping": 60000,
            "bills": 55000
        },
        "savings": 150000,
        "goals": [
            {"name": "Автомобиль", "target": 8000000, "current": 1200000, "timeline": 24},
            {"name": "Образование", "target": 1000000, "current": 300000, "timeline": 12}
        ],
        "risk_profile": "умеренный",
        "preferences": ["инвестиции", "технологии"],
        "profession": "IT-специалист",
        "family_status": "холост"
    },
    "user2": {
        "user_id": 2,
        "name": "Гульнара",
        "age": 35,
        "income": 650000,
        "expenses": {
            "food": 60000,
            "transport": 15000,
            "entertainment": 25000,
            "shopping": 35000,
            "bills": 70000,
            "education": 40000
        },
        "savings": 800000,
        "goals": [
            {"name": "Ипотека", "target": 20000000, "current": 3000000, "timeline": 60},
            {"name": "Пенсионные накопления", "target": 5000000, "current": 1500000, "timeline": 120}
        ],
        "risk_profile": "консервативный",
        "preferences": ["недвижимость", "накопления"],
        "profession": "Бухгалтер",
        "family_status": "замужем, 2 детей"
    },
    "user3": {
        "user_id": 3,
        "name": "Арман",
        "age": 42,
        "income": 1200000,
        "expenses": {
            "food": 120000,
            "transport": 50000,
            "entertainment": 80000,
            "shopping": 100000,
            "bills": 150000,
            "travel": 100000
        },
        "savings": 3500000,
        "goals": [
            {"name": "Бизнес", "target": 10000000, "current": 5000000, "timeline": 36},
            {"name": "Образование детей", "target": 3000000, "current": 1000000, "timeline": 24}
        ],
        "risk_profile": "агрессивный",
        "preferences": ["бизнес", "акции", "криптовалюты"],
        "profession": "Предприниматель",
        "family_status": "женат, 3 детей"
    }
}

def get_user_by_id(user_id):
    """Получить пользователя по ID"""
    return users_database.get(user_id)