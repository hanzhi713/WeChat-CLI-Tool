import itchat


class ModuleBasics:
    """
        Inherit this class if the module requires the message handler to process proceeding user commands
    """

    # your name obviously
    __author__ = "Anonymous"

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
        The command name used to call this module, in this case is '/foo'
        Please remember to check clashes between aliases of different modules
    """
    alias = "foo"

    # description and detailed instructions on how to use this module
    description = ""

    # Give a fancy title to your module!
    title = "foobar"

    """
        print out the instructions of this command when /help or /help <alias> is invoked
        generally there's no need to modify this method (except for one line)
    """

    @classmethod
    def help(cls, from_user):
        """
            print out the instructions of this command when /help or /help <alias> is invoked
            generally there's no need to modify this method (except for one line)
        """
        itchat.send_msg("\n\t".join(["/{} {}".format(cls.alias, cls.parameters),
                                     "{} by {}".format(cls.title, cls.__author__),
                                     cls.description]), from_user)


class Interactive(ModuleBasics):

    interactive = True

    def __init__(self, from_user, args):
        """
            the constructor which accepts a list parameters from the command line
            e.g. when user called /foo 1 2 3, args = ['1', '2', '3']
        """

        # The finish flag for this session, which must set to True when session is finished
        self.finished = False

    def msg_handler(self, msg):
        """
        the message handler which accepts the itchat message object
        please return True if the session ends, otherwise return False
        This method must be non-blocking or only block for no more than 5s
        you must respond to /q command (force quit) in this method

        It is recommended that you only write code that handles interaction like itchat.send() here, 
        putting calculations, IO and other methods outside
        """
        return False

    def file_handler(self, file):
        """
            the file handler which accepts the itchat file object
            please return True if the session ends, otherwise return False
        """
        return False

    def send_separator(self, dst):
        """
        Send a dash line to inform user about the start / end of the session
        """
        itchat.send_msg("-" * 30, dst)

    """
        You may define other helper methods or classes as you wish
        After you've finished writing the module, please put your .py file inside the 'module' folder
    """


class Static(ModuleBasics):
    """
        Inherit this class if the module only needs a static method call
    """

    interactive = False

    """
        if your call() method will be completed within a second or is non-blocking, then set this to True
        this prevents executing call() in a separated process, 
        which means you don't need to execute itchat.auto_login(hotReload=True) that often takes a second to complete
    """
    fast_execution = False

    @staticmethod
    def call(from_user, args):
        """
            This method accepts the from_user, which is the WeChat user ID, and args,
            the list of arguments passed from the command line.
            This method can be blocking
        """

        # You must keep this line if fast_execution == False
        # You should remove this line if fast_execution == True
        itchat.auto_login(hotReload=True)

        """
            It is recommended that you only write code that call itchat.send() here.
            Calculations, IO and other methods shall be written in helper methods
        """

    """
        You may define other helper methods or classes as you wish
        After you've finished writing the module, please put your .py file inside the 'module' folder
    """
