import flet as ft
import threading
from scraper import export_to_excel, parse_steam_comments

class Message:
    def __init__(self, user_name: str, time: str, text: str):
        self.user_name = user_name
        self.time = time
        self.text = text

class Comment(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.Image(
                src="https://avatars.steamstatic.com/b5bd56c1aa4644a474a2e4972be27ef9e82e517e_full.jpg",
                width=40,
                height=40,
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.time, size=12, color=ft.colors.GREY),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

def main(page: ft.Page):
    page.title = "Steam Comments Parser"
    page.window.width = 1000
    page.window.height = 800

    profile_id_input = ft.TextField(label="Steam Profile ID", width=300)
    start_button = ft.ElevatedButton(text="Start", on_click=lambda e: start_parsing(e, page))
    export_button = ft.ElevatedButton(text="Export to Excel", on_click=lambda e: export_to_excel_file(), disabled=True)
    loading_indicator = ft.ProgressBar(width=300, visible=False)
    total_comments_text = ft.Text("")

    chat_list = ft.ListView(
        expand=True,
        auto_scroll=True,
        spacing=15, 
    )

    def start_parsing(e, page):
        profile_id = profile_id_input.value
        pagesize = 10

        loading_indicator.visible = True
        total_comments_text.value = ""
        export_button.disabled = True
        chat_list.controls.clear()

        page.update()

        def run_parsing():
            nonlocal profile_id, pagesize
            comments = parse_steam_comments(profile_id, pagesize)
            loading_indicator.visible = False
            if comments:
                total_comments_text.value = f"Total Comments: {len(comments)}"
                export_button.disabled = False
                display_comments(comments)
            else:
                total_comments_text.value = "No comments found"
            page.update()

        threading.Thread(target=run_parsing).start()

    def export_to_excel_file():
        comments = parse_steam_comments(profile_id_input.value, 10)
        export_to_excel(comments)

    def display_comments(comments):
        for comment in comments:
            chat_list.controls.append(Comment(Message(comment['username'], comment['time'], comment['comment'])))
        page.update()

    page.add(
        ft.Row([profile_id_input, start_button, export_button]),
        loading_indicator,
        total_comments_text,
        ft.Container(
            content=chat_list,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
    )

ft.app(target=main)