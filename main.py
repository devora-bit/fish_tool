"""
Главный файл приложения трекера выловленной рыбы
"""
import flet as ft
from data_manager import DataManager
from models import AppData
from ui_components.log_view import LogView
from ui_components.wiki_view import WikiView
from ui_components.stats_view import StatsView


def main(page: ft.Page):
    """Главная функция приложения"""
    
    # Настройка страницы
    page.title = "Fishing Log - Трекер выловленной рыбы"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True
    )
    
    # Настройка размеров окна
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 800
    page.window.min_height = 600
    page.window.resizable = True
    page.padding = 0
    page.spacing = 0
    
    # Настройка шрифтов
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
    }
    page.theme.page_transitions.windows = ft.PageTransitionTheme.CUPERTINO
    page.theme.page_transitions.macos = ft.PageTransitionTheme.CUPERTINO
    page.theme.page_transitions.linux = ft.PageTransitionTheme.CUPERTINO
    
    # Инициализация менеджера данных
    data_manager = DataManager()
    app_data = data_manager.load_app_data()
    
    # Создание представлений
    log_view = LogView(page, data_manager, app_data, on_data_changed=lambda: refresh_all())
    wiki_view = WikiView(page, data_manager, app_data)
    stats_view = StatsView(page, data_manager, app_data)
    
    # Контейнер для контента
    content_container = ft.Ref[ft.Container]()
    
    def on_navigation_change(e):
        """Обработчик изменения навигации"""
        selected_index = e.control.selected_index
        
        if selected_index == 0:
            # Страница журнала
            content_container.current.content = log_view.build()
            log_view.refresh()
        elif selected_index == 1:
            # Страница справочника
            content_container.current.content = wiki_view.build()
            wiki_view.refresh()
        elif selected_index == 2:
            # Страница статистики
            content_container.current.content = stats_view.build()
            stats_view.refresh()
        
        page.update()
    
    def refresh_all():
        """Обновить все представления"""
        # Перезагрузить данные
        nonlocal app_data
        app_data = data_manager.load_app_data()
        
        # Обновить представления
        log_view.app_data = app_data
        wiki_view.app_data = app_data
        stats_view.app_data = app_data
        
        # Обновить текущее представление
        if page.navigation_bar.selected_index == 0:
            log_view.refresh()
        elif page.navigation_bar.selected_index == 1:
            wiki_view.refresh()
        elif page.navigation_bar.selected_index == 2:
            stats_view.refresh()
    
    # Навигационная панель
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME,
                selected_icon=ft.Icons.HOME_OUTLINED,
                label="Журнал"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.BOOK,
                selected_icon=ft.Icons.BOOK_OUTLINED,
                label="Справочник"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.BAR_CHART,
                selected_icon=ft.Icons.BAR_CHART_OUTLINED,
                label="Статистика"
            )
        ],
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
    )
    
    # Главный контейнер
    page.add(
        ft.Container(
            ref=content_container,
            content=log_view.build(),
            expand=True
        )
    )
    
    # Инициализация первого представления
    log_view.refresh()
    
    page.update()


if __name__ == "__main__":
    # Запуск приложения
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,
        assets_dir="assets"
    )
