import os
from google.cloud import translate_v2 as translate
from pathlib import Path
import json
import random
import html
import threading

LANGUAGES_CACHE_FILE_PATH = "cached_languages.json"
ORIGINAL_LANG = "fr"
FINAL_LANG = "fr"

DISALLOWED_PAIRS = {
    "iw": "he",
    "ji": "yi",
    "in": "id",
    "jw": "jv",
}

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
    

    def wrap_with_limit(self, text, limit=33):
        words = text.split()
        result = ""
        line_length = 0
        
        for word in words:
            extra_length = len(word) + (1 if line_length > 0 else 0)
            
            if line_length + extra_length > limit:
                result += "\r\n" + word
                line_length = len(word)
            else:
                if line_length > 0:
                    result += " "
                    line_length += 1
                result += word
                line_length += len(word)
        
        return result
    
    def _swap_disallowed_pair(self, lang):
        if lang in DISALLOWED_PAIRS.keys():
            return DISALLOWED_PAIRS[lang]
        return lang
    
    def translate(self, original_text, iterations = 1):
        result = { "translatedText": original_text }
        original_lang = ORIGINAL_LANG
        for i in range(0, iterations):
            #print(f"\t({i+1}/{iterations})", end="\r")
            target = random.choice(self.available_langs)
            target = self._swap_disallowed_pair(target)
            while target == original_lang:
                target = random.choice(self.available_langs)
            result = self.client.translate(values=html.unescape(result["translatedText"]), target_language=target, source_language=original_lang)
            original_lang = target

        while target == FINAL_LANG:
            target = random.choice(self.available_langs)
            result = self.client.translate(values=html.unescape(result["translatedText"]), target_language=target, source_language=original_lang)
            original_lang = target

        final_translation = self.client.translate(values=html.unescape(result["translatedText"]), target_language=FINAL_LANG, source_language=original_lang)

        final_translation_wrapped = self.wrap_with_limit(final_translation["translatedText"])

        #print(f'{original_text} -> {final_translation["translatedText"]}')
        return html.unescape(final_translation_wrapped)
    
    def threaded_translate(self, in_file, out_dir):
         with open(in_file, "r") as file:
                    translated = {}
                    messages = json.load(file)
                    mess_progress = 1
                    print(f"Thread #{threading.get_ident()} - {in_file}: {mess_progress}/{len(messages)}")
                    for mess in messages.items():
                        translated_str = self.translate(mess[1]['message'], 100)
                        translated[mess[0]] = {
                            "name": mess[0],
                            "message": translated_str,
                            "attribute": mess[1]['attribute'],
                            "style_index": mess[1]['style_index']
                        }
                        mess_progress+=1
                        
                        #print(f"Thread #{threading.get_ident()} - Translated \"{mess[1]['message']}\" -> \"{translated_str}\"")
                        print(f"Thread #{threading.get_ident()} - {in_file}: {mess_progress}/{len(messages)}")

                    with open(f"{out_dir}/{os.path.basename(file.name)[:-10]}_trans.msbt.json", "w+") as file_out:
                        json.dump(translated, file_out, ensure_ascii=False, indent=4)
    
    def translate_from_json_dir(self, input_dir, output_dir):
        input_dir_path = Path(input_dir)
        threads = []
        for json_file in input_dir_path.iterdir():
            output_file = Path(f"{output_dir}{os.path.basename(json_file.name)[:-10]}_trans.msbt.json")
            if json_file.is_file() and json_file.suffix == '.json' and not output_file.is_file():

                thread = threading.Thread(target=self.threaded_translate, kwargs={"in_file": json_file, "out_dir": output_dir})
                threads.append(thread)

                """
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
                        
                        print(f"Translated \"{mess[1]['message']}\" -> \"{translated_str}\"")
                        print(f"{json_file}: {mess_progress}/{len(messages)}")

                    with open(f"{output_dir}/{os.path.basename(file.name)[:-10]}_trans.msbt.json", "w+") as file_out:
                        json.dump(translated, file_out, ensure_ascii=False, indent=4)
                        """
            else:
                print(f"{json_file.name} already processed or invalid, skipping...")

            active_threads = []

        while(len(threads) > 0):
            for t in threads:
                if len(active_threads) < 3:
                    t.start()
                    active_threads.append(t)


            for a in active_threads:
                a.join(timeout=10)
                if not a.is_alive:
                    active_threads.remove(a)

            
