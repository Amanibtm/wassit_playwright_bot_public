import datetime
import random
import flet as ft
from components import textfield, button, alert, show_spinner, hide_spinner, open_language_dialog
from notifier import start_alert, stop_alert
from theme import SPACING, clicked_button_color, button_color, toggle_theme, themed_bg
from logicUI import login, signin, logout, show_history, delete, check, deactivate_account
from theme import borders_color
import asyncio
from translation import t


def content_main_view(page):

    # ---------------------------textFields---------------------------------------:

    numWassit = textfield(t("wassit_label"))
    icon = ft.Icon(ft.Icons.WORK_OUTLINE, color=ft.Colors.GREEN_ACCENT_200)
    wassit_row = ft.Row([icon, numWassit], spacing=SPACING, alignment=ft.MainAxisAlignment.CENTER)

    id_ = textfield(t("id_label"))
    icon = ft.Icon(ft.Icons.PERSON_OUTLINE, color=ft.Colors.GREEN_ACCENT_200)
    id_row = ft.Row([icon, id_], spacing=SPACING, alignment=ft.MainAxisAlignment.CENTER)

    empty_row = ft.Row([], spacing=SPACING, alignment=ft.MainAxisAlignment.CENTER)

    content = ft.Column(
        [wassit_row, id_row, empty_row],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=SPACING,
        expand=True
    )

    return content, id_, numWassit


