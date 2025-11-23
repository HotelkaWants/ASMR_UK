import flet as ft
import theme.colors as colors
from data_classes import User
from database import Database
from dialog_manager import DialogManager

class UsersScreen(ft.Page):
    def __init__(self, page):
        self.page = page
        self.db = Database()
        self.db.connect()
        self.users = self.db.get_all_users()
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить пользователя", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=200
        )
        table_header = ft.Row(
            controls=[
                ft.Text("ФИО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Роль", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Логин", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("ДЗО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self.display_content(user, None)) for user in self.users]
        for i, user in enumerate(self.users):
            self.rows[i].content = self.display_content(user, self.rows[i])

        self.page.floating_action_button = add_fab
        self.body = ft.Column(
            controls=[
                table_header,
                ft.Divider(color=colors.grey),
                *self.rows,
                ft.Container(height=50)
            ]
        )
        return self.body

    def add_dialog(self):
        dialog = self.build_add_user_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_user_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить пользователя", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="ФИО", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Роль", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Логин", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Пароль", expand=True, password=True, can_reveal_password=True, text_style=ft.TextStyle(size=14)),  # Добавлено поле пароля
                    ft.TextField(label="ДЗО", expand=True, text_style=ft.TextStyle(size=14)),
                ]
            ),
            actions=[
                ft.TextButton(
                    "Отмена",
                    on_click=lambda e: DialogManager._close_dialog(self.page, dialog),
                    style=ft.ButtonStyle(color=colors.dark_blue)
                ),
                ft.TextButton(
                    "Добавить",
                    on_click=lambda e: self.add_user(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                        dialog.content.controls[2].value.strip(),
                        dialog.content.controls[3].value.strip(),  # пароль
                        dialog.content.controls[4].value.strip(),
                    ),
                    style=ft.ButtonStyle(color=colors.accent_blue)
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog

    def add_user(self, full_name, role, login, password, dzo):
        try:
            if not full_name or not role or not login or not password or not dzo:
                self.show_message("Все поля должны быть заполнены", True)
                return
            user = User({
                "ФИО": full_name,
                "Роль": role,
                "Логин": login,
                "Пароль": password,
                "ДЗО": dzo
            })
            self.db.create_user(user)
            self.show_message("Пользователь успешно добавлен", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.users = self.db.get_all_users()
        self.rows = [ft.Container(content=self.display_content(user, None)) for user in self.users]
        for i, user in enumerate(self.users):
            self.rows[i].content = self.display_content(user, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def display_content(self, user: User, container: ft.Container):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(user.full_name, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(user.role, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(user.login, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(str(user.dzo), color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, u=user, c=container: self.enter_edit(u, c))
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def enter_edit(self, user: User, container: ft.Container):
        container.content = self.edit_content(user, container)
        self.page.update()

    def edit_content(self, user: User, container: ft.Container):
        tf_full_name = ft.TextField(label="ФИО", value=user.full_name, expand=True, text_style=ft.TextStyle(size=14))
        tf_role = ft.TextField(label="Роль", value=user.role, expand=True, text_style=ft.TextStyle(size=14))
        tf_login = ft.TextField(label="Логин", value=user.login, expand=True, text_style=ft.TextStyle(size=14))
        tf_dzo = ft.TextField(label="ДЗО", value=str(user.dzo), expand=True, text_style=ft.TextStyle(size=14))

        def on_save(e):
            new_full_name = tf_full_name.value.strip()
            new_role = tf_role.value.strip()
            new_login = tf_login.value.strip()
            new_dzo = tf_dzo.value.strip()
            if not new_full_name or not new_role or not new_login or not new_dzo:
                self.show_message("Все поля должны быть заполнены", True)
                return
            try:
                self.db.update_user(user.id, new_full_name, new_role, new_login, user.password, new_dzo)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_user(user.id)
                self.show_message("Пользователь удалён", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self.display_content(user, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_full_name,
                        tf_role,
                        tf_login,
                        tf_dzo,
                        ft.Container(width=40)
                    ],
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Сохранить", on_click=on_save, bgcolor=colors.accent_blue, style=ft.ButtonStyle(color=colors.background_blue)),
                        ft.ElevatedButton("Удалить", on_click=on_delete, bgcolor=colors.red, style=ft.ButtonStyle(color=colors.background_blue)),
                        ft.ElevatedButton("Отмена", on_click=on_cancel, bgcolor=colors.grey, style=ft.ButtonStyle(color=colors.dark_blue)),
                        ft.Container(width=40)
                    ],
                    alignment=ft.MainAxisAlignment.END
                ),
                ft.Divider(color=colors.grey),
            ]
        )