import pickle
import pydotplus
import time
import sys
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

import pickle
import pydotplus
import time
import sys

from tabulate import tabulate

Grammar = {}
with open("Grammar.pickle", "rb") as f:
    Grammar = pickle.load(f)

terminals = Grammar['terminals']
nonTerminals = Grammar['nonTerminals']
productions = Grammar['productions']
items = Grammar['items']
automatonStates = {}
automatonTransitions = []
count = 0
State = "I0"
usedStates = []
Firsts = {}
Follows = {}

def main(args=None):
    start_time = time.time()
    print()
    terminals.append("$")

    first = [productions[0][0], productions[0][1].copy()]
    first[1].insert(0, ".")

    G = []
    G = closure([first])
    prod = [stat for stat in G if stat != first]
    automatonStates["I"+str(count)] = {"nucleous": [first], "productions": prod}
    C = [G]

    added = True
    while added == True:
        added = False
        for it in C:
            I = []
            for item in it:
                newItem = [item[0], item[1].copy()]
                I.append(newItem)
            for gram in items:
                go = goto(I, gram)
                if go != [] and go not in C:
                    added = True
                    C.append(go)

    final = [productions[0][0], productions[0][1].copy()]
    final[1].append(".")

    Firsts = firstFunction(productions, terminals, nonTerminals).copy()

    # print("Firsts: ")
    # for f in Firsts:
    #     print(f+":", Firsts[f])


    followFunction(productions, terminals, nonTerminals, Firsts)

    # print("Follows: ")
    # for f in Follows:
    #     print(f+":", Follows[f])

    for state in automatonStates:
        core = automatonStates[state]['nucleous']
        if final in core:
            automatonTransitions.append([state, "$", "accept"])
            break


    Action, Goto = tableConstructor(Follows, terminals)

    print_table(Action, Goto, terminals, nonTerminals)

    print("\n==========================================================================")    
    print("Simulation\n")

    pydotplus.find_graphviz()

    graph = graph_automaton()

    # Save or display the graph
    png_file_path = "result/automaton.png"
    graph.write_png(png_file_path)  # Save PNG file

    simulate_parsing(Action, Goto, Grammar['tokens'])

    end_time = time.time()

    time_taken = end_time - start_time

    print("\n==========================================================================")    
    print(f"Simulation executed in {round(time_taken, 3)}s")
    print("==========================================================================\n")    


def closure(I):
    J = []
    J.extend(I)
    global productions, nonTerminals
    added = True
    while added == True:
        added = False
        for item in J:
            if "." in item[1] and item[1].index('.') != len(item[1])-1:
                nextItem = item[1][item[1].index('.')+1]
                if nextItem in nonTerminals:
                    for production in productions:
                        if production[0] == nextItem:
                            pro = [production[0], production[1].copy()]
                            pro[1].insert(0, ".")
                            if pro not in J:
                                J.append(pro)
                                added = True
    return J    


def goto(I, X):
    A = []
    lista = []
    lenI = len(I)
    for item in I:
        if "." in item[1] and item[1].index('.') != len(item[1])-1:
            if item[1][item[1].index('.')+1] == X:
                for key in automatonStates:
                    tempState = automatonStates[key]

                    if item in tempState['nucleous'] and [item[0], item[1].copy(), key] not in usedStates:
                        currentState = key
                        break
                    
                    if item in tempState['productions'] and [item[0], item[1].copy(), key] not in usedStates:
                        currentState = key
                        break

                try:
                    type(currentState)
                except:
                    break

                used = [item[0], item[1].copy(), currentState]
                usedStates.append(used)
                newItem = [item[0], item[1].copy()]
                index = newItem[1].index('.')
                newItem[1][index] = newItem[1][index+1]
                newItem[1][index+1] = '.'
                temp = closure([newItem])
                for stat in temp:
                    if stat != newItem and stat not in A:
                        A.append(stat)
                addAutomaton(newItem, A, X, currentState, lenI)
                newList = []
                if A == []:
                    newList = [newItem + A]
                else:
                    newList = [newItem] + A
                for li in newList:
                    if li not in lista:
                        lista.append(li)

    return lista


def addAutomaton(nucleous, product, X, currentState, lenI):
    global count, automatonStates, State
    alreadyExists = False
    nextState = ""

    for key in automatonTransitions:
        if currentState == key[0] and X == key[1]:
            alreadyExists = True
            nextState = key[2]
            break

    if alreadyExists == False:
        for key in automatonStates:
            tempState = automatonStates[key]
            # if nucleous == tempState['nucleous'][0] and len(tempState['nucleous']) == 1:
            if nucleous == tempState['nucleous'][0]:
                alreadyExists = True
                nextState = key
                break

    if alreadyExists == False:
        count += 1
        automatonStates["I"+str(count)] = {"nucleous": [nucleous], "productions": product}

        automatonTransitions.append([currentState, X, "I"+str(count)])
        State = "I"+str(count)

    else:
        if nucleous not in automatonStates[nextState]['nucleous']:
            automatonStates[nextState]['nucleous'].append(nucleous)

        add = False
        for tran in automatonTransitions:
            if currentState == tran[0] and X == tran[1]:
                add = True
                break

        if add == False:
            automatonTransitions.append([currentState, X, nextState])


