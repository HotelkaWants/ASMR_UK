import flet as ft
import theme.colors as colors
from data_classes import ValueIndicator, DZO
from database import Database
from dialog_manager import DialogManager
from datetime import datetime
class ValuesIndicatorsScreen(ft.Page):

    def __init__(self, page, user):
        self.allow_admin_features = user.role == "Администратор УК"
        self.page = page
        self.db = Database()
        self.db.connect()
        self.values_indicators = self.db.get_values_indicators()
        self.body = None
        self.rows = []

    def build(self):
        add_fab = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=colors.accent_blue,
            content=ft.Text("Добавить значение", color=colors.background_blue),
            on_click=lambda e: self.add_dialog(),
            width=180
        ) if self.allow_admin_features else None
        table_header = ft.Row(
            controls=[
                ft.Text("Дата начала периода", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Дата окончания периода", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Код показателя", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Код аналитики 1", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),   
                ft.Text("Код аналитики 2", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Код аналитики 3", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Сумма", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),     
                ft.Text("ДЗО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Text("Адрес ДЗО", color=colors.dark_blue, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40)
            ]
        )
        self.rows = [ft.Container(content=self.display_content(value_indicator, None)) for value_indicator in self.values_indicators]
        for i, value_indicator in enumerate(self.values_indicators):
            self.rows[i].content = self.display_content(value_indicator, self.rows[i])

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
        dialog = self.build_add_value_indicator_dialog()
        self.page.add(dialog)
        dialog.open = True
        self.page.update()

    def build_add_value_indicator_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить новое значение показателя", size=20, weight=ft.FontWeight.BOLD, color=colors.dark_blue),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Дата начала периода", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Дата окончания периода", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Код показателя", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Код аналитики 1", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Код аналитики 2", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Код аналитики 3", expand=True, text_style=ft.TextStyle(size=14)),
                    ft.TextField(label="Сумма", expand=True, text_style=ft.TextStyle(size=14)),
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
                    on_click=lambda e: self.add_value_indicator(
                        dialog.content.controls[0].value.strip(),
                        dialog.content.controls[1].value.strip(),
                        dialog.content.controls[2].value.strip(),
                        dialog.content.controls[3].value.strip(),
                        dialog.content.controls[4].value.strip(),
                        dialog.content.controls[5].value.strip(),
                        dialog.content.controls[6].value.strip(),
                    ),
                    style=ft.ButtonStyle(color=colors.accent_blue)
                )
            ],
            bgcolor="#FFFFFF",
        )
        return dialog

    def add_value_indicator(self, date_start, date_end, id_indicator, analytic_1, analytic_2, analytic_3, sum_value, dzo_id ):
        try:
            if not date_start or not date_end or not id_indicator or not analytic_1 or not sum_value:
                self.show_message("Обязательные поля: даты, код показателя, аналитика 1, сумма", True)
                return
            value_indicator = ValueIndicator({
                "Дата начала периода": date_start,
                "Дата окончания периода": date_end,
                "Код показателя": id_indicator,
                "Код аналитики 1": analytic_1,
                "Код аналитики 2": analytic_2,
                "Код аналитики 3": analytic_3,
                "Сумма": float(sum_value),
                "ДЗО": dzo_id
            })
            self.db.create_values_indicator(value_indicator)
            self.show_message("Значение успешно добавлено", False)
            self.refresh()
        except Exception as exc:
            self.show_message(f"Ошибка добавления значения: {exc}", True)

    def show_message(self, text, error: bool = False):
        if error:
            DialogManager.show_error_dialog(self.page, "Ошибка", text)
        else:
            DialogManager.show_success_dialog(self.page, "Успех", text)

    def refresh(self):
        self.values_indicators = self.db.get_values_indicators()
        self.rows = [ft.Container(content=self.display_content(value_indicator, None)) for value_indicator in self.values_indicators]
        for i, value_indicator in enumerate(self.values_indicators):
            self.rows[i].content = self.display_content(value_indicator, self.rows[i])
        header = self.body.controls[0] if self.body and len(self.body.controls) > 0 else None
        divider = ft.Divider(color=colors.grey)
        self.body.controls = [self.body.controls[0], divider, *self.rows] if header else [divider, *self.rows]
        self.page.update()

    def display_content(self, value_indicator: ValueIndicator, container: ft.Container):
        dzo = self.get_dzo(value_indicator.dzo)
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(value_indicator.date_period_start, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(value_indicator.date_period_end, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(value_indicator.id_indicator, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(value_indicator.analytic_1, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),   
                        ft.Text(value_indicator.analytic_2, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(value_indicator.analytic_3, color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(str(value_indicator.sum_value), color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(dzo.name if dzo else "Неизвестно", color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.Text(dzo.address if dzo else "Неизвестно", color=colors.dark_blue, expand=True, text_align=ft.TextAlign.CENTER),
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=colors.accent_blue, on_click=lambda e, v=value_indicator, c=container: self.enter_edit(v, c)) if self.allow_admin_features else ft.Container(width=40)
                    ]
                ),
                ft.Divider(color=colors.grey),
            ]
        )

    def enter_edit(self, value_indicator: ValueIndicator, container: ft.Container):
        container.content = self.edit_content(value_indicator, container)
        self.page.update()

    def edit_content(self, value_indicator: ValueIndicator, container: ft.Container):
        tf_start = ft.TextField(label="Дата начала периода", value=value_indicator.date_period_start, expand=True, text_style=ft.TextStyle(size=14))
        tf_end = ft.TextField(label="Дата окончания периода", value=value_indicator.date_period_end, expand=True, text_style=ft.TextStyle(size=14))
        tf_id = ft.TextField(label="Код показателя", value=value_indicator.id_indicator, expand=True, text_style=ft.TextStyle(size=14))
        tf_a1 = ft.TextField(label="Код аналитики 1", value=value_indicator.analytic_1, expand=True, text_style=ft.TextStyle(size=14))
        tf_a2 = ft.TextField(label="Код аналитики 2", value=value_indicator.analytic_2, expand=True, text_style=ft.TextStyle(size=14))
        tf_a3 = ft.TextField(label="Код аналитики 3", value=value_indicator.analytic_3, expand=True, text_style=ft.TextStyle(size=14))
        tf_sum = ft.TextField(label="Сумма", value=str(value_indicator.sum_value), expand=True, text_style=ft.TextStyle(size=14))
        tf_dzo = ft.TextField(label="Идентификатор ДЗО", value=str(value_indicator.dzo), expand=True, text_style=ft.TextStyle(size=14), disabled=True)
        
        def on_save(e):
            def get_date_value(tf):
                if isinstance(tf.value, datetime):
                    return tf.value.strftime("%Y-%m-%d")
                elif isinstance(tf.value, str):
                    return tf.value.strip()
                else:
                    return str(tf.value)

            new_start = get_date_value(tf_start)
            new_end = get_date_value(tf_end)
            new_id = tf_id.value.strip()
            new_a1 = tf_a1.value.strip()
            new_a2 = tf_a2.value.strip()
            new_a3 = tf_a3.value.strip()
            new_sum = tf_sum.value.strip()
            dzo_id = tf_dzo.value.strip()
            if not new_start or not new_end or not new_id or not new_a1 or not new_sum:
                self.show_message("Обязательные поля: даты, код показателя, аналитика 1, сумма", True)
                return
            try:
                new_value_indicator = ValueIndicator({
                    "Дата начала периода": new_start,
                    "Дата окончания периода": new_end,
                    "Код показателя": new_id,
                    "Код аналитики 1": new_a1,
                    "Код аналитики 2": new_a2,
                    "Код аналитики 3": new_a3,
                    "Сумма": float(new_sum),
                    "ДЗО": dzo_id
                })
                self.db.update_values_indicator(value_indicator, new_value_indicator)
                self.show_message("Изменения сохранены", False)
            except Exception as exc:
                self.show_message(f"Ошибка сохранения: {exc}", True)
                return
            self.refresh()

        def on_delete(e):
            try:
                self.db.delete_values_indicator(
                    value_indicator.id_indicator,
                    value_indicator.date_period_start,
                    value_indicator.date_period_end,
                    value_indicator.analytic_1,
                    value_indicator.analytic_2,
                    value_indicator.analytic_3,
                )
                self.show_message("Запись удалена", False)
            except Exception as exc:
                self.show_message(f"Ошибка удаления: {exc}", True)
                return
            self.refresh()

        def on_cancel(e):
            container.content = self.display_content(value_indicator, container)
            self.page.update()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tf_start,
                        tf_end,
                        tf_id,
                        tf_a1,
                        tf_a2,
                        tf_a3,
                        tf_sum,
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
    
    def get_dzo(self, dzo_id) -> DZO:
        return self.db.get_dzo_by_id(dzo_id)