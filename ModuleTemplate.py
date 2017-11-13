import itchat


# Important! There must be a class whose name is the same as that of the .py file!
class ModuleTemplate:

    # your name obviously
    __author__ = ""

    """
        description of parameters required
        recommended format:
        [required parameter]
        <optional parameter>
        
        2 choose 1 or 3 choose 1 or many choose one
        <a|b> <a|b|c> ...
    """
    parameters = ""

    """
        The command name used to call this module
        in this case is '/foo'
    """
    alias = "foo"

    # description and detailed instructions on how to use this module
    description = ""

    # Give a fancy title to your module!
    title = "foobar"

    """
        whether this module requires the message handler to process proceeding user commands
    """
    interactive = False

    """
        You don't need this parameter if interactive = True
        
        if your call() method will be completed within a second or is non-blocking, then set this to True
        this prevents executing call() in a separated process, which means you don't need to execute itchat.auto_login(hotReload=True)
    """
    fast_execution = False

    """
        print out the instructions of this command when /help or /help <alias> is invoked
        generally there's no need to modify this method (except for one line)
    """
    @staticmethod
    def help(from_user):

        # remember to change this line to your class
        my_class = ModuleTemplate
        itchat.send_msg("\n\t".join(["/{} {}".format(my_class.alias, my_class.parameters),
                                     "{} by {}".format(my_class.title, my_class.__author__),
                                     my_class.description]), from_user)

    """
        Please delete this method if interactive = False
        
        the constructor which accepts a list parameters from the command line
        e.g. when user called /foo 1 2 3, args = ['1', '2', '3']
    """
    def __init__(self, args):

        """
            The finish flag for this session
            Must set to True when session is finished
        """
        self.finished = False

        pass

    """
        Please delete this method if interactive = False
        
        This method must exist if interactive = True
        
        the message handler which accepts the itchat message object
        please return True if the session ends, otherwise return False
        This method must be non-blocking or only block for no more than 5s
        you must respond to /q command (force quit) in this method
    """
    def msg_handler(self, msg):
        pass

    """
        Please delete this method if interactive = False
        
        This method must exist if interactive = True
        
        the file handler which accepts the itchat file object
        please return True if the session ends, otherwise return False
    """
    def file_handler(self, file):
        pass

    """
        Please delete this method if interactive = True

        This method must exist if interactive = False
        
        This method accepts the from_user, which is the WeChat user ID, and args,
        the list of arguments passed from the command line.
        This method can be blocking
        """
    @staticmethod
    def call(from_user, args):

        # this line is extremely important since this method will be executed in a separated process
        itchat.auto_login(hotReload=True)

        pass

    """
        You may define other helper methods or classes as you wish
        After you've finished writing the module, please put your .py file inside the 'module' folder
    """