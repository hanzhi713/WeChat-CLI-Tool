import itchat
from itchat.content import *
import os
import traceback
import re
from modules.__config__ import multi_process, terminal_QR

if multi_process:
    from multiprocessing import Process
else:
    from modules.__stoppable__ import Process

if __name__ == "__main__":

    # load modules in ./modules folder
    modules = dict()
    for file in os.listdir('./modules'):
        if file.find('__') > -1:
            continue

        if file.find('.py') > -1:
            module_name = file.split('.')[0]

            # import the main class
            mod = getattr(__import__('modules.' + module_name, fromlist=['*']), module_name)

            # create command key
            modules[mod.alias] = mod

    print(modules)

    # dictionaries which store user sessions objects (interaction) and processes (static call)
    session_objects = dict()
    session_processes = dict()


    @itchat.msg_register(TEXT)
    def msg_listener(msg):
        global session_objects, session_processes

        # when new commands are received
        cmd = msg['Text']
        from_user = msg['FromUserName']

        # get the user session
        current_process_info = session_processes.get(from_user)
        current_object = session_objects.get(from_user)

        if current_process_info is not None:
            if current_process_info[0].is_alive():
                if cmd == '/q':
                    current_process_info[0].terminate()
                    itchat.send_msg("{} is terminated".format(current_process_info[1]), from_user)
                    del session_processes[from_user]
                    return
                else:
                    itchat.send_msg("{} is running".format(current_process_info[1]), from_user)
                    return
            else:
                del session_processes[from_user]

        # if the previous session is not ended
        if current_object is not None:
            if current_object.finished:
                del session_objects[from_user]
            else:
                if current_object.msg_handler(msg):
                    del session_objects[from_user]
                return

        # if this is really a command
        if cmd[:1] == "/":

            if len(cmd) > 1:

                # parse the command and arguments
                cmd = re.split(" +", cmd[1:])
                if cmd[-1] == "":
                    del cmd[-1]

                if cmd[0] == 'help':
                    if len(cmd) > 1:
                        if cmd[1][0] == '/':
                            mod = modules.get(cmd[1][1:])
                        else:
                            mod = modules.get(cmd[1])
                        if mod is not None:
                            mod.help(from_user)
                        else:
                            itchat.send_msg(
                                "Non-existent command name " + cmd[1] + "\nType /help to see all available commands",
                                from_user)
                    else:
                        keys = list(modules.keys())
                        keys.sort()
                        for module_name in keys:
                            modules[module_name].help_brief(from_user)
                        itchat.send_msg("Type /help [command] to get detailed instructions on a specific command",
                                        from_user)

                elif cmd[0] in modules.keys():
                    if len(session_objects.keys()) + len(session_processes.keys()) > 10:
                        itchat.send_msg('Too many people sending commands. Please try again later.', from_user)
                        return

                    mod = modules[cmd[0]]

                    # interaction required -> create a new object to handle message
                    if mod.interactive:
                        try:
                            session_objects[from_user] = mod(from_user, mod.parse_args(from_user, cmd[1:]))
                            itchat.send_msg("Type /q to quit", from_user)
                        except Exception as e:
                            traceback.print_exc()
                            itchat.send_msg(str(e), from_user)

                    # no interaction -> static method call
                    else:

                        # fast_execution -> call in the main thread
                        if mod.fast_execution:
                            try:
                                mod.call(from_user, mod.parse_args(from_user, cmd[1:]))
                            except Exception as e:
                                traceback.print_exc()
                                itchat.send_msg(str(e), from_user)

                        # fast_execution -> create a new process
                        else:
                            try:
                                session_processes[from_user] = [
                                    Process(target=mod.call, args=(from_user, mod.parse_args(from_user, cmd[1:]),)),
                                    cmd[0]]
                                session_processes[from_user][0].start()
                                itchat.send_msg("Type /q to stop", from_user)
                            except Exception as e:
                                traceback.print_exc()
                                itchat.send_msg(str(e), from_user)

                else:
                    itchat.send_msg("\n".join(["Non-existent command {}".format("/" + cmd[0]),
                                               "Type /help to see all available commands",
                                               "Type /help [command] to get detailed instructions on a specific command"]),
                                    from_user)
            else:
                itchat.send_msg("\n".join(["Error: Empty command body.",
                                           "Type /help to see all available commands",
                                           "Type /help [command] to get detailed instructions on a specific command"]),
                                from_user)


    @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
    def file_listener(file):
        global session_objects
        from_user = file['FromUserName']
        if session_objects.get(from_user) is not None:
            if session_objects[from_user].file_handler(file):
                del session_objects[from_user]


    itchat.auto_login(hotReload=True, enableCmdQR=terminal_QR)
    itchat.run(True)
