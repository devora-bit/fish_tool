"""
Менеджер данных для работы с JSON файлами
"""
import json
import os
from pathlib import Path
from typing import Optional
from models import AppData, Fish, TemporaryStorage


class DataManager:
    """Класс для управления данными приложения"""
    
    def __init__(self, data_dir: str = "assets"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.saved_data_path = self.data_dir / "saved_data.json"
        self.fish_data_path = self.data_dir / "fish_data.json"
        
    def load_fish_reference(self) -> dict:
        """Загрузить справочник рыб"""
        if not self.fish_data_path.exists():
            # Создать справочник по умолчанию
            default_fish_data = {
                "рыбы": [
                    # Высокоуровневые рыбы (уровни 7-9, запретные зоны) - rare/trophy
                    {
                        "name": "Сериола",
                        "rarity": "trophy",
                        "weight_range": [15.0, 40.0],
                        "best_bait": "Вертушка-пуля",
                        "price_guide": 8000
                    },
                    {
                        "name": "Рустер",
                        "rarity": "trophy",
                        "weight_range": [12.0, 35.0],
                        "best_bait": "Вертушка-пуля",
                        "price_guide": 7500
                    },
                    {
                        "name": "Марлин",
                        "rarity": "trophy",
                        "weight_range": [50.0, 200.0],
                        "best_bait": "Воблер",
                        "price_guide": 15000
                    },
                    {
                        "name": "Тарпон",
                        "rarity": "trophy",
                        "weight_range": [20.0, 80.0],
                        "best_bait": "Свимбейт",
                        "price_guide": 10000
                    },
                    {
                        "name": "Красный горбыль",
                        "rarity": "trophy",
                        "weight_range": [8.0, 25.0],
                        "best_bait": "Безбородочная вертушка",
                        "price_guide": 6000
                    },
                    {
                        "name": "Барракуда",
                        "rarity": "rare",
                        "weight_range": [5.0, 20.0],
                        "best_bait": "Тритон",
                        "price_guide": 2500
                    },
                    {
                        "name": "Тёмный горбыль",
                        "rarity": "rare",
                        "weight_range": [6.0, 18.0],
                        "best_bait": "Топпер",
                        "price_guide": 2000
                    },
                    {
                        "name": "Круглый трахинот",
                        "rarity": "rare",
                        "weight_range": [4.0, 15.0],
                        "best_bait": "Джитовая блесна",
                        "price_guide": 1800
                    },
                    # Среднеуровневые рыбы (уровни 4-7) - uncommon/rare
                    {
                        "name": "Стальноголовый лосось",
                        "rarity": "rare",
                        "weight_range": [3.0, 12.0],
                        "best_bait": "Тритон",
                        "price_guide": 1500
                    },
                    {
                        "name": "Прибрежный басс",
                        "rarity": "rare",
                        "weight_range": [2.0, 8.0],
                        "best_bait": "Колеблющаяся блесна",
                        "price_guide": 1200
                    },
                    {
                        "name": "Альбула",
                        "rarity": "rare",
                        "weight_range": [1.5, 6.0],
                        "best_bait": "Узкая блесна",
                        "price_guide": 1000
                    },
                    {
                        "name": "Снук обыкновенный",
                        "rarity": "rare",
                        "weight_range": [2.5, 10.0],
                        "best_bait": "Средняя блесна",
                        "price_guide": 1100
                    },
                    {
                        "name": "Полосатый лаврак",
                        "rarity": "rare",
                        "weight_range": [2.0, 9.0],
                        "best_bait": "Джерк",
                        "price_guide": 1300
                    },
                    {
                        "name": "Жерех",
                        "rarity": "uncommon",
                        "weight_range": [1.0, 5.0],
                        "best_bait": "Колеблющаяся блесна / Креветки",
                        "price_guide": 400
                    },
                    {
                        "name": "Стерлядь",
                        "rarity": "trophy",
                        "weight_range": [1.5, 8.0],
                        "best_bait": "Мясо лобстера",
                        "price_guide": 5000
                    },
                    {
                        "name": "Сазан",
                        "rarity": "uncommon",
                        "weight_range": [2.0, 12.0],
                        "best_bait": "Пеллетсы",
                        "price_guide": 300
                    },
                    {
                        "name": "Голавль",
                        "rarity": "uncommon",
                        "weight_range": [0.5, 3.0],
                        "best_bait": "Крэнк",
                        "price_guide": 250
                    },
                    {
                        "name": "Судак обыкновенный",
                        "rarity": "uncommon",
                        "weight_range": [1.0, 8.0],
                        "best_bait": "Двухвостый твистер",
                        "price_guide": 350
                    },
                    # Низкоуровневые рыбы (уровни 1-5) - common/uncommon
                    {
                        "name": "Сом обыкновенный",
                        "rarity": "uncommon",
                        "weight_range": [3.0, 20.0],
                        "best_bait": "Двухвостый тамстер / Латушка",
                        "price_guide": 200
                    },
                    {
                        "name": "Зеркальный карп",
                        "rarity": "uncommon",
                        "weight_range": [2.0, 15.0],
                        "best_bait": "Почки буйвола",
                        "price_guide": 180
                    },
                    {
                        "name": "Радужная форель",
                        "rarity": "uncommon",
                        "weight_range": [0.5, 4.0],
                        "best_bait": "Спиннинг",
                        "price_guide": 220
                    },
                    {
                        "name": "Обыкновенная щука",
                        "rarity": "uncommon",
                        "weight_range": [1.0, 10.0],
                        "best_bait": "Поппер-лягушка / Речной рак",
                        "price_guide": 280
                    },
                    {
                        "name": "Речной окунь",
                        "rarity": "common",
                        "weight_range": [0.3, 2.0],
                        "best_bait": "Отвесная блесна / Живец",
                        "price_guide": 80
                    },
                    {
                        "name": "Серебряный карась",
                        "rarity": "common",
                        "weight_range": [0.2, 1.5],
                        "best_bait": "Мотыль",
                        "price_guide": 60
                    },
                    {
                        "name": "Коричневый сом",
                        "rarity": "common",
                        "weight_range": [1.0, 8.0],
                        "best_bait": "Сверчки",
                        "price_guide": 100
                    },
                    {
                        "name": "Плотва",
                        "rarity": "common",
                        "weight_range": [0.1, 0.8],
                        "best_bait": "Тесто",
                        "price_guide": 40
                    },
                    {
                        "name": "Лещ",
                        "rarity": "common",
                        "weight_range": [0.5, 3.0],
                        "best_bait": "Кукуруза",
                        "price_guide": 70
                    },
                    {
                        "name": "Краснопёрка",
                        "rarity": "common",
                        "weight_range": [0.2, 1.0],
                        "best_bait": "Хлеб",
                        "price_guide": 50
                    },
                    {
                        "name": "Вобла",
                        "rarity": "common",
                        "weight_range": [0.1, 0.6],
                        "best_bait": "Сверчки",
                        "price_guide": 45
                    },
                    # Особые и трофейные рыбы
                    {
                        "name": "Древняя гинерия",
                        "rarity": "trophy",
                        "weight_range": [50.0, 200.0],
                        "best_bait": "Особая приманка",
                        "price_guide": 20000
                    },
                    {
                        "name": "Токсичный окунь",
                        "rarity": "trophy",
                        "weight_range": [2.0, 10.0],
                        "best_bait": "Защитная приманка",
                        "price_guide": 12000
                    },
                    {
                        "name": "Оранжевый карп",
                        "rarity": "trophy",
                        "weight_range": [5.0, 25.0],
                        "best_bait": "Специальная приманка",
                        "price_guide": 8000
                    },
                    {
                        "name": "Карась",
                        "rarity": "common",
                        "weight_range": [0.2, 1.2],
                        "best_bait": "Универсальная приманка",
                        "price_guide": 55
                    },
                    {
                        "name": "Красный солдат",
                        "rarity": "trophy",
                        "weight_range": [10.0, 50.0],
                        "best_bait": "Трофейная приманка",
                        "price_guide": 15000
                    },
                    {
                        "name": "Золотая рыбка",
                        "rarity": "trophy",
                        "weight_range": [0.1, 0.5],
                        "best_bait": "Золотая наживка",
                        "price_guide": 25000
                    },
                    {
                        "name": "Аквамарин",
                        "rarity": "trophy",
                        "weight_range": [8.0, 30.0],
                        "best_bait": "Морская приманка",
                        "price_guide": 10000
                    },
                    {
                        "name": "Тунец",
                        "rarity": "rare",
                        "weight_range": [20.0, 100.0],
                        "best_bait": "Сардина",
                        "price_guide": 3000
                    },
                    {
                        "name": "Камбала",
                        "rarity": "uncommon",
                        "weight_range": [0.5, 5.0],
                        "best_bait": "Морская приманка",
                        "price_guide": 400
                    },
                    {
                        "name": "Форель",
                        "rarity": "trophy",
                        "weight_range": [1.0, 8.0],
                        "best_bait": "Трофейная приманка",
                        "price_guide": 5000
                    }
                ]
            }
            self.save_fish_reference(default_fish_data)
            return default_fish_data
        
        with open(self.fish_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_fish_reference(self, data: dict):
        """Сохранить справочник рыб"""
        with open(self.fish_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_app_data(self) -> AppData:
        """Загрузить данные приложения"""
        if not self.saved_data_path.exists():
            app_data = AppData.create_default()
            self.save_app_data(app_data)
            return app_data
        
        with open(self.saved_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return AppData.from_dict(data)
    
    def save_app_data(self, app_data: AppData):
        """Сохранить данные приложения"""
        with open(self.saved_data_path, 'w', encoding='utf-8') as f:
            json.dump(app_data.to_dict(), f, ensure_ascii=False, indent=2)
    
    def get_fish_info(self, name: str) -> Optional[dict]:
        """Получить информацию о рыбе из справочника"""
        fish_data = self.load_fish_reference()
        for fish in fish_data.get("рыбы", []):
            if fish["name"].lower() == name.lower():
                return fish
        return None
