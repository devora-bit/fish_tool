"""
UI компонент для страницы журнала и хранилища
"""
import flet as ft
from datetime import datetime
from typing import Callable, Optional
from models import Fish, TemporaryStorage, AppData


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


class LogView:
    """Виджет страницы журнала"""
    
    def __init__(self, page: ft.Page, data_manager, app_data: AppData, 
                 on_data_changed: Callable):
        self.page = page
        self.data_manager = data_manager
        self.app_data = app_data
        self.on_data_changed = on_data_changed
        
        # Состояние формы
        self.selected_rarity = ft.Ref[ft.SegmentedButton]()
        self.fish_name_field = ft.Ref[ft.TextField]()
        self.weight_field = ft.Ref[ft.TextField]()
        self.storage_dropdown = ft.Ref[ft.Dropdown]()
        self.fish_list_view = ft.Ref[ft.ListView]()
        self.progress_bar = ft.Ref[ft.ProgressBar]()
        self.progress_text = ft.Ref[ft.Text]()  # Текст заполнения временного хранилища
        self.warning_banner = ft.Ref[ft.Banner]()
        self.permanent_list_view = ft.Ref[ft.ListView]()
        self.permanent_progress_bar = ft.Ref[ft.ProgressBar]()  # Прогресс постоянного хранилища
        self.permanent_progress_text = ft.Ref[ft.Text]()  # Текст заполнения постоянного хранилища
        
        # Флаг для отслеживания показанного предупреждения
        self._last_warning_percentage = {}  # {storage_name: last_shown_percentage}
        
        # Список рыб из справочника для автодополнения
        self.fish_reference = data_manager.load_fish_reference()
        self.fish_names = [f["name"] for f in self.fish_reference.get("рыбы", [])]
        
    def build(self) -> ft.Container:
        """Построить главный контейнер страницы"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=self._build_left_panel(),
                                col={"sm": 12, "md": 12, "lg": 4, "xl": 4},
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 4)
                                ),
                                height=700
                            ),
                            ft.Container(
                                content=self._build_center_panel(),
                                col={"sm": 12, "md": 12, "lg": 3, "xl": 3},
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 4)
                                ),
                                height=700
                            ),
                            ft.Container(
                                content=self._build_right_panel(),
                                col={"sm": 12, "md": 12, "lg": 5, "xl": 5},
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=15,
                                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 4)
                                ),
                                height=700
                            )
                        ],
                        spacing=20,
                        run_spacing=20
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            padding=20,
            expand=True
        )
    
    def _build_left_panel(self) -> ft.Column:
        """Левая панель: форма добавления и список текущего улова"""
        return ft.Column(
            [
                ft.Text("Временное хранилище", size=20, weight=ft.FontWeight.BOLD),
                self._build_add_fish_form(),
                ft.Divider(),
                self._build_current_catch_list(),
                self._build_progress_indicator()
            ],
            spacing=15,
            expand=True
        )
    
    def _build_rarity_selector(self) -> ft.SegmentedButton:
        """Создать селектор редкости"""
        segments = [
            ft.Segment(
                value="common",
                label="Серая",
                icon=ft.Icon(ft.Icons.CIRCLE, color=RARITY_COLORS["common"], size=16)
            ),
            ft.Segment(
                value="uncommon",
                label="Синяя",
                icon=ft.Icon(ft.Icons.CIRCLE, color=RARITY_COLORS["uncommon"], size=16)
            ),
            ft.Segment(
                value="rare",
                label="Красная",
                icon=ft.Icon(ft.Icons.CIRCLE, color=RARITY_COLORS["rare"], size=16)
            ),
            ft.Segment(
                value="trophy",
                label="Зеленая",
                icon=ft.Icon(ft.Icons.CIRCLE, color=RARITY_COLORS["trophy"], size=16)
            ),
        ]
        # Создаем кнопку с allow_empty_selection=True, чтобы можно было не устанавливать selected сразу
        button = ft.SegmentedButton(
            ref=self.selected_rarity,
            segments=segments,
            allow_multiple_selection=False,
            allow_empty_selection=True
        )
        # Устанавливаем selected после создания, используя список, который потом преобразуется в set
        # Это нужно сделать после создания, чтобы избежать проблем с сериализацией при инициализации
        return button
    
    def _build_add_fish_form(self) -> ft.Column:
        """Форма добавления новой рыбы"""
        return ft.Column(
            [
                # Селектор редкости
                ft.Text("Редкость:", size=14),
                self._build_rarity_selector(),
                
                # Поле названия с автодополнением
                ft.Text("Название рыбы:", size=14),
                ft.Dropdown(
                    ref=self.fish_name_field,
                    options=[ft.dropdown.Option(name) for name in self.fish_names],
                    hint_text="Выберите или введите название",
                    autofocus=False
                ),
                
                # Поле веса (в граммах)
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Text("Вес:", size=14),
                            col={"xs": 2, "sm": 2}
                        ),
                        ft.Container(
                            content=ft.TextField(
                                ref=self.weight_field,
                                hint_text="Введите вес в граммах",
                                keyboard_type=ft.KeyboardType.NUMBER
                            ),
                            col={"xs": 8, "sm": 8}
                        ),
                        ft.Container(
                            content=ft.Text("г", size=14, color=ft.Colors.GREY_600),
                            col={"xs": 2, "sm": 2}
                        )
                    ],
                    spacing=10
                ),
                
                # Кнопка добавления
                ft.ElevatedButton(
                    "Добавить в лог",
                    icon=ft.Icons.ADD,
                    on_click=self._on_add_fish,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_700
                    )
                )
            ],
            spacing=10
        )
    
    def _build_current_catch_list(self) -> ft.Container:
        """Список текущего улова"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Текущий улов:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.ListView(
                            ref=self.fish_list_view,
                            spacing=5,
                            expand=True
                        ),
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=5,
                        padding=5,
                        expand=True
                    )
                ],
                spacing=5,
                expand=True
            ),
            expand=True
        )
    
    def _build_progress_indicator(self) -> ft.Container:
        """Индикатор заполнения хранилища"""
        current_storage = self.app_data.get_current_storage()
        if not current_storage:
            return ft.Container()
        
        fill_percentage = current_storage.get_fill_percentage()
        is_warning = fill_percentage > 95
        
        # Показать предупреждение, если заполнено на 95% или больше
        warning_text = None
        if fill_percentage >= 95:
            warning_text = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=16),
                        ft.Text(
                            f"Хранилище заполнено на {fill_percentage:.1f}%!",
                            size=12,
                            color=ft.Colors.ORANGE,
                            weight=ft.FontWeight.BOLD
                        )
                    ],
                    spacing=5
                ),
                padding=ft.padding.only(bottom=5)
            )
        
        content_list = []
        if warning_text:
            content_list.append(warning_text)
        
        current_weight_kg = current_storage.get_total_weight_kg()
        content_list.extend([
            ft.ProgressBar(
                ref=self.progress_bar,
                value=min(fill_percentage / 100, 1.0),
                color=ft.Colors.RED if is_warning else ft.Colors.BLUE,
                bgcolor=ft.Colors.GREY_300
            ),
            ft.Text(
                ref=self.progress_text,
                value=f"Заполнено: {current_weight_kg:.2f} / {current_storage.limit:.1f} кг ({fill_percentage:.1f}%) • {len(current_storage.fishes)} шт",
                size=12
            )
        ])
        
        return ft.Container(
            content=ft.Column(
                content_list,
                spacing=5
            )
        )
    
    def _build_center_panel(self) -> ft.Column:
        """Центральная панель: управление хранилищами"""
        return ft.Column(
            [
                ft.Text("Управление хранилищами", size=20, weight=ft.FontWeight.BOLD),
                self._build_storage_selector(),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Создать",
                            icon=ft.Icons.ADD_BOX,
                            on_click=self._on_create_storage,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_700
                            ),
                            expand=True
                        ),
                        ft.ElevatedButton(
                            "Настроить",
                            icon=ft.Icons.SETTINGS,
                            on_click=self._on_edit_storage,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLUE_GREY_700
                            ),
                            expand=True
                        )
                    ],
                    spacing=10
                ),
                ft.ElevatedButton(
                    "Удалить хранилище",
                    icon=ft.Icons.DELETE,
                    on_click=self._on_delete_storage,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700
                    )
                ),
                ft.Divider(),
                ft.FilledTonalButton(
                    "Перевести в Постоянное хранилище",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=self._on_transfer_to_permanent,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_600
                    ),
                    height=50
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True
        )
    
    def _build_storage_selector(self) -> ft.Dropdown:
        """Селектор активного хранилища"""
        storage_names = [s.name for s in self.app_data.temporary_storages]
        dropdown = ft.Dropdown(
            ref=self.storage_dropdown,
            options=[ft.dropdown.Option(name) for name in storage_names],
            value=self.app_data.current_storage_name if storage_names else None,
            label="Активное хранилище"
        )
        # Устанавливаем обработчик после создания
        dropdown.on_change = self._on_storage_changed
        return dropdown
    
    def _build_right_panel(self) -> ft.Column:
        """Правая панель: постоянное хранилище"""
        fill_percentage = self.app_data.get_permanent_fill_percentage()
        is_warning = fill_percentage > 95
        
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Постоянное хранилище", size=20, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            tooltip="Настроить лимит",
                            on_click=self._on_configure_permanent_limit,
                            icon_size=20
                        )
                    ],
                    spacing=5
                ),
                ft.Column(
                    [
                        ft.Text(
                            ref=self.permanent_progress_text,
                            value=f"Заполнено: {self.app_data.get_permanent_total_weight_kg():.2f} / {self.app_data.permanent_storage_limit:.1f} кг • {len(self.app_data.permanent_storage)} шт",
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
                        ft.ProgressBar(
                            ref=self.permanent_progress_bar,
                            value=min(fill_percentage / 100, 1.0),
                            color=ft.Colors.RED if is_warning else ft.Colors.GREEN,
                            bgcolor=ft.Colors.GREY_300,
                            height=8
                        )
                    ],
                    spacing=5
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.ListView(
                        ref=self.permanent_list_view,
                        spacing=5,
                        expand=True
                    ),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=5,
                    padding=5,
                    expand=True
                ),
                ft.FilledButton(
                    "Продать весь улов",
                    icon=ft.Icons.SELL,
                    on_click=self._on_sell_all,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700
                    ),
                    height=50
                )
            ],
            spacing=15,
            expand=True
        )
    
    def _on_fish_name_selected(self, e):
        """Обработчик выбора рыбы из списка"""
        # Автоматически заполнить данные из справочника
        fish_name = e.control.value
        if fish_name:
            fish_info = self.data_manager.get_fish_info(fish_name)
            if fish_info:
                # Можно автоматически установить редкость, но не будем менять вес
                pass
    
    def _on_add_fish(self, e):
        """Добавить рыбу в лог"""
        print("DEBUG: _on_add_fish вызван!")
        try:
            # Получить выбранную редкость
            rarity = "common"  # Значение по умолчанию
            try:
                if self.selected_rarity.current:
                    selected_attr = getattr(self.selected_rarity.current, 'selected', None)
                    if selected_attr:
                        selected_list = list(selected_attr) if isinstance(selected_attr, (set, list, tuple)) else []
                        if selected_list:
                            rarity = selected_list[0]
            except Exception:
                rarity = "common"
            
            # Получить название
            fish_name = self.fish_name_field.current.value
            if not fish_name or not fish_name.strip():
                self._show_snackbar("Введите название рыбы!", ft.Colors.RED)
                return
            
            # Получить вес
            try:
                weight = float(self.weight_field.current.value or "0")
                if weight <= 0:
                    raise ValueError
            except ValueError:
                self._show_snackbar("Введите корректный вес!", ft.Colors.RED)
                return
            
            # Получить информацию о рыбе из справочника
            fish_info = self.data_manager.get_fish_info(fish_name)
            if not fish_info:
                price_guide = 50
                best_bait = "Неизвестно"
            else:
                price_guide = fish_info.get("price_guide", 50)
                best_bait = fish_info.get("best_bait", "Неизвестно")
            
            # Создать рыбу
            fish = Fish.create(
                name=fish_name.strip(),
                rarity=rarity,
                weight=weight,
                price_guide=price_guide,
                best_bait=best_bait,
                storage="temporary"
            )
            
            # Добавить в текущее хранилище
            current_storage = self.app_data.get_current_storage()
            if not current_storage:
                self._show_snackbar("Ошибка: нет активного хранилища!", ft.Colors.RED)
                return
            
            # Проверить лимит по весу (вес в граммах, лимит в кг)
            weight_kg = weight / 1000
            if current_storage.get_total_weight_kg() + weight_kg > current_storage.limit:
                available = current_storage.get_available_weight_kg()
                self._show_snackbar(
                    f"Недостаточно места! Доступно: {available:.2f} кг, пытаетесь добавить: {weight_kg:.2f} кг",
                    ft.Colors.RED
                )
                return
            
            current_storage.fishes.append(fish)
            
            # Очистить форму
            self.fish_name_field.current.value = ""
            self.weight_field.current.value = ""
            
            # Сохранить и обновить UI
            print(f"DEBUG: Сохраняю рыбу {fish_name}")
            self.data_manager.save_app_data(self.app_data)
            print("DEBUG: Данные сохранены")
            self.refresh()
            print("DEBUG: UI обновлен")
            self.on_data_changed()
            print("DEBUG: on_data_changed вызван")
            self._show_snackbar(f"Рыба '{fish_name}' добавлена!", ft.Colors.GREEN)
            print("DEBUG: _on_add_fish завершен успешно")
        except Exception as ex:
            print(f"ERROR в _on_add_fish: {ex}")
            import traceback
            traceback.print_exc()
            self._show_snackbar(f"Ошибка при добавлении рыбы: {ex}", ft.Colors.RED)
    
    def _on_edit_storage(self, e):
        """Редактировать текущее хранилище"""
        print("DEBUG: _on_edit_storage вызван!")
        current_storage = self.app_data.get_current_storage()
        if not current_storage:
            self._show_snackbar("Нет активного хранилища!", ft.Colors.RED)
            return
        
        current_weight_kg = current_storage.get_total_weight_kg()
        
        name_field = ft.TextField(
            label="Название хранилища", 
            value=current_storage.name,
            hint_text="Новое название (оставьте пустым, чтобы не менять)"
        )
        limit_field = ft.TextField(
            label="Лимит вместимости (кг)", 
            value=str(current_storage.limit),
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text=f"Минимум: {current_weight_kg:.2f} кг (текущий вес)",
            autofocus=True
        )
        
        def on_cancel(e):
            self._close_dialog(dialog)
        
        def on_confirm(e):
            new_name = name_field.value
            try:
                new_limit = float(limit_field.value or str(current_storage.limit))
                if new_limit <= 0:
                    self._show_snackbar("Лимит должен быть больше 0!", ft.Colors.RED)
                    return
                
                # Проверка: если новый лимит меньше текущего веса
                if new_limit < current_weight_kg:
                    self._show_snackbar(
                        f"Невозможно установить лимит {new_limit:.1f} кг! Текущий вес: {current_weight_kg:.2f} кг.",
                        ft.Colors.RED
                    )
                    return
                
                old_name = current_storage.name
                
                # Обновить данные
                if new_name and new_name.strip() and new_name.strip() != old_name:
                    # Проверить, что новое имя не занято
                    if any(s.name == new_name.strip() for s in self.app_data.temporary_storages if s.name != old_name):
                        self._show_snackbar("Хранилище с таким названием уже существует!", ft.Colors.RED)
                        return
                    current_storage.name = new_name.strip()
                    self.app_data.current_storage_name = new_name.strip()
                
                current_storage.limit = new_limit
                
                self.data_manager.save_app_data(self.app_data)
                self._close_dialog(dialog)
                self.refresh()
                self.on_data_changed()
                self._show_snackbar(f"Хранилище обновлено!", ft.Colors.GREEN)
            except ValueError:
                self._show_snackbar("Введите корректное число для лимита!", ft.Colors.RED)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Настройка: {current_storage.name}"),
            content=ft.Column(
                [
                    ft.Text(f"Текущий вес: {current_weight_kg:.2f} кг ({len(current_storage.fishes)} шт)", size=13, color=ft.Colors.GREY_400),
                    name_field,
                    limit_field
                ],
                tight=True,
                width=300,
                spacing=10
            ),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.FilledButton("Сохранить", on_click=on_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        print("DEBUG: Открываю диалог редактирования...")
        self._open_dialog(dialog)
    
    def _on_delete_storage(self, e):
        """Удалить текущее временное хранилище"""
        print("DEBUG: _on_delete_storage вызван!")
        current_storage = self.app_data.get_current_storage()
        if not current_storage:
            self._show_snackbar("Нет активного хранилища!", ft.Colors.RED)
            return
        
        # Нельзя удалить последнее хранилище
        if len(self.app_data.temporary_storages) <= 1:
            self._show_snackbar("Нельзя удалить последнее хранилище!", ft.Colors.RED)
            return
        
        fish_count = len(current_storage.fishes)
        weight_kg = current_storage.get_total_weight_kg()
        storage_name = current_storage.name
        
        def on_cancel(e):
            self._close_dialog(dialog)
        
        def on_confirm(e):
            # Удалить хранилище
            self.app_data.temporary_storages = [
                s for s in self.app_data.temporary_storages if s.name != storage_name
            ]
            
            # Переключиться на первое доступное хранилище
            if self.app_data.temporary_storages:
                self.app_data.current_storage_name = self.app_data.temporary_storages[0].name
            
            self.data_manager.save_app_data(self.app_data)
            self._close_dialog(dialog)
            self.refresh()
            self.on_data_changed()
            self._show_snackbar(f"Хранилище '{storage_name}' удалено!", ft.Colors.GREEN)
        
        # Предупреждение, если в хранилище есть рыба
        warning_text = ""
        if fish_count > 0:
            warning_text = f"\n\n⚠️ В хранилище {fish_count} рыб ({weight_kg:.2f} кг)!\nОни будут потеряны!"
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Удалить хранилище?"),
            content=ft.Column(
                [
                    ft.Text(f"Удалить хранилище '{storage_name}'?", size=14),
                    ft.Text(
                        warning_text if warning_text else "Хранилище пустое.",
                        size=13,
                        color=ft.Colors.RED if warning_text else ft.Colors.GREY_400
                    )
                ],
                tight=True,
                spacing=5
            ),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.FilledButton(
                    "Удалить",
                    on_click=on_confirm,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        print("DEBUG: Открываю диалог удаления...")
        self._open_dialog(dialog)
    
    def _on_storage_changed(self, e):
        """Обработчик смены хранилища"""
        self.app_data.current_storage_name = e.control.value
        self.data_manager.save_app_data(self.app_data)
        self.refresh()
        self.on_data_changed()
    
    def _open_dialog(self, dialog):
        """Универсальный метод открытия диалога для разных версий Flet"""
        try:
            # Flet 0.21+ требует добавления в overlay
            if dialog not in self.page.overlay:
                self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Ошибка при открытии диалога: {ex}")
            # Альтернативный способ
            try:
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            except Exception as ex2:
                print(f"DEBUG: Альтернативный способ тоже не сработал: {ex2}")
    
    def _close_dialog(self, dialog):
        """Универсальный метод закрытия диалога"""
        try:
            dialog.open = False
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Ошибка при закрытии диалога: {ex}")
    
    def _on_create_storage(self, e):
        """Создать новое хранилище"""
        print("DEBUG: _on_create_storage вызван!")
        try:
            name_field = ft.TextField(
                label="Название хранилища", 
                autofocus=True,
                hint_text="Например: Озеро, Река, Море"
            )
            limit_field = ft.TextField(
                label="Лимит вместимости (кг)", 
                value="50", 
                keyboard_type=ft.KeyboardType.NUMBER,
                hint_text="По умолчанию: 50 кг"
            )
            
            def on_cancel(e):
                self._close_dialog(dialog)
            
            def on_confirm(e):
                name = name_field.value
                try:
                    limit = float(limit_field.value or "50")
                    if limit <= 0:
                        limit = 50.0
                except ValueError:
                    limit = 50.0
                
                if name and name.strip():
                    new_storage = TemporaryStorage(
                        name=name.strip(),
                        limit=limit,
                        fishes=[]
                    )
                    self.app_data.temporary_storages.append(new_storage)
                    self.app_data.current_storage_name = name.strip()
                    self.data_manager.save_app_data(self.app_data)
                    self._close_dialog(dialog)
                    self.refresh()
                    self.on_data_changed()
                    self._show_snackbar(f"Хранилище '{name.strip()}' создано (лимит: {limit:.1f} кг)", ft.Colors.GREEN)
                else:
                    self._show_snackbar("Введите название хранилища!", ft.Colors.RED)
        
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Создать новое хранилище"),
                content=ft.Column([name_field, limit_field], tight=True, width=300, spacing=15),
                actions=[
                    ft.TextButton("Отмена", on_click=on_cancel),
                    ft.FilledButton("Создать", on_click=on_confirm)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            print("DEBUG: Диалог создан, открываю...")
            self._open_dialog(dialog)
            print("DEBUG: Диалог открыт")
        except Exception as ex:
            print(f"ERROR в _on_create_storage: {ex}")
            import traceback
            traceback.print_exc()
            self._show_snackbar(f"Ошибка: {ex}", ft.Colors.RED)
    
    def _on_transfer_to_permanent(self, e):
        """Перевести все рыбы в постоянное хранилище"""
        print("DEBUG: _on_transfer_to_permanent вызван!")
        current_storage = self.app_data.get_current_storage()
        if not current_storage or not current_storage.fishes:
            self._show_snackbar("Нет рыбы для переноса!", ft.Colors.ORANGE)
            return
        
        # Проверка лимита постоянного хранилища по весу
        weight_to_transfer_kg = current_storage.get_total_weight_kg()
        current_permanent_kg = self.app_data.get_permanent_total_weight_kg()
        permanent_limit_kg = self.app_data.permanent_storage_limit
        available_kg = self.app_data.get_permanent_available_weight_kg()
        
        if current_permanent_kg + weight_to_transfer_kg > permanent_limit_kg:
            self._show_snackbar(
                f"Недостаточно места! Доступно: {available_kg:.2f} кг, пытаетесь перенести: {weight_to_transfer_kg:.2f} кг",
                ft.Colors.RED
            )
            return
        
        def on_cancel(e):
            self._close_dialog(dialog)
        
        def on_confirm(e):
            # Сохранить данные перед переносом
            fish_count = len(current_storage.fishes)
            weight_kg = current_storage.get_total_weight_kg()
            
            # Переместить все рыбы
            for fish in current_storage.fishes:
                fish.storage = "permanent"
                self.app_data.permanent_storage.append(fish)
            
            # Очистить временное хранилище
            current_storage.fishes.clear()
            
            self.data_manager.save_app_data(self.app_data)
            self._close_dialog(dialog)
            self.refresh()
            self.on_data_changed()
            self._show_snackbar(f"Переведено {fish_count} рыб ({weight_kg:.2f} кг) в постоянное хранилище!", ft.Colors.GREEN)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтверждение переноса"),
            content=ft.Column(
                [
                    ft.Text(
                        f"Перевести {len(current_storage.fishes)} рыб ({weight_to_transfer_kg:.2f} кг) из '{current_storage.name}'?",
                        size=14
                    ),
                    ft.Text(
                        f"Свободно: {available_kg:.2f} кг",
                        size=12,
                        color=ft.Colors.GREY_400
                    )
                ],
                tight=True,
                spacing=5
            ),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.FilledButton("Подтвердить", on_click=on_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        print("DEBUG: Открываю диалог переноса...")
        self._open_dialog(dialog)
    
    def _on_configure_permanent_limit(self, e):
        """Настроить лимит постоянного хранилища"""
        print("DEBUG: _on_configure_permanent_limit вызван!")
        
        current_weight_kg = self.app_data.get_permanent_total_weight_kg()
        
        limit_field = ft.TextField(
            label="Лимит вместимости (кг)", 
            value=str(self.app_data.permanent_storage_limit),
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text=f"Минимум: {current_weight_kg:.2f} кг (текущий вес)",
            autofocus=True
        )
        
        def on_cancel(e):
            self._close_dialog(dialog)
        
        def on_confirm(e):
            try:
                new_limit = float(limit_field.value or "100")
                if new_limit <= 0:
                    self._show_snackbar("Лимит должен быть больше 0!", ft.Colors.RED)
                    return
                
                # Проверка: если новый лимит меньше текущего веса
                if new_limit < current_weight_kg:
                    self._show_snackbar(
                        f"Невозможно установить лимит {new_limit:.1f} кг! Текущий вес: {current_weight_kg:.2f} кг.",
                        ft.Colors.RED
                    )
                    return
                
                self.app_data.permanent_storage_limit = new_limit
                self.data_manager.save_app_data(self.app_data)
                self._close_dialog(dialog)
                self.refresh()
                self.on_data_changed()
                self._show_snackbar(f"Лимит постоянного хранилища: {new_limit:.1f} кг", ft.Colors.GREEN)
            except ValueError:
                self._show_snackbar("Введите корректное число!", ft.Colors.RED)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Настройка постоянного хранилища"),
            content=ft.Column(
                [
                    ft.Text(f"Текущий вес: {current_weight_kg:.2f} кг ({len(self.app_data.permanent_storage)} шт)", size=13, color=ft.Colors.GREY_400),
                    limit_field
                ],
                tight=True,
                width=300,
                spacing=10
            ),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.FilledButton("Сохранить", on_click=on_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        print("DEBUG: Открываю диалог настройки постоянного хранилища...")
        self._open_dialog(dialog)
    
    def _on_sell_all(self, e):
        """Продать весь улов"""
        print("DEBUG: _on_sell_all вызван!")
        if not self.app_data.permanent_storage:
            self._show_snackbar("Нет рыбы для продажи!", ft.Colors.ORANGE)
            return
        
        total_weight_kg = self.app_data.get_permanent_total_weight_kg()
        fish_count = len(self.app_data.permanent_storage)
        
        def on_cancel(e):
            self._close_dialog(dialog)
        
        def on_confirm(e):
            weight_kg = self.app_data.get_permanent_total_weight_kg()
            count = len(self.app_data.permanent_storage)
            
            self.app_data.permanent_storage.clear()
            self.data_manager.save_app_data(self.app_data)
            self._close_dialog(dialog)
            self.refresh()
            self.on_data_changed()
            self._show_snackbar(f"Улов продан! {count} рыб ({weight_kg:.2f} кг)", ft.Colors.GREEN)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтверждение продажи"),
            content=ft.Column(
                [
                    ft.Text(f"Продать весь улов?", size=14),
                    ft.Text(f"{fish_count} рыб • {total_weight_kg:.2f} кг", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                ],
                tight=True,
                spacing=10
            ),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.FilledButton("Продать", on_click=on_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        print("DEBUG: Открываю диалог продажи...")
        self._open_dialog(dialog)
    
    def _build_fish_card(self, fish: Fish, on_delete: Callable = None) -> ft.Container:
        """Создать карточку рыбы"""
        rarity_color = RARITY_COLORS.get(fish.rarity, RARITY_COLORS["common"])
        
        card_content = [
            ft.Row(
                [
                    ft.Container(
                        width=4,
                        height=60,
                        bgcolor=rarity_color,
                        border_radius=2
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(fish.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        ft.Text(fish.rarity_display, size=10),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        bgcolor=rarity_color,
                                        border_radius=5
                                    )
                                ],
                                spacing=10
                            ),
                            ft.Text(f"Вес: {fish.weight:.0f} г ({fish.weight/1000:.2f} кг)", size=12),
                            ft.Text(f"Наживка: {fish.best_bait}", size=11, color=ft.Colors.GREY_400)
                        ],
                        spacing=2,
                        expand=True
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Удалить",
                        on_click=lambda _, f=fish: on_delete(f) if on_delete else None,
                        icon_size=20
                    ) if on_delete else ft.Container()
                ],
                spacing=10
            )
        ]
        
        return ft.Container(
            content=ft.Column(card_content),
            padding=10,
            border_radius=5,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )
    
    def _sort_fishes(self, fishes: list[Fish]) -> list[Fish]:
        """Сортировка рыб: сначала по редкости, затем по весу"""
        rarity_order = {"trophy": 0, "rare": 1, "uncommon": 2, "common": 3}
        return sorted(fishes, key=lambda f: (rarity_order.get(f.rarity, 99), -f.weight))
    
    def refresh(self):
        """Обновить отображение"""
        # НЕ устанавливаем selected здесь - это вызывает проблему с сериализацией set
        # Значение будет установлено автоматически при первом взаимодействии пользователя
        # или мы будем использовать значение по умолчанию "common" при чтении
        
        # Обновить список текущего улова
        current_storage = self.app_data.get_current_storage()
        if current_storage:
            sorted_fishes = self._sort_fishes(current_storage.fishes)
            self.fish_list_view.current.controls = [
                self._build_fish_card(fish, self._on_delete_fish) for fish in sorted_fishes
            ]
            
            # Обновить прогресс-бар временного хранилища
            fill_percentage = current_storage.get_fill_percentage()
            current_weight_kg = current_storage.get_total_weight_kg()
            
            self.progress_bar.current.value = min(fill_percentage / 100, 1.0)
            self.progress_bar.current.color = ft.Colors.RED if fill_percentage > 95 else ft.Colors.BLUE
            
            # Обновить текст заполнения временного хранилища
            if self.progress_text.current:
                self.progress_text.current.value = f"Заполнено: {current_weight_kg:.2f} / {current_storage.limit:.1f} кг ({fill_percentage:.1f}%) • {len(current_storage.fishes)} шт"
            
            # Показать уведомление при заполнении на 95%
            if fill_percentage >= 95:
                self._show_storage_warning(current_storage, fill_percentage)
        
        # Обновить список постоянного хранилища
        sorted_permanent = self._sort_fishes(self.app_data.permanent_storage)
        self.permanent_list_view.current.controls = [
            self._build_fish_card(fish) for fish in sorted_permanent
        ]
        
        # Обновить прогресс-бар постоянного хранилища
        perm_fill_percentage = self.app_data.get_permanent_fill_percentage()
        perm_weight_kg = self.app_data.get_permanent_total_weight_kg()
        
        if self.permanent_progress_bar.current:
            self.permanent_progress_bar.current.value = min(perm_fill_percentage / 100, 1.0)
            self.permanent_progress_bar.current.color = ft.Colors.RED if perm_fill_percentage > 95 else ft.Colors.GREEN
        
        if self.permanent_progress_text.current:
            self.permanent_progress_text.current.value = f"Заполнено: {perm_weight_kg:.2f} / {self.app_data.permanent_storage_limit:.1f} кг • {len(self.app_data.permanent_storage)} шт"
        
        # Обновить селектор хранилищ
        storage_names = [s.name for s in self.app_data.temporary_storages]
        self.storage_dropdown.current.options = [ft.dropdown.Option(name) for name in storage_names]
        self.storage_dropdown.current.value = self.app_data.current_storage_name
        
        self.page.update()
    
    def _on_delete_fish(self, fish: Fish):
        """Удалить рыбу из временного хранилища"""
        current_storage = self.app_data.get_current_storage()
        if current_storage:
            current_storage.fishes = [f for f in current_storage.fishes if f.id != fish.id]
            self.data_manager.save_app_data(self.app_data)
            self.refresh()
            self.on_data_changed()
            self._show_snackbar(f"Рыба '{fish.name}' удалена", ft.Colors.ORANGE)
    
    def _show_storage_warning(self, storage: TemporaryStorage, fill_percentage: float):
        """Показать предупреждение о заполнении хранилища"""
        # Показываем предупреждение только если процент изменился (чтобы не спамить)
        last_shown = self._last_warning_percentage.get(storage.name, 0)
        if fill_percentage >= 95 and fill_percentage != last_shown:
            weight_kg = storage.get_total_weight_kg()
            message = f"⚠️ Внимание! Хранилище '{storage.name}' заполнено на {fill_percentage:.1f}% ({weight_kg:.2f}/{storage.limit:.1f} кг)"
            self._show_snackbar(message, ft.Colors.ORANGE)
            self._last_warning_percentage[storage.name] = fill_percentage
    
    def _show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Показать уведомление"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()
