import sys
import pickle
import time
import utils.shuntingYard as shun
import utils.tree as tree
import utils.asciiTransformer as ascii_reg
import utils.asciiMachine as ascii_machine
import automatons.directDFA as dfa_dir
import automatons.minDFA as dfa_min
import simulators.DFA as simAFD

import sys
import time
import pickle

symbolsDict = {
    "!": "exclamation_mark",
    "@": "at_sign",
    "#": "hash",
    "$": "dollar",
    "%": "percent",
    "^": "caret",
    "&": "ampersand",
    "*": "asterisk",
    "(": "open_parenthesis",
    ")": "close_parenthesis",
    "-": "minus",
    "_": "underscore",
    "=": "equals",
    "+": "plus",
    "[": "open_bracket",
    "]": "close_bracket",
    "{": "open_brace",
    "}": "close_brace",
    ";": "semicolon",
    ":": "colon",
    ",": "comma",
    ".": "dot",
    "<": "less_than",
    ">": "greater_than",
    "/": "slash",
    "?": "question_mark",
    "|": "vertical_bar",
    "\\": "backslash",
    "`": "grave_accent",
    "~": "tilde",
    "\"": "double_quote",
    "'": "single_quote"
}


def main(myFile):

    file = myFile
    Machines = {
        "Comments": "\"(*\" *[' '-'&''+'-'}''a''e''i''o''u''ñ''\n''\t']* *\"*)\"",
        "Header": "{ *(^})*}",
        "Declaration": "let +['a'-'z''_']* +=",
        "Variables": "('['(^])*]|^[ \n]*)+",
        "Rules": "rule *tokens *=",
        "Tokens1": "['&'-'}']+",
        "Tokens2": "'|' *['\"'-'}']*",
        "Returns": "{ *(^})*}",
        "Trailer": "{ *(_)*",
    }

    start_time = time.time()

    values, tokens, tokens_dictionary, dictionary = readYalexFile(Machines, file)

    print("==========================================================================")
    print("Values: ")
    for val in values:
        print("  " + val, ": ", values[val])
    print("\n==========================================================================")
    print("Tokens: ", end=" ")
    for token in tokens:
        print(token, end=" ")
    print("\n==========================================================================")
    print("\n")
    for dic in tokens_dictionary:
        print(dic, ": ", tokens_dictionary[dic])

    toekns = tokens_dictionary.copy()

    values = setValues(values)

    print()
    print("==========================================================================")
    print("Rules:\n")
    for lal in values:
        print(lal, ": ", values[lal])
    print("==========================================================================")

    imports = """
import simulators.Scanner as simSCAN
import pickle
import time
import sys
"""

    scanner = """
def readYalexFile(file):
    with open(file, 'r') as file:
        script = file.read()
    return script


def getGrammar():
    Grammar = {}
    with open("Grammar.pickle", "rb") as f:
        Grammar = pickle.load(f)
    return Grammar


def main(arg=None):
    input = "input.txt"
    result = readYalexFile(input)

    MinDFA = {}
    with open("MinDFA.pickle", "rb") as f:
        MinDFA = pickle.load(f)

    grammar = getGrammar()
        
    start_time = time.time()

    tokens = readString(result, MinDFA, grammar)

    grammar["tokens"] = tokens

    with open("Grammar.pickle", "wb") as f:
        pickle.dump(grammar, f)

    end_time = time.time()

    time_taken = end_time - start_time

    print(f"\\nScan.py executed in {round(time_taken, 3)}s")

    pass


def readString(data, MinDFA, grammar):
    i = 0
    counter = 0
    tokens = []

    lengthData = len(data)

    while i < lengthData:
        print("\\ni: " + str(i))
        num, values, temp, error = simSCAN.exec(MinDFA["transitions"], MinDFA["start_states"], MinDFA["returns"], data, i)
        if error:
            print(f"Value unrecognized: '{temp}'")
            i += 1
            print("m: " + str(i))
            continue
        token = ""
        for key in MinDFA["new_returns"]:
            if values in MinDFA["new_returns"][key]:
                token = key
                break
        if grammar["ignores"] != []:        
            if len(grammar["ignores"]) == 1 and token != grammar["ignores"][0]:
                tokens.append(token)
            elif len(grammar["ignores"]) > 1 and token not in grammar["ignores"]:
                tokens.append(token)
        else:
            tokens.append(token)

        print("m: " + str(num))
        print("Value: " + temp)
        print("Token: " + token)
        print("Command: " + values)
        print("Execution: ")
        try:
            exec(values)
        except:
            print("Error in command execution")
        counter += 1
        i = num
        continue
    
    print(tokens)
        
    return tokens

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)

"""

    with open('scan.py', 'w') as f:
        f.write(imports)
        if 'Header' in dictionary:
            f.write(dictionary['Header'][1:-1])
        for value in tokens_dictionary:
            write_value, function = defString(value, tokens_dictionary[value][2:-2])
            tokens_dictionary[value] = f"{{ {function} }}"
            f.write(write_value)

        f.write(scanner)
        if 'Trailer' in dictionary:
            f.write(dictionary['Trailer'][1:-1])

    print("\nScan.py created with this functions:\n")

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in values:
            tokens[i] = values[tokens[i]]
        if tok in tokens_dictionary:
                tokens[i] += tokens_dictionary[tok]
        i += 1

    superRegex = ''.join(str(i) for i in tokens)

    superAscii = ascii_reg.ASCIITransformer(superRegex)

    for tok in tokens_dictionary:
        print(tok, ": ", tokens_dictionary[tok])    

    superPostfix = shun.exec(superAscii)
    stack, node_list, treeAlphabet = tree.exec(superPostfix)


    states, alphabet, Dtran, initState, finalState = dfa_dir.exec(stack, node_list, treeAlphabet)
    # print("Direct DFA created!")

    DFAStates = set()
    for i in states:
        DFAStates.add(str(i))

    DFAAlphabet = set()
    for i in alphabet:
        DFAAlphabet.add(str(i))

    DFATransitions = set()
    for tran in Dtran:
        trans = ()
        for t in tran:
            trans = trans + (str(t),)
        DFATransitions.add(trans)

    DFAInitState = {str(initState)}

    DFAAcceptedStates = set()
    for i in finalState:
        DFAAcceptedStates.add(str(i))

    new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(DFAStates, DFAAlphabet, DFATransitions, DFAInitState, DFAAcceptedStates, False, True)

    # print("Min DFA created!")

    newReturns = tokens_dictionary.copy()
    for ret in newReturns:
        if ret[0] == '"' and ret[-1] == '"':
            new_string = ret.replace('"', '')
            tokens_dictionary[new_string] = tokens_dictionary.pop(ret)[2:-2]
        else:
            tokens_dictionary.pop(ret)

    MinDFA = {
        "states": new_states,
        "transitions": new_transitions,
        "symbols": symbols,
        "start_states": newStart_states,
        "final_states": newFinal_states,
        "returns": tokens_dictionary,
        "new_returns": newReturns,
        "tokens": toekns
    }

    with open('MinDFA.pickle', 'wb') as f:
        pickle.dump(MinDFA, f)

    # print("\nMin DFA saved in MinDFA.pickle\n")

    end_time = time.time()

    time_taken = end_time - start_time

    print("\n==========================================================================")
    print(f"YalexReader execution time was {round(time_taken, 3)}s")
    print("==========================================================================\n")

    pass


