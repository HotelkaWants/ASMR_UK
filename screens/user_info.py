from data_classes import User
import flet as ft
import theme.colors as colors
from database import Database

class UserInfoScreen(ft.Page):
    def __init__(self, page, user: User):
        self.page = page
        self.db = Database()
        self.db.connect()
        self.user = user

    def build(self):
        id = ft.Text(f"Идентификатор: {self.user.id}", color=colors.dark_blue, weight=ft.FontWeight.BOLD)
        full_name = ft.Text(f"ФИО: {self.user.full_name}", color=colors.dark_blue, weight=ft.FontWeight.BOLD)
        role = ft.Text(f"Роль: {self.user.role}", color=colors.dark_blue)
        login = ft.Text(f"Логин: {self.user.login}", color=colors.dark_blue)
        das = ft.Text(f"Пока ставим id: {self.user.das}" , color=colors.dark_blue)

        log_out_button = ft.ElevatedButton(
            text="Выйти",
            bgcolor=colors.red,
            color=colors.white,
            on_click=self.on_logout
        )
        return ft.Column(
            controls=[
                id,
                full_name,
                role,
                login,
                das,
                ft.Divider(color=colors.grey),
                log_out_button
            ]
        )
    def logout_click(self, e):
        """Обработка выхода из системы"""
        pass
        def on_confirm():
            self.page.client_storage.remove("current_user")
            
            self.page.clean()
            # login_page = LoginPage(self.page)
            # self.page.add(login_page.build())
            # self.page.update()
        
        # DialogManager.show_warning_dialog(
        #     self.page,
        #     "Выход из системы",
        #     "Вы уверены, что хотите выйти?",
        #     on_confirm=on_confirm
        # )  

