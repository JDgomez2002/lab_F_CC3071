def getPrecedence(ope):
    precedencia = {'(': 1, '|': 2, '.': 3, '+': 4, '?': 4, '*': 4} # 40 = '(', 124 = '|', 45 = '-', 46 = '.', 43 = '+', 63 = '?', 42 = '*'
    if ope not in precedencia:
        return 5
    return precedencia[ope]

def formatear_regex(regex):
    all_operators = ['|', '+', '?', '*']
    binary_operators = ['|']
    res = []

    for i in range(len(regex)):
        c1 = regex[i]

        if i + 1 < len(regex):
            
            c2 = regex[i + 1]

            res.append(c1)

            if c1 != '(' and c2 != ')' and c2 not in all_operators and c1 not in binary_operators:
                res.append('.')
    
    res.append(regex[-1])

    return res

def infix_to_postfix(regex):
    stack = []
    postfix = []
    regexp = formatear_regex(regex)

    i = 0
    while i < len(regexp):
        c = regexp[i]
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        elif c == '\\':
            postfix.append(c)
            postfix.append(regexp[i + 1])
            i += 2
            continue
        else:
            while len(stack) > 0:
                peekedChar = stack[-1]
                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(c)

                if peekedCharPrecedence >= currentCharPrecedence:
                    postfix.append(stack.pop())
                else:
                    break

            stack.append(c)
        i += 1

    while len(stack) > 0:
        postfix.append(stack.pop())
    return postfix

def exec(expression):
    postfix = infix_to_postfix(expression)
    return postfix