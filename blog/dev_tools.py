import app as a
import pycmd as pc


create_all_command = pc.Command(a.create_all)
delete_user_command = pc.Command(a.delete_user)
add_admin_command = pc.Command(a.add_admin)

reader = pc.CommandReader(
    [
        create_all_command,
        delete_user_command,
        add_admin_command
    ],
    "./dev_tools_help.yaml"
)

reader.prompt()
