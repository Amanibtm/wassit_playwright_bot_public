import os
import platform
import sys

from plyer import notification
from translation import t


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)


icon_path = resource_path("assets/icons/app.png")
audio_path = resource_path("assets/ringtones/alert.mp3")


vibrator = None
try:
    if platform.system() == "Android":
        from plyer import vibrator
except:
    vibrator = None

import flet as ft

# GLOBALS
alert_audio = None
stop_button = None
alerting = False


def setup_alert_system(page: ft.Page):
    """Call this once in main() to prepare audio + stop button."""
    global alert_audio, stop_button

    # ---- SOUND PLAYER ----
    alert_audio = ft.Audio(
        src=audio_path,
        autoplay=False,
        volume=1.0
    )
    page.overlay.append(alert_audio)

    # ---- STOP BUTTON ----
    stop_button = ft.Container(
        visible=False,
        alignment=ft.alignment.center,
        content=ft.ElevatedButton(
            text="STOP ALERT",
            on_click=lambda _: stop_alert(page),
            bgcolor=ft.Colors.RED_400,
            color=ft.Colors.WHITE,
            width=200,
            height=60,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )
    )
    page.overlay.append(stop_button)

    page.update()


# --------------------------------------------------
def start_alert(page: ft.Page):
    """Start sound + vibration + notification."""
    global alert_audio, stop_button, alerting

    if alerting:
        return
    alerting = True

    # 1. SYSTEM NOTIFICATION
    try:
        notification.notify(
            app_icon=icon_path,
            title=t("main_title"),
            message=t("dates_available"),
            timeout=5
        )
    except:
        pass

    # 2. PLAY SOUND
    try:
        alert_audio.play()
    except:
        pass

    # 3. VIBRATION ONLY ON ANDROID
    if platform.system().lower() == "android":
        try:
            if vibrator:
                vibrator.vibrate(1500)  # vibrate for 1.5 seconds
        except:
            pass

    # 4. SHOW STOP BUTTON
    stop_button.visible = True
    page.update()


# --------------------------------------------------
def stop_alert(page: ft.Page):
    """Stops sound + hides stop button."""
    global alert_audio, stop_button, alerting

    if not alerting:
        return

    alerting = False

    # stop audio
    try:
        alert_audio.pause()
        alert_audio.seek(0)
    except:
        pass

    if vibrator:
        try:
            vibrator.cancel()
        except:
            pass
    else:
        pass

    # hide button
    stop_button.visible = False
    page.update()
