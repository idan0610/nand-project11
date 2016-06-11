import re
symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '&lt;', '&gt;', '&quot;', '&amp;']
keyword = ['class',  'constructor',  'function',  'method',  'field',  'static', 'var',  'int',  'char',  'boolean',  'void',  'true',  'false',  'null',  'this',  'let',  'do',  'if',  'else',  'while',  'return']
token_types = {}
token_types['KEYWORD'] = 0
token_types['SYMBOL'] = 1
token_types['IDENTIFIER'] = 2
token_types['INT_CONST'] = 3
token_types['STRING_CONST'] = 4


class JackTokenizer:

    def __init__(self, file):
        self.Jack_file = open(file, 'r')
        self.tokens = []
        #self.allfile = self.Jack_file.read().strip()
        self.allfile = ""
        self.string_list = []
        self.__initializeFile()
        self.currentToken = 0
        self.string_counter = 0
        self.Jack_file.close()

    def __initializeFile(self):

        inString = False
        inNormalComment = False
        inLongComment = False
        lastChar = ''
        while True:
            c = self.Jack_file.read(1)
            if not c:
                break

            flag = False
            while c == "*":
                lastChar = c
                c = self.Jack_file.read(1)
                if c == "/" and inLongComment:
                    inLongComment = False
                    flag = True
                elif not inNormalComment and not inLongComment:
                    self.allfile += lastChar

            if flag:
                continue

            if inNormalComment and c == "\n":
                inNormalComment = False

            if inNormalComment or inLongComment:
                continue

            if c == '"':
                inString = not inString

            if inString:
                self.allfile += c
                continue

            if c == "/":
                lastChar = c
                c = self.Jack_file.read(1)
                if c == "/":
                    inNormalComment = True
                    continue
                elif c == "*":
                    inLongComment = True
                    continue
                else:
                    self.allfile += lastChar

            self.allfile += c

        # # find all strings
        self.string_list = re.findall("\".*?\"", self.allfile)
        self.allfile = re.sub(re.compile("\".*?\"", re.DOTALL),"@",  self.allfile)
        # look \n
        self.allfile = self.allfile.replace('\n', " ")
        self.allfile = self.allfile.replace('\t', " ")

        for sym in symbols:
            newsym = " " + sym + " "
            self.allfile = self.allfile.replace(sym, newsym)

        self.tokens = self.allfile.split(" ")
        # self.tokens = filter(None, self.tokens)
        self.tokens = [x for x in self.tokens if x]

        for i in range(len(self.string_list)):
            self.string_list[i] = self.string_list[i].replace('&' , "&amp;")
            self.string_list[i] = self.string_list[i].replace('<' , "&lt;")
            self.string_list[i] = self.string_list[i].replace('>' , "&gt;")


    def hasMoreTokens(self):
        if self.currentToken < len(self.tokens):
            return True
        return False

    def advance(self):
        self.currentToken += 1

    def tokenType(self):
        if self.tokens[self.currentToken] in keyword:
            return token_types['KEYWORD']
        if self.tokens[self.currentToken] in symbols:
            return token_types['SYMBOL']
        if self.tokens[self.currentToken] == "@":
            return token_types['STRING_CONST']
        if self.tokens[self.currentToken][0].isdigit():
            return token_types['INT_CONST']
        return token_types['IDENTIFIER']

    def stringVal(self):
        string = self.string_list[self.string_counter][1:len(self.string_list[self.string_counter])-1]
        self.string_counter += 1
        return string

    def keyWord(self):
        return self.tokens[self.currentToken]

    def symbol(self):
        if self.tokens[self.currentToken] == '<':
            self.tokens[self.currentToken] = "&lt;"
        elif self.tokens[self.currentToken] == '>':
            self.tokens[self.currentToken] = "&gt;"
        elif self.tokens[self.currentToken] == '&':
            self.tokens[self.currentToken] = "&amp;"
        elif self.tokens[self.currentToken] == '"':
            self.tokens[self.currentToken] = "&quot;"

        return self.tokens[self.currentToken]

    def identifier(self):
        return self.tokens[self.currentToken]

    def intVal(self):
        return self.tokens[self.currentToken]