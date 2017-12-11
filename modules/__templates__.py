import itchat


class ModuleBasics:
    # your name
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

    # Give an example of using your module
    example = ""

    @classmethod
    def help(cls, from_user):
        """
            print the instructions of this command when /help [alias] is invoked
            generally there's no need to override this method
        """
        ins = ["/{} {}".format(cls.alias, cls.parameters),
               "{} by {}".format(cls.title, cls.__author__)]
        if cls.description != "":
            ins.append(cls.description)
        if cls.example != "":
            ins.append(cls.example)
        itchat.send_msg("\n\t".join(ins), from_user)

    @classmethod
    def help_brief(cls, from_user):
        """
            print a brief info about this module when /help is invoked
            generally there's no need to override this method
        """
        itchat.send_msg("/{} {}".format(cls.alias, cls.parameters), from_user)


class Interactive(ModuleBasics):
    """
        Inherit this class if the module requires the message handler to process proceeding user commands
    """

    interactive = True

    @classmethod
    def parse_args(cls, from_user, args):
        return args

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
        This method must be non-blocking or only block for no more than a few seconds
        you must respond to /q command (force quit) in this method

        It is recommended that you only write code that handles interaction like itchat.send() here, 
        putting calculations, IO and other procedures in helper methods
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
        Send a dash line to inform user about the start or the end of the session
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
        this prevents executing call() in a separated process by main.py, 
        which means you don't need to execute itchat.auto_login(hotReload=True) that often takes a second to complete
    """
    fast_execution = False

    @classmethod
    def parse_args(cls, from_user, args):
        return args

    @classmethod
    def call(cls, from_user, args):
        """
            This method accepts the from_user, which is the WeChat user ID, and args,
            the list of arguments passed from the command line.
            If this method is blocking, you should set fast_execution = False, otherwise set that to True
            
            Remember to put the following line of code if fast_execution = False, otherwise you won't be able to send messages
            itchat.auto_login(hotReload=True)
            
            It is recommended that you only write code that calls itchat.send() here.
            Calculations, IO and other methods should be written in helper methods
        """

    """
        You may define other helper methods or classes as you wish
        After you've finished writing the module, please put your .py file inside the 'module' folder
    """
