"""
Модели данных для трекера выловленной рыбы
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Fish:
    """Модель рыбы"""
    id: str
    name: str
    rarity: str  # 'common', 'uncommon', 'rare', 'trophy'
    rarity_display: str  # 'Серая', 'Синяя', 'Красная', 'Зеленая'
    weight: float
    timestamp: str  # ISO format datetime string
    price_guide: float
    best_bait: str
    storage: str  # 'temporary' or 'permanent'
    
    @classmethod
    def create(cls, name: str, rarity: str, weight: float, 
               price_guide: float, best_bait: str, storage: str = "temporary"):
        """Создать новую рыбу"""
        rarity_map = {
            "common": "Серая",
            "uncommon": "Синяя",
            "rare": "Красная",
            "trophy": "Зеленая"
        }
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            rarity=rarity,
            rarity_display=rarity_map.get(rarity, "Серая"),
            weight=weight,
            timestamp=datetime.now().isoformat(),
            price_guide=price_guide,
            best_bait=best_bait,
            storage=storage
        )
    
    def to_dict(self):
        """Преобразовать в словарь для JSON"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Создать из словаря"""
        return cls(**data)


@dataclass
class TemporaryStorage:
    """Временное хранилище"""
    name: str
    limit: float  # Лимит в килограммах
    fishes: list[Fish]
    
    def to_dict(self):
        return {
            "name": self.name,
            "limit": self.limit,
            "fishes": [f.to_dict() for f in self.fishes]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            limit=float(data["limit"]),
            fishes=[Fish.from_dict(f) for f in data.get("fishes", [])]
        )
    
    def get_total_weight_grams(self) -> float:
        """Получить общий вес рыбы в граммах"""
        return sum(f.weight for f in self.fishes)
    
    def get_total_weight_kg(self) -> float:
        """Получить общий вес рыбы в килограммах"""
        return self.get_total_weight_grams() / 1000
    
    def get_fill_percentage(self):
        """Получить процент заполнения по весу"""
        if self.limit == 0:
            return 0
        return (self.get_total_weight_kg() / self.limit) * 100
    
    def get_available_weight_kg(self) -> float:
        """Получить доступное место в кг"""
        return max(0, self.limit - self.get_total_weight_kg())


@dataclass
class AppData:
    """Основная структура данных приложения"""
    temporary_storages: list[TemporaryStorage]
    permanent_storage: list[Fish]
    current_storage_name: str
    permanent_storage_limit: float = 100.0  # Лимит в килограммах
    
    def to_dict(self):
        return {
            "temporary_storages": [ts.to_dict() for ts in self.temporary_storages],
            "permanent_storage": [f.to_dict() for f in self.permanent_storage],
            "current_storage_name": self.current_storage_name,
            "permanent_storage_limit": self.permanent_storage_limit
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            temporary_storages=[TemporaryStorage.from_dict(ts) for ts in data.get("temporary_storages", [])],
            permanent_storage=[Fish.from_dict(f) for f in data.get("permanent_storage", [])],
            current_storage_name=data.get("current_storage_name", ""),
            permanent_storage_limit=float(data.get("permanent_storage_limit", 100.0))
        )
    
    @classmethod
    def create_default(cls):
        """Создать структуру по умолчанию"""
        default_storage = TemporaryStorage(
            name="Основное хранилище",
            limit=50.0,  # 50 кг
            fishes=[]
        )
        return cls(
            temporary_storages=[default_storage],
            permanent_storage=[],
            current_storage_name="Основное хранилище",
            permanent_storage_limit=100.0  # 100 кг
        )
    
    def get_current_storage(self) -> Optional[TemporaryStorage]:
        """Получить текущее временное хранилище"""
        for storage in self.temporary_storages:
            if storage.name == self.current_storage_name:
                return storage
        if self.temporary_storages:
            self.current_storage_name = self.temporary_storages[0].name
            return self.temporary_storages[0]
        return None
    
    def get_permanent_total_weight_grams(self) -> float:
        """Получить общий вес в постоянном хранилище (граммы)"""
        return sum(f.weight for f in self.permanent_storage)
    
    def get_permanent_total_weight_kg(self) -> float:
        """Получить общий вес в постоянном хранилище (кг)"""
        return self.get_permanent_total_weight_grams() / 1000
    
    def get_permanent_fill_percentage(self) -> float:
        """Получить процент заполнения постоянного хранилища по весу"""
        if self.permanent_storage_limit == 0:
            return 0
        return (self.get_permanent_total_weight_kg() / self.permanent_storage_limit) * 100
    
    def get_permanent_available_weight_kg(self) -> float:
        """Получить доступное место в постоянном хранилище (кг)"""
        return max(0, self.permanent_storage_limit - self.get_permanent_total_weight_kg())
