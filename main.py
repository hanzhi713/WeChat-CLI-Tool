import itchat
from itchat.content import *
import os, multiprocessing

if __name__ == "__main__":

    # load modules
    modules = dict()
    for file in os.listdir('./modules'):
        if file.find('.py') > -1:
            module_name = file.split('.')[0]
            mod = getattr(__import__('modules.' + module_name, fromlist=['*']), module_name)

            # create command key
            modules[mod.alias] = mod

    print(modules)

    # for interactive modules
    global_lock = None

    # for non-interactive modules
    current_process = None
    current_process_cmd = None

    @itchat.msg_register(TEXT)
    def msg_listener(msg):
        global global_lock, current_process, current_process_cmd

        if current_process is not None:
            if current_process.is_alive():
                if msg['Text'] == '/q':
                    current_process.terminate()
                    itchat.send_msg("{} is terminated".format(current_process_cmd), msg['FromUserName'])
                    current_process = None
                    current_process_cmd = None
                    return
                else:
                    itchat.send_msg("{} is running".format(current_process_cmd), msg['FromUserName'])
                    return
            else:
                current_process = None
                current_process_cmd = None

        if global_lock is not None and global_lock.finished:
            global_lock = None

        # if previous interaction is not ended
        if global_lock is not None:
            if global_lock.msg_handler(msg):
                global_lock = None

        # when new commands are received
        else:
            cmd = msg['Text']
            from_user = msg['FromUserName']

            # if this is really a command
            if cmd[:1] == "/":
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
                            global_lock = mod(from_user, cmd[1:])
                        except:
                            pass
                            # itchat.send_msg("Error when executing {}".format("/" + cmd[0]))

                    # no interaction -> static method call
                    else:
                        if mod.fast_execution:
                            try:
                                mod.call(from_user, cmd[1:])
                            except:
                                pass
                                # itchat.send_msg("Error when executing {}".format("/" + cmd[0]))
                        else:
                            current_process = multiprocessing.Process(target=mod.call, args=(from_user, cmd[1:],))
                            current_process.start()
                            current_process_cmd = cmd[0]

                else:
                    itchat.send_msg("\n".join(["Non-existent command {}".format("/" + cmd[0]),
                                               "Type /help to see all available commands",
                                               "Type /help [command] to get instructions on a specific command"]),
                                    from_user)


    @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
    def file_listener(file):
        global global_lock
        if global_lock is not None:
            if global_lock.file_handler(file):
                global_lock = None


    itchat.auto_login(hotReload=True)
    itchat.run(True)
