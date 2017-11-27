from modules.__templates__ import Static
import itchat


class Calc24(Static):
    __author__ = "Fangchen Chen"
    alias = "calc24"
    parameters = "[n1] [n2] [n3] [n4]"
    title = "24 Point Calculation"
    description = "Find an arithmetic combination, if exists, of four integers that equals to 24"
    fast_execution = True

    @staticmethod
    def call(from_user, args):
        operands = ['+', '-', '*', '/']
        parentheses = ['(', ')']
        result_list = []
        try:
            a = int(args[0])
            b = int(args[1])
            c = int(args[2])
            d = int(args[3])
        except:
            itchat.send_msg("Illegal Arguments\n4 integer parameters are required", from_user)
            raise Exception
        num = [a, b, c, d]
        check = 0
        for x in range(0, 4):
            if check >= 10:
                break
            for y in range(0, 4):
                if check >= 10:
                    break
                if y == x:
                    continue
                for z in range(0, 4):
                    if check >= 10:
                        break
                    if z == x or z == y:
                        continue
                    for w in range(0, 4):
                        if check >= 10:
                            break
                        if w == x or w == y or w == z:
                            continue
                        for q in range(0, 4):
                            if check >= 10:
                                break
                            for p in range(0, 4):
                                if check >= 10:
                                    break
                                for r in range(0, 4):
                                    if check >= 10:
                                        break
                                    fn = num[x] + operands[q] + num[y] + operands[p] + num[z] + operands[r] + num[w]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                                    fn = parentheses[0] + num[x] + operands[q] + num[y] + parentheses[1] + operands[p] + \
                                         num[z] + operands[r] + num[w]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                                    fn = parentheses[0] + num[x] + operands[q] + num[y] + operands[p] + num[z] + \
                                         parentheses[1] + operands[r] + num[w]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                                    fn = parentheses[0] + num[x] + operands[q] + parentheses[0] + num[y] + operands[p] + \
                                         num[z] + parentheses[1] + parentheses[
                                             1] + operands[r] + num[w]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                                    fn = num[x] + operands[q] + parentheses[0] + num[y] + operands[p] + num[z] + \
                                         parentheses[1] + operands[r] + num[w]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                                    fn = parentheses[0] + num[x] + operands[q] + num[y] + parentheses[1] + operands[p] + \
                                         parentheses[0] + num[z] + operands[
                                             r] + num[w] + parentheses[1]
                                    try:
                                        result = eval(fn)
                                    except:
                                        result = 0
                                    if result == 24:
                                        result_list.append(fn)
                                        check += 1
                                        continue
                            r = 0
                        p = 0
                    q = 0
                w = 0
            z = 0
        y = 0
        if check == 0:
            result_list.append("No result")
        itchat.send_msg("".join(result_list), from_user)
