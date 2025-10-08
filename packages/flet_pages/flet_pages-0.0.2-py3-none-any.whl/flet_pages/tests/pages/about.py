import flet as ft
import flet_pages
import time
from flet_pages.router import PageMeta
from flet_pages.i18n import t

def get_about_content(ui:flet_pages.pages):
    co = ft.Button(t("switch_to_start"),on_click=lambda e: ui.change_page_by_label("start"))
    time.sleep(1)
    return co

page = PageMeta(
    label="about",
    func=get_about_content,
    title=lambda: t("about"),
)