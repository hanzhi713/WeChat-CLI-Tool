from modules.__templates__ import Static
import itchat
from math import *


class RPN(Static):
    __author__ = "Hanzhi Zhou"
    title = "Reverse Polish Notation (RPN) Calculator"
    description = "\n".join(["Evaluate a postfix expression or convert it to infix expression",
                             "which returns 1.0-2.0"])
    parameters = "<eval|conv> [expression]"
    alias = "rpn"
    fast_execution = True

    example = "Example: /rpn conv 1 2 -",

    one_param_func = ["sin", "cos", "tan", "atan", "acos", "asin", "floor", "ceil", "factorial"
    , "radians", "degrees", "sinh", "cosh", "tanh", "acosh", "asinh", "atanh"]

    two_param_func = ["round", "log", "pow", "atan2", "gcd"]

    @staticmethod
    def eval_postfix(expr):
        token_list = expr
        stack = []
        for token in token_list:
            if token == "" or token == " ":
                continue
            if token in "+-*/":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(eval("o2" + token + "o1"))
            elif token in RPN.one_param_func:
                stack.append(eval(token + "(stack.pop())"))
            elif token in RPN.two_param_func:
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(eval(token + "(o2, o1)"))
            elif token == "^":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(o2 ** o1)
            else:
                try:
                    stack.append(float(token))
                except:
                    continue
        return stack.pop()

    @staticmethod
    def post_to_in(expr):
        token_list = expr
        stack = []
        for token in token_list:
            if token == "" or token == " ":
                continue
            if token in "+-":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append("(" + str(o2) + token + str(o1) + ")")
            elif token in "*/^":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(str(o2) + token + str(o1))
            elif token in RPN.one_param_func:
                stack.append(token + "(" + str(stack.pop()) + ")")
            elif token in RPN.two_param_func:
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(token + "(" + str(o2) + "," + str(o1) + ")")
            else:
                try:
                    stack.append(float(token))
                except:
                    continue
        st = ''
        for i in stack:
            st += str(i) + ' '

        # remove the outermost parentheses
        if st.startswith("(") and st.endswith(")"):
            st = st[1:len(st) - 1]
        return st

    @staticmethod
    def call(from_user, args):
        try:
            expression = args[1:]
            if args[0] == "eval":
                try:
                    itchat.send_msg(RPN.eval_postfix(expression), from_user)
                except:
                    raise SyntaxError
            elif args[0] == "conv":
                try:
                    itchat.send_msg(RPN.post_to_in(expression), from_user)
                except:
                    raise SyntaxError
            else:
                itchat.send_msg("Must be either \"eval\" or \"conv\"", from_user)
                raise AssertionError
        except SyntaxError:
            itchat.send_msg("Improper postfix expression!", from_user)
            raise Exception
        except:
            itchat.send_msg("Illegal Arguments!", from_user)
            raise Exception