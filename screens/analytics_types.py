from data_classes import AnalyticType
import flet as ft
import theme.colors as colors
from database import Database
from dialog_manager import DialogManager

class AnalyticsTypesScreen(ft.Page):
    def __init__(self, page, user):
        self.allow_admin_features = user.role == "Администратор УК"
        self.page = page
        self.db = Database()
        self.db.connect()
        self.analytics_types = self.db.get_all_analytic_types()
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить вид аналитики", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=200
        ) if self.allow_admin_features else None
        table_header = ft.Row(
            controls=[
                ft.Text("Код вида аналитики", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Вид аналитики", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),   
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self.display_content(analytic_type, None)) for analytic_type in self.analytics_types]
        for i, analytic_type in enumerate(self.analytics_types):
            self.rows[i].content = self.display_content(analytic_type, self.rows[i])

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
        dialog = self.build_add_analytic_type_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_analytic_type_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить новый вид аналитики", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Код вида аналитики", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Вид аналитики", expand=True, text_style=ft.TextStyle(size=14)),
                ]
            ),
            actions=[
                ft.TextButton(
                    "Отмена",
                    on_click=lambda e: DialogManager._close_dialog(self.page, dialog),
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLACK,    
                    ),
                ),
                ft.TextButton(
                    "Добавить",
                    on_click=lambda e: self.add_analytic_type(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                    ),
                    style=ft.ButtonStyle(color=colors.accent_blue)
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog
    

    def add_analytic_type(self, analytic_type_id: str, analytic_type_name: str):
        try:
            if analytic_type_id == "" or analytic_type_name == "":
                self.show_message("Все поля должны быть заполнены", True)
                return
            analytic_type = AnalyticType({
                "Код вида аналитики": analytic_type_id,
                "Вид аналитики": analytic_type_name,
            })
            self.db.create_analytic_type(analytic_type)
            self.show_message("Вид аналитики успешно добавлен", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.analytics_types = self.db.get_all_analytic_types()
        self.rows = [ft.Container(content=self.display_content(analytic_type, None)) for analytic_type in self.analytics_types]
        for i, analytic_type in enumerate(self.analytics_types):
            self.rows[i].content = self.display_content(analytic_type, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def display_content(self, analytic_type: AnalyticType, container: ft.Container):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(analytic_type.id, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(analytic_type.analytic_type_name, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, a=analytic_type, c=container: self.enter_edit(a, c)) if self.allow_admin_features else ft.Container(width=40),
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def enter_edit(self, analytic_type: AnalyticType, container: ft.Container):
        container.content = self.edit_content(analytic_type, container)
        self.page.update()

    def edit_content(self, analytic_type: AnalyticType, container: ft.Container):
        tf_id = ft.TextField(label="Код вида аналитики", value=analytic_type.id, expand=True, text_style=ft.TextStyle(size=14), disabled=True)
        tf_name = ft.TextField(label="Вид аналитики", value=analytic_type.analytic_type_name, expand=True, text_style=ft.TextStyle(size=14))

        def on_save(e):
            new_name = tf_name.value.strip()
            if not new_name:
                self.show_message("Наименование не может быть пустым", True)
                return
            try:
                self.db.update_analytic_type(analytic_type.id, new_name)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_analytic_type(analytic_type.id)
                self.show_message("Запись удалена", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self.display_content(analytic_type, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_id,
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