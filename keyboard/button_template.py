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
    ("🤝 Сотрудничество — партнерские программы и предложения", "cooperation_company"),
]

admin_kb = [
    ("🗂️ Добавить категорию мебели", "new_category_furniture"),
    ("🪑 Добавить мебель", "new_furniture"),
    ("🗑️ Удалить мебель", "remove_furniture"),
    ("✏️ Редактировать мебель", "edit_furniture"),
    ("📋 Список категорий мебели", "list_categories_furniture"),
    ("🤝 Заявки на сотрудничество", "cooperation_requests"),
    ("◀️ Назад", "back_to_main")
]

cancel_cooperation = [
    ("⏪ Отмена", 'cancel_cooperation')
]

build_cancel_kb = [
    ("❌ Отменить", "cancel_category"),
]


def get_accept_cancel_buttons(request_id: int):
    return [
        ("❌ Отклонить", f"cancel_cooperation_requests_{request_id}"),
        ("✅ Одобрить", f"accepted_cooperation_requests_{request_id}"),
        ("⏪ Отмена", "show_requests_cooperation_2")
    ]