def main_view(page):
    # Create two *distinct* sets of controls
    content1, id1, wassit1 = content_main_view(page)
    content2, id2, wassit2 = content_main_view(page)

    def on_login(e):
        btn_login.disabled = True
        btn_login.bgcolor = clicked_button_color
        show_spinner(page)
        page.update()
        success, message, data = login(id1.value, wassit1.value)
        hide_spinner(page)
        page.update()

        if success:
            # example: show alert or switch view
            page.client_storage.set("current_user", {
                "user_id": id1.value,
                "wassit_number": wassit1.value,
                "logged_in_at": datetime.datetime.now().isoformat(),
                "lang": "en",
            })
            page.go("/dashboard")
        else:
            alert(page, message, success)
            page.update()
        btn_login.bgcolor = button_color
        btn_login.disabled = False
        page.update()

    def on_signin(e):
        btn_signin.disabled = True
        btn_signin.bgcolor = clicked_button_color
        show_spinner(page)
        page.update()
        success, message, data = signin(id2.value, wassit2.value)
        hide_spinner(page)
        page.update()

        alert(page, message, success)
        btn_signin.bgcolor = button_color
        btn_signin.disabled = False
        page.update()

    btn_login = button(t("login_btn"), on_login)
    btn_signin = button(t("signin_btn"), on_signin)

    loginbtn_row = ft.Row([btn_login], alignment=ft.MainAxisAlignment.CENTER)
    signinbtn_row = ft.Row([btn_signin], alignment=ft.MainAxisAlignment.CENTER)

    content1.controls.append(loginbtn_row)
    content2.controls.append(signinbtn_row)

    final_login_content = ft.Container(content1, expand=True, alignment=ft.alignment.center)
    final_signin_content = ft.Container(content2, expand=True, alignment=ft.alignment.center)

    tab1 = final_login_content
    tab2 = final_signin_content

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text=t("login_tab"), content=tab1),
            ft.Tab(text=t("signin_tab"), content=tab2),
        ],
        expand=True,
        tab_alignment=ft.TabAlignment.CENTER,
        indicator_color=borders_color,
        divider_color=ft.Colors.TRANSPARENT,
        label_color=borders_color,  # Selected tab color
        unselected_label_color=ft.Colors.GREY,  # Unselected tab color
    )

    page.update()
    return ft.Container(expand=True, alignment=ft.alignment.center,
                content=ft.Column(
                    [tabs], expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )


is_running = None
light_on = True


def dashboard_view(page):
    from logicUI import success_times
    last_success = success_times

    global is_running

    time_field_state = page.client_storage.get("time_field_state")
    time_field_value = page.client_storage.get("time_field_value")

    # Load saved preference
    notif_enabled = page.client_storage.get("notif_enabled")
    if notif_enabled is None:
        notif_enabled = True
        page.client_storage.set("notif_enabled", True)

    async def ui_updater():
        nonlocal last_success
        while True:
            from logicUI import message, data, success_times, failure_times

            success_count_label.value = str(success_times)
            fail_count_label.value = str(failure_times)
            status_text.value = f"{t("last_result")} {message if message else t('nothing')} {data if data else ''}"
            page.update()

            # ---- 🔊 Notifier ----
            if success_times > last_success:  # new success happened
                last_success = success_times
                if notif_enabled:
                    start_alert(page)
            page.update()
            await asyncio.sleep(1)

    success_count_label = ft.Text("", size=22, weight=ft.FontWeight.BOLD, selectable=True)
    fail_count_label = ft.Text("", size=22, weight=ft.FontWeight.BOLD, selectable=True)
    status_text = ft.Text("", size=14, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500, selectable=True)

    # === 1️⃣ Top bar ===
    # Menu button (left)

    def toggle_notification(_):
        nonlocal notif_enabled
        notif_enabled = not notif_enabled
        page.client_storage.set("notif_enabled", notif_enabled)
        notification_item.icon = ft.Icons.NOTIFICATIONS_ACTIVE if notif_enabled else ft.Icons.NOTIFICATIONS_OFF_OUTLINED
        notification_item.text = f"{t('receive_notifications')} : {t('on') if notif_enabled else t('off')}"
        page.update()

        if not notif_enabled:
            stop_alert(page)

    notification_item = ft.PopupMenuItem(
        text=f"{t('receive_notifications')} : {t('on') if notif_enabled else t('off')}",
        icon=ft.Icons.NOTIFICATIONS_ACTIVE if notif_enabled else ft.Icons.NOTIFICATIONS_OFF_OUTLINED,
        on_click=toggle_notification
    )

    menu = ft.PopupMenuButton(
        icon=ft.Icons.MENU,
        items=[
            ft.PopupMenuItem(text=t("profile_title"), icon=ft.Icons.PERSON_OUTLINE, on_click=lambda _: page.go("/profile")),
            ft.PopupMenuItem(text=t("history_title"), icon=ft.Icons.HISTORY, on_click=lambda _: page.go("/history")),
            ft.PopupMenuItem(text=t("toggle_theme"), icon=ft.Icons.BRIGHTNESS_6_OUTLINED, on_click=lambda _: toggle_theme(page)),
            notification_item,
            ft.PopupMenuItem(text=t("change_language"), icon=ft.Icons.LANGUAGE, on_click=lambda _: open_language_dialog(page)),
            ft.PopupMenuItem(text=t("logout_btn"), icon=ft.Icons.LOGOUT, on_click=lambda _: logout(page)),
        ],
        tooltip=t("menu"))

    # Dark/Light mode button (right)

    aboutus_btn = ft.IconButton(
        icon=ft.Icons.INFO_OUTLINE,
        tooltip=t("aboutus_title"),
        on_click=lambda _: page.go("/about"),
    )

    # Align both at the top
    top_bar = ft.Row(
        [menu, aboutus_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # === 2️⃣ Time selector ===
    # (like a dropdown spinner)
    time_field = ft.Dropdown(
        label=t("start_check_title"),
        options=[
            ft.dropdown.Option("3"),
            ft.dropdown.Option("5"),
            ft.dropdown.Option("10"),
            ft.dropdown.Option("15"),
            ft.dropdown.Option("30"),
            ft.dropdown.Option("60"),
        ],
        value=time_field_value if time_field_value else "5",
        width=180,
        label_style=ft.TextStyle(weight=ft.FontWeight.W_500),
        border_color=borders_color,
        border_radius=10,
        disabled=time_field_state if time_field_state else False
    )

    # === 3️⃣ Latest status area ===

    status_container = ft.Container(
        status_text,
        alignment=ft.alignment.center,
        margin=ft.margin.symmetric(vertical=10),
    )

    # === 4️⃣ Big circular start button ===
    user = page.client_storage.get("current_user")
    if user:
        userId = user["user_id"]
        userWassitNum = user["wassit_number"]

    def start_or_stop_check():
        global is_running
        if is_running:
            #print(is_running)
            is_running = False
            start_btn.icon = ft.Icons.PLAY_CIRCLE_FILL_OUTLINED
            start_btn.icon_color = ft.Colors.RED_ACCENT_100
            start_btn.tooltip = t("start_check_btn_tooltip")
            status_text.value = t("pause")
            time_field.disabled = False
            page.client_storage.set("time_field_state", time_field.disabled)
            page.client_storage.set("time_field_value", time_field.value)
            page.update()
            check(userId, userWassitNum, int(time_field.value), True)

        else:
            #print(is_running)
            is_running = True
            start_btn.icon = ft.Icons.PAUSE_CIRCLE_FILLED_OUTLINED
            start_btn.icon_color = ft.Colors.GREEN_ACCENT_200
            start_btn.tooltip = t("pause_check_btn_tooltip")
            time_field.disabled = True
            page.client_storage.set("time_field_state", time_field.disabled)
            page.client_storage.set("time_field_value", time_field.value)
            page.update()
            check(userId, userWassitNum, int(time_field.value), False)
        page.update()

    start_btn = ft.IconButton(
            icon=ft.Icons.PLAY_CIRCLE_FILL_OUTLINED if not is_running else ft.Icons.PAUSE_CIRCLE_FILLED_OUTLINED,
            icon_size=120,
            icon_color=ft.Colors.RED_ACCENT_100 if not is_running else ft.Colors.GREEN_ACCENT_200,
            on_click=lambda _: start_or_stop_check()
        )

    # === 5️⃣ Success / Fail counters ===
    success_box = ft.Container(
        ft.Column(
            [
                ft.Text(t("success"), color=ft.Colors.GREEN_ACCENT_200, selectable=True),
                success_count_label
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=100,
        height=80,
        border=ft.border.all(1, borders_color),
        border_radius=10,
        alignment=ft.alignment.center,
    )

    fail_box = ft.Container(
        ft.Column(
            [
                ft.Text(t("failed"), color=ft.Colors.RED_ACCENT_200, selectable=True),
                fail_count_label
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=100,
        height=80,
        border=ft.border.all(1, borders_color),
        border_radius=10,
        alignment=ft.alignment.center,
    )

    counters_row = ft.Row(
        [success_box, fail_box],
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=40)

    # === Layout everything ===
    dashboard_content = ft.Column(
        [
            top_bar,
            ft.Container(time_field, alignment=ft.alignment.center, margin=ft.margin.only(top=10)),
            status_container,
            ft.Container(start_btn, alignment=ft.alignment.center, margin=ft.margin.only(top=20)),
            ft.Container(counters_row, alignment=ft.alignment.center, margin=ft.margin.only(top=20)),
        ],
        adaptive=True,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.run_task(ui_updater)

    return dashboard_content


def history(page):
    card_id = 0

    cards = ft.Column([], alignment=ft.MainAxisAlignment.START
                      , horizontal_alignment=ft.CrossAxisAlignment.CENTER
                      , expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    user = page.client_storage.get("current_user")

    # Check if user exists before accessing user_id
    if not user:
        # Return a message if no user is logged in
        no_user_message = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING, size=48, color=ft.Colors.ORANGE),
                ft.Text(t("no_user_loggedin"), size=18, weight=ft.FontWeight.BOLD, selectable=True),
                ft.Text(t("login_request_for_history"), size=14, selectable=True),
                ft.ElevatedButton(
                    t("go_to_login"),
                    on_click=lambda _: page.go("/")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        return no_user_message

    userId = user["user_id"]
    buffer = []

    show_history(buffer, userId)

    # Create a message for empty history
    if not buffer:
        empty_history = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=48, color=ft.Colors.GREY),
                ft.Text(t("no_history_yet"), size=18, weight=ft.FontWeight.BOLD, selectable=True),
                ft.Text(t("history_here"), size=14, selectable=True),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        return empty_history

    # Build history cards
     #created_at = ft.Text("", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, expand=True, selectable=True)
    
    if buffer:
        for each in buffer:

            msg = ft.Text("", weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, expand=True, selectable=True)
            data = ft.Text("", weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, expand=True, selectable=True)

            card_id += 1
            id = each[0]
            succ_fail = each[1]
            if succ_fail:
                card_color = ft.Colors.GREEN_100
            else:
                card_color = ft.Colors.RED_100
            msg.value = each[2]
            data.value = each[3]
            #created_at.value = each[4]
            card = ft.Card(content=ft.Container(content=ft.Column([ft.ListTile(leading=ft.Icon(ft.Icons.HISTORY, color=ft.Colors.BLACK),
                                                                                         # ListTile --> a single fixed-height row
                                                                                         title=ft.Text(f"#{card_id}", color=ft.Colors.BLACK, selectable=True)),

                                                                                ft.Row([msg], spacing=10, expand=True),
                                                                                ft.Row([ft.Text(t("dates :"), color=ft.Colors.BLACK), data], spacing=10, expand=True),
                                                                                ft.Row([ft.IconButton(
                                                                                    icon=ft.Icons.DELETE_OUTLINE_SHARP,
                                                                                    icon_color=ft.Colors.RED_900,
                                                                                    on_click=lambda e, key=id: delete(key, cards))],
                                                                                    alignment=ft.MainAxisAlignment.END,
                                                                                    expand=True)])
                                                , bgcolor=card_color, padding=10, border_radius=15),
                        key=id)

            cards.controls.append(card)
    return ft.Container(cards, expand=True, padding=20, alignment=ft.alignment.top_center)


def delete_account_view(page):
    page.overlay.clear()
    page.update()

    user = page.client_storage.get("current_user")
    if not user:
        return

    user_id = user["user_id"]

    # Generate a random 5-digit confirmation code
    code = str(random.randint(10000, 99999))

    # TextField for user input
    input_field = ft.TextField(label=t("confirm_deletion_code"))

    # Area to show errors
    error_text = ft.Text("", color=ft.Colors.RED_400, selectable=True)

    # Dialog
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("confirm_deletion_title"), selectable=True),
        content=ft.Column([
            ft.Text(t("confirm_deletion_request_enter_code"), selectable=True),
            ft.Text(code, size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400, selectable=True),
            input_field,
            error_text
        ], tight=True),
        actions=[
            ft.TextButton(t("cancel_btn"), on_click=lambda _: close_dialog()),
            ft.TextButton(t("confirm_btn"), on_click=lambda _: confirm_delete()),
        ], actions_alignment=ft.MainAxisAlignment.END)

    def close_dialog():
        dlg.open = False
        page.update()  # first close the dialog properly

    def confirm_delete():
        if input_field.value == code:
            # Delete logic
            close_dialog()
            deactivate_account(page, user_id)
        else:
            error_text.value = t("code_incorrect")
            page.update()

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def profile_view(page):
    user = page.client_storage.get("current_user")

    if not user:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.WARNING, size=50, color=ft.Colors.ORANGE),
                ft.Text(t("no_user_loggedin"), size=18, weight=ft.FontWeight.BOLD, selectable=True),
                ft.Text(t("login_request_for_profile"), selectable=True),
                ft.ElevatedButton(t("go_to_login"), on_click=lambda _: page.go("/"))
            ], alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

    # ---- User data ----
    user_id = user["user_id"]
    user_wassitNum = user["wassit_number"]

    # ---- UI elements ----

    card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_300),
                    ft.Text(t("id_label"), weight=ft.FontWeight.BOLD, expand=True, selectable=True),
                    ft.Text(user_id, expand=True, selectable=True)
                ], alignment=ft.MainAxisAlignment.START),

                ft.Row([
                    ft.Icon(ft.Icons.WORK_OUTLINE, color=ft.Colors.GREEN_300),
                    ft.Text(t("wassit_label"), weight=ft.FontWeight.BOLD, expand=True, selectable=True),
                    ft.Text(user_wassitNum, expand=True, selectable=True)
                ], alignment=ft.MainAxisAlignment.START),


            ], spacing=15),

            padding=20,
            bgcolor=themed_bg(page),
            border_radius=12,
            border=ft.border.all(1, borders_color)
        ),
        elevation=3
    )

    # ---- Buttons ----

    logout_btn = ft.ElevatedButton(
        t("logout_btn"),
        icon=ft.Icons.LOGOUT,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.RED_400,
        on_click=lambda _: logout(page),
        width=200
    )

    delete_btn = ft.OutlinedButton(
        t("delete_account_btn"),
        icon=ft.Icons.DELETE_FOREVER,
        icon_color=ft.Colors.RED_400,
        on_click=lambda _: delete_account_view(page),
        width=200,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1, ft.Colors.RED_400),
            color=ft.Colors.RED_400
        )
    )

    return ft.Container(
        content=ft.Column(
            [

                ft.Divider(),

                card,

                ft.Container(height=20),

                delete_btn,
                logout_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        expand=True,
        padding=20,
        bgcolor=themed_bg(page),
        alignment=ft.alignment.top_center
    )


def about_us(page):
    facebook_url = "https://facebook.com/yourpage"  # change this
    support_email = "support@yourapp.com"  # safer than personal Gmail
    app_version = "1.0.0"

    fb_button = ft.ElevatedButton(
                t("fb_page_label"),
                icon=ft.Icons.FACEBOOK,
                on_click=lambda _: open_facebook(_),
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                width=180)

    email_button = ft.ElevatedButton(
                support_email,
                icon=ft.Icons.EMAIL_OUTLINED,
                on_click=lambda _: send_email(_),
                width=220)

    def open_facebook(e):
        page.launch_url(facebook_url)

    def send_email(e):
        page.launch_url(f"mailto:{support_email}")

    content = ft.Column(
        [
            ft.Text(t("main_title"), size=24, weight=ft.FontWeight.BOLD, selectable=True),
            ft.Text(t("app_description"), size=14, text_align=ft.TextAlign.CENTER, selectable=True),

            ft.Divider(),

            # Facebook button
            ft.Text(t("follow_us_label"), size=16, weight=ft.FontWeight.W_600, selectable=True),
            fb_button,

            # Email button
            ft.Text(t("contact_label"), size=16, weight=ft.FontWeight.W_600, selectable=True),
            email_button,

            ft.Divider(),

            ft.Text(f"{t("version_label")} {app_version}", size=12, color=ft.Colors.GREY, selectable=True),
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Container(content, padding=20, alignment=ft.alignment.top_center)






