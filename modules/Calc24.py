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

    # maximum number of solutions to output
    num_solutions = 3

    @staticmethod
    def eval_postfix(expr):
        token_list = expr
        stack = []
        for token in token_list:
            if token in "+-**/":
                o1 = stack.pop()
                o2 = stack.pop()
                if token == "/":
                    if int(o2) // int(o1) != int(o2) / int(o1):
                        return False
                stack.append(str(int(eval(o2 + token + o1))))
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
        for per in itertools.permutations(nums, 4):
            for ops in itertools.combinations_with_replacement(operands, 3):
                for op in itertools.permutations(ops, 3):
                    expr = [per[0], per[1], op[0], per[2], op[1], per[3], op[2]]
                    if cls.eval_postfix(expr) == 24:
                        if expr not in results:
                            results.append(expr)
        if len(results) == 0:
            itchat.send_msg("No solution!", from_user)
        else:
            for result in results:
                if result[2] == "*" or result[2] == "+":
                    if result[2] == result[4] and result[4] == result[6]:
                        idx = 0
                        for per in itertools.permutations([result[0], result[1], result[3], result[5]]):
                            if idx == 0:
                                idx += 1
                                continue
                            try:
                                results.remove([per[0], per[1], result[2], per[2], result[4], per[3], result[6]])
                            except:
                                pass
                    elif result[2] == result[4]:
                        idx = 0
                        for per in itertools.permutations([result[0], result[1], result[3]]):
                            if idx == 0:
                                idx += 1
                                continue
                            try:
                                results.remove([per[0], per[1], result[2], per[2], result[4], result[5], result[6]])
                            except:
                                pass
                    else:
                        try:
                            results.remove(
                                [result[1], result[0], result[2], result[3], result[4], result[5], result[6]])
                        except:
                            pass

            if len(results) > cls.num_solutions:
                dist = len(results) // cls.num_solutions
                results = results[0], results[dist], results[-1]

            for result in results:
                itchat.send_msg(cls.post_to_in(result))
