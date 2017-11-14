import itchat
from itchat.content import *
import os
import multiprocessing

if __name__ == "__main__":

    # load modules
    modules = dict()
    for file in os.listdir('./modules'):
        if file.find('.py') > -1:
            module_name = file.split('.')[0]

            # import the main class
            mod = getattr(__import__('modules.' + module_name, fromlist=['*']), module_name)

            # create command key
            modules[mod.alias] = mod

    print(modules)

    session_objects = dict()
    session_processes = dict()

    @itchat.msg_register(TEXT)
    def msg_listener(msg):
        global session_objects, session_processes

        # when new commands are received
        cmd = msg['Text']
        from_user = msg['FromUserName']

        current_process_info = session_processes.get(from_user, None)
        current_object = session_objects.get(from_user, None)

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

        # if previous interaction is not ended
        if current_object is not None:
            if current_object.finished:
                del session_objects[from_user]
                return
            else:
                if current_object.msg_handler(msg):
                    del session_objects[from_user]

        # if this is really a command
        if cmd[:1] == "/":

            # parse command and arguments
            cmd = cmd[1:].split(' ')
            if cmd[0] == 'help':
                try:
                    modules[cmd[1]].help(from_user)
                except:
                    keys = list(modules.keys())
                    keys.sort()
                    for module_name in keys:
                        modules[module_name].help(from_user)

            elif cmd[0] in modules.keys():
                mod = modules[cmd[0]]

                # interaction required -> create new object to handle message
                if mod.interactive:
                    try:
                        session_objects[from_user] = mod(from_user, cmd[1:])
                    except:
                        pass
                        # itchat.send_msg("Error when executing {}".format("/" + cmd[0]))

                # no interaction -> static method call
                else:

                    # fast_execution -> call in main process
                    if mod.fast_execution:
                        try:
                            mod.call(from_user, cmd[1:])
                        except:
                            pass
                            # itchat.send_msg("Error when executing {}".format("/" + cmd[0]))

                    # fast_execution -> create a new process
                    else:
                        session_processes[from_user] = [multiprocessing.Process(target=mod.call, args=(from_user, cmd[1:],)), cmd[0]]
                        session_processes[from_user][0].start()

            else:
                itchat.send_msg("\n".join(["Non-existent command {}".format("/" + cmd[0]),
                                           "Type /help to see all available commands",
                                           "Type /help [command] to get instructions on a specific command"]),
                                from_user)


    @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
    def file_listener(file):
        global session_objects
        from_user = file['FromUserName']
        if session_objects[from_user] is not None:
            if session_objects[from_user].file_handler(file):
                del session_objects[from_user]


    itchat.auto_login(hotReload=True)
    itchat.run(True)
