import platform
import requests


def detect_element_type_name(element):
    tag = element.evaluate("el => el.tagName.toLowerCase()")
    element_type = element.evaluate("el => el.getAttribute('type')")

    # Classification logic:
    if tag == "input":
        element_name = element.input_value() or ""
        if element_type in ["text", None]:
            return f'{"text field : ", element_name}'
        elif element_type == "password":
            return f'{"password field : ", element_name}'
        elif element_type == "checkbox":
            return f'{"checkbox : ", element_name}'
        elif element_type == "radio":
            return f'{"radio button : ", element_name}'
        elif element_type == "email":
            return f'{"email field : ", element_name}'
        elif element_type == "number":
            return f'{"number field : ", element_name}'
        else:
            return f"input ({element_type} : {element_type})"
    elif tag == "textarea":
        return "text area"
    elif tag == "button":
        element_name = element.inner_text()
        return f"button : {element_name}"
    elif tag == "select":
        element_name = element.inner_text()
        return f"dropdown (select) : {element_name}"
    elif tag == "a":
        element_name = element.inner_text()
        return f"link : '{element_name if element_name.strip() != "" else element.get_attribute('href')}'"
    else:
        return f"generic element <{tag}>"


def checkExistance(element):
    return element.count() > 0


def checkVisibility(element):
    if not checkExistance(element):
        #print("⚠ Element not found")
        return False
    element_name = detect_element_type_name(element)
    element.wait_for(state="visible", timeout=5000)

    if not element.is_visible():
        #print(f"⚠ Element ->{element_name}<- exists but doesn't appear on screen")
        return False
    return True


def start_alert_listener(page):
    page.expose_function("pythonAlertHandler", lambda msg: print("⚠ Alert:", msg))

    page.evaluate("""
        () => {
            const observer = new MutationObserver(mutations => {
                for (const mutation of mutations) {
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === 1 && node.classList.contains('MuiAlert-message')) {
                            window.pythonAlertHandler(node.innerText);
                        }
                    }
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    """)


def send_telegram_message(bot_token, chat_id, message, notification=True):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "disable_notification": notification}
    requests.post(url, data=data)


def send_whatsapp_message(number, message):
    import pywhatkit as kit     #Simplifies tasks such as sending WhatsApp messages, playing YouTube videos, performing web searches
    kit.sendwhatmsg_instantly(number, message)


def detect_device():
    import subprocess
    system = platform.system()
    machine = platform.machine()

    if system == "Linux":
        try:
            # if getprop works → we’re on Android
            model = subprocess.check_output(["getprop", "ro.product.model"], stderr=subprocess.DEVNULL).decode().strip() #stderr=subprocess.DEVNULL to silence unwanted getprop errors on non-Android systems:
            return "Android", model
        except Exception:
            return system, machine
    return system, machine


def get_device_viewport():
    from playwright.sync_api import sync_playwright
    os, device = detect_device()
    with sync_playwright() as p:
        if os.lower() in ['android', 'ios']:
            device_cara = p.devices[device]
            width, height = device_cara['viewport']['width'], device_cara['viewport']['height']
            return width, height
        else:
            return None, None


def select_context(p, os_name, model):
    supported_device = None
    if os_name == "Android":
        devices = p.devices
        for device_name in devices:
            if device_name.lower() in model.lower():
                supported_device = device_name
                break
        if supported_device is None:
            for device_name in devices:
                if not device_name.lower().startswith(('iphone', 'ipad')):
                    supported_device = device_name
                    break
    elif os_name == "iOS":
        devices = p.devices
        supported_device = None
        for device_name in devices:
            if device_name.lower() in model.lower():
                supported_device = device_name
                break
        if supported_device is None:
            for device_name in devices:
                if device_name.lower().startswith(('iphone', 'ipad')):
                    supported_device = device_name
                    break

    browser = p.chromium.launch(headless=True, slow_mo=1000)
    if supported_device is not None:
        device_config = p.devices[supported_device]
        context = browser.new_context(**device_config)
        page = context.new_page()
        return browser, context, page
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    page = context.new_page()
    return browser, context, page


def click_tap(os_name, element):
    try:
        if os_name == "Android" or os_name == "iOS":
            element.tap()
        else:
            element.click()
    except:
        return False