def defString(name, value):
    name = name.replace('"', '')
    name = name.replace('\'', '')
    if len(name) == 1:
        if name in symbolsDict:
            name = symbolsDict[name]
            return f"\ndef {name}():\n\t{value}\n", f"{name}()"
        return f"\ndef n{ord(name)}():\n\t{value}\n", f"n{ord(name)}()"

    return f"\ndef {name.upper()}():\n\t{value}\n", f"{name.upper()}()"



def getYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def getMachine(regex, graph=False):
    ascii_regex = ascii_machine.ASCIITransformer(regex)
    postfix_regex = shun.exec(ascii_regex)
    stack, node_list, treeAlphabet = tree.exec(postfix_regex)
    states, alphabet, Dtran, initState, finalState = dfa_dir.exec(stack, node_list, treeAlphabet)
    DFAStates = set()
    for i in states:
        DFAStates.add(str(i))

    DFAAlphabet = set()
    for i in alphabet:
        DFAAlphabet.add(str(i))

    DFATransitions = set()
    for tran in Dtran:
        trans = ()
        for t in tran:
            trans = trans + (str(t),)
        DFATransitions.add(trans)

    DFAInitState = {str(initState)}

    DFAAcceptedStates = set()
    for i in finalState:
        DFAAcceptedStates.add(str(i))

    new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(DFAStates, DFAAlphabet, DFATransitions, DFAInitState, DFAAcceptedStates, graph=graph, check=False)
    return new_states, new_transitions, newStart_states, newFinal_states


