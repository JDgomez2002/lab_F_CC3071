
import simulators.Scanner as simSCAN
import pickle
import time
import sys

print("header")

def WS():
	WS

def ID():
	ID

def TOKEN1():
	print()

def TOKEN2():
	print()

def TOKEN3():
	print()

def TOKEN4():
	print()

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

    print("\n==========================================================================")    
    print(f"Scan.py executed in {round(time_taken, 3)}s")
    print("==========================================================================\n")

    pass


def readString(data, MinDFA, grammar):
    i = 0
    counter = 0
    tokens = []

    lengthData = len(data)

    while i < lengthData:
        print("\ni: " + str(i))
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


print("trailer")
