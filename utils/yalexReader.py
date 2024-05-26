import sys
import pickle
import time
import utils.shuntingYard as shuntingYard
import utils.tree as tree
import utils.asciiTransformer as asciiTransformer
import utils.asciiMachine as asciiMachine
import automatons.directDFA as directDFA
import automatons.minDFA as minDFA
import simulators.DFA as DFASimulator

symbols = {
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
    "-": "hyphen",
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

def defString(name, value):
    name = name.replace('"', '')
    name = name.replace('\'', '')
    if len(name) == 1:
        if name in symbols:
            name = symbols[name]
            return f"def {name}():\n\t{value}\n\n", f"{name}()"
        return f"def n{ord(name)}():\n\t{value}\n\n", f"n{ord(name)}()"

    return f"def {name}():\n\t{value}\n\n", f"{name}()"

def readYalex(file):
    with open(file, 'r') as file:
        data = file.read()
    return data

def createDFA(regex, graph=False):
    asciiRegex = asciiMachine.ASCIITransformer(regex)
    postfixAscii = shuntingYard.exec(asciiRegex)
    stack, nodes, alphabet = tree.exec(postfixAscii)
    dfaStates, dfaAlphabet, dfaTransitions, dfaInitStates, finalDfaStates = directDFA.exec(stack, nodes, alphabet)
    dfaStatesSet = set()
    for i in dfaStates:
        dfaStatesSet.add(str(i))

    newDfaAlphabet = set()
    for i in dfaAlphabet:
        newDfaAlphabet.add(str(i))

    dfaTransitionsSet = set()
    for tran in dfaTransitions:
        trans = ()
        for t in tran:
            trans = trans + (str(t),)
        dfaTransitionsSet.add(trans)

    initDfaState = {str(dfaInitStates)}

    finalDfaStatesSet = set()
    for i in finalDfaStates:
        finalDfaStatesSet.add(str(i))

    newStates, symbols, newTransitions, newInitStates, newFinalStates = minDFA.exec(dfaStatesSet, newDfaAlphabet, dfaTransitionsSet, initDfaState, finalDfaStatesSet, graph=graph, check=False)
    return newStates, newTransitions, newInitStates, newFinalStates


def setValues(values):
    for val in values:
        value = values[val]

        if 'let ' in value:
            print("Error léxico, no se cerro el corchete ", value.split()[0])
            sys.exit()

        for subValue in reversed(values):
            first = value.find(subValue)
            last = 0
            if first != -1:
                last = first + len(subValue)

            if first != -1:
                if first - 1 >= 0 and value[first - 1] == '\'' and last < len(value) and value[last] == '\'':
                    continue
                newValue = value[:first] + values[subValue] + value[last:]
                value = newValue
                values[val] = newValue

            while first != -1:

                first = value.find(subValue)
                if first != -1:
                    last = first + len(subValue)

                if first != -1:
                    if first - 1 >= 0 and value[first - 1] == '\'' and last < len(value) and value[last] == '\'':
                        continue
                    newValue = value[:first] + values[subValue] + value[last:]
                    value = newValue
                    values[val] = newValue
    
    return values


def readYalexFile(file, regexs=None):

    regexs = {
        "Comments": "\"(*\" (^*)* *\"*)\"",
        "Header": "{ *(^})*}",
        "Declaration": "let +['a'-'z']* +=",
        "Variables": "('['(^])*]|^[ \n]*)+",
        "Rules": "rule *tokens *=",
        "InitialToken": "['&'-'}']+",
        "Tokens": "'|' *['\"'-'}']*",
        "Returns": "{ *(^})*}",
        "Trailer": "{ *(_)*",
    }

    # print("\n#########################################################################################")
    # print("####################################### DFAs ############################################")
    # print("#########################################################################################\n")

    commentsRegex = regexs['Comments']
    commentsStates, commentsTransitions, initCommentsStates, finalCommentsStates = createDFA(commentsRegex)
    # print("Comments DFA done")

    headersRegex = regexs['Header']
    headerStates, headersTransitions, initialHeadersStates, finalHeadersStates = createDFA(headersRegex)
    # print("Headers DFA done")

    declarationRegex = regexs['Declaration']
    declarationStates, declarationTransitions, initDeclarationStates, finalDeclarationStates = createDFA(declarationRegex)
    # print("Declaration DFA done")

    variablesRegex = regexs['Variables']
    variablesStates, variablesTransitions, initVariablesStates, finalVariablesStates = createDFA(variablesRegex)
    # print("Variables DFA done")

    rulesRegex = regexs['Rules']
    rulesStates, rulesTransitions, initRulesStates, finalRulesStates = createDFA(rulesRegex)
    # print("Rules DFA done")

    initToken = regexs['InitialToken']
    initTokenStates, initTokenTransitions, initInitTokenStates, finalInitTokenStates = createDFA(initToken)
    # print("1st Token DFA done (without '|')")

    tokensRegex = regexs['Tokens']
    tokensStates, tokensTransitions, initTokensStates, finalTokensStates = createDFA(tokensRegex)
    # print("Tokens DFA done")

    returnsRegex = regexs['Returns']
    returnsStates, returnsTransitions, initReturnsStates, finalReturnsStates = createDFA(returnsRegex)
    # print("Returns DFA done")

    trailerRegex = regexs['Trailer']
    trailerStates, trailerTransitions, initTrailerStates, finalTrailerStates = createDFA(trailerRegex)
    # print("Trailer DFA done\n")

    data = readYalex(file)
    i = 0
    dict = {}
    variables = []
    values = {}
    tokens = []
    tempTokens = []
    dictTokens = {}
    counter = 0
    dataLength = len(data)
    readTokens = False
    headerBooleans = False
    tokenBooleans = False

    # print("\n#########################################################################################")
    # print("#################################### YalexReader ########################################")
    # print("#########################################################################################\n")

    while i < dataLength:
        bol, num, newValues = DFASimulator.exec(commentsTransitions, initCommentsStates, finalCommentsStates, data, i)
        if bol:
            # print("\nComment: " + newValues)
            dict[counter] = newValues
            counter += 1
            i = num
            continue

        if headerBooleans == False:
            bol, num, newValues = DFASimulator.exec(headersTransitions, initialHeadersStates, finalHeadersStates, data, i)
            if bol and headerBooleans == False:
                # print("\nHeader: " + newValues)
                dict['Header'] = newValues
                counter += 1
                i = num
                headerBooleans = True
                continue

        bol, num, newValues = DFASimulator.exec(rulesTransitions, initRulesStates, finalRulesStates, data, i)
        if bol:
            # print("\nRules: " + newValues)
            dict[counter] = newValues
            counter += 1
            readTokens = True
            i = num
            if variables != []:
                print("Lexical error, id without definition")
                print(variables)
                print(values)
                sys.exit()
            continue

        if readTokens == False:
            bol, num, newValues = DFASimulator.exec(declarationTransitions, initDeclarationStates, finalDeclarationStates, data, i)
            if bol:
                # print("\nDeclaration: " + newValues)
                dict[counter] = newValues
                listValues = newValues.split()
                variables.append(listValues[1])
                counter += 1
                i = num
                continue

            bol, num, newValues = DFASimulator.exec(variablesTransitions, initVariablesStates, finalVariablesStates, data, i)
            if bol:
                # print("Value: " + newValues)
                dict[counter] = newValues
                if variables != [] and len(variables) < 2:
                    values[variables.pop()] = newValues
                else:
                    print("Lexical error, id without definition")
                    print("values: ", newValues)
                    print(variables)
                    print(values)
                    sys.exit()
                tempTokens.append(newValues)
                counter += 1
                i = num
                continue
        
        bol, num, newValues = DFASimulator.exec(trailerTransitions, initTrailerStates, finalTrailerStates, data, i)
        if bol:
            # print("\nTrailer: " + newValues)
            dict['Trailer'] = newValues
            counter += 1
            i = num
            continue

        if readTokens:

            bol, num, newValues = DFASimulator.exec(tokensTransitions, initTokensStates, finalTokensStates, data, i)
            if bol:
                # print("\nToken: " + newValues)
                dict[counter] = newValues
                listValues = newValues.split()
                tokens.append(listValues[0])
                tokens.append(listValues[1])
                tempTokens.append(listValues[1])
                counter += 1
                i = num

                while True:
                    bol, num, newValues = DFASimulator.exec(returnsTransitions, initReturnsStates, finalReturnsStates, data, i)
                    if bol:
                        # print("\nReturn: " + newValues)
                        dict[counter] = newValues
                        if tempTokens != []:
                            dictTokens[tempTokens.pop()] = newValues
                        else:
                            print("Lexical error, no token for next return")
                            sys.exit()
                        counter += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Lexical error in line: ", data[i])
                        sys.exit()
                continue

            if tokenBooleans == False:
                bol, num, newValues = DFASimulator.exec(initTokenTransitions, initInitTokenStates, finalInitTokenStates, data, i)
                if bol:
                    # print("\nToken: " + newValues)
                    dict[counter] = newValues
                    tokens.append(newValues)
                    tempTokens.append(newValues)
                    counter += 1
                    i = num
                    tokenBooleans = True
                    
                    while True:
                        bol, num, newValues = DFASimulator.exec(returnsTransitions, initReturnsStates, finalReturnsStates, data, i)
                        if bol:
                            # print("Return: " + newValues)
                            dict[counter] = newValues
                            if tempTokens != []:
                                dictTokens[tempTokens.pop()] = newValues
                            else:
                                print("Lexical error, no token for next return")
                                sys.exit()
                            counter += 1
                            i = num
                            break

                        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
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

    return values, tokens, dictTokens, dict

