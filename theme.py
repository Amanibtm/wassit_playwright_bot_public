import flet as ft

borders_color = ft.Colors.GREEN_ACCENT_200
textfield_bg_color = ft.Colors.WHITE54
labels_color = ft.Colors.BLACK
text_color = ft.Colors.BLACK87
BGcolor = ft.Colors.YELLOW_100
AlertBoxBGcolor = [ft.Colors.ORANGE_400, ft.Colors.WHITE70]
Weight = ft.FontWeight.W_500
clicked_button_color = ft.Colors.GREY_500
button_color = ft.Colors.GREEN_ACCENT_400

# Fonts
FONT_FAMILY = "system-ui"

# Common paddings/spacings
PADDING = 12
SPACING = 20

# Icons
ICON_SIZE = 20


def themed_bg(page):
    return ft.Colors.YELLOW_100 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_900


def toggle_theme(page):
    page.theme_mode = (
        ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
    )
    for view in page.views:
        view.bgcolor = themed_bg(page)
        if view.appbar:
            view.appbar.bgcolor = themed_bg(page)
    page.bgcolor = themed_bg(page)
    page.update()

