import flet as ft
from flet_pages.router import PageMeta
import flet_pages.i18n as i18n
from flet_pages import pages
import time


def get_about_content(ui: pages):
    co = ft.Column()
    co.controls.append(ft.Text(i18n.t("hello")))
    co.controls.append(ft.Text(i18n.t("world")))
    # 语言选择下拉框
    lang_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("zh", "中文"), ft.dropdown.Option("en", "English")],
        value=i18n.default.get_lang(),
        on_change=lambda e: (
            i18n.default.set_lang(e.control.value),
            ui.update_pages(),
        ),
    )
    co.controls.append(lang_dropdown)
    co.controls.append(
        ft.Switch(
            label=i18n.t("theme_switch"),
            on_change=lambda e: (
                setattr(e.page, "theme_mode", ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT),
                e.page.client_storage.set("theme_mode", e.page.theme_mode.value),
                ui.update_pages(),
            ),
            value=True if ui.the_page.theme_mode == ft.ThemeMode.DARK else False,
        )
    )

    async def open_sub_page_handler(e):
        await ui.open_sub_page(ft.Text(f"这是子页面的内容！生成时间 {time.ctime()}"), title="我的子页面")

    # 添加一个按钮来打开子页面
    co.controls.append(
        ft.ElevatedButton(
            "打开子页面",
            on_click=open_sub_page_handler,
        )
    )
    return co


page = PageMeta(
    label="start",
    func=get_about_content,
    title=lambda: i18n.t("start"),
    icon=ft.Icons.HOME_ROUNDED,
    selected_icon=ft.Icons.HOME_OUTLINED,
)
