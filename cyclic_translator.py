import os
from google.cloud import translate_v2 as translate
from pathlib import Path
import json
import random
import html

LANGUAGES_CACHE_FILE_PATH = "cached_languages.json"
ORIGINAL_LANG = "fr"
FINAL_LANG = "fr"

class CyclicTranslator:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"
        self.client = translate.Client()
        self.available_langs = self.get_available_languages()

    def get_available_languages(self, no_cache = False):
        cache = Path(LANGUAGES_CACHE_FILE_PATH)
        if not cache.is_file() or no_cache:
            with open(LANGUAGES_CACHE_FILE_PATH, "w+") as file:
                lang_dict = self.client.get_languages()
                json.dump(lang_dict, file)
        else:
            with open(LANGUAGES_CACHE_FILE_PATH, "r") as file:
                lang_dict = json.load(file)

        lang_list = []
        for lang in lang_dict:
            lang_list.append(lang["language"])

        return lang_list
    
    def translate(self, original_text, iterations = 1):
        result = { "translatedText": original_text }
        original_lang = ORIGINAL_LANG
        for i in range(0, iterations):
            print(f"\t({i}/{iterations})", end="\r")
            target = random.choice(self.available_langs)
            #print(target, original_lang)
            while target == original_lang:
                target = random.choice(self.available_langs)
            result = self.client.translate(values=html.unescape(result["translatedText"]), target_language=target, source_language=original_lang)
            original_lang = target

        final_translation = self.client.translate(values=html.unescape(result["translatedText"]), target_language=FINAL_LANG, source_language=original_lang)

        #print(f'{original_text} -> {final_translation["translatedText"]}')
        return html.unescape(final_translation["translatedText"])
    
    def translate_from_json_dir(self, input_dir, output_dir):
        input_dir_path = Path(input_dir)
        for json_file in input_dir_path.iterdir():
            output_file = Path(f"{output_dir}{os.path.basename(json_file.name)[:-10]}_trans.msbt.json")
            if json_file.is_file() and json_file.suffix == '.json' and not output_file.is_file():
                with open(json_file, "r") as file:
                    translated = {}
                    messages = json.load(file)
                    mess_progress = 1
                    print(f"{json_file}: {mess_progress}/{len(messages)}")
                    for mess in messages.items():
                        translated_str = self.translate(mess[1]['message'], 100)
                        translated[mess[0]] = {
                            "name": mess[0],
                            "message": translated_str,
                            "attribute": mess[1]['attribute'],
                            "style_index": mess[1]['style_index']
                        }
                        mess_progress+=1

                    with open(f"{output_dir}/{os.path.basename(file.name)[:-10]}_trans.msbt.json", "w+") as file_out:
                        json.dump(translated, file_out, ensure_ascii=False, indent=4)
            else:
                print(f"{json_file.name} already processed or invalid, skipping...")

            break