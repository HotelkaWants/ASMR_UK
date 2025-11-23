import flet as ft
from data_classes import Indicator, User
import theme.colors as colors
from database import Database
from dialog_manager import DialogManager

class IndicatorsScreen(ft.Page):
    def __init__(self, page, user: User):
        self.page = page
        self.db = Database()
        self.db.connect()
        self.indicators = self.db.get_all_indicators()
        self.allow_admin_features = user.role == "Администратор УК"
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить показатель", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=180
        ) if self.allow_admin_features else None
        table_header = ft.Row(
            controls=[
                ft.Text("Код показателя", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Показатель", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Вид аналитики 1", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),   
                ft.Text("Вид аналитики 2", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Вид аналитики 3", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self._display_content(ind, None)) for ind in self.indicators]
        for i, ind in enumerate(self.indicators):
            self.rows[i].content = self._display_content(ind, self.rows[i])

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
        dialog = self.build_add_indicator_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_indicator_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить новый показатель", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Код показателя", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Показатель", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Вид аналитики 1", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Вид аналитики 2", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Вид аналитики 3", expand=True, text_style=ft.TextStyle(size=14)),
                ]
            ),
            actions=[
                ft.TextButton(
                    "Отмена",
                    on_click=lambda e: DialogManager._close_dialog(self.page, dialog),
                    style=ft.ButtonStyle(
                        color=colors.dark_blue,    
                    )
                ),
                ft.TextButton(
                    "Добавить",
                    on_click=lambda e: self.add_indicator(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                        dialog.content.controls[2].value.strip(),
                        dialog.content.controls[3].value.strip(),
                        dialog.content.controls[4].value.strip(),
                    ),
                    style=ft.ButtonStyle(
                        color=colors.accent_blue,    
                    )
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog
    
    def add_indicator(self, indicator_id: str, indicator_name: str, id_analytic_type_1: str, id_analytic_type_2: str, id_analytic_type_3: str):
        try:
            if indicator_id == "" or indicator_name == "" or id_analytic_type_1 == "":
                self.show_message("Код показателя, Показатель и Вид аналитики 1 являются обязательными полями", True)
                return
            indicator = Indicator({
                "Код показателя": indicator_id,
                "Показатель": indicator_name,
                "Код вида аналитики 1": id_analytic_type_1,
                "Код вида аналитики 2": id_analytic_type_2,
                "Код вида аналитики 3": id_analytic_type_3,
            })
            self.db.create_indicator(indicator)
            self.show_message("Показатель успешно добавлен", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления показателя: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.indicators = self.db.get_all_indicators()
        self.rows = [ft.Container(content=self._display_content(ind, None)) for ind in self.indicators]
        for i, ind in enumerate(self.indicators):
            self.rows[i].content = self._display_content(ind, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def _display_content(self, indicator: Indicator, container: ft.Container):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(indicator.id, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(indicator.indicator_name, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(indicator.id_analytic_type_1, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(indicator.id_analytic_type_2, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(indicator.id_analytic_type_3, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, ind=indicator, c=container: self._enter_edit(ind, c)) if self.allow_admin_features else ft.Container(width=40)
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def _enter_edit(self, indicator: Indicator, container: ft.Container):
        container.content = self._edit_content(indicator, container)
        self.page.update()

    def _edit_content(self, indicator: Indicator, container: ft.Container):
        tf_id = ft.TextField(label="Код показателя", value=indicator.id, expand=True, text_style=ft.TextStyle(size=14), disabled=True)
        tf_name = ft.TextField(label="Показатель", value=indicator.indicator_name, expand=True, text_style=ft.TextStyle(size=14))
        tf_a1 = ft.TextField(label="Вид аналитики 1", value=indicator.id_analytic_type_1, expand=True, text_style=ft.TextStyle(size=14))
        tf_a2 = ft.TextField(label="Вид аналитики 2", value=indicator.id_analytic_type_2, expand=True, text_style=ft.TextStyle(size=14))
        tf_a3 = ft.TextField(label="Вид аналитики 3", value=indicator.id_analytic_type_3, expand=True, text_style=ft.TextStyle(size=14))

        def on_save(e):
            new_name = tf_name.value.strip()
            new_a1 = tf_a1.value.strip()
            new_a2 = tf_a2.value.strip()
            new_a3 = tf_a3.value.strip()
            if not new_name:
                self.show_message("Наименование не может быть пустым", True)
                return
            try:
                self.db.update_indicator(indicator.id, new_name, new_a1, new_a2, new_a3)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            # refresh rows to reflect DB changes
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_indicator(indicator.id)
                self.show_message("Запись удалена", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self._display_content(indicator, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_id, 
                        tf_name, 
                        tf_a1, 
                        tf_a2, 
                        tf_a3, 
                        ft.Container(width=40)],
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