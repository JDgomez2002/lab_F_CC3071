import time

def exec(transiciones, estado_inicial, estados_aceptacion, cadena, i):

    valores = ""
    error = False
    estado_actual = estado_inicial
    a = i
    while a < len(cadena) and error == False:
        cad = ord(cadena[a])
        pasa = False
        for tran in transiciones:
            if estado_actual == tran[0] and cad == tran[1]:
                estado_actual = tran[2]
                pasa = True
                valores += cadena[a]
                break
        if pasa == False:
            error = True
            break
        a += 1

    if estado_actual in estados_aceptacion:
        return True, a, valores
    else:
        return False, a, valores