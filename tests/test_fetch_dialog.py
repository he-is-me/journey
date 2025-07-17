from pathlib import Path

def test_fetch_dialog():
    header = "TEST LINE"
    """Reads the dialog.md file and gets the correct lines of text
    and gives it to the text area and updates it"""
    dialogs = {}
    buff = []
    in_block = False
    with open(Path("journey/dialog.md"), 'r') as file:
        contents = file.read()
        for line in contents.splitlines():
            if line.startswith("## ") and header in line[3:]:
                in_block = True
                print("IN THE BLOCK NOW")
                continue
            if in_block and not line.startswith("---") and not line.startswith("## "): # --- means end of the block 
                print("RUNNING END OF SECTION CHECK")
                buff.append(line)
                print("APPENDED TO BUFFER:", line)
            else:
                break
    dialogs[header] = '\n'.join(buff).strip()
    assert dialogs[header]
 