def firstFunction(grammar, terminals, non_terminals):
    firsts = {}

    for non_terminal in non_terminals:
        firsts[non_terminal] = first(grammar, terminals, non_terminals, non_terminal)

    return firsts
    

def first(grammar, terminals, non_terminals, symbol):    
    first_set = set()

    if symbol in terminals:
        first_set.add(symbol)

    elif symbol in non_terminals:
        for simbolo, production in productions:
            if simbolo != symbol:
                continue

            if production == '𝜀':
                first_set.add('𝜀')
            else:
                for s in production:
                    
                    # ==================================================
                    if s == symbol:
                        continue
                    # ==================================================

                    s_first = first(grammar, terminals, non_terminals, s)

                    if '𝜀' not in s_first:
                        first_set = first_set.union(s_first)
                        break

                    s_first.remove('𝜀')

                    first_set = first_set.union(s_first)
                else:
                    first_set.add('𝜀')

    return first_set


def followFunction(grammar, terminals, non_terminals, firstsList):
    for non_terminal in nonTerminals:
        Follows[non_terminal] = follow(grammar, terminals, non_terminals, non_terminal, firstsList)


def follow(grammar, terminals, non_terminals, symbol, firstsList):
    follow_set = set()

    if symbol == productions[0][0]:
        follow_set.add('$')

    for simbolo, prod in productions:
        if symbol in prod:
            position = prod.index(symbol)
            if position != len(prod) - 1:
                next_symbol = prod[position + 1]
                if next_symbol in terminals:
                    follow_set.add(next_symbol)
                else:
                    follow_set = follow_set.union(firstsList[next_symbol])

                if next_symbol not in terminals and '𝜀' in firstsList[next_symbol]:
                    follow_set.remove('𝜀')
                    tempSet = Follows[simbolo]
                    follow_set = follow_set.union(tempSet)

            elif position == len(prod) - 1:
                if simbolo != symbol:
                    follow_set = follow_set.union(follow(grammar, terminals, non_terminals, simbolo, firstsList))
    
    return follow_set


def tableConstructor(followsList, terminals):
    Action = {}
    Goto = {}

    for states in automatonStates:
        allTransitions = []
        tempTransitions = list(automatonStates[states].values())
        for i in tempTransitions:
            if len(i) == 1:
                allTransitions.append(i[0])
            else:
                for j in i:
                    allTransitions.append(j)

        for nucleous in allTransitions:
            if '.' in nucleous[1] and nucleous[1].index('.') < len(nucleous[1])-1:
                nextSymbol = nucleous[1][nucleous[1].index('.')+1]
                if nextSymbol in terminals:
                    nextState = ""
                    for tran in automatonTransitions:
                        if states == tran[0] and nextSymbol == tran[1]:
                            nextState = tran[2]

                            if (states, nextSymbol) in Action and "S"+nextState[1:] != Action[(states, nextSymbol)]:
                                print("\n==========================================================================")
                                if "S" in Action[(states, nextSymbol)]:
                                    print("=== Shift-Reduce Error ===")
                                    print("In: ",'State: '+states, ' -> ',nextSymbol)
                                    print("Current action: ", Action[(states, nextSymbol)])
                                    print("New action: ", "S"+str(nextState[1:]))
                                    print("- Simulation terminated!")
                                    sys.exit()
                                else:
                                    print("=== Shift-Reduce Error ===")
                                    print("In: ",'State: '+states, ' -> ',nextSymbol)
                                    print("Current action: ", Action[(states, nextSymbol)])
                                    print("Nueva Acción: ", "S"+str(nextState[1:]))
                                    print("- Simulation terminated!")
                                    sys.exit()
                            else:
                                Action[(states, nextSymbol)] = "S"+nextState[1:]

            elif nucleous[1].index('.') == len(nucleous[1])-1 and nucleous[0] != productions[0][0]:
                beforeState = 0
                result = nucleous[1].copy()
                result.remove('.')
                for num, prod in enumerate(productions):
                    if prod[0] == nucleous[0] and prod[1] == result:
                        beforeState = num
                        break
                for ite in followsList[nucleous[0]]:
                    if (states, ite) in Action and "R"+str(beforeState) != Action[(states, ite)]:
                        print("\n==========================================================================")
                        if "S" in Action[(states, ite)]:
                            print("=== Shift-Reduce Error ===")
                            print("In: ",'State: '+states, ' -> ',ite)
                            print("Current action: ", Action[(states, ite)])
                            print("New action: ", "R"+str(nextState[1:]))
                            print("- Simulation terminated!")
                            sys.exit()
                        else:
                            print("=== Reduce-Reduce Error ===")
                            print("In: ",'State: '+states, ' -> ',ite)
                            print("Current action: ", Action[(states, ite)])
                            print("New action: ", "R"+str(nextState[1:]))
                            print("- Simulation terminated!")
                            sys.exit()
                    else:
                        Action[(states, ite)] = "R"+str(beforeState)

            
            elif nucleous[1].index('.') == len(nucleous[1])-1 and nucleous[0] == productions[0][0]:
                Action[(states, '$')] = "accept"
        
        for tran in automatonTransitions:
            if tran[1] not in terminals and tran[1] != '$':
                Goto[(tran[0], tran[1])] = tran[2][1:]

    return Action, Goto


def print_table(action, goto, terminals, non_terminals):
    header = ["State"] + terminals + non_terminals

    states = set(state for state, _ in action.keys()).union(set(state for state, _ in goto.keys()))

    rows = []
    for state in sorted(states, key=lambda state: int(state[1:])):
        row = [state]
        for terminal in terminals:
            row.append(action.get((state, terminal), ""))
        for non_terminal in non_terminals:
            row.append(goto.get((state, non_terminal), ""))
        rows.append(row)

    table = tabulate(rows, headers=header, tablefmt="pretty")
    # print(table)

    # Convert the table to a dataframe for easier manipulation
    df = pd.DataFrame(rows, columns=header)

    # Plot the table
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # Save the table as a PNG file
    plt.savefig("result/table.png", bbox_inches='tight', dpi=300)
    plt.close()


def simulate_parsing(action, goto, input_string):
    stack = [0]

    input_string.append('$')

    symbols = []

    while True:
        state = stack[-1]

        symbol = input_string[0]

        if ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)][0] == "S":

            print("=== SHIFT ===")
            print("Stack:", stack, "  \nState:", state, "  \nSymbols:", symbols, "  \nShift:", action[('I'+str(state), symbol)], "  \nInput:", input_string, end="\n\n")

            stack.append(action[('I'+str(state), symbol)][1:])

            symbols.append(input_string.pop(0))

        elif ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)][0] == "R":

            nucleous, product = productions[int(action[('I'+str(state), symbol)][1:])]

            print("=== REDUCE ===")
            print("Stack:", stack, "  \nState:", state, "  \nSymbols:", symbols, "  \nReduce:", action[('I'+str(state), symbol)], "  \nProductions:", nucleous + " \u2192 " + ' '.join(product), "  \nInput", input_string, end="\n\n")

            if len(product) == 1 and len(symbols) > 1:
                symbols.insert(symbols.index(product[0]), nucleous)
                symbols.remove(product[0])
                stack.pop()
            elif len(product) == 1 and len(symbols) == 1 and symbols == product:
                symbols.clear()
                symbols.append(nucleous)
                stack.pop()
            elif len(product) > 1 and symbols == product:
                symbols.clear()
                symbols.append(nucleous)
                for i in range (0,len(product)):
                    stack.pop()

            stack.append(goto[('I'+str(stack[-1]), nucleous)])

        elif ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)] == "accept":
            print("==========================================================================")
            print("\nInput accepted")
            return

        else:
            print("==========================================================================")
            print("\nInput not accepted")
            print("Error in state:", 'I'+str(state), ", with:", symbol, end="\n\n")
            return


def is_sublist(larger, smaller):
    smaller_length = len(smaller)
    for i in range(len(larger)):
        if larger[i:i+smaller_length] == smaller:
            return True
    return False


def graph_automaton():

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("TB")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    state_nodes = {}
    num = 0
    for state in automatonStates:
        allStringNucleo = ""
        for n in automatonStates[state]['nucleous']:
            allStringNucleo += n[0] + " \u2192 " + ' '.join(n[1]) + "\n"

        allStringNucleo = allStringNucleo.replace('\n', '<BR/>')
        
        if automatonStates[state]['productions'] != []:
            allStringProduct = ""
            for p in automatonStates[state]['productions']:
                allStringProduct += p[0] + " \u2192 " + ' '.join(p[1]) + "\n"
        
            allStringProduct = allStringProduct.replace('\n', '<BR/>')
        
            node_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR><TD>{state}</TD></TR>        
    <TR><TD>{allStringNucleo}</TD></TR>
    <TR><TD BGCOLOR="lightgrey">{allStringProduct}</TD></TR>
    </TABLE>>'''
        
        else:
            node_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR><TD>{state}</TD></TR>        
    <TR><TD>{allStringNucleo}</TD></TR>
    </TABLE>>'''

        node = pydotplus.Node(state, label=node_label, shape="none")    
        state_nodes[state] = node
        dot.add_node(node)

        num += 1

    # Add transitions as edges
    for (source, symbol, target) in automatonTransitions:
        if str(source) in state_nodes and str(target) == "accept":
            edge = pydotplus.Edge(state_nodes[str(source)], str(target), label=symbol)
            dot.add_edge(edge)
        elif (str(source) in state_nodes and str(target) in state_nodes):
            edge = pydotplus.Edge(state_nodes[str(source)], state_nodes[str(target)], label=symbol)
            dot.add_edge(edge)

    return dot

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
