import flet as ft
import typing
import asyncio
import inspect
from flet import OptionalNumber
from .page_meta import PageMeta


def get_label(label: typing.Union[str, typing.Callable[[], str]]) -> str:
    if isinstance(label, str):
        return label
    else:
        return label()


class UIBase:
    PHONE_BREAKPOINT: typing.ClassVar[int] = 768
    TABLET_BREAKPOINT: typing.ClassVar[int] = 1024
    the_page: ft.Page
    pages: typing.List[PageMeta]
    current_index: int
    main_content: ft.Control
    animated_switcher: ft.AnimatedSwitcher
    root_stack: ft.Stack
    _is_changing_page: bool
    _content_build_token: int
    progress_ring: ft.ProgressRing
    use_custom_titlebar: bool
    is_phone: bool
    is_web: bool
    is_mac: bool
    show_title_bar: bool
    content_cache: typing.Dict[str, ft.Control]
    _window_controls: typing.Optional[ft.Row]
    show_top_button: bool
    show_full_button: bool
    show_min_button: bool
    show_max_button: bool
    show_close_button: bool
    show_opacity_slider: bool
    top: ft.IconButton
    full: ft.IconButton
    min: ft.IconButton
    max: ft.IconButton
    close: ft.IconButton
    opacity_slider: ft.Slider
    content_area: ft.Container
    navigation: typing.Optional[typing.Union[ft.NavigationBar, ft.NavigationRail]]
    full_hotkey: typing.Optional[str]

    def __init__(
        self,
        pages: typing.List[PageMeta],
        the_page: ft.Page,
        use_custom_titlebar: bool = True,
        show_top_button: bool = True,
        show_full_button: bool = True,
        show_min_button: bool = True,
        show_max_button: bool = True,
        show_close_button: bool = True,
        show_opacity_slider: bool = True,
        full_hotkey: typing.Optional[str] = "F11",
    ):
        self.pages = pages
        self.the_page = the_page
        self.current_index = 0
        self._is_changing_page = False
        self._content_build_token = 0
        self.progress_ring = ft.ProgressRing(width=48, height=48)
        self.use_custom_titlebar = use_custom_titlebar
        self.content_cache = {}
        self._window_controls = None
        self.show_top_button = show_top_button
        self.show_full_button = show_full_button
        self.show_min_button = show_min_button
        self.show_max_button = show_max_button
        self.show_close_button = show_close_button
        self.show_opacity_slider = show_opacity_slider
        self.full_hotkey = full_hotkey
        self.navigation = None
        # 系统类型
        self.get_ui()

    def setup_window(self, page: ft.Page) -> None:
        self.the_page = page
        """初始化窗口设置"""
        # 加载上次选择的主题
        saved_theme = page.client_storage.get("theme_mode")
        if saved_theme:
            page.theme_mode = ft.ThemeMode(saved_theme)

        # 加载上次的透明度
        saved_opacity = page.client_storage.get("window_opacity")
        if saved_opacity is not None:
            page.window.opacity = float(saved_opacity)
 
        page.title = self.the_page.title
        if self.use_custom_titlebar:
            page.window.title_bar_hidden = True
            page.window.title_bar_buttons_hidden = True
        page.padding = 0
        page.on_resized = self.handle_resize
        page.on_close = self.close_window
        if self.full_hotkey is not None:
            page.on_keyboard_event = self.on_keyboard
        self.is_web = self.the_page.web
        self.is_mac = self.the_page.platform == ft.PagePlatform.MACOS

        # 顶栏的显示只由平台决定
        self.show_title_bar = not (
            self.the_page.platform == ft.PagePlatform.ANDROID
            or self.the_page.platform == ft.PagePlatform.IOS
            or self.is_web
        )

        # 导航模式由窗口宽度决定
        if page.width is not None and page.width > 0:
            self.is_phone = page.width < self.PHONE_BREAKPOINT
        else:
            # 初始回退到平台判断
            self.is_phone = not self.show_title_bar

    def create_window_controls(self) -> ft.Row:
        """创建窗口控制按钮"""
        if self._window_controls is not None:
            return self._window_controls
        self.top = ft.IconButton(
            icon=ft.Icons.PUSH_PIN_OUTLINED,
            selected_icon=ft.Icons.PUSH_PIN_ROUNDED,
            icon_size=16,
            selected=False,
            on_click=self.toggle_always_on_top,
            style=self.get_button_style(),
            tooltip="置顶窗口",
        )
        self.full = ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            selected_icon=ft.Icons.FULLSCREEN_EXIT_ROUNDED,
            icon_size=16,
            selected=False,
            on_click=self.toggle_fullscreen,
            style=self.get_button_style(),
            tooltip="全屏",
        )
        self.min = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            icon_size=16,
            on_click=self.minimize_window,
            style=self.get_button_style(),
            tooltip="最小化",
        )
        self.max = ft.IconButton(
            icon=ft.Icons.BRANDING_WATERMARK,
            selected_icon=ft.Icons.BRANDING_WATERMARK_OUTLINED,
            selected=False,
            icon_size=16,
            on_click=self.toggle_maximize,
            style=self.get_button_style(),
            tooltip="最大化",
        )
        self.close = ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_size=16,
            hover_color=ft.Colors.RED_900,
            on_click=self.close_window,
            style=self.get_button_style(),
            tooltip="关闭",
        )
        saved_opacity = self.the_page.client_storage.get("window_opacity")
        if saved_opacity is None:
            saved_opacity = 1.0
        else:
            saved_opacity = float(saved_opacity)

        self.opacity_slider = ft.Slider(
            min=0.2,
            max=1.0,
            divisions=8,
            value=saved_opacity,
            width=100,
            on_change=self.change_opacity,
            tooltip="调整窗口透明度",
        )
        if self.is_mac:
            # 修改颜色
            self.close.icon_color = ft.Colors.RED
            self.close.icon = ft.Icons.CIRCLE
            self.min.icon_color = ft.Colors.YELLOW
            self.min.icon = ft.Icons.CIRCLE
            self.max.icon_color = ft.Colors.GREEN
            self.max.selected_icon = ft.Icons.CIRCLE
            self.max.selected_icon_color = ft.Colors.GREEN
            self.max.icon = ft.Icons.CIRCLE
            self.close.hover_color = None

        mac_controls = []
        if self.show_close_button:
            mac_controls.append(self.close)
        if self.show_min_button:
            mac_controls.append(self.min)
        if self.show_max_button:
            mac_controls.append(self.max)
        if self.show_top_button:
            mac_controls.append(self.top)
        if self.show_full_button:
            mac_controls.append(self.full)
        if self.show_opacity_slider:
            mac_controls.append(self.opacity_slider)

        other_controls = []
        if self.show_opacity_slider:
            other_controls.append(self.opacity_slider)
        if self.show_top_button:
            other_controls.append(self.top)
        if self.show_full_button:
            other_controls.append(self.full)
        if self.show_min_button:
            other_controls.append(self.min)
        if self.show_max_button:
            other_controls.append(self.max)
        if self.show_close_button:
            other_controls.append(self.close)

        self._window_controls = ft.Row(
            controls=mac_controls if self.is_mac else other_controls,
            spacing=5,
        )
        return self._window_controls

    def get_button_style(self) -> ft.ButtonStyle:
        """获取按钮样式"""
        return ft.ButtonStyle(
            padding=12,
            shape=ft.RoundedRectangleBorder(radius=0),
        )

    def create_title_bar(self, page: ft.Page) -> ft.Container:
        controls = [
            ft.WindowDragArea(
                content=ft.Container(
                    content=ft.Row(
                        controls=(
                            [
                                ft.Image(f"/icon.png"),
                                ft.Text(
                                    page.title,
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                ),
                            ]
                        ),
                        spacing=8,
                        expand=True,
                        alignment=(
                            ft.MainAxisAlignment.START
                            if not self.is_mac
                            else ft.MainAxisAlignment.CENTER
                        ),
                    ),
                    padding=ft.padding.only(left=12, top=8, bottom=8, right=100),
                    expand=True,
                ),
                expand=True,
            ),
            self.create_window_controls(),
        ]
        """创建标题栏"""
        return ft.Container(
            content=ft.Row(
                controls=controls if not self.is_mac else controls[::-1],
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=40,
            border=ft.border.only(bottom=ft.BorderSide(1)),
            bgcolor="background",
        )

    def create_navigation_bar(
        self, change_page_handler: typing.Callable[[ft.ControlEvent], None]
    ) -> ft.NavigationBar:
        return ft.NavigationBar(
            elevation=-100,
            selected_index=self.current_index,
            destinations=[
                ft.NavigationBarDestination(
                    icon=i.icon,
                    selected_icon=i.selected_icon,
                    label=i.title(),
                )
                for i in self.pages
            ],
            on_change=change_page_handler,
        )

    def create_navigation_rail(
        self, change_page_handler: typing.Callable[[ft.ControlEvent], None]
    ) -> ft.NavigationRail:
        """创建导航栏"""
        return ft.NavigationRail(
            animate_size=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            selected_index=self.current_index,
            leading=(
                ft.Column(
                    [
                        ft.Image(f"/icon.png", height=75),
                        ft.Text(self.the_page.title, size=16),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                if self.is_web
                else None
            ),
            min_width=100,
            min_extended_width=200,
            extended=not (
                self.the_page.width is not None
                and self.PHONE_BREAKPOINT
                <= self.the_page.width
                < self.TABLET_BREAKPOINT
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=i.icon,
                    selected_icon=i.selected_icon,
                    label=i.title(),
                )
                for i in self.pages
            ],
            on_change=change_page_handler,
        )

    def create_content_area(self) -> ft.Container:
        """创建内容区域"""
        self.animated_switcher = ft.AnimatedSwitcher(
            content=ft.Text("主页内容"),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
        )
        return ft.Container(
            content=self.animated_switcher,
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
            bgcolor=self.the_page.bgcolor,
        )

    def create_main_layout(
        self, page: ft.Page
    ) -> typing.Union[ft.Column, ft.SafeArea, ft.Stack]:
        """创建主布局"""
        self.content_area = self.create_content_area()
        base_layout = None

        # 单页时不显示侧边栏
        if len(self.pages) <= 1:
            base_layout = self.content_area
        else:
            if self.is_phone:
                self.navigation = self.create_navigation_bar(self.change_page_content)
                base_layout = ft.Column(
                    controls=[
                        self.content_area,
                        self.navigation,
                    ],
                    spacing=0,
                    expand=True,
                )
            else:
                self.navigation = self.create_navigation_rail(self.change_page_content)
                base_layout = ft.Row(
                    controls=[
                        self.navigation,
                        ft.VerticalDivider(width=1),
                        self.content_area,
                    ],
                    spacing=0,
                    expand=True,
                )

        self.root_stack = ft.Stack(controls=[base_layout], expand=True)

        if not self.show_title_bar:
            return ft.SafeArea(self.root_stack, expand=True)
        else:
            if self.use_custom_titlebar:
                return ft.Column(
                    controls=[self.create_title_bar(page), self.root_stack],
                    spacing=0,
                    expand=True,
                )
            else:
                return self.root_stack

    def _switch_to_page_content(self) -> None:
        """将 animated_switcher 的内容切换到当前页面。支持异步/耗时加载并避免竞态。"""
        # 确保 animated_switcher 已经初始化并添加到页面上
        if not (hasattr(self, "animated_switcher") and self.animated_switcher.page is not None):
            return

        # 增加构建令牌，避免快速切换导致的错位更新
        self._content_build_token += 1
        token = self._content_build_token

        # 先显示加载指示器
        self.animated_switcher.content = self.progress_ring
        self.animated_switcher.update()

        current_page_meta = self.pages[self.current_index]
        page_label = get_label(current_page_meta.label)

        # 命中缓存则直接切换
        if page_label in self.content_cache:
            content = self.content_cache[page_label]
            self.animated_switcher.content = content
            self.animated_switcher.update()
            return

        # 没有缓存则根据函数类型异步构建，避免阻塞 UI
        func = current_page_meta.func if callable(current_page_meta.func) else None
        if func is None:
            # 兜底占位
            self.animated_switcher.content = ft.Container()
            self.animated_switcher.update()
            return

        if inspect.iscoroutinefunction(func):
            async def _job():
                await self._build_content_async(func, page_label, token)
            self.the_page.run_task(_job)
        else:
            async def _job():
                await self._build_content_in_thread(func, page_label, token)
            self.the_page.run_task(_job)

    def _set_content_if_current(self, page_label: str, content: ft.Control, token: int) -> None:
        """仅当仍为当前目标页面时才设置内容，防止竞态覆盖。"""
        if token != self._content_build_token:
            return
        # 缓存并更新 UI
        self.content_cache[page_label] = content
        if hasattr(self, "animated_switcher") and self.animated_switcher.page is not None:
            self.animated_switcher.content = content
            self.animated_switcher.update()

    async def _build_content_async(
        self,
        func: typing.Callable[["UIBase"], typing.Awaitable[ft.Control]],
        page_label: str,
        token: int,
    ) -> None:
        try:
            content = await func(self)
            if not isinstance(content, ft.Control):
                content = ft.Container(content=ft.Text(str(content)))
        except Exception as ex:
            content = ft.Container(content=ft.Text(f"加载页面出错: {ex}"), padding=20)
        self._set_content_if_current(page_label, content, token)

    async def _build_content_in_thread(
        self,
        func: typing.Callable[["UIBase"], ft.Control],
        page_label: str,
        token: int,
    ) -> None:
        try:
            content = await asyncio.to_thread(func, self)
            if not isinstance(content, ft.Control):
                content = ft.Container(content=ft.Text(str(content)))
        except Exception as ex:
            content = ft.Container(content=ft.Text(f"加载页面出错: {ex}"), padding=20)
        self._set_content_if_current(page_label, content, token)

    def change_page_content(self, e: ft.ControlEvent) -> None:
        """处理页面切换"""
        # 判断是否点击当前页
        if self.current_index == int(e.control.selected_index):
            return
        if not self._is_changing_page:
            self._is_changing_page = True
            self.current_index = int(e.control.selected_index)
            self._switch_to_page_content()
            self._is_changing_page = False
        else:
            e.control.selected_index = self.current_index
            e.control.update()

    def toggle_always_on_top(self, e: ft.ControlEvent) -> None:
        """切换窗口置顶状态"""
        e.control.page.window.always_on_top = not e.control.page.window.always_on_top
        e.control.selected = not e.control.selected
        e.control.page.update()

    def minimize_window(self, e: ft.ControlEvent) -> None:
        """最小化窗口"""
        e.control.page.window.minimized = True
        e.control.page.update()

    def toggle_maximize(self, e: ft.ControlEvent) -> None:
        """切换最大化状态"""
        if e.control.page.window.full_screen:
            self.toggle_fullscreen(e)
        else:
            e.control.page.window.maximized = not e.control.page.window.maximized
        e.control.page.update()

    def toggle_fullscreen(self, e: ft.ControlEvent) -> None:
        """切换全屏状态"""
        is_fullscreen = not e.control.page.window.full_screen
        e.control.page.window.full_screen = is_fullscreen
        e.control.page.update()

    def close_window(self, e: ft.ControlEvent) -> None:
        """关闭窗口"""
        e.control.page.window.close()

    def on_keyboard(self, e: ft.KeyboardEvent):
        """处理键盘事件"""
        if self.full_hotkey and e.key == self.full_hotkey and self.show_full_button:
            # The handle_resize event will update the button state.
            is_fullscreen = not self.the_page.window.full_screen
            self.the_page.window.full_screen = is_fullscreen
            self.the_page.update()

    def change_opacity(self, e: ft.ControlEvent) -> None:
        """改变窗口透明度"""
        e.control.page.window.opacity = e.control.value
        e.control.page.client_storage.set("window_opacity", e.control.value)
        e.control.page.update()

    def handle_resize(self, e: ft.ControlEvent) -> None:
        """处理窗口大小调整"""
        if self.the_page.width is None:
            return

        if self.use_custom_titlebar and self.show_title_bar:
            is_narrow = self.the_page.width < 340
            # 置顶按钮
            if hasattr(self, "top"):
                new_visibility = not is_narrow and self.show_top_button
                if self.top.visible != new_visibility:
                    self.top.visible = new_visibility
                    self.top.update()
            # 全屏按钮
            if hasattr(self, "full"):
                new_visibility = not is_narrow and self.show_full_button
                if self.full.visible != new_visibility:
                    self.full.visible = new_visibility
                    self.full.update()
            # 透明度滑块
            if hasattr(self, "opacity_slider"):
                new_visibility = not is_narrow and self.show_opacity_slider
                if self.opacity_slider.visible != new_visibility:
                    self.opacity_slider.visible = new_visibility
                    self.opacity_slider.update()

        new_is_phone = self.the_page.width < self.PHONE_BREAKPOINT
        if new_is_phone != self.is_phone:
            self.is_phone = new_is_phone
            self.update_pages(keep_cache=True)
        elif isinstance(self.navigation, ft.NavigationRail):
            is_tablet_size = (
                self.PHONE_BREAKPOINT
                <= self.the_page.width
                < self.TABLET_BREAKPOINT
            )
            if self.navigation.extended == is_tablet_size:
                self.navigation.extended = not is_tablet_size
                self.navigation.update()

        if hasattr(self, "max"):
            is_maximized = self.the_page.window.maximized
            if self.max.selected != is_maximized:
                self.max.selected = is_maximized
                self.max.update()

        if hasattr(self, "full"):
            is_fullscreen = self.the_page.window.full_screen
            if self.full.selected != is_fullscreen:
                self.full.selected = is_fullscreen
                self.full.update()

    def update_pages(
        self,
        new_pages: typing.Optional[typing.List[PageMeta]] = None,
        keep_cache: bool = False,
    ) -> None:
        """更新页面配置"""
        if not keep_cache:
            self.content_cache.clear()
        if new_pages is None:
            new_pages = self.pages
        # 记住当前选中的页面
        current_label = self.pages[self.current_index].label if self.pages else None

        # 检查是否有子页面存在
        sub_page = None
        if hasattr(self, "root_stack") and len(self.root_stack.controls) > 1:
            sub_page = self.root_stack.controls[1]

        self.pages = new_pages

        if self.the_page:
            # 清除当前页面内容
            self.the_page.clean()

            # 创建新的布局
            self.main_content = self.create_main_layout(self.the_page)

            # 如果存在子页面，则重新添加到stack中
            if sub_page:
                self.root_stack.controls.append(sub_page)

            # 恢复之前的选中状态
            if current_label:
                for i, page in enumerate(self.pages):
                    if page.label == current_label:
                        self.current_index = i
                        break

            # 先添加主内容到页面
            self.the_page.add(self.main_content)

            # 更新当前显示的内容
            if hasattr(self, "animated_switcher"):
                self._switch_to_page_content()

            self.the_page.update()

    def the_page_wh(self) -> typing.Tuple[OptionalNumber, OptionalNumber]:
        return self.the_page.width, self.the_page.height

    def change_page_by_label(self, label: str) -> None:
        """通过页面label切换当前页面"""
        for i, page in enumerate(self.pages):
            if page.label == label:
                if self.current_index != i:
                    self.current_index = i
                    # 更新内容区域
                    # 使用动画切换内容
                    self._switch_to_page_content()

                    # 更新导航栏选中状态
                    if hasattr(self, "navigation"):
                        if isinstance(self.navigation, ft.NavigationBar):
                            self.navigation.selected_index = self.current_index
                            self.navigation.update()
                        elif isinstance(self.navigation, ft.NavigationRail):
                            self.navigation.selected_index = self.current_index
                            self.navigation.update()
                return
        raise ValueError(f"未找到label为'{label}'的页面")

    def get_ui(self) -> None:
        """获取UI函数"""
        self.the_page.clean()
        self.setup_window(self.the_page)
        self.main_content = self.create_main_layout(self.the_page)
        self._is_changing_page = True
        # 初始化动画组件
        self.animated_switcher.content = self.progress_ring
        self.the_page.add(self.main_content)
        # 异步/同步加载当前页内容（不阻塞 UI）
        self._switch_to_page_content()
        self.the_page.update()
        self._is_changing_page = False

    async def open_sub_page(self, component: ft.Control, title: str) -> None:
        """打开子页面"""
        # 如果已经打开了一个子页面，则不允许再次打开
        if len(self.root_stack.controls) > 1:
            return
        # 创建返回按钮和标题
        back_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=self.close_sub_page, tooltip="返回"
        )
        title_text = ft.Text(
            title,
            size=16,
            weight=ft.FontWeight.W_600,
            expand=True,
            text_align=ft.TextAlign.CENTER,
        )

        # 创建顶部操作栏
        top_bar = ft.Row(
            controls=[
                back_button,
                title_text,
                ft.Container(width=48),  # a spacer to balance the back button
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # 子页面布局
        sub_page_layout = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        top_bar,
                        border=ft.border.only(bottom=ft.BorderSide(1)),
                        padding=ft.padding.symmetric(vertical=5),
                    ),
                    ft.Container(component, expand=True, padding=10),
                ],
                expand=True,
                spacing=0,
            ),
            expand=True,
            offset=ft.Offset(0, 1),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            bgcolor=self.the_page.bgcolor if self.the_page.bgcolor else "background",
        )

        self.root_stack.controls.append(sub_page_layout)
        self.the_page.update()

        await asyncio.sleep(0.03)

        sub_page_layout.offset = ft.Offset(0, 0)
        self.the_page.update()

    def close_sub_page(self, e: ft.ControlEvent) -> None:
        """关闭子页面"""
        sub_page_layout = self.root_stack.controls[-1]

        async def _remove_from_stack():
            await asyncio.sleep(0.3)
            self.root_stack.controls.pop()
            self.the_page.update()

        if isinstance(sub_page_layout, ft.Container) and hasattr(sub_page_layout, "offset"):
            sub_page_layout.offset = ft.Offset(0, 1)
            self.the_page.update()
            self.the_page.run_task(_remove_from_stack)
