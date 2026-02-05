"""
UI компонент для страницы статистики
"""
import flet as ft
from models import AppData, Fish
from collections import Counter


# Цвета редкости
RARITY_COLORS = {
    "common": "#9CA3AF",      # gray-400
    "uncommon": "#60A5FA",    # blue-400
    "rare": "#F87171",        # red-400
    "trophy": "#34D399"       # emerald-400
}

RARITY_NAMES = {
    "common": "Серая",
    "uncommon": "Синяя",
    "rare": "Красная",
    "trophy": "Зеленая"
}


class StatsView:
    """Виджет страницы статистики"""
    
    def __init__(self, page: ft.Page, data_manager, app_data: AppData):
        self.page = page
        self.data_manager = data_manager
        self.app_data = app_data
        
        self.stats_container = ft.Ref[ft.Container]()
    
    def build(self) -> ft.Container:
        """Построить главный контейнер страницы"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Статистика", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        ref=self.stats_container,
                        content=ft.Column([], spacing=15),
                        expand=True
                    )
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            padding=20,
            expand=True
        )
    
    def _calculate_stats(self) -> dict:
        """Вычислить статистику"""
        # Собрать все рыбы из всех хранилищ
        all_fishes = []
        
        # Из временных хранилищ
        for storage in self.app_data.temporary_storages:
            all_fishes.extend(storage.fishes)
        
        # Из постоянного хранилища
        all_fishes.extend(self.app_data.permanent_storage)
        
        if not all_fishes:
            return {
                "total": 0,
                "most_common": None,
                "max_weight": None,
                "rarity_distribution": {},
                "top_fishes": []
            }
        
        # Общее количество
        total = len(all_fishes)
        
        # Самый частый улов
        name_counter = Counter(f.name for f in all_fishes)
        most_common = name_counter.most_common(1)[0] if name_counter else None
        
        # Рекордный вес
        max_weight_fish = max(all_fishes, key=lambda f: f.weight) if all_fishes else None
        
        # Распределение по редкости
        rarity_counter = Counter(f.rarity for f in all_fishes)
        rarity_distribution = dict(rarity_counter)
        
        # Топ-5 самых пойманных
        top_fishes = name_counter.most_common(5)
        
        return {
            "total": total,
            "most_common": most_common,
            "max_weight": max_weight_fish,
            "rarity_distribution": rarity_distribution,
            "top_fishes": top_fishes
        }
    
    def _build_stats_display(self) -> ft.Column:
        """Построить отображение статистики"""
        stats = self._calculate_stats()
        
        widgets = [
            # Общая статистика
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Общая статистика", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.WATER_DROP, size=40, color=ft.Colors.BLUE),
                                ft.Column(
                                    [
                                        ft.Text("Всего поймано:", size=14, color=ft.Colors.GREY_400),
                                        ft.Text(str(stats["total"]), size=24, weight=ft.FontWeight.BOLD)
                                    ],
                                    spacing=5
                                )
                            ],
                            spacing=15
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.TRENDING_UP, size=30, color=ft.Colors.GREEN),
                                ft.Column(
                                    [
                                        ft.Text("Самый частый улов:", size=14, color=ft.Colors.GREY_400),
                                        ft.Text(
                                            f"{stats['most_common'][0]} ({stats['most_common'][1]} шт.)" 
                                            if stats["most_common"] else "Нет данных",
                                            size=16,
                                            weight=ft.FontWeight.W_500
                                        )
                                    ],
                                    spacing=5
                                )
                            ],
                            spacing=15
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.STAR, size=30, color=ft.Colors.AMBER),
                                ft.Column(
                                    [
                                        ft.Text("Рекордный вес:", size=14, color=ft.Colors.GREY_400),
                                        ft.Text(
                                            f"{stats['max_weight'].name} - {stats['max_weight'].weight:.2f} кг" 
                                            if stats["max_weight"] else "Нет данных",
                                            size=16,
                                            weight=ft.FontWeight.W_500
                                        )
                                    ],
                                    spacing=5
                                )
                            ],
                            spacing=15
                        )
                    ],
                    spacing=10
                ),
                padding=15,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
            ),
            
            # Распределение по редкости (круговой график - упрощенная версия)
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Распределение по редкости", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        self._build_rarity_chart(stats["rarity_distribution"])
                    ],
                    spacing=10
                ),
                padding=15,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
            ),
            
            # Топ-5 рыб
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Топ-5 самых пойманных", size=20, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        self._build_top_fishes_chart(stats["top_fishes"])
                    ],
                    spacing=10
                ),
                padding=15,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
            )
        ]
        
        return ft.Column(widgets, spacing=15, scroll=ft.ScrollMode.AUTO)
    
    def _build_rarity_chart(self, distribution: dict) -> ft.Column:
        """Построить график распределения по редкости"""
        total = sum(distribution.values())
        if total == 0:
            return ft.Column([ft.Text("Нет данных", color=ft.Colors.GREY_400)])
        
        items = []
        for rarity in ["trophy", "rare", "uncommon", "common"]:
            count = distribution.get(rarity, 0)
            percentage = (count / total * 100) if total > 0 else 0
            color = RARITY_COLORS.get(rarity, RARITY_COLORS["common"])
            name = RARITY_NAMES.get(rarity, "Серая")
            
            items.append(
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Container(
                                width=20,
                                height=20,
                                bgcolor=color,
                                border_radius=10
                            ),
                            col={"xs": 1, "sm": 1}
                        ),
                        ft.Container(
                            content=ft.Text(name, size=14),
                            col={"xs": 7, "sm": 8}
                        ),
                        ft.Container(
                            content=ft.Text(f"{count} ({percentage:.1f}%)", size=14, weight=ft.FontWeight.W_500),
                            col={"xs": 4, "sm": 3}
                        )
                    ],
                    spacing=10
                )
            )
            
            # Прогресс-бар
            items.append(
                ft.ProgressBar(
                    value=percentage / 100,
                    color=color,
                    bgcolor=ft.Colors.GREY_300,
                    height=8
                )
            )
            items.append(ft.Divider(height=1))
        
        return ft.Column(items, spacing=5)
    
    def _build_top_fishes_chart(self, top_fishes: list) -> ft.Column:
        """Построить график топ-5 рыб"""
        if not top_fishes:
            return ft.Column([ft.Text("Нет данных", color=ft.Colors.GREY_400)])
        
        max_count = top_fishes[0][1] if top_fishes else 1
        
        items = []
        for i, (name, count) in enumerate(top_fishes, 1):
            bar_width = (count / max_count) * 100 if max_count > 0 else 0
            
            items.append(
                ft.Column(
                    [
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    content=ft.Text(f"{i}.", size=14),
                                    col={"xs": 1, "sm": 1}
                                ),
                                ft.Container(
                                    content=ft.Text(name, size=14),
                                    col={"xs": 9, "sm": 10}
                                ),
                                ft.Container(
                                    content=ft.Text(str(count), size=14, weight=ft.FontWeight.W_500),
                                    col={"xs": 2, "sm": 1}
                                )
                            ],
                            spacing=10
                        ),
                        ft.ProgressBar(
                            value=bar_width / 100,
                            color=ft.Colors.BLUE_600,
                            bgcolor=ft.Colors.GREY_300,
                            height=20
                        )
                    ],
                    spacing=5
                )
            )
        
        return ft.Column(items, spacing=10)
    
    def refresh(self):
        """Обновить отображение"""
        # Обновить статистику
        self.stats_container.current.content = self._build_stats_display()
        self.page.update()
    
    def _show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Показать уведомление"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()