def setValues(values):
    for val in values:
        value = values[val]

        if 'let ' in value:
            print("Lexical error, bracket not closed. ", value.split()[0])
            sys.exit()

        for valo in reversed(values):
            first = value.find(valo)
            last = 0
            if first != -1:
                last = first + len(valo)

            if first != -1:
                if first - 1 >= 0 and value[first - 1] == '\'' and last < len(value) and value[last] == '\'':
                    continue
                new_string = value[:first] + values[valo] + value[last:]
                value = new_string
                values[val] = new_string

            while first != -1:

                first = value.find(valo)
                if first != -1:
                    last = first + len(valo)

                if first != -1:
                    if first - 1 >= 0 and value[first - 1] == '\'' and last < len(value) and value[last] == '\'':
                        continue
                    new_string = value[:first] + values[valo] + value[last:]
                    value = new_string
                    values[val] = new_string
    
    return values


def readYalexFile(Machines, file):
    ascii_comments = Machines['Comments']
    comments_states, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)
    # print('comments DFA created')

    ascii_headers = Machines['Header']
    headers_states, headers_transitions, headers_inicial, headers_final = getMachine(ascii_headers)
    # print('Header DFA created')

    ascii_declaration = Machines['Declaration']
    declaration_states, declaration_transitions, declaration_inicial, declaration_final = getMachine(ascii_declaration)
    # print("Declaration DFA created")

    ascii_variables = Machines['Variables']
    variables_states, variables_transitions, variables_inicial, variables_final = getMachine(ascii_variables)
    # print("Variables DFA created")

    ascii_rules = Machines['Rules']
    rules_states, rules_transitions, rules_inicial, rules_final = getMachine(ascii_rules)
    # print("Rules DFA created")

    ascii_tokens1 = Machines['Tokens1']
    tokens1_states, tokens1_transitions, tokens1_inicial, tokens1_final = getMachine(ascii_tokens1)
    # print("Tokens DFA created")

    ascii_tokens2 = Machines['Tokens2']
    tokens2_states, tokens2_transitions, tokens2_inicial, tokens2_final = getMachine(ascii_tokens2)
    # print("Special Tokens DFA created")

    ascii_returns = Machines['Returns']
    returns_states, returns_transitions, returns_inicial, returns_final = getMachine(ascii_returns)
    # print("Returns DFA created")

    ascii_trailer = Machines['Trailer']
    trailer_states, trailer_transitions, trailer_inicial, trailer_final = getMachine(ascii_trailer)
    # print("Trailer DFA created")
    # print("\n")

    data = getYalexFile(file)

    i = 0
    dictionary = {}
    variables = []
    values = {}
    tokens = []
    temp_tokens = []
    tokens_dictionary = {}
    counter = 0
    length_data = len(data)
    read_tokens = False
    header_bool = False
    token1_bool = False
    numToken = 1
    
    while i < length_data:
        bol, num, simulationValues = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if bol:
            print("Comment: " + simulationValues)
            dictionary[counter] = simulationValues
            counter += 1
            i = num
            continue

        if header_bool == False:
            bol, num, simulationValues = simAFD.exec(headers_transitions, headers_inicial, headers_final, data, i)
            if bol and header_bool == False:
                # print("Header: '" + simulationValues +"'")
                dictionary['Header'] = simulationValues
                counter += 1
                i = num
                header_bool = True

                if "let " in simulationValues:
                    print("Lexical error, not closed bracket in header")
                    sys.exit()
                continue

        bol, num, simulationValues = simAFD.exec(rules_transitions, rules_inicial, rules_final, data, i)
        if bol:
            # print("Rules: " + simulationValues)
            dictionary[counter] = simulationValues
            counter += 1
            read_tokens = True
            i = num
            if variables != []:
                print("Lexical error, id without definition")
                print(variables)
                print(values)
                sys.exit()
            continue

        if read_tokens == False:
            bol, num, simulationValues = simAFD.exec(declaration_transitions, declaration_inicial, declaration_final, data, i)
            if bol:
                # print("Declaration: " + simulationValues)
                dictionary[counter] = simulationValues
                listValues = simulationValues.split()
                variables.append(listValues[1])
                counter += 1
                i = num
                continue

            bol, num, simulationValues = simAFD.exec(variables_transitions, variables_inicial, variables_final, data, i)
            if bol:
                # print("Variables: " + simulationValues)
                dictionary[counter] = simulationValues
                if variables != [] and len(variables) < 2:
                    values[variables.pop()] = simulationValues
                else:
                    print("Lexical error, id without definition")
                    print("Simulation values: ", simulationValues)
                    print(variables)
                    print(values)
                    sys.exit()
                counter += 1
                i = num
                continue
        
        bol, num, simulationValues = simAFD.exec(trailer_transitions, trailer_inicial, trailer_final, data, i)
        if bol:
            # print("Trailer: '" + simulationValues + "'")
            dictionary['Trailer'] = simulationValues
            counter += 1
            i = num

            if '}' not in simulationValues[-3:]:
                print("Lexical error, bracket not closed in trailer")
                sys.exit()

            continue

        if read_tokens:

            bol, num, simulationValues = simAFD.exec(tokens2_transitions, tokens2_inicial, tokens2_final, data, i)
            if bol:
                # print("Token: " + simulationValues)
                dictionary[counter] = simulationValues
                listValues = simulationValues.split()

                if listValues[1] in values:
                    newToken = listValues[1]
                else:
                    newToken = 'Token'+str(numToken)
                    values[newToken] = listValues[1]
                    numToken += 1
                # print("ListValues: ", listValues)
                if tokens == []:
                    tokens.append(newToken)
                else:
                    tokens.append(listValues[0])
                    tokens.append(newToken)
                temp_tokens.append(newToken)
                counter += 1
                i = num

                while True:
                    bol, num, simulationValues = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
                    if bol:
                        # print("Return: " + simulationValues)
                        dictionary[counter] = simulationValues
                        if temp_tokens != []:
                            tokens_dictionary[temp_tokens.pop()] = simulationValues
                        else:
                            print("Lexical error, no token for the next return")
                            sys.exit()
                        counter += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        break
                continue

            if token1_bool == False:
                bol, num, simulationValues = simAFD.exec(tokens1_transitions, tokens1_inicial, tokens1_final, data, i)
                if bol:
                    print("Token: " + simulationValues)
                    dictionary[counter] = simulationValues
                    print("Values: ")
                    for val in simulationValues:
                        print(val)

                    if simulationValues in values:
                        newToken = simulationValues
                    else:
                        newToken = 'Token'+str(numToken)
                        values[newToken] = simulationValues
                        numToken += 1
                    
                    tokens.append(newToken)
                    temp_tokens.append(newToken)
                    counter += 1
                    i = num
                    token1_bool = True
                    
                    while True:
                        bol, num, simulationValues = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
                        if bol:
                            print("Return: " + simulationValues)
                            dictionary[counter] = simulationValues
                            if temp_tokens != []:
                                tokens_dictionary[temp_tokens.pop()] = simulationValues
                            else:
                                print("Lexical error, no token for the next return")
                                sys.exit()
                            counter += 1
                            i = num
                            break

                        if data[i] == ' ' or data[i] == '\t':
                            i += 1
                            continue

                        else:
                            break
                    continue

        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
            i += 1
            continue

        else:
            print("Lexical error in line: ", data[i])
            sys.exit()

    if tokens == []:
        print("Lexical error, no tokens found")
        sys.exit()

    if temp_tokens != []:
        for tok in temp_tokens:
            tokens_dictionary[tok] = "{ print() }"
    

    return values, tokens, tokens_dictionary, dictionary

if __name__ == "__main__":
    import sys
    main(sys.argv[1])