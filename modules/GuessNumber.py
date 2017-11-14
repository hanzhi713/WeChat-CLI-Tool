import itchat
import random


class GuessNumber:
    __author__ = "Fangchen Chen"
    parameters = "[lower] [upper]"
    alias = "gn"
    interactive = True
    title = "Number Guessing Game"
    description = "Guess a number which the computer randomly generates in a give range"

    @staticmethod
    def help(from_user):
        my_class = GuessNumber
        itchat.send_msg("\n\t".join(["/{} {}".format(my_class.alias, my_class.parameters),
                                     "{} by {}".format(my_class.title, my_class.__author__),
                                     my_class.description]), from_user)

    def __init__(self, from_user, args):
        try:
            lower = int(args[0])
            upper = int(args[1])
            if upper <= lower:
                itchat.send_msg("Upper bound must be greater than the lower bound!".format(lower, upper), from_user)
                raise AssertionError
            self.number = random.randint(lower, upper + 1)
        except AssertionError:
            raise Exception
        except:
            itchat.send_msg("Illegal Arguments!\nTwo integer parameters are required: [lower] and [upper]", from_user)
            raise Exception

        self.trials = 0
        self.finished = False
        self.send_separator(from_user)
        itchat.send_msg("Guessing between {} and {}\nType /q to quit the game".format(lower, upper), from_user)

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

    def file_handler(self, file):
        return False

    def send_separator(self, dst):
        itchat.send_msg("-" * 30, dst)
