from modules.__templates__ import Static
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

    @staticmethod
    def call(from_user, args):
        operands = ['+', '-', '*', '/']
        try:
            nums = str(int(args[0])), str(int(args[1])), str(int(args[2])), str(int(args[3]))
        except:
            itchat.send_msg("Illegal Arguments\n4 integer parameters are required", from_user)
            raise Exception
        results = []
        for per in list(itertools.permutations(nums, 4)):
            print(per)
            for op in list(itertools.permutations(operands, 3)):
                expr = [per[0], per[1], op[0], per[2], op[1], per[3], op[2]]
                if Calc24.eval_postfix(expr) == 24:
                    results.append(Calc24.post_to_in(expr))
        if len(results) == 0:
            itchat.send_msg("No solution!", from_user)
        else:
            for result in results:
                itchat.send_msg(str(result), from_user)