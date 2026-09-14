import flet as ft
from views.home_view import HomeView
from views.chat_view import ChatView

def main(page: ft.Page):
    page.title = "Duolingo Thrive RAG App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 450
    page.window.height = 700

    # Función que reacciona cada vez que cambia la ruta
    def route_change(route):
        page.views.clear()

        # Evaluar la ruta actual y anexar la vista correspondiente
        if page.route == "/":
            page.views.append(HomeView(page))
        elif page.route == "/chat":
            page.views.append(ChatView(page))

        page.update()

    # Función para manejar el botón de retroceso nativo o de la app
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Arrancar la aplicación en la ruta raíz ("/")
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)