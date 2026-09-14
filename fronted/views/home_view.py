import flet as ft

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/",
            controls=[
                ft.Column(
                    [
                        ft.Text("Duolingo Thrive - Asistente RAG", size=26, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "Explora la documentación oficial conectada a AWS RDS y Azure OpenAI.",
                            size=14,
                            color=ft.Colors.GREY_700
                        ),
                        ft.ElevatedButton(
                            "Ir al Chatbot",
                            icon=ft.Icons.CHAT,
                            on_click=lambda _: page.go("/chat")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            ]
        )