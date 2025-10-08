import flet as ft
import flet_pages
import flet_pages.i18n
from pages import about,start

def get_pages():
    pages = [
        start.page,about.page
    ]
    return pages
def main(page: ft.Page):
    flet_pages.i18n.I18n({
        "zh": {
            "hello": "你好",
            "world": "世界",
            "about": "关于",
            "start": "开始",
            "switch_to_start": "切换到开始",
            "theme_switch": "亮暗模式切换",
        },
        "en": {
            "hello": "Hello",
            "world": "World",
            "about": "About",
            "start": "Start",
            "switch_to_start": "Switch to Start",
            "theme_switch": "Toggle Dark/Light Mode",
        }
    }, "en","./.config",True)
    page.title = "测试"
    pages = get_pages()
    ui = flet_pages.pages(pages,page,True)


ft.app(main)