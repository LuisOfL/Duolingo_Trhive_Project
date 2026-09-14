import flet as ft
import requests

class ChatView(ft.View):
    def __init__(self, page: ft.Page):
        self.chat_list = ft.ListView(expand=True, spacing=12, auto_scroll=True)
        self.user_input = ft.TextField(
            hint_text="Pregúntale algo al asistente de Duolingo...",
            expand=True,
            border_radius=8,
            on_submit=self.enviar_mensaje
        )

        super().__init__(
            route="/chat",
            controls=[
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ft.Text("Duolingo Thrive - Asistente RAG", size=18, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.Divider(height=1),
                ft.Container(
                    content=self.chat_list,
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10
                ),
                ft.Row(
                    [
                        self.user_input,
                        ft.IconButton(
                            icon=ft.Icons.SEND_ROUNDED,
                            icon_color=ft.Colors.BLUE_600,
                            tooltip="Enviar mensaje",
                            on_click=self.enviar_mensaje
                        )
                    ]
                )
            ]
        )
        self.page_ref = page

    def enviar_mensaje(self, e):
        texto = self.user_input.value.strip()
        if not texto:
            return

        # 1. Mensaje del usuario (burbuja alineada a la derecha)
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(texto, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE_600,
                        padding=12,
                        border_radius=ft.border_radius.all(12),
                        width=280  # Flet no soporta max_width, usamos width fijo
                    )
                ],
                alignment=ft.MainAxisAlignment.END
            )
        )

        pregunta_actual = texto
        self.user_input.value = ""
        self.page_ref.update()

        # 2. Indicador de carga
        indicador_carga = ft.Row(
            [
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text(" Buscando en la BD...", italic=True, size=12, color=ft.Colors.GREY_600)
            ],
            alignment=ft.MainAxisAlignment.START
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
                respuesta_ia = f" Error en el servidor ({response.status_code}): {response.text}"

        except requests.exceptions.ConnectionError:
            self.chat_list.controls.remove(indicador_carga)
            respuesta_ia = "Error de conexión: No se pudo contactar al backend de FastAPI. Asegúrate de que el servidor Uvicorn esté encendido."
        except Exception as ex:
            self.chat_list.controls.remove(indicador_carga)
            respuesta_ia = f" Error inesperado: {str(ex)}"

        # 4. Respuesta de la IA (burbuja alineada a la izquierda)
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(respuesta_ia, color=ft.Colors.BLACK87),
                        bgcolor=ft.Colors.GREY_200,
                        padding=12,
                        border_radius=ft.border_radius.all(12),
                        width=320  # antes max_width=320
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )
        self.page_ref.update()