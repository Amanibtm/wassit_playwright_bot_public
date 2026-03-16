import json
import os

# Stores all languages
translations = {}

# Currently selected language ("en" will be default)
current_language = "en"


def load_translations(folder="locale"):
    global translations
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            lang = filename.replace(".json", "")
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)


def set_language(lang):
    global current_language
    if lang in translations:
        current_language = lang


def t(key):
    """
    Translates `key` using the loaded translations.
    If missing: returns the key itself.
    """
    return translations.get(current_language, {}).get(key, key)
