import os
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
from Fixtures import checkVisibility, start_alert_listener, send_telegram_message, detect_device, select_context, click_tap
from translation import t

load_dotenv()
bot_token = os.getenv("bot_token")
chat_id = os.getenv("chat_id")
url = os.getenv("url")
myID = os.getenv("myID")
numWassit = os.getenv("numWassit")

system, platform = detect_device()


def wait_and_close(context, browser):
    try:
        time.sleep(2)  # Reduced from 3 to 2 seconds
        context.close()
        browser.close()
        #print("✅ Browser closed successfully")
    except Exception as e:
        #print(f"⚠️ Error closing browser: {e}")
        pass


def try_logginIn(myID, numWassit):
    with sync_playwright() as p:
        browser, context, page = select_context(p, system, platform)
        start_alert_listener(page)

        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
        except:
            wait_and_close(context, browser)
            return False, t("inaccessibility_in_website"), None
        #print("Page loaded.")

        numWassitelement = page.locator('input#numeroWassit,input[name="numeroWassit"]')
        if checkVisibility(numWassitelement):  # check if exists , then if visible
            # Fill inputs
            numWassitelement.type(numWassit)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        numID = page.locator('input#numeroPieceIdentite,input[name="numeroPieceIdentite"]')
        if checkVisibility(numID):  # check if exists , then if visible
            # Fill inputs
            numID.type(myID)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        # Click submit
        submitBtn = page.locator('button[type="submit"]')
        if checkVisibility(submitBtn):
            click_tap(system, submitBtn)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        #print("Submitted.")

        # Wait for continuation button or message
        continuation_btn = page.locator("//button[@type='button'][contains(., 'واصل')]")
        if checkVisibility(continuation_btn):
            return True, t("successfull_login"), None

        else:
            return False, t("unable_first_account_access"), None


def wassitDatesDetector(myID, numWassit):
    with sync_playwright() as p:

        browser, context, page = select_context(p, system, platform)
        start_alert_listener(page)

        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
        except:
            wait_and_close(context, browser)
            return False, t("inaccessibility_in_website"), None
        #print("Page loaded.")

        numWassitelement = page.locator('input#numeroWassit,input[name="numeroWassit"]')
        if checkVisibility(numWassitelement):  # check if exists , then if visible
            # Fill inputs
            numWassitelement.type(numWassit)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        numID = page.locator('input#numeroPieceIdentite,input[name="numeroPieceIdentite"]')
        if checkVisibility(numID):  # check if exists , then if visible
            # Fill inputs
            numID.type(myID)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        # Click submit
        submitBtn = page.locator('button[type="submit"]')
        if checkVisibility(submitBtn):
            click_tap(system, submitBtn)
        else:
            wait_and_close(context, browser)
            return False, t("form_load_issue"), None

        #print("Submitted.")

        response = None
        # Wait for continuation button or message
        continuation_btn = page.locator("//button[@type='button'][contains(., 'واصل')]")
        if checkVisibility(continuation_btn):
            #print("Successful --> المواصلة")
            with page.expect_response(lambda res: "GetAvailableDates" in res.url) as response_info:    #   wait and capture any link contains the string "GetAvailableDates"
                click_tap(system, continuation_btn)
            response = response_info.value
            data = response.json()
            #print("✅ URL:", response.url)
            #print("✅ Status:", response.status)
            #print("✅ JSON body:", response.json())  # only if it's JSON

        else:
            return False, t("login_failed"), None

        if response and response.status == 200:
            dates = data.get('dates', [])
            current_time = datetime.now().strftime("%H:%M:%S")  # capture current time
            if dates:
                send_telegram_message(bot_token, chat_id, f"🎉 [{current_time}] ✅ DATES AVAILABLE: {dates}")
                wait_and_close(context, browser)
                return True, f"{current_time} ➜ {t("dates_available")}", dates

            else:
                # send_telegram_message(bot_token, chat_id, f"[{current_time}] ❌No dates available", False)
                wait_and_close(context, browser)
                return False, f"{current_time} ➜ {t("dates_unavailable")} ", None

        else:
            #print("HTTP response :", response.status)
            wait_and_close(context, browser)
            return False, f"HTTP response : {response.status}", None
