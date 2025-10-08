# Главное меню

start_kb = [
    ("🛏️ Спальная мебель", "sleep_furniture"),
    ("🍳 Кухонная мебель", "kitchen_furniture"),
    ("🛋️ Мягкая мебель", "soft_furniture"),
    ("📚 Столы и стулья", "tables_chairs"),
    ("📺 Тумбы и комоды", "cabinets_commodes"),
    ("🛏️ Кровати", "bed_furniture"),
    ("🛏️️ Матрасы", "mattresses"),
    ("🚪 Шкафы", "wardrobes"),
    ("ℹ️ О компании / Контакты", "about_company"),
    ("🤝 Сотрудничество", "cooperation_company"),
]

# Админ меню
admin_kb = [
    ("🗂️ Добавить категорию", "new_category_furniture"),
    ("🪑 Добавить мебель", "new_furniture"),
    ("🗑️ Удалить мебель", "remove_furniture"),
    ("📋 Список категорий", "list_categories_furniture"),
    ("🤝 Заявки", "cooperation_requests"),
    ("◀️ Назад", "back_to_main")
]

# Кнопка отмены для сотрудничества
cancel_cooperation = [
    ("⏪ Отмена", 'cancel_cooperation')
]

# Кнопка отмены для категорий
build_cancel_kb = [
    ("❌ Отменить", "cancel_category"),
]

country_kb = [
    "🇷🇺 Россия",
    "🇹🇷 Турция"
]

# Страны производства
contry_of_origin_kb = [
    ("🇷🇺 Россия", "russian_origin"),
    ("🇹🇷 Турция", "turkey_origin"),
    ("⬅️ Назад", "back_to_main")
]

# Подкатегории кухонной мебели
kitchen_subcategory_kb = [
    ("📏 Прямая кухня", "straight_kitchen"),
    ("📐 Угловая кухня", "corner_kitchen"),
    ("⬅️ Назад", "back_to_main")
]


def get_accept_cancel_buttons(request_id: int):
    return [
        ("❌ Отклонить", f"cancel_cooperation_requests_{request_id}"),
        ("✅ Одобрить", f"accepted_cooperation_requests_{request_id}"),
        ("⏪ Отмена", "show_requests_cooperation_2")
    ]


send_furnitures_buttons = [
    "⏩",
    "🏠 Главное меню"
]
