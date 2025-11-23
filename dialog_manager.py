import flet as ft

class DialogManager:
    """Менеджер для управления диалоговыми окнами"""
    
    def show_error_dialog(page: ft.Page, title: str, message: str, on_close=None):
        """Показать диалог ошибки"""
        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=28),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
                ],
                spacing=10
            ),
            content=ft.Text(message, size=14, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(
                    "Закрыть",
                    on_click=lambda e: DialogManager._close_dialog(page, dialog, on_close),
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLACK,    
                    )
                )
            ],
            bgcolor="#FFFFFF",
        )
        page.add(dialog)
        dialog.open = True
        page.update()

    @staticmethod
    def show_warning_dialog(page: ft.Page, title: str, message: str, on_confirm=None, on_cancel=None):
        """Показать диалог предупреждения с кнопками подтверждения"""
        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.WARNING, color="#FF9800", size=28),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#FF9800")
                ],
                spacing=10
            ),
            content=ft.Text(message, size=14, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(
                    "Отмена",
                    on_click=lambda e: DialogManager._close_dialog(page, dialog, on_cancel),
                    style=ft.ButtonStyle(
                        color="#00FA9A",    
                    )
                ),
                ft.TextButton(
                    "Подтвердить",
                    on_click=lambda e: DialogManager._close_dialog(page, dialog, on_confirm),
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLACK,    
                    )
                )
            ],
            bgcolor="#FFFFFF",
        )
        page.add(dialog)
        dialog.open = True
        page.update()

    @staticmethod
    def show_info_dialog(page: ft.Page, title: str, message: str, on_close=None):
        """Показать информационный диалог"""
        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO, color="#2196F3", size=28),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#2196F3")
                ],
                spacing=10
            ),
            content=ft.Text(message, size=14, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: DialogManager._close_dialog(page, dialog, on_close),
                    style=ft.ButtonStyle(
                        color="#00FA9A",    
                    )
                )
            ],
            bgcolor="#FFFFFF",
        )
        page.add(dialog)
        dialog.open = True
        page.update()

    @staticmethod
    def show_success_dialog(page: ft.Page, title: str, message: str, on_close=None):
        """Показать диалог успеха"""
        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#4CAF50", size=28),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#4CAF50")
                ],
                spacing=10
            ),
            content=ft.Text(message, size=14, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: DialogManager._close_dialog(page, dialog, on_close),
                    style=ft.ButtonStyle(
                        color="#00FA9A",    
                    )
                )
            ],
            bgcolor="#FFFFFF",
        )
        page.add(dialog)
        dialog.open = True
        page.update()

    @staticmethod
    def _close_dialog(page: ft.Page, dialog: ft.AlertDialog, callback=None):
        """Закрыть диалог и выполнить callback"""
        dialog.open = False
        page.close(dialog)
        page.update()
        if callback:
            callback()

    @staticmethod
    def show_snackbar(page: ft.Page, message: str, message_type: str = "info"):

        colors = {
            "error": ft.Colors.RED,
            "warning": "#FF9800",
            "success": "#4CAF50",
            "info": "#2196F3"
        }
        
        snackbar = ft.SnackBar(
            ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=colors.get(message_type, colors["info"]),
            duration=3000
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()