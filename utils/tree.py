import pydotplus

class Node:
    def __init__(self, value, id):
        self.value = value
        self.id = id
        self.number = None
        self.nullable = False
        self.primerapos = set()
        self.ultimapos = set()
        self.siguientepos = set()
        self.padre = None
        self.left = None
        self.right = None

    def id_return(self):
        return self.id

def tree_graph(stack):

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("TB")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    # Create nodes for each state
    state_nodes = {}
    num = 0
    for nodo in stack:
        node = pydotplus.Node(num)
        if type(nodo.value) == int:
            if nodo.value == 32:
                label = 'Space'
            elif nodo.value == 9:
                label = 'Tab'
            elif nodo.value == 10:
                label = 'Newline'
            elif nodo.value == 44:
                label = 'Comma'
            elif nodo.value == 92:
                label = 'Backslash'
            elif nodo.value == 39:
                label = 'Single Quote'
            elif nodo.value == 34:
                label = 'Double Quote'
            else:
                if nodo.value > 32 and nodo.value < 127:
                    label = chr(nodo.value)
                else:
                    label = str(nodo.value)
        else:
            label = str(nodo.value)
            
        node.set_label(label)
            
        # node.set_label(nodo.value) 
        node.set_fontsize(12)  # Set font size
        node.set_width(0.6)  # Set the desired width
        node.set_height(0.6)  # Set the desired height
        state_nodes[nodo.id] = node
        dot.add_node(node)

        num += 1

    # Add transitions as edges
    for nodo in stack:
        if nodo.padre != None:
            edge = pydotplus.Edge(state_nodes[nodo.padre], state_nodes[nodo.id])
            dot.add_edge(edge)

    return dot


def search_node(stack, id):
    for i in range(len(stack)):
        item = stack[i]
        if item.id == id:
            return item
    return None

def search_node_by_number(stack, number):
    for i in range(len(stack)):
        item = stack[i]
        if item.number == number:
            return item
    return None

def siguiente_pos(stack, node_list, pos, primerapos):
    pos_node = search_node_by_number(stack, pos)
    pos_node.siguientepos = pos_node.siguientepos.union(primerapos)
    node_list[pos_node.number] = [pos_node.value, pos_node.siguientepos]
    index = stack.index(pos_node)
    stack[index] = pos_node
    return stack, node_list

