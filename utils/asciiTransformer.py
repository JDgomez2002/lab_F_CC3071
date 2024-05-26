import sys

def ASCIITransformer(infix_regex):
    new_infix = []

    def handle_slash (infix_regex, i, new_infix):

        next = infix_regex[i+1]

        if next == 'n':
            new_infix.append(ord('\n'))
            i += 2
        elif next == 't':
            new_infix.append(ord('\t'))
            i += 2
        elif next == 's':
            new_infix.append(ord(' '))
            i += 2
        elif next == '\\':
            new_infix.append(ord('\\'))
            i += 2
        elif next == '\"':
            new_infix.append(ord('\"'))
            i += 2
        elif next == '\'':
            new_infix.append(ord('\''))
            i += 2
        else:
            print("Error léxico, operador no reconocido despues de slash: ", next)
            sys.exit()

        return infix_regex, i, new_infix
    

    def handle_comilla (infix_regex, i, new_infix):
        if i + 2 < len(infix_regex):
            next = infix_regex[i + 1]
            if i - 1 >= 0 and infix_regex[i - 1] == '\'' and infix_regex[i] == '\'' and next == '\'':
                print("Error léxico, no se puede tener dos comillas simples seguidas")
                sys.exit()
            elif next == '\'':
                new_infix.append('|')
                i += 1
            elif next == '\\':
                i += 1
                infix_regex, i, new_infix = handle_slash(infix_regex, i, new_infix)
            elif infix_regex[i + 2] == '\'':
                new_infix.append(ord(next))
                i += 3
                if i < len(infix_regex):
                    if infix_regex[i] == '\'' or infix_regex[i] == '\"':
                        new_infix.append('|')
            else:
                i += 1

        else:
            i += 1

        return infix_regex, i, new_infix
    

    def handle_double_comilla (infix_regex, i, new_infix):
        temp_regex = []
        j = i + 1

        if infix_regex[j] == '\"':
            print("Error léxico, no se puede tener dos comillas dobles seguidas")
            sys.exit()

        while j < len(infix_regex) and infix_regex[j] != '\"':
            temp_regex.append(infix_regex[j])
            j += 1

        h = 0
        while h < len(temp_regex):
            if temp_regex[h] == '\\':
                infix_regex, h, new_infix = handle_slash(temp_regex, h, new_infix)
                continue
            else:
                new_infix.append(ord(temp_regex[h]))
                h += 1
            
        if j + 1 < len(infix_regex) and (infix_regex[j + 1] == '\'' or infix_regex[j + 1] == '\"'):
            new_infix.append('|')

        i = j + 1

        return infix_regex, j + 1, new_infix
    
    def handle_double_comilla_brackets (infix_regex, i, new_infix):
        temp_regex = []

        if infix_regex[i + 1] == '\"':
            print("Error léxico, no se puede tener dos comillas seguidas")
            sys.exit()

        j = i + 1

        while j < len(infix_regex) and infix_regex[j] != '\"':
            temp_regex.append(infix_regex[j])
            j += 1

        h = 0
        while h < len(temp_regex):
            if temp_regex[h] == '\\':
                infix_regex, h, new_infix = handle_slash(temp_regex, h, new_infix)
            else:
                new_infix.append(ord(temp_regex[h]))
                h += 1
                
            if h < (len(temp_regex)):
                new_infix.append('|')

        i = j + 1

        return infix_regex, j + 1, new_infix
    

    def handle_brackets (infix_regex, i, new_infix):
        temp_regex = []
        new_infix.append('(')
        j = i + 1

        while j < len(infix_regex) and infix_regex[j] != ']':
            if infix_regex[j] == '[':
                print("Error léxico, no se puede no se cerro el corchete")
                sys.exit()
            temp_regex.append(infix_regex[j])
            j += 1

        l = 0
        while l < len(temp_regex):
            char = temp_regex[l]
            if char == '-':
                first = new_infix.pop()
                second = temp_regex[l+1]
                if second == '\'':
                    second = ord(temp_regex[l+2])
                    l += 1
                else:
                    second = ord(second)

                p = first
                for p in range(first, second + 1):
                    if p == second:
                        new_infix.append(p)
                        break
                    new_infix.append(p)
                    new_infix.append('|')
                    p += 1

                l += 2
                continue

            elif char == '\'':
                temp_regex, l, new_infix = handle_comilla(temp_regex, l, new_infix)
                continue

            elif char == '\\':
                temp_regex, l, new_infix = handle_slash(temp_regex, l, new_infix)
                continue

            elif char == '^':
                temp_regex, l, new_infix = handle_negate(temp_regex, l, new_infix)
                continue

            elif char == '\"':
                temp_regex, l, new_infix = handle_double_comilla_brackets(temp_regex, l, new_infix)
                continue
            else: 
                new_infix.append(ord(char))
                l += 1
        
        i = j + 1
        new_infix.append(')')
        return infix_regex, i, new_infix
    
    
    def handle_negate (infix_regex, i, new_infix):
        next = infix_regex[i+1]
        if next == '(':
            temp = []
            j = i + 2
            while j < len(infix_regex) and infix_regex[j] != ')':
                temp.append(infix_regex[j])
                j += 1
            i = j

            new_temp = []
            a = 0
            while a < len(temp):
                t = temp[a]
                if t == '\\':
                    temp, a, new_infix = handle_slash(temp, a, new_infix)
                    continue
                new_temp.append(ord(t))
                a += 1 

            j = 0
            for j in range(0, Universo + 1):
                if j == Universo and j not in new_temp:
                    new_infix.append(j)
                    break
                if j not in new_temp:
                    new_infix.append(j)
                    new_infix.append('|')
                j += 1
                
        elif next == '[':
            Set = []
            infix_regex, i, Set = handle_brackets(infix_regex, i, Set)

            Set = set(Set)

            Set.discard(')')
            Set.discard('(')
            Set.discard('|')

            j = 0
            for j in range(0, Universo + 1):
                if j == Universo and j not in Set:
                    new_infix.append(j)
                    break
                if j not in Set:
                    new_infix.append(j)
                    new_infix.append('|')
                j += 1
            

        else:
            next_ascii = ord(next)
            j = 0
            for j in range(0, Universo + 1):
                if j == Universo and j != next_ascii:
                    new_infix.append(j)
                    break
                if j != next_ascii:
                    new_infix.append(j)
                    new_infix.append('|')
                j += 1

        i += 2

        return infix_regex, i, new_infix
    

    def char_universe (infix_regex, i, new_infix):
        p = 0
        for p in range(0, Universo + 1):
            if p == Universo:
                new_infix.append(p)
                break
            new_infix.append(p)
            new_infix.append('|')
            p += 1

        i += 1

        return infix_regex, i, new_infix
    

    def char_arroba (infix_regex, i, new_infix):
        i += 1

        first_set = set()
        new_infix.pop()
        value_pop = ''
        while value_pop != '(':
            value_pop = new_infix.pop()
            if value_pop != '(' and value_pop != '|' and value_pop != ')':
                first_set.add(value_pop)

        second_set = []
        infix_regex, i, second_set = handle_brackets(infix_regex, i, second_set)

        second_set = set(second_set)

        second_set.discard(')')
        second_set.discard('(')
        second_set.discard('|')

        new_set = first_set.difference(second_set)

        new_infix.append('(')

        var = 0
        for varia in new_set:
            new_infix.append(varia)
            if var < (len(new_set) - 1):
                new_infix.append('|')
            var += 1

        new_infix.append(')')

        return infix_regex, i, new_infix
    

    def corchetes (infix_regex, i, new_infix):
        temp_regex = ''
        j = i + 1

        while j < len(infix_regex) and infix_regex[j] != '}':
            temp_regex += infix_regex[j]
            j += 1
        
        if temp_regex[0] == ' ':
            temp_regex = temp_regex[1:]
        if temp_regex[-1] == ' ':
            temp_regex = temp_regex[:-1]

        new_infix.append(temp_regex)
        
        i = j + 1

        return infix_regex, i, new_infix

    operadores = ['*', '+', '?', '|', '(', ')', '!']

    Universo = 255

    i = 0
    while i < len(infix_regex):
        char = infix_regex[i]

        if char in operadores:
            new_infix.append(char)
            i += 1
            continue

        elif char == '\\':
            infix_regex, i, new_infix = handle_slash(infix_regex, i, new_infix)
            continue
        
        elif char == '\'':
            infix_regex, i, new_infix = handle_comilla(infix_regex, i, new_infix)
            continue

        elif char == '[':
            infix_regex, i, new_infix = handle_brackets(infix_regex, i, new_infix)
            continue
        
        elif char == '^':
            infix_regex, i, new_infix = handle_negate(infix_regex, i, new_infix)
            continue

        elif char == '\"':
            infix_regex, i, new_infix = handle_double_comilla(infix_regex, i, new_infix)
            continue

        elif char == '_':
            infix_regex, i, new_infix = char_universe(infix_regex, i, new_infix)
            continue
        
        elif char == '#':
            infix_regex, i, new_infix = char_arroba(infix_regex, i, new_infix)
            continue
            
        elif char == '{':
            infix_regex, i, new_infix = corchetes(infix_regex, i, new_infix)
            continue
        else:
            print("Error léxico, operador no reconocido: ", char)
            sys.exit()             

    return new_infix