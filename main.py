import flet as ft
import theme.colors as colors

def main(page: ft.Page):
    page.title = "Показатели"
    page.bgcolor = colors.background_blue
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    user = page.client_storage.get("user")
    if user:
        from data_classes import User
        user = User(user)
    else:
        from screens.login_page import LoginPage
        page.add(
            ft.Container(
                expand=True,
                bgcolor=colors.background_blue,
                content=LoginPage(page).build(),
            )
        )
        page.update()
        return
    allow_admin_features = user.role == "Администратор УК"

    def navigate_routes_drawer(e):
        selected_route = e.control.selected_index if e else 0
        page.controls.clear()
        page.floating_action_button = None
        
        if selected_route == 0:
            from screens.indicators import IndicatorsScreen
            page.title = "Показатели"
            print("Navigate to Indicators Screen")
            indicators = IndicatorsScreen(page, user)
            page.add(
                ft.Container(
                    expand=True,
                    content=indicators.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
            page.drawer.open = False
        elif selected_route == 1:
            from screens.analytics import AnalyticsPage
            page.title = "Аналитики"
            analytics = AnalyticsPage(page, user)
            print("Navigate to Analytics Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=analytics.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
            page.drawer.open = False
        elif selected_route == 2:
            from screens.analytics_types import AnalyticsTypesScreen
            page.title = "Виды аналитик"
            analytics_types = AnalyticsTypesScreen(page, user)
            print("Navigate to Analytics Types Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=analytics_types.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
            page.drawer.open = False
        elif selected_route == 3:
            from screens.values_indicators import ValuesIndicatorsScreen
            page.title = "Значения показателей ДЗО"
            values_indicators = ValuesIndicatorsScreen(page, user)
            print("Navigate to Values Indicators Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=values_indicators.build(),
                )   
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
            page.drawer.open = False
        elif selected_route == 4:
            if allow_admin_features:
                from screens.dzos import DZOsScreen
                page.title = "Дочерние зависимые общества"
                dzos = DZOsScreen(page)
                print("Navigate to DZOS Screen")
                page.add(
                    ft.Container(
                        expand=True,
                        content=dzos.build(),
                    )   
                )
                page.appbar.title = ft.Text(page.title, color=colors.grey)
                page.update()
                page.drawer.open = False
            else:
                page.client_storage.remove("user")
                from screens.login_page import LoginPage
                page.controls.clear()
                page.appbar = None
                page.drawer = None
                page.floating_action_button = None
                page.add(
                    ft.Container(
                        expand=True,
                        bgcolor=colors.background_blue,
                        content=LoginPage(page).build(),
                    )
                )
                page.update()
        elif selected_route == 5:
            from screens.users import UsersScreen
            page.title = "Пользователи"
            users = UsersScreen(page)
            print("Navigate to Users Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=users.build(),
                )   
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
            page.drawer.open = False
        elif selected_route == 6:
            page.client_storage.remove("user")
            from screens.login_page import LoginPage
            page.controls.clear()
            page.appbar = None
            page.drawer = None
            page.floating_action_button = None
            page.add(
                ft.Container(
                    expand=True,
                    bgcolor=colors.background_blue,
                    content=LoginPage(page).build(),
                )
            )
            page.update()
            
        

    drawer_theme = ft.NavigationDrawerTheme(
        label_text_style=ft.TextStyle(color = colors.background_blue),
    )
    page.theme = ft.Theme(navigation_drawer_theme=drawer_theme)
   
    nav_drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12), 
            ft.NavigationDrawerDestination(
                label="Показатели",
            ),
            ft.NavigationDrawerDestination(
                label="Аналитики",
            ),
            ft.NavigationDrawerDestination(
                label="Виды аналитик",
            ),
            ft.NavigationDrawerDestination(
                label="Значения показателей ДЗО",
            ),
            ft.NavigationDrawerDestination(
                label="Дочерние зависимые общества",
            ) if allow_admin_features else ft.Container(),
            ft.NavigationDrawerDestination(
                label="Пользователи",
            ) if allow_admin_features else ft.Container(),
            ft.Divider(color=colors.grey),
            ft.NavigationDrawerDestination(
                label="Выйти",
            ),
        ],
        indicator_shape=ft.RoundedRectangleBorder(radius=8),
        indicator_color=colors.accent_blue,
        bgcolor=colors.fade_blue,
    )

    def navigate_routes(e):
        route = page.route
        page.controls.clear()
        page.floating_action_button = None
        
        if route == "/indicators":
            from screens.indicators import IndicatorsScreen
            page.title = "Показатели"
            print("Navigate to Indicators Screen")
            indicators = IndicatorsScreen(page, user)
            page.add(
                ft.Container(
                    expand=True,
                    content=indicators.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
        elif route == "/analytics":
            from screens.analytics import AnalyticsPage
            page.title = "Аналитики"
            analytics = AnalyticsPage(page, user)
            print("Navigate to Analytics Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=analytics.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
        elif route == "/analytics_types":
            from screens.analytics_types import AnalyticsTypesScreen
            page.title = "Виды аналитик"
            analytics_types = AnalyticsTypesScreen(page, user)
            print("Navigate to Analytics Types Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=analytics_types.build(),
                )
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
        elif route == "/values_indicators":
            from screens.values_indicators import ValuesIndicatorsScreen
            page.title = "Значения показателей ДЗО"
            values_indicators = ValuesIndicatorsScreen(page)
            print("Navigate to Values Indicators Screen")
            page.add(
                ft.Container(
                    expand=True,
                    content=values_indicators.build(),
                )   
            )
            page.appbar.title = ft.Text(page.title, color=colors.grey)
            page.update()
    
    nav_drawer.on_change = navigate_routes_drawer
    page.drawer = nav_drawer
    page.appbar = ft.AppBar(
            title=ft.Text(page.title, color=colors.grey),
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=colors.grey,
                on_click=lambda e: page.open(nav_drawer)
            ),
            bgcolor=colors.dark_blue
        )
    
    page.on_route_change = lambda e: navigate_routes(None)
    page.go("/indicators")
    page.update()

if __name__ == "__main__":
    ft.app(target=main)