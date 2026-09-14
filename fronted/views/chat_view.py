import flet as ft
import requests

class ChatView(ft.View):
    def __init__(self, page: ft.Page):
        self.chat_list = ft.ListView(expand=True, spacing=20, auto_scroll=True, padding=20)

        # Campo de texto optimizado para fondo oscuro
        self.user_input = ft.TextField(
            hint_text="Pregúntale algo al asistente...",
            border=ft.InputBorder.NONE,
            filled=False,
            expand=True,
            text_size=14,
            color=ft.Colors.WHITE,
            cursor_color=ft.Colors.DEEP_PURPLE_ACCENT,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
            on_submit=self.enviar_mensaje
        )

        super().__init__(
            route="/chat",
            bgcolor="#121212",
            controls=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_ROUNDED,
                                icon_color=ft.Colors.GREY_400,
                                on_click=lambda _: page.go("/")
                            ),
                            ft.Row([
                                ft.Icon(ft.Icons.AUTO_AWESOME, size=18, color=ft.Colors.DEEP_PURPLE_ACCENT),
                                ft.Text("Duolingo Thrive AI", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                            ], spacing=8)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5)
                ),
                ft.Divider(height=1, color="#2A2A2A"),

                ft.Container(
                    content=self.chat_list,
                    expand=True,
                    bgcolor="#121212"
                ),

                ft.Container(
                    content=ft.Row(
                        [
                            self.user_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                icon_color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.DEEP_PURPLE_700,
                                tooltip="Enviar mensaje",
                                on_click=self.enviar_mensaje
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    bgcolor="#1E1E1E",
                    padding=ft.padding.symmetric(horizontal=16, vertical=4),
                    border_radius=30,
                    margin=ft.margin.all(15)
                )
            ]
        )
        self.page_ref = page

    def enviar_mensaje(self, e):
        texto = self.user_input.value.strip()
        if not texto:
            return

        # 1. Mensaje del usuario
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(texto, color=ft.Colors.WHITE, size=14),
                        bgcolor="#2A2A2A",
                        padding=12,
                        border_radius=16,
                        width=320  # antes max_width
                    ),
                    ft.CircleAvatar(
                        content=ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.WHITE),
                        bgcolor="#333333",
                        radius=16
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10
            )
        )

        pregunta_actual = texto
        self.user_input.value = ""
        self.page_ref.update()

        # 2. Indicador de carga
        indicador_carga = ft.Row(
            [
                ft.CircleAvatar(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME, size=14, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.DEEP_PURPLE_700,
                    radius=16
                ),
                ft.Row([
                    ft.ProgressRing(width=12, height=12, stroke_width=2, color=ft.Colors.DEEP_PURPLE_ACCENT),
                    ft.Text(" Pensando respuesta...", italic=True, size=13, color=ft.Colors.GREY_400)
                ], spacing=10)
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        self.chat_list.controls.append(indicador_carga)
        self.page_ref.update()

        # 3. Petición HTTP POST al backend de FastAPI
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"pregunta": pregunta_actual},
                timeout=45
            )
            self.chat_list.controls.remove(indicador_carga)

            if response.status_code == 200:
                data = response.json()
                respuesta_ia = data.get("respuesta", "No se obtuvo respuesta.")
            else:
                respuesta_ia = f"❌ Error en el servidor ({response.status_code}): {response.text}"

        except requests.exceptions.ConnectionError:
            self.chat_list.controls.remove(indicador_carga)
            respuesta_ia = "❌ Error de conexión: No se pudo contactar al backend de FastAPI."
        except Exception as ex:
            self.chat_list.controls.remove(indicador_carga)
            respuesta_ia = f"❌ Error inesperado: {str(ex)}"

        # 4. Respuesta de la IA
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.CircleAvatar(
                        content=ft.Icon(ft.Icons.AUTO_AWESOME, size=14, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.DEEP_PURPLE_700,
                        radius=16
                    ),
                    ft.Container(
                        content=ft.Text(respuesta_ia, color=ft.Colors.GREY_200, size=14),
                        padding=ft.padding.all(4),
                        width=330  # antes max_width
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10
            )
        )
        self.page_ref.update()