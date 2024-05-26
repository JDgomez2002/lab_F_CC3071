import re

class Yalp:
  def __init__(self, file: str) -> None:
    self.file = file
    self.tokens = []
    self.nonTerminals = []
    self.productions = []
    self.items = []
    self.parse()

  def parse(self) -> None:
    try:
      with open(self.file, "r") as file:
        grammar = file.read()

      tokenSection, productionSection = grammar.split("%%")

      tokenPattern = r"%token\s+(.*?)(?=\n%token|\n%%|\nIGNORE|$)"
      tokens = re.findall(tokenPattern, tokenSection)

      ignorePattern = r"IGNORE\s+(\w+)"
      ignoredTokens = re.findall(ignorePattern, tokenSection)
      self.tokens = [token for token in tokens if token not in ignoredTokens]
      self.tokens = [symbol for token in self.tokens for symbol in token.split()]

      rulePattern = r"(\w+)\s*:\s*(.*?)\s*;"
      rules = re.findall(rulePattern, productionSection, re.DOTALL)

      for rule in rules:
        nonTerminal, prodString = rule
        prodString = prodString.strip()
        productionAlternatives = prodString.split("|")

        for prod in productionAlternatives:
          symbols = prod.strip().split()
          self.productions.append([nonTerminal, symbols])

          if nonTerminal not in self.nonTerminals:
            self.nonTerminals.append(nonTerminal)

      self.items = self.nonTerminals + self.tokens

    except FileNotFoundError:
      print(f"Error reading file: {self.file}")
      return

  def getGrammar(self) -> dict:
    return {
      "T": self.tokens,
      "NT": self.nonTerminals,
      "P": self.productions,
      "items": self.items,  # items = NT + T, in other words, all symbols
    }