'''
Algoritmo de Conversión Directa
'''

import pydotplus

def create_dfa_graph(states, acceptance_states, transitions, start_state):
    # Convierte conjuntos a cadenas de texto
    states = [str(state) for state in states]
    start_state = str(start_state)
    acceptance_states = [str(state) for state in acceptance_states]

    # Crear una representación del DFA en formato DOT
    dot = pydotplus.Dot()
    dot.set_rankdir("LR")  # Utilizar 'TB' para un diseño de arriba hacia abajo
    dot.set_prog("neato")

    # Create nodes for each state
    state_nodes = {}
    num = 0
    for state in states:
        node = pydotplus.Node(state)
        if state == start_state:
            node.set_shape("circle")
            node.set_style("filled")

        if state in acceptance_states:
            node.set_shape("doublecircle")  # Final states are double circled
        node.set_fontsize(12)  # Set font size
        node.set_width(0.6)  # Set the desired width
        node.set_height(0.6)  # Set the desired height
        state_nodes[state] = node
        dot.add_node(node)

        num += 1

    # Agrega transiciones como arcos
    for (source, symbol, target) in transitions:
        if str(source) in state_nodes and str(target) in state_nodes:
            edge = pydotplus.Edge(state_nodes[str(source)], state_nodes[str(target)], label=symbol)
            dot.add_edge(edge)

    return dot


def set_estados(primer, elements, node_list, Dtran, Destados):

    element1_key = 0
    element1 = []

    for ele in elements:
        element1_key = ele
        element1 = node_list[ele]
        break

    list_elements = []
    list_elements.append(element1_key)
    for element in elements:
        element_value = node_list[element]
        if element1_key != element and element1[0] == element_value[0]:
            list_elements.append(element)

    new_state = set()
    for element in list_elements:
        new_state = new_state.union(node_list[element][1])
        elements.remove(element)

    if new_state != set():
        flag = False
        for estado in Destados:
            if new_state == estado[0]:
                flag = True
                break

        if flag == False:
            Destados.append([new_state, False])

    if element1[0] != '#' and element1[0] != '𝜀':
        Dtran.append((primer, element1[0], new_state))

    return elements, node_list, Dtran, Destados


def exec(stack_arbol, node_list, alfabeto, graph=False):
    Destados = []
    Dtran = []

    Destados.append([stack_arbol[len(stack_arbol) - 1].primerapos, False])

    flag = False
    while flag == False:
        for estado in Destados:
            if estado[1] == False:
                estado_actual = estado[0]
                estado[1] = True
                Destados[Destados.index(estado)] = estado
                flag = False
                break
            else:
                flag = True
        if flag == True:
            break

        temp_estado = estado_actual.copy()

        while temp_estado != set():
            temp_estado, node_list, Dtran, Destados = set_estados(estado_actual, temp_estado, node_list, Dtran, Destados)

    estados = []
    estado_final = []

    lastKey, lastValue = list(node_list.items())[-1]

    for estado in Destados:
        estados.append(estado[0])
        if lastKey in estado[0]:
            estado_final.append(estado[0])

    estado_inicial = Destados[0][0]

    if graph:
        pydotplus.find_graphviz()

        graph = create_dfa_graph(estados, estado_final, Dtran, estado_inicial)

        # Save or display the graph
        png_file_path = "result/directDFA.png"
        graph.write_png(png_file_path)  # Save PNG file

    return estados, alfabeto, Dtran, estado_inicial, estado_final
