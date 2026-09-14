import flet as ft

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            bgcolor="#121212",  # Fondo negro oscuro elegante
            controls=[
                ft.Column(
                    [
                        # Icono central con brillo sutil
                        ft.Container(
                            content=ft.Icon(ft.Icons.AUTO_AWESOME, size=40, color=ft.Colors.DEEP_PURPLE_ACCENT),
                            bgcolor="#1E1E1E",
                            padding=20,
                            border_radius=50
                        ),
                        ft.Container(height=10),
                        ft.Text("Duolingo Thrive", size=28, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                        ft.Text(
                            "¿En qué te puedo ayudar hoy con tu aprendizaje?",
                            size=15,
                            color=ft.Colors.GREY_400,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Container(height=20),
                        # Botón principal en tono oscuro/violeta
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Text("Iniciar conversación", color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=ft.Colors.WHITE, size=18)
                                ],
                                tight=True,
                                spacing=10
                            ),
                            bgcolor=ft.Colors.DEEP_PURPLE_700,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(horizontal=24, vertical=16)
                            ),
                            on_click=lambda _: page.go("/chat")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            ]
        )