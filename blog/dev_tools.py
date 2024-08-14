from pdb import run
import app as a
import pycmd as pc

def quit() -> None:
    global running
    running = False

reader = pc.CommandReader(
    [
        a.create_all,
        a.delete_user,
        a.add_admin,
        quit
    ],
    "./dev_tools_help.yaml"
)

running = True

while running:
    reader.prompt()
