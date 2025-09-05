from pathlib import Path
import json
from lms.message.msbtio import read_msbt_path
from lms.message.msbtio import write_msbt_path
import os
import re

ORIG_DIR = "mess_orig"
DEST_DIR = "mess_json"

class MSBT:

    def _remove_tags(self, input_str):
        pattern = r'\[[^\]]*\]'
        return re.sub(pattern, '', input_str)
    
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

    def from_json(self, input_dir, orig_mess_dir, output_dir):
        msbt_orig_dir = Path(orig_mess_dir)
        for msbt_orig_file in msbt_orig_dir.iterdir():
            if msbt_orig_file.is_file() and msbt_orig_file.suffix == '.msbt':
                orig_msbt = read_msbt_path(str(msbt_orig_file))
                msbt_orig_msbt_obj = read_msbt_path(str(msbt_orig_file))

                with open(f"{input_dir}{os.path.basename(msbt_orig_file.name)[:-5]}_trans.msbt.json", "r") as json_trans_file:
                    json_trans = json.load(json_trans_file)

                    for mess_trans in json_trans.items():
                        mess = msbt_orig_msbt_obj.get_entry_by_name(mess_trans[0])

                        mess.message.text = self._remove_tags(mess_trans[1]['message'])

            write_msbt_path(f"{output_dir}{os.path.basename(msbt_orig_file.name)}", msbt_orig_msbt_obj)       

        #a = orig_msbt.get_entry_by_index(0)
        #m = a.to_dict()
        #print(m)

        #a.message.text = "AAAAA"