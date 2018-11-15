from .__templates__ import Static
import itchat
from math import *


class RPN(Static):
    one_param_func = ["sin", "cos", "tan", "atan", "acos", "asin", "floor", "ceil", "factorial", "radians", "degrees",
                      "sinh", "cosh", "tanh", "acosh", "asinh", "atanh", "round"]

    two_param_func = ["log", "pow", "atan2", "gcd"]

    __author__ = "Hanzhi Zhou"
    title = "Reverse Polish Notation (RPN) Calculator"
    description = "\n".join(["Evaluate a postfix expression or convert it to infix expression",
                             "which returns 1.0-2.0", "Supported function: ", " ".join(one_param_func)], " ".join(two_param_func))
    parameters = "<eval|conv> [expression]"
    alias = "rpn"
    fast_execution = True

    example = "Example:\n/rpn conv 1 2 -\n/rpn eval 1 2 * sin",

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
                stack.append(float(token))
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
                stack.append(float(token))
        st = ''
        for i in stack:
            st += str(i) + ' '

        # remove the outermost parentheses, if they exist
        if st.startswith("(") and st.endswith(")"):
            st = st[1:len(st) - 1]
        return st

    @classmethod
    def parse_args(cls, from_user, args):
        assert len(args) >= 2, "Two parameters are required: <eval|conv> and [expression]"
        assert args[0] == "eval" or args[0] == "conv", "Must be either \"eval\" or \"conv\""
        return args

    @classmethod
    def call(cls, from_user, args):
        expression = args[1:]
        if args[0] == "eval":
            try:
                itchat.send_msg(cls.eval_postfix(expression), from_user)
            except Exception as e:
                print(e)
                raise SyntaxError('Unable to evaluate {}, probably due to a syntax error.'.format(" ".join(expression)))
        else:
            try:
                itchat.send_msg(cls.post_to_in(expression), from_user)
            except Exception as e:
                print(e)
                raise SyntaxError('Unable to convert {}, probably due to a syntax error.'.format(" ".join(expression)))