def or_operation(stack, temp_stack, contador_simbolos, left_node, right_node):
    or_node = Node('|', contador_simbolos)
    left_node.padre = or_node.id
    or_node.left = left_node.id
    stack.append(left_node)
    right_node.padre = or_node.id
    or_node.right = right_node.id
    stack.append(right_node)
    temp_stack.append(or_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos

def kleene_operation(stack, temp_stack, contador_simbolos, left_node):
    kleene_node = Node('*', contador_simbolos)
    left_node.padre = kleene_node.id
    kleene_node.left = left_node.id
    kleene_node.nullable = True
    stack.append(left_node)
    temp_stack.append(kleene_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos

def concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node):
    concat_node = Node('.', contador_simbolos)
    left_node.padre = concat_node.id
    concat_node.left = left_node.id
    stack.append(left_node)
    right_node.padre = concat_node.id
    concat_node.right = right_node.id
    stack.append(right_node)
    temp_stack.append(concat_node)
    contador_simbolos += 1
    return stack, temp_stack, contador_simbolos

def operando_operation(temp_stack, alfabeto, simbolo, contador_simbolos, contador_leafs):
    if simbolo not in alfabeto and simbolo != '𝜀' and simbolo != '#':
        alfabeto.append(simbolo)

    leaf_node = Node(simbolo, contador_simbolos)
    if simbolo == '𝜀':
        leaf_node.nullable = True
    leaf_node.number = contador_leafs
    leaf_node.primerapos.add(contador_leafs)
    leaf_node.ultimapos.add(contador_leafs)
    temp_stack.append(leaf_node)
    contador_simbolos += 1
    contador_leafs += 1
    return temp_stack, alfabeto, contador_simbolos, contador_leafs


def exec(postfix, graph_this = False):
    postfix.append('#')
    postfix.append('.')
    stack = []
    temp_stack = []
    alfabeto = []

    contador_simbolos = 0
    contador = 0
    contador_leafs = 1

    while contador < len(postfix):
        simbolo = postfix[contador]
        if simbolo == '|':
            right_node = temp_stack.pop()
            if len(temp_stack) > 0:
                left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = or_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == '.':
            right_node = temp_stack.pop()
            left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == '*':
            left_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = kleene_operation(stack, temp_stack, contador_simbolos, left_node)

        elif simbolo == '+':
            left_node = temp_stack.pop()

            list_values = []
            list_ids_temp = []
            list_values.append(left_node.value)
            list_ids_temp.append(left_node.left)
            list_ids_temp.append(left_node.right)
            paso = True
            while paso == True and list_ids_temp != []:
                paso = False
                current_id = list_ids_temp.pop()
                for i in range(len(stack)):
                    current_node = stack[i]
                    if current_node.id == current_id:
                        paso = True
                        list_values.append(current_node.value)
                        if current_node.left != None:
                            list_ids_temp.append(current_node.left)
                        if current_node.right != None:
                            list_ids_temp.append(current_node.right)
                        break

            list_values.reverse()
            plustack, plusnode_list, plusalfabeto = exec(list_values)

            temp_contador_simbolos = contador_simbolos
            temp_contador_leafs = contador_leafs - 1

            plustack.pop()
            plustack.pop()
            
            for i in range(len(plustack)):
                stock = plustack[i]
                stock.id += temp_contador_simbolos
                contador_simbolos += 1
                if stock.padre != None:
                    stock.padre += temp_contador_simbolos
                if stock.left != None:
                    stock.left += temp_contador_simbolos
                    contador_simbolos += 1
                if stock.right != None:
                    stock.right += temp_contador_simbolos
                    contador_simbolos += 1
                if stock.number != None:
                    stock.number += temp_contador_leafs
                    contador_leafs += 1
                    if stock.primerapos != set():
                        extraer = stock.primerapos.pop()
                        stock.primerapos.add(extraer + temp_contador_leafs)
                    if stock.ultimapos != set():
                        extraer = stock.ultimapos.pop()
                        stock.ultimapos.add(extraer + temp_contador_leafs)
                plustack[i] = stock

            copy_node = plustack.pop()

            for i in range(len(plustack)):
                stack.append(plustack[i])

            stack, temp_stack, contador_simbolos = kleene_operation(stack, temp_stack, contador_simbolos, copy_node)
            right_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = concat_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        elif simbolo == '?':
            left_node = temp_stack.pop()
            temp_stack, alfabeto, contador_simbolos, contador_leafs = operando_operation(temp_stack, alfabeto, '𝜀', contador_simbolos, contador_leafs)
            right_node = temp_stack.pop()
            stack, temp_stack, contador_simbolos = or_operation(stack, temp_stack, contador_simbolos, left_node, right_node)

        else:
            temp_stack, alfabeto, contador_simbolos, contador_leafs = operando_operation(temp_stack, alfabeto, simbolo, contador_simbolos, contador_leafs)

        contador += 1

    if len(temp_stack) > 0:
        stack.append(temp_stack.pop())

    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            if item.value == '|':
                item.nullable = search_node(stack, item.left).nullable or search_node(stack, item.right).nullable
                stack[i] = item
            elif item.value == '.':
                item.nullable = search_node(stack, item.left).nullable and search_node(stack, item.right).nullable
                stack[i] = item

    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            if item.value == '|':
                item.primerapos = item_left.primerapos.union(item_right.primerapos)
                stack[i] = item
            elif item.value == '.':
                if item_left.nullable:
                    item.primerapos = item_left.primerapos.union(item_right.primerapos)
                else:
                    item.primerapos = item_left.primerapos
                stack[i] = item
        elif item.value == '*':
            item.primerapos = search_node(stack, item.left).primerapos
            stack[i] = item

    for i in range(len(stack)):
        item = stack[i]
        if item.left != None and item.right != None:
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            if item.value == '|':
                item.ultimapos = item_left.ultimapos.union(item_right.ultimapos)
                stack[i] = item
            elif item.value == '.':
                if item_right.nullable:
                    item.ultimapos = item_left.ultimapos.union(item_right.ultimapos)
                else:
                    item.ultimapos = item_right.ultimapos
                stack[i] = item
        elif item.value == '*':
            item.ultimapos = search_node(stack, item.left).ultimapos
            stack[i] = item

    node_list = {}

    for i in range(len(stack)):
        item = stack[i]
        if item.value == '.':
            item_left = search_node(stack, item.left)
            item_right = search_node(stack, item.right)
            for pos in item_left.ultimapos:
                stack, node_list = siguiente_pos(stack, node_list, pos, item_right.primerapos)
        elif item.value == '*':
            for pos in item.ultimapos:
                stack, node_list = siguiente_pos(stack, node_list, pos, item.primerapos)

    for i in range(len(stack)):
        node = stack[i]
        if node.value == '#':
            node_list[node.number] = [node.value, node.siguientepos]


    if (graph_this == True):
        pydotplus.find_graphviz()

        graph = tree_graph(stack);

        # Save or display the graph
        png_file_path = "result/tree.png"
        graph.write_png(png_file_path)  # Save PNG file

    return stack, node_list, alfabeto
