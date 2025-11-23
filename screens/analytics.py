import flet as ft
import theme.colors as colors
from data_classes import Analytic
from database import Database
from dialog_manager import DialogManager

class AnalyticsPage(ft.Page):
    def __init__(self, page, user):
        self.allow_admin_features = user.role == "Администратор УК"
        self.page = page
        self.db = Database()
        self.db.connect()
        self.analytics = self.db.get_all_analytics()
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить аналитику", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=180
        ) if self.allow_admin_features else None
        table_header = ft.Row(
            controls=[
                ft.Text("Код аналитики", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Код вида аналитики", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Аналитика", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),   
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self.display_content(analytic, None)) for analytic in self.analytics]
        for i, analytic in enumerate(self.analytics):
            self.rows[i].content = self.display_content(analytic, self.rows[i])

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
        dialog = self.build_add_analytic_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_analytic_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить новую аналитику", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Код аналитики", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Код вида аналитики", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Аналитика", expand=True, text_style=ft.TextStyle(size=14)),
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
                    on_click=lambda e: self.add_analytic(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                        dialog.content.controls[2].value.strip(),
                    ),
                    style=ft.ButtonStyle(color=colors.accent_blue)
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog

    def add_analytic(self, analytic_id: str, id_analytic_type: str, analytic_name: str):
        try:
            if analytic_id == "" or id_analytic_type == "" or analytic_name == "":
                self.show_message("Все поля должны быть заполнены", True)
                return
            analytic = Analytic({
                "Код аналитики": analytic_id,
                "Код вида аналитики": id_analytic_type,
                "Аналитика": analytic_name,
            })
            self.db.create_analytic(analytic)
            self.show_message("Аналитика успешно добавлена", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления аналитики: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.analytics = self.db.get_all_analytics()
        self.rows = [ft.Container(content=self.display_content(analytic, None)) for analytic in self.analytics]
        for i, analytic in enumerate(self.analytics):
            self.rows[i].content = self.display_content(analytic, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def display_content(self, analytic: Analytic, container: ft.Container):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(analytic.id, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(analytic.id_analytic_type, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(analytic.analytic_name, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, a=analytic, c=container: self.enter_edit(a, c)) if self.allow_admin_features else ft.Container(width=40)
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def enter_edit(self, analytic: Analytic, container: ft.Container):
        container.content = self.edit_content(analytic, container)
        self.page.update()

    def edit_content(self, analytic: Analytic, container: ft.Container):
        tf_id = ft.TextField(label="Код аналитики", value=analytic.id, expand=True, text_style=ft.TextStyle(size=14))
        tf_type = ft.TextField(label="Код вида аналитики", value=analytic.id_analytic_type, expand=True, text_style=ft.TextStyle(size=14))
        tf_name = ft.TextField(label="Аналитика", value=analytic.analytic_name, expand=True, text_style=ft.TextStyle(size=14))

        def on_save(e):
            new_id = tf_id.value.strip()
            new_type = tf_type.value.strip()
            new_name = tf_name.value.strip()
            if not new_name:
                self.show_message("Наименование не может быть пустым", True)
                return
            try:
                self.db.update_analytic(new_type,new_id, new_name)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_analytic(analytic.id_analytic_type, analytic.id)
                self.show_message("Запись удалена", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self.display_content(analytic, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_id,
                        tf_type,
                        tf_name,
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