import app as a
import pycmd as pc

reader = pc.CommandReader(
    [
        a.create_all,
        a.delete_user,
        a.add_admin
    ],
    "./dev_tools_help.yaml"
)

reader.prompt()
