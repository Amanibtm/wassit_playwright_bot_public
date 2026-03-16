import flet as ft
from theme import AlertBoxBGcolor, text_color, textfield_bg_color, labels_color, borders_color, PADDING, FONT_FAMILY, \
    Weight, button_color, themed_bg, toggle_theme
from translation import t, set_language


def textfield(label):
    return ft.TextField(label=label, label_style=ft.TextStyle(color=labels_color, font_family=FONT_FAMILY, weight=Weight),
                    bgcolor=textfield_bg_color, color=ft.Colors.BLACK87,
                    border_color=borders_color, cursor_color=ft.Colors.BLACK87, border_radius=25, height=50, expand=True, adaptive=True,
                    text_style=ft.TextStyle(size=17, font_family=FONT_FAMILY, weight=Weight))


def button(label, onclick):
    return ft.ElevatedButton(label, style=ft.ButtonStyle(bgcolor=button_color, color=ft.Colors.BLACK87, padding=PADDING, shadow_color=ft.Colors.GREEN_ACCENT_100), on_click=onclick)


def addtext(words):
    return ft.Text(words, color=text_color, font_family=FONT_FAMILY, size=17, weight=Weight)


def alert(page, message, status):
    page.overlay.clear()
    page.update()
    if status:
        icon = ft.Icon(ft.Icons.THUMB_UP_OUTLINED, color=ft.Colors.GREEN)
        color = AlertBoxBGcolor[1]
    else:
        icon = ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED)
        color = AlertBoxBGcolor[0]
    dlg = ft.AlertDialog(
        title=icon,
        content=ft.Text(message, color=ft.Colors.BLACK),
        actions=[
            ft.Row([ft.TextButton(t("ok"), on_click=lambda e: close_alert(page, dlg), style=ft. ButtonStyle(color=ft.Colors.BLACK))], alignment=ft.MainAxisAlignment.CENTER)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=color)
    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def close_alert(page, dlg):
    dlg.open = False
    page.update()


def open_language_dialog(page):
    current_language = page.client_storage.get("language")
    language_selector = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="en", label="English"),
            ft.Radio(value="fr", label="Français"),
            ft.Radio(value="ar", label="العربية")],
            tight=True), value=current_language)

    def confirm(dlg):
        page.client_storage.set("language", language_selector.value)
        set_language(language_selector.value)
        dlg.open = False
        page.update()
        import time
        time.sleep(0.05)  # Small delay to ensure clean state
        page.go(page.route)  # reload view to apply translations
        page.on_route_change(None)  # This will call route_change which clears and rebuilds views

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("change_language")),
        content=language_selector,
        actions=[
            ft.TextButton(t("cancel_btn"), on_click=lambda _: close_alert(page, dlg)),
            ft.TextButton(t("confirm_btn"), on_click=lambda _: confirm(dlg)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def show_spinner(page: ft.Page):
    global spinner_overlay

    spinner_overlay = ft.Container(
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
        content=ft.ProgressRing(width=50, height=50)
    )

    page.overlay.append(spinner_overlay)
    page.update()


def hide_spinner(page: ft.Page):
    global spinner_overlay

    if spinner_overlay in page.overlay:
        page.overlay.remove(spinner_overlay)
        page.update()


def page_appbar(page, title_content, route):
    return ft.AppBar(
        leading=ft.IconButton(
            ft.Icons.ARROW_BACK_IOS,
            on_click=lambda _: page.go(route)),
        leading_width=60,
        title=ft.Text(title_content),
        center_title=True,
        bgcolor=themed_bg(page))


def main_page_appbar(page, title_content):
    return ft.AppBar(
        leading=ft.PopupMenuButton(
        icon=ft.Icons.MENU,
        items=[
            ft.PopupMenuItem(content=ft.ListTile(leading=ft.Icon(ft.Icons.BRIGHTNESS_6_OUTLINED, color=ft.Colors.ORANGE_400),
                                                title=ft.Text(t("toggle_theme")), on_click=lambda _: toggle_theme(page))),
            ft.PopupMenuItem(text=t("change_language"), icon=ft.Icons.LANGUAGE, on_click=lambda _: open_language_dialog(page)),
        ],
        tooltip =t("menu"),),
        leading_width=60,
        title=ft.Text(title_content),
        center_title=True,
        bgcolor=themed_bg(page))
