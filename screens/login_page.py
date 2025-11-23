import flet as ft   
import theme.colors as colors
from data_classes import User
from database import Database
from dialog_manager import DialogManager

class LoginPage(ft.Page):
    def __init__(self, page):
        self.page = page
        self.db = Database()
        self.db.connect()

    def build(self):
        tf_login = ft.TextField(label="Логин", width=300)
        tf_password = ft.TextField(label="Пароль", width=300, password=True, can_reveal_password=True)
        btn_login = ft.ElevatedButton(
            text="Войти",
            width=300,
            on_click=lambda e: self.authenticate(tf_login.value, tf_password.value)
        )
        container = ft.Container(
            content=ft.Column(
                controls=[
                    tf_login,
                    tf_password,
                    btn_login
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        return container
    
    def authenticate(self, login, password):
        user = self.db.get_user_by_credentials(login, password)
        if user:
            self.navigate_main(user)
            print("User authenticated:", user.full_name)
        else:
            self.show_message("Неверный логин или пароль")
    
    def show_message(self, message):
        DialogManager.show_error_dialog(self.page, "Ошибка", message,)            

    def navigate_main(self, user):
        self.page.client_storage.set("user", user.to_dict())
        self.page.controls.clear()
        from main import main
        main(self.page)