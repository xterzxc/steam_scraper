import flet as ft
from scraper import parse_steam_comments, export_to_excel
import threading


def main(page: ft.Page):
    page.title = "Steam Comments Parser"
    page.window.width = 1000
    page.window.height = 800

    profile_id_input = ft.TextField(label="Steam Profile ID", width=300)
    pagesize_input = ft.TextField(label="Page Size", width=100, value="10")
    start_button = ft.ElevatedButton(text="Start", on_click=lambda e: start_parsing(e, page))
    export_button = ft.ElevatedButton(text="Export to Excel", on_click=lambda e: export_to_excel_file(), disabled=True)
    loading_indicator = ft.ProgressBar(width=300, visible=False)
    total_comments_text = ft.Text("")

    def start_parsing(e, page):
        profile_id = profile_id_input.value
        pagesize = int(pagesize_input.value)

        loading_indicator.visible = True
        total_comments_text.value = ""
        export_button.disabled = True

        page.update()

        def run_parsing():
            comments = parse_steam_comments(profile_id, pagesize)
            loading_indicator.visible = False
            if comments:
                total_comments_text.value = f"Total Comments: {len(comments)}"
                export_button.disabled = False
            else:
                total_comments_text.value = "No comments found"
            page.update()

        threading.Thread(target=run_parsing).start()

    def export_to_excel_file():
        comments = parse_steam_comments(profile_id_input.value, int(pagesize_input.value))
        export_to_excel(comments)
        ft.alert("Exported to steam_comments.xlsx")

    page.add(
        ft.Row([profile_id_input, pagesize_input, start_button, export_button]),
        loading_indicator,
        total_comments_text,
    )

ft.app(target=main)
