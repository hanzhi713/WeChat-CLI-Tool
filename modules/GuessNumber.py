from .__templates__ import Interactive
import itchat
import random


class GuessNumber(Interactive):
    __author__ = "Fangchen Chen"
    parameters = "[lower] [upper]"
    alias = "gn"
    title = "Number Guessing Game"
    description = "Guess a number which the computer randomly generates in a give range"
    example = "Example: /gn 20 30"

    @classmethod
    def parse_args(cls, from_user, args):
        assert len(args) >= 2, "Two positive integer parameters are required: [lower] and [upper]"
        assert args[0].isdigit(), "Two positive integer parameters are required: [lower] and [upper]"
        assert args[1].isdigit(), "Two positive integer parameters are required: [lower] and [upper]"
        lower = int(args[0])
        upper = int(args[1])
        assert lower < upper, "Upper bound must be greater than the lower bound!"
        return lower, upper

    def __init__(self, from_user, args):
        super(self.__class__, self).__init__(from_user, args)
        lower, upper = args
        self.number = random.randint(lower, upper)
        self.trials = 0
        self.send_separator(from_user)
        itchat.send_msg("Guessing between {} and {}".format(lower, upper), from_user)

    def msg_handler(self, msg):
        from_user = msg['FromUserName']
        if msg['Text'] == '/q':
            itchat.send_msg("Quitting the game", from_user)
            self.finished = True
            self.send_separator(from_user)
            return True

        try:
            guess = int(msg['Text'])
        except:
            itchat.send_msg("Illegal Input!", from_user)
            return False

        if guess < self.number:
            self.trials += 1
            itchat.send_msg("Too Small. Try again.", from_user)
            return False
        elif guess > self.number:
            self.trials += 1
            itchat.send_msg("Too Big. Try again.", from_user)
            return False
        else:
            self.trials += 1
            itchat.send_msg("Bingo! You have got it in {} trials!".format(self.trials), from_user)
            self.send_separator(from_user)
            self.finished = True
            return True
