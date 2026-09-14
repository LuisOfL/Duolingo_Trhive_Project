import flet as ft
# Desde aquí puedes importar tu función de RDS y Azure si lo deseas:
# from services.rag_service import buscar_chunks_similares

class ChatView(ft.View):
    def __init__(self, page: ft.Page):
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.user_input = ft.TextField(
            hint_text="Pregúntale algo al asistente de Duolingo...",
            expand=True,
            on_submit=self.enviar_mensaje
        )

        super().__init__(
            route="/chat",
            controls=[
                # Barra superior con botón de regreso
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/")),
                        ft.Text("Chat RAG - Duolingo Thrive", size=20, weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.Divider(),
                # Contenedor del historial de chat
                ft.Container(
                    content=self.chat_list,
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10
                ),
                # Caja de texto inferior
                ft.Row(
                    [
                        self.user_input,
                        ft.IconButton(
                            icon=ft.Icons.SEND,
                            icon_color=ft.Colors.BLUE,
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

        # 1. Añadir mensaje del usuario
        self.chat_list.controls.append(
            ft.Row([ft.Text(f"Tú: {texto}", weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.END)
        )
        self.user_input.value = ""
        self.page_ref.update()

        # 2. Simulación de respuesta (Aquí integrarías tu lógica de RDS + OpenAI)
        # contextos = buscar_chunks_similares(texto)
        respuesta_ia = f"Respuesta generada para: '{texto}' (Conexión a RDS pendiente de prueba)."

        # 3. Añadir respuesta del asistente
        self.chat_list.controls.append(
            ft.Row([ft.Text(f"Asistente: {respuesta_ia}", color=ft.Colors.BLUE_800)], alignment=ft.MainAxisAlignment.START)
        )
        self.page_ref.update()