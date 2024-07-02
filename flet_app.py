import flet as ft
import threading
from scraper import export_to_excel, parse_steam_comments
import time

class Message:
    def __init__(self, user_name: str, time: str, text: str, avatar_url: str):
        self.user_name = user_name
        self.time = time
        self.text = text
        self.avatar_url = avatar_url

class Comment(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.Image(
                src=message.avatar_url,
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
    limit_input = ft.TextField(label="Limit", width=100, value="10")
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
        limit = int(limit_input.value)

        loading_indicator.visible = True
        total_comments_text.value = ""
        export_button.disabled = True
        chat_list.controls.clear()
        page.update()

        def run_parsing():
            nonlocal profile_id, pagesize, limit
            start_time = time.time()
            comments = parse_steam_comments(profile_id, pagesize, limit)
            loading_indicator.visible = False
            if comments:
                total_comments_text.value = f"Total Comments: {len(comments)}"
                export_button.disabled = False
                display_comments(comments)
                end_time = time.time()
                parsing_time = end_time - start_time
                print('Parsing time: ', parsing_time)
            else:
                total_comments_text.value = "No comments found"
            page.update()

        threading.Thread(target=run_parsing).start()

    def export_to_excel_file():
        comments = parse_steam_comments(profile_id_input.value, 10, limit_input.value)
        export_to_excel(comments)

    def display_comments(comments):
        for comment in comments:
            chat_list.controls.append(Comment(Message(comment['username'], comment['time'], comment['comment'], comment['avatar_url'])))
        page.update()

    page.add(
        ft.Row([profile_id_input, limit_input, start_button, export_button]),
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