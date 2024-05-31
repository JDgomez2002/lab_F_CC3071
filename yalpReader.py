import sys
import time
import pickle
import utils.shuntingYard as shun
import utils.tree as tree
import utils.asciiTransformer as ascii_reg
import utils.asciiMachine as ascii_machine
import automatons.directDFA as dfa_dir
import automatons.minDFA as dfa_min
import simulators.DFA as simAFD

def main(myFile):

    Machines = {
        "Comments": "\"/*\" *(^*)*\"*/\"",
        "Declaration": "%token ",
        "Token": "['a'-'z''A'-'Z''𝜀']['a'-'z''A'-'Z''|'' ''_''0'-'9''𝜀']*",
        "Ignore": "IGNORE ",
        "Productions": "%%",
        "Production": "['a'-'z''A'-'Z''0'-'9']+:",
        "Product": "['a'-'z''A'-'Z''|''\n'' ''0'-'9''𝜀']+;",
    }

    start_time = time.time()

    terminals, dictionary, productions, ignores = readYaparFile(Machines, myFile)

    # tokenCheck(terminals)

    print("\n==========================================================================")

    print("\nTokens: ", terminals)

    print("\n==========================================================================")

    print("\nDictionary: ")
    for key in dictionary:
        if key % 2 == 0:
            print(dictionary[key], end="-> ")
        else:
            print(dictionary[key])

    productions.insert(0,[productions[0][0]+"'", [productions[0][0]]])

    print("\n==========================================================================")

    print("\nProductions: ")
    for production in productions:
        print("\t" + production[0], "->", production[1])

    nonTerminals = []

    for produccion in productions:
        if produccion[0] not in nonTerminals:
            nonTerminals.append(produccion[0])
    
    items = []
    items.extend(nonTerminals)
    items.extend(terminals)

    produccionesCheck(items, productions)

    print("\n==========================================================================")
    print("\nIgnores: ", ignores, "\n")

    gramatica = {
        "terminals": terminals,
        "nonTerminals": nonTerminals,
        "productions": productions,
        "items": items,
        "ignores": ignores
    }

    with open('Grammar.pickle', 'wb') as f:
        pickle.dump(gramatica, f)

    end_time = time.time()

    time_taken = end_time - start_time

    print("==========================================================================")
    print(f"YalpReader execution time was {round(time_taken, 3)}s")
    print("==========================================================================\n")


def tokenCheck(tokens):
    MinDFA = {}

    with open("MinDFA.pickle", "rb") as f:
        MinDFA = pickle.load(f)

    for token in tokens:
        if token not in MinDFA["tokens"] and token != "𝜀":
            print("Lexical error, token not recognized ", token)
            sys.exit()


def produccionesCheck(items, producciones):
    for product in producciones:
        if product[0] not in items and product[0] != "𝜀":
            print("Lexical error, token not recognized ", product[0])
            sys.exit()
        for elem in product[1]:
            if elem not in items and elem != "𝜀":
                print("Lexical error, token not recognized ", elem)
                sys.exit()


def getYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def getMachine(regex, graph=False):
    ascii_regex = ascii_machine.ASCIITransformer(regex)
    postfix_regex = shun.exec(ascii_regex)
    # print("Postfix: ", postfix_regex)
    # print()
    stack, node_list, alfabeto = tree.exec(postfix_regex)
    estadoscon, alfabetocon, Dtran, estado_inicialcon, estado_finalcon = dfa_dir.exec(stack, node_list, alfabeto)
    estadosAFD = set()
    for i in estadoscon:
        estadosAFD.add(str(i))

    alfabetoAFD = set()
    for i in alfabetocon:
        alfabetoAFD.add(str(i))

    transicionesAFD = set()
    for tran in Dtran:
        trans = ()
        for t in tran:
            trans = trans + (str(t),)
        transicionesAFD.add(trans)

    estado_inicialAFD = {str(estado_inicialcon)}

    estados_aceptacionAFD = set()
    for i in estado_finalcon:
        estados_aceptacionAFD.add(str(i))

    new_states, symbol, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, graph=graph, check=False)
    return new_states, new_transitions, newStart_states, newFinal_states


def readYaparFile(Machines, myFile):
    ascii_comments = Machines['Comments']
    _, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)

    ascii_declaration = Machines['Declaration']
    _, declaration_transitions, declaration_inicial, declaration_final = getMachine(ascii_declaration)

    ascii_token = Machines['Token']
    _, token_transitions, token_inicial, token_final = getMachine(ascii_token)

    ascii_ignore = Machines['Ignore']
    _, ignore_transitions, ignore_inicial, ignore_final = getMachine(ascii_ignore)

    ascii_producciones = Machines['Productions']
    _, producciones_transitions, producciones_inicial, producciones_final = getMachine(ascii_producciones)

    ascii_produccion = Machines['Production']
    _, produccion_transitions, produccion_inicial, produccion_final = getMachine(ascii_produccion)

    ascii_producto = Machines['Product']
    _, producto_transitions, producto_inicial, producto_final = getMachine(ascii_producto)

    data = getYalexFile(myFile)

    i = 0
    dictionary = {}
    terminals = []
    producciones_temp = []
    producciones = []
    ignores = []
    contador = 0
    length_data = len(data)
    read_tokens = True
    
    while i < length_data:
        bol, num, simulationValues = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if bol:
            print("Comment: " + simulationValues)
            dictionary[contador] = simulationValues
            contador += 1
            i = num
            continue

        if read_tokens:

            bol, num, simulationValues = simAFD.exec(producciones_transitions, producciones_inicial, producciones_final, data, i)
            if bol:
                print("\nProductions: " + simulationValues)
                dictionary[contador] = simulationValues
                read_tokens = False
                contador += 1
                i = num
                continue

            bol, num, simulationValues = simAFD.exec(ignore_transitions, ignore_inicial, ignore_final, data, i)
            if bol:
                print("\nIgnore: " + simulationValues, end="-> ")
                dictionary[contador] = simulationValues
                contador += 1
                i = num

                while True:
                    bol, num, simulationValues = simAFD.exec(token_transitions, token_inicial, token_final, data, i)
                    if bol:
                        print(simulationValues)
                        dictionary[contador] = simulationValues
                        ignores.append(simulationValues)
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Lexical error in line: ", data[i])
                        sys.exit()
                continue


            bol, num, simulationValues = simAFD.exec(declaration_transitions, declaration_inicial, declaration_final, data, i)
            if bol:
                print(simulationValues, end="-> ")
                dictionary[contador] = simulationValues
                contador += 1
                i = num

                while True:
                    bol, num, simulationValues = simAFD.exec(token_transitions, token_inicial, token_final, data, i)
                    if bol:
                        print(simulationValues)
                        dictionary[contador] = simulationValues
                        listValues = simulationValues.split()
                        for item in listValues:
                            terminals.append(item)
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Lexical error in line: ",'i'+data[i]+'i')
                        sys.exit()
                continue

        
        if read_tokens == False:
            bol, num, simulationValues = simAFD.exec(produccion_transitions, produccion_inicial, produccion_final, data, i)
            if bol:
                print("\n" + simulationValues, end="")
                dictionary[contador] = simulationValues
                producciones_temp.append(simulationValues[:-1])
                contador += 1
                i = num

                while True:
                    bol, num, simulationValues = simAFD.exec(producto_transitions, producto_inicial, producto_final, data, i)
                    if bol:
                        print(simulationValues)
                        dictionary[contador] = simulationValues
                        pro = producciones_temp.pop()
                        listValues = simulationValues.split("|")
                        for item in listValues:
                            item = item.replace("\n", "")
                            item = item.strip()
                            if len(item) < 1:
                                continue
                            if item[-1] == ";":
                                item = item[:-1]
                            
                            item = item.split()
                            producciones.append([pro, item])
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Lexical error in line: ", data[i])
                        sys.exit()
                continue

        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
            i += 1
            continue

        else:
            print("Lexical error in line: ", data[i])
            sys.exit()

    if terminals == []:
        print("Lexical errors, token not found")
        sys.exit()

    return terminals, dictionary, producciones, ignores

if __name__ == "__main__":
    import sys
    main(sys.argv[1])