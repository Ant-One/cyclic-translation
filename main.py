from cyclic_translator import CyclicTranslator
from msbt import MSBT

import pyphen

def wrap_with_limit(text, limit=33):
    words = text.split()
    result = ""
    line_length = 0
    
    for word in words:
        # +1 pour l'espace si ce n'est pas le début de ligne
        extra_length = len(word) + (1 if line_length > 0 else 0)
        
        if line_length + extra_length > limit:
            # retour à la ligne avant le mot
            result += "\r\n" + word
            line_length = len(word)
        else:
            # ajouter avec espace si besoin
            if line_length > 0:
                result += " "
                line_length += 1
            result += word
            line_length += len(word)
    
    return result


if __name__ == "__main__":
    ct = CyclicTranslator()

    #a = ct.translate("Ingénieur-stagiaire ouvrages d'art", 100)
    #print(a)

    ct.translate_from_json_dir("mess_json/", "mess_trans/")

    #extractor = MSBT().to_json()

    #msbt = MSBT()

    #msbt.from_json("/Users/antoine/cyclic-translation/mess_orig/glossary.msbt")

    #ct.translate_from_json_dir(input_dir = "mess_json", output_dir = "mess_json_trans")

    #texte = "Des joueurs du monde entier vous attendent ! Voulez-vous les affronter ?"

    #print(wrap_with_limit(texte))