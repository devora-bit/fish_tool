"""
UI компонент для страницы справочника рыб
"""
import flet as ft
from typing import Callable


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


class WikiView:
    """Виджет страницы справочника рыб"""
    
    def __init__(self, page: ft.Page, data_manager, app_data):
        self.page = page
        self.data_manager = data_manager
        self.app_data = app_data
        
        self.search_field = ft.Ref[ft.TextField]()
        self.fish_list_view = ft.Ref[ft.ListView]()
        
        self.fish_reference = data_manager.load_fish_reference()
        self.filtered_fishes = self.fish_reference.get("рыбы", [])
    
    def build(self) -> ft.Container:
        """Построить главный контейнер страницы"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Справочник рыб", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.TextField(
                            ref=self.search_field,
                            label="Поиск",
                            prefix_icon=ft.Icons.SEARCH,
                            on_change=self._on_search,
                            hint_text="Введите название рыбы...",
                            expand=True
                        ),
                        width=None
                    ),
                    ft.Container(
                        content=ft.ListView(
                            ref=self.fish_list_view,
                            spacing=10,
                            expand=True
                        ),
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
    
    def _build_fish_card(self, fish_data: dict) -> ft.Container:
        """Создать карточку рыбы из справочника"""
        rarity = fish_data.get("rarity", "common")
        rarity_color = RARITY_COLORS.get(rarity, RARITY_COLORS["common"])
        rarity_name = RARITY_NAMES.get(rarity, "Серая")
        weight_range = fish_data.get("weight_range", [0, 1])
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.WATER_DROP, color=rarity_color, size=30),
                                    ft.Column(
                                        [
                                            ft.Text(fish_data["name"], size=18, weight=ft.FontWeight.BOLD),
                                            ft.Container(
                                                ft.Text(rarity_name, size=12),
                                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                                bgcolor=rarity_color,
                                                border_radius=5
                                            )
                                        ],
                                        spacing=5,
                                        expand=True
                                    )
                                ],
                                spacing=15
                            ),
                            ft.Divider(),
                            ft.ResponsiveRow(
                                [
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("Вес:", size=12, color=ft.Colors.GREY_400),
                                                ft.Text(f"{weight_range[0]:.1f} - {weight_range[1]:.1f} кг", size=14)
                                            ],
                                            spacing=2
                                        ),
                                        col={"xs": 12, "sm": 4, "md": 4}
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("Наживка:", size=12, color=ft.Colors.GREY_400),
                                                ft.Text(fish_data.get("best_bait", "Неизвестно"), size=14)
                                            ],
                                            spacing=2
                                        ),
                                        col={"xs": 12, "sm": 4, "md": 4}
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("Цена:", size=12, color=ft.Colors.GREY_400),
                                                ft.Text(f"{fish_data.get('price_guide', 0):.0f}", size=14)
                                            ],
                                            spacing=2
                                        ),
                                        col={"xs": 12, "sm": 4, "md": 4}
                                    )
                                ],
                                spacing=10
                            )
                        ],
                        spacing=10
                    ),
                    padding=15
                )
            ),
            border_radius=5
        )
    
    def _on_search(self, e):
        """Обработчик поиска"""
        search_term = e.control.value.lower() if e.control.value else ""
        all_fishes = self.fish_reference.get("рыбы", [])
        
        if search_term:
            self.filtered_fishes = [
                f for f in all_fishes 
                if search_term in f.get("name", "").lower()
            ]
        else:
            self.filtered_fishes = all_fishes
        
        self._refresh_fish_list()
    
    def _refresh_fish_list(self):
        """Обновить список рыб"""
        self.fish_list_view.current.controls = [
            self._build_fish_card(fish) for fish in self.filtered_fishes
        ]
        self.page.update()
    
    def refresh(self):
        """Обновить отображение"""
        self._refresh_fish_list()
    
    def _show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Показать уведомление"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()
