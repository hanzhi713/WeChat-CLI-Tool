from .__templates__ import Static
import itchat
import itertools


class Calc24(Static):
    __author__ = "Hanzhi Zhou"
    alias = "calc24"
    parameters = "[n1] [n2] [n3] [n4]"
    title = "24 Point Calculation"
    description = "Find an arithmetic combination, if exists, of four integers that equals to 24"
    example = "Example: /calc24 2 4 6 8"
    fast_execution = True

    @staticmethod
    def eval_postfix(expr):
        token_list = expr
        stack = []
        for token in token_list:
            if token in "+-**/":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append(str(eval(o2 + token + o1)))
            else:
                stack.append(token)
        return float(stack.pop())

    @staticmethod
    def post_to_in(expr):
        token_list = expr
        stack = []
        for token in token_list:
            if token in "+-":
                o1 = stack.pop()
                o2 = stack.pop()
                stack.append("({} {} {})".format(o2, token, o1))
            elif token in "**/":
                o1 = stack.pop()
                o2 = stack.pop()
                if token == "*":
                    r = u" × "
                elif token == "/":
                    r = u" ÷ "
                else:
                    r = " ^ "
                stack.append(o2 + r + o1)
            else:
                stack.append(token)

        st = stack[0]
        # remove the outermost parentheses
        if st.startswith("(") and st.endswith(")"):
            st = st[1:len(st) - 1]
        return st

    @classmethod
    def parse_args(cls, from_user, args):
        assert len(args) >= 4, "4 positive integer parameters are required!"
        assert args[0].isdigit() and args[1].isdigit() and args[2].isdigit() and args[
            3].isdigit(), "4 positive integer parameters are required!"
        return args[0:4]

    @classmethod
    def call(cls, from_user, args):
        operands = ['+', '-', '*', '/']
        nums = args
        results = []
        for per in list(itertools.permutations(nums, 4)):
            print(per)
            for op in list(itertools.permutations(operands, 3)):
                expr = [per[0], per[1], op[0], per[2], op[1], per[3], op[2]]
                if cls.eval_postfix(expr) == 24:
                    results.append(cls.post_to_in(expr))
        if len(results) == 0:
            itchat.send_msg("No solution!", from_user)
        else:
            for result in results:
                itchat.send_msg(str(result), from_user)
