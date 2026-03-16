import flet as ft
import sqlite3
from Fixtures import get_device_viewport, detect_device
from components import page_appbar, main_page_appbar
from translation import load_translations, set_language, t
from views import main_view, dashboard_view, history, profile_view, about_us
from theme import themed_bg
from notifier import setup_alert_system


#  -------------------------------------create a database then a table :-----------------------------------------------

conn = sqlite3.connect('wassitdata.db')  # name the db as you like / Without 'check_same_thread=False': If a thread in your app opens a connection to the database and another thread tries to use the same connection, SQLite will raise an error because it expects only the thread that opened the connection to use it.
cursor = conn.cursor()  # use the cursor of db for secure and synchronous operations
cursor2 = conn.cursor()
cursor.execute('''
       CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id TEXT NOT NULL,
           wassit_number TEXT,
           is_active BOOLEAN,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
   ''')

cursor2.execute('''
       CREATE TABLE IF NOT EXISTS history (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id TEXT NOT NULL,
           success BOOLEAN,
           message TEXT,
           data TEXT,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
   ''')
conn.commit()
conn.close()
# -----------------------------------------------------------------------------------------------------------


def main(page: ft.Page):
    os,  model = detect_device()
    width, height = get_device_viewport()
    setup_alert_system(page)

    # ---------------------Interface----------------------------------------------------------------------------------------------------------------------------
    if model.lower() in ['ios', 'android']:
        page.window.width = width
        page.window.height = height
        page.window.maximized = True

    else:
        page.window.width = 600
        page.window.height = 600
        # page.window.resizable = False
        page.window.maximizable = False

    page.title = 'WDD'
    page.bgcolor = themed_bg(page)
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.theme_mode = ft.ThemeMode.LIGHT

    current_language = page.client_storage.get("language")
    if not current_language:
        page.client_storage.set("language", "ar")

    load_translations()  # load en.json, fr.json, ar.json
    set_language(current_language if current_language else "ar")  # default language

    def route_change(_):
        page.views.clear()
        if page.route == "/":
            page.views.append(ft.View("/", [main_view(page)], appbar=main_page_appbar(page, t("main_title")), bgcolor=themed_bg(page)))
        elif page.route == "/dashboard":
            page.views.append(ft.View("/dashboard", [dashboard_view(page)], bgcolor=themed_bg(page)))
        elif page.route == "/history":
            page.views.append(ft.View("/history", [history(page)], appbar=page_appbar(page, t("history_title"), "/dashboard"), bgcolor=themed_bg(page)))
        elif page.route == "/profile":
            page.views.append(ft.View("/profile", [profile_view(page)], appbar=page_appbar(page, t("profile_title"), "/dashboard"), bgcolor=themed_bg(page)))
        elif page.route == "/about":
            page.views.append(ft.View("/about", [about_us(page)], appbar=page_appbar(page, t("aboutus_title"), "/dashboard"), bgcolor=themed_bg(page)))

        page.update()

    page.on_route_change = route_change
    page.go("/")

    stored_user = page.client_storage.get("current_user")  # get current logged in user
    if stored_user:
        #print(f"Restoring session for user: {stored_user['user_id']}")
        page.go("/dashboard")  # directly go to dashboard if user already logged in
    else:
        page.go("/")  # go to login view

    page.go(page.route)  # responsible for the 'verb' of changing routes


ft.app(main)
