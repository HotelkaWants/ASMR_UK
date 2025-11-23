import flet as ft
import theme.colors as colors
from data_classes import DZO
from database import Database
from dialog_manager import DialogManager

class DZOsScreen(ft.Page):
    def __init__(self, page):
        self.page = page
        self.db = Database()
        self.db.connect()
        self.dzos = self.db.get_all_dzos()
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить ДЗО", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=180
        )
        table_header = ft.Row(
            controls=[
                ft.Text("Идентификатор ДЗО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Наименование ДЗО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Адрес", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self.display_content(dzo, None)) for dzo in self.dzos]
        for i, dzo in enumerate(self.dzos):
            self.rows[i].content = self.display_content(dzo, self.rows[i])

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
        dialog = self.build_add_dzo_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_dzo_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить ДЗО", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Наименование ДЗО", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Адрес", expand=True, text_style=ft.TextStyle(size=14)),
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
                    on_click=lambda e: self.add_dzo(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                    ),
                    style=ft.ButtonStyle(color=colors.accent_blue)
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog

    def add_dzo(self, name, address):
        try:
            if not name or not address:
                self.show_message("Все поля должны быть заполнены", True)
                return
            self.db.create_dzo(name, address)
            self.show_message("ДЗО успешно добавлено", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления ДЗО: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.dzos = self.db.get_all_dzos()
        self.rows = [ft.Container(content=self.display_content(dzo, None)) for dzo in self.dzos]
        for i, dzo in enumerate(self.dzos):
            self.rows[i].content = self.display_content(dzo, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def display_content(self, dzo: DZO, container: ft.Container):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(dzo.id, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(dzo.name, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(dzo.address, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, d=dzo, c=container: self.enter_edit(d, c))
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def enter_edit(self, dzo: DZO, container: ft.Container):
        container.content = self.edit_content(dzo, container)
        self.page.update()

    def edit_content(self, dzo: DZO, container: ft.Container):
        tf_id = ft.TextField(label="Идентификатор ДЗО", value=dzo.id, expand=True, text_style=ft.TextStyle(size=14), disabled=True)
        tf_name = ft.TextField(label="Наименование ДЗО", value=dzo.name, expand=True, text_style=ft.TextStyle(size=14))
        tf_address = ft.TextField(label="Адрес", value=dzo.address, expand=True, text_style=ft.TextStyle(size=14))

        def on_save(e):
            new_name = tf_name.value.strip()
            new_address = tf_address.value.strip()
            if not new_name or not new_address:
                self.show_message("Все поля должны быть заполнены", True)
                return
            try:
                self.db.update_dzo(dzo.id, new_name, new_address)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_dzo(dzo.id)
                self.show_message("ДЗО удалено", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self.display_content(dzo, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_id,
                        tf_name,
                        tf_address,
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