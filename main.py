from cyclic_translator import CyclicTranslator
from msbt import MSBT

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