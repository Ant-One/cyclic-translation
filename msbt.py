from pathlib import Path
import json
from lms.message.msbtio import read_msbt_path
from lms.message.msbtio import write_msbt_path

ORIG_DIR = "mess_orig"
DEST_DIR = "mess_json"

class MSBT:
    def to_json(self):
        msbt_orig = Path(ORIG_DIR)

        for msbt_file in msbt_orig.iterdir():
            mess_dict = {}
            
            if msbt_file.is_file() and msbt_file.suffix == '.msbt':
                msbt = read_msbt_path(str(msbt_file))

                for entry in msbt.entries:
                    d = entry.to_dict()
                    mess_dict[d['name']] = d

                print(f"Processing {msbt_file}")

                with open(f"{DEST_DIR}/{msbt_file.name}.json", "w+") as file:
                    json.dump(mess_dict, file, indent=4)

    def from_json(self, input):
        orig_msbt = read_msbt_path(input)
        a = orig_msbt.get_entry_by_index(0)
        m = a.to_dict()
        print(m)

        a.message.text = "AAAAA"