# responsible for

from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import  SymbolTable
operators = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
keyword_const = ["true" , "false", "null", "this"]

class CompilationEngine:

    def __init__(self, inputFile, outputFile):
        self.tokenizer = JackTokenizer(inputFile)
        self.vmWriter = VMWriter(outputFile)
        self.symbolTable = SymbolTable()
        self.classname = ""
        self.CompileClass()
        self.whilecounter = 0
        self.ifcounter = 0

    def CompileClass(self):
        #classname
        self.tokenizer.advance()
        self.classname = self.tokenizer.identifier()
        self.tokenizer.advance()
        # ignore {
        self.tokenizer.advance()

        while self.tokenizer.keyWord() == "static" or self.tokenizer.keyWord() == "field":
            self.CompileClassVarDec()

        while self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "method":
            self.CompileSubroutine()

        #ignore }
        self.tokenizer.advance()



    def CompileClassVarDec(self):

        kind = self.tokenizer.keyWord()
        self.tokenizer.advance()
        type = self.compileType()
        name = self.tokenizer.identifier()
        self.symbolTable.define(name, type, kind)
        self.tokenizer.advance()

        # add the rest of var names, if there are
        while self.tokenizer.symbol() == ",":
            self.tokenizer.advance()
            name = self.tokenizer.identifier()
            self.symbolTable.define(name, type, kind)
            self.tokenizer.advance()

        # ignore ;
        self.tokenizer.advance()

    def CompileSubroutine(self):

        self.symbolTable.startSubroutine()
        self.ifcounter = 0
        self.whilecounter = 0
        # constructor | function | method
        functype = self.tokenizer.keyWord()
        self.tokenizer.advance()

        if functype == "method":
            self.symbolTable.define("this", self.classname, "arg")

        self.tokenizer.advance()

        subrotineName = self.classname + "." + self.tokenizer.identifier()
        self.tokenizer.advance()

        # ( parameterList )
        self.tokenizer.advance()
        self.compileParameterList()
        self.tokenizer.advance()

        # subrotineBody
        # ignore {
        self.tokenizer.advance()
        # varDec*
        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()

        self.vmWriter.writeFunction(subrotineName, self.symbolTable.varCount("var"))
        # allocate memory for constructor
        # if functype == "constructor":
        #     self.vmWriter.writePush("constant" , self.symbolTable.varCount("field"))
        #     self.vmWriter.writeCall("Memory.alloc", "1")

        if functype == "constructor" or functype == "method":
            if functype == "constructor":
                self.vmWriter.writePush("constant" , self.symbolTable.varCount("field"))
                self.vmWriter.writeCall("Memory.alloc", "1")
            else:
                self.vmWriter.writePush("argument", "0")
            self.vmWriter.writePop("pointer", "0")


        # statements
        self.compileStatements()

        # ignore }
        self.tokenizer.advance()

    def compileParameterList(self):
        # if not )
        if self.tokenizer.tokenType() != 1:

            # type varName
            argtype = self.compileType()
            argname = self.tokenizer.identifier()
            self.symbolTable.define(argname, argtype, "arg")
            self.tokenizer.advance()

            # (, type varName)*
            while self.tokenizer.symbol() == ",":
                self.tokenizer.advance()
                argtype = self.compileType()
                argname = self.tokenizer.identifier()
                self.symbolTable.define(argname, argtype, "arg")
                self.tokenizer.advance()

    def compileVarDec(self):

        # var
        self.tokenizer.advance()

        # type
        type = self.compileType()

        # varName
        varname = self.tokenizer.identifier()
        self.symbolTable.define(varname, type, "var")
        self.tokenizer.advance()

        # (, varName)*
        while self.tokenizer.symbol() == ",":
            self.tokenizer.advance()
            varname = self.tokenizer.identifier()
            self.symbolTable.define(varname, type, "var")

            self.tokenizer.advance()

        # ignore ;
        self.tokenizer.advance()


    def compileStatements(self):

        while self.tokenizer.tokenType() == 0:
            if self.tokenizer.keyWord() == "let":
                self.compileLet()
            elif self.tokenizer.keyWord() == "if":
                self.compileIf()
            elif self.tokenizer.keyWord() == "while":
                self.compileWhile()
            elif self.tokenizer.keyWord() == "do":
                self.compileDo()
            elif self.tokenizer.keyWord() == "return":
                self.compileReturn()


    def compileDo(self):

        self.tokenizer.advance()
        self.compileSubRoutineCall()
        self.vmWriter.writePop("temp", "0")

        # ignore ;
        self.tokenizer.advance()

    def compileLet(self):

        # let
        self.tokenizer.advance()
        # varName
        varname = self.tokenizer.identifier()
        varkind = self.symbolTable.kindOf(varname)

        self.tokenizer.advance()

        # ([ expression ])?
        if self.tokenizer.symbol() == "[":
            self.tokenizer.advance()
            self.CompileExpression()
            if varkind == "field":
                self.vmWriter.writePush("this", self.symbolTable.indexOf(varname))
            elif varkind == "var":
                self.vmWriter.writePush("local", self.symbolTable.indexOf(varname))
            elif varkind == "arg":
                self.vmWriter.writePush("argument", self.symbolTable.indexOf(varname))
            elif varkind == "static":
                self.vmWriter.writePush("static", self.symbolTable.indexOf(varname))
            self.vmWriter.writeArithmetic("add")

            #ignore ]
            self.tokenizer.advance()
            #ignore =
            self.tokenizer.advance()
            self.CompileExpression()
            self.vmWriter.writePop("temp", "0")

            # that
            self.vmWriter.writePop("pointer", "1")
            self.vmWriter.writePush("temp", "0")
            self.vmWriter.writePop("that", "0")
            self.tokenizer.advance()


        else:

            # ignore =
            self.tokenizer.advance()

            # expression
            self.CompileExpression()

            if varkind == "field":
                self.vmWriter.writePop("this", self.symbolTable.indexOf(varname))
            elif varkind == "var":
                self.vmWriter.writePop("local", self.symbolTable.indexOf(varname))
            elif varkind == "arg":
                self.vmWriter.writePop("argument", self.symbolTable.indexOf(varname))
            elif varkind == "static":
                self.vmWriter.writePop("static", self.symbolTable.indexOf(varname))

            #ignore ;
            self.tokenizer.advance()


    def compileWhile(self):

        # while
        self.tokenizer.advance()

        # ( expression )
        self.tokenizer.advance()
        whileindex = self.whilecounter
        self.whilecounter += 1
        self.vmWriter.writeLabel("WHILE_EXP" + str(whileindex))
        self.CompileExpression()
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf("WHILE_END" + str(whileindex))
        self.tokenizer.advance()

        # ignore {
        self.tokenizer.advance()

        # statements
        self.compileStatements()

        # ignore }
        self.tokenizer.advance()
        self.vmWriter.writeGoto("WHILE_EXP" + str(whileindex))
        self.vmWriter.writeLabel("WHILE_END" + str(whileindex))

    def compileReturn(self):

        # return
        self.tokenizer.advance()

        # expression?
        if self.isTerm():
            self.CompileExpression()
            self.vmWriter.writeReturn()
        else:
            self.vmWriter.writePush("constant", "0")
            self.vmWriter.writeReturn()

        # ignore;
        self.tokenizer.advance()


    def compileIf(self):
        #if
        self.tokenizer.advance()
        # ( expression )
        self.tokenizer.advance()
        self.CompileExpression()
        ifindex = self.ifcounter
        self.ifcounter += 1
        self.vmWriter.writeIf("IF_TRUE" + str(ifindex))
        self.vmWriter.writeGoto("IF_FALSE" + str(ifindex))
        self.vmWriter.writeLabel("IF_TRUE" + str(ifindex))
        self.tokenizer.advance()

        # { statements }
        self.tokenizer.advance()
        self.compileStatements()
        self.tokenizer.advance()

        if self.tokenizer.tokenType() == 0 and self.tokenizer.keyWord() == "else":
            # else
            self.vmWriter.writeGoto("IF_END" + str(ifindex))
            self.vmWriter.writeLabel("IF_FALSE" + str(ifindex))

            self.tokenizer.advance()

            # { statements }
            self.tokenizer.advance()
            self.compileStatements()
            self.tokenizer.advance()

            self.vmWriter.writeLabel("IF_END" + str(ifindex))

        else:
            self.vmWriter.writeLabel("IF_FALSE" + str(ifindex))


    def CompileExpression(self):
        #term
        self.CompileTerm()
        # (op term)*
        op = self.tokenizer.symbol()
        while self.tokenizer.tokenType() == 1 and op in operators:
            self.tokenizer.advance()
            self.CompileTerm()
            if op == "=":
                self.vmWriter.writeArithmetic("eq")
            elif op == "+":
                self.vmWriter.writeArithmetic("add")
            elif op == "-":
                self.vmWriter.writeArithmetic("sub")
            elif op == "*":
                self.vmWriter.writeCall("Math.multiply", "2")
            elif op == "/":
                self.vmWriter.writeCall("Math.divide", "2")
            elif op == "&amp;":
                self.vmWriter.writeArithmetic("and")
            elif op == "|":
                self.vmWriter.writeArithmetic("or")
            elif op == "&lt;":
                self.vmWriter.writeArithmetic("lt")
            elif op == "&gt;":
                self.vmWriter.writeArithmetic("gt")
            op = self.tokenizer.symbol()

    def CompileTerm(self):
        if self.tokenizer.tokenType() == 3:
            self.vmWriter.writePush("constant", self.tokenizer.intVal())
            self.tokenizer.advance()

        elif self.tokenizer.tokenType() == 4:
            conststring = self.tokenizer.stringVal()
            self.vmWriter.writePush("constant", str(len(conststring)))
            self.vmWriter.writeCall("String.new", "1")
            for i in range(len(conststring)):
                self.vmWriter.writePush("constant", str(ord(conststring[i])))
                self.vmWriter.writeCall("String.appendChar", "2")

            self.tokenizer.advance()

        elif self.tokenizer.tokenType() == 0:
            keywordconst = self.tokenizer.keyWord()
            if keywordconst == "true":
                self.vmWriter.writePush("constant", "0")
                self.vmWriter.writeArithmetic("not")
            elif keywordconst == "false" or keywordconst == "null":
                self.vmWriter.writePush("constant", "0")
            elif keywordconst == "this":
                self.vmWriter.writePush("pointer", "0")
            self.tokenizer.advance()

        elif self.tokenizer.tokenType() == 2:
            # varName [ expression]
            if self.tokenizer.tokens[self.tokenizer.currentToken +1] == '[':
                varname = self.tokenizer.identifier()
                varkind = self.symbolTable.kindOf(varname)
                self.tokenizer.advance()
                # [ expression ]
                self.tokenizer.advance()
                self.CompileExpression()
                if varkind == "field":
                    self.vmWriter.writePush("this", self.symbolTable.indexOf(varname))
                elif varkind == "var":
                    self.vmWriter.writePush("local", self.symbolTable.indexOf(varname))
                elif varkind == "arg":
                    self.vmWriter.writePush("argument", self.symbolTable.indexOf(varname))
                elif varkind == "static":
                    self.vmWriter.writePush("static", self.symbolTable.indexOf(varname))
                self.vmWriter.writeArithmetic("add")
                # that
                self.vmWriter.writePop("pointer", "1")
                self.vmWriter.writePush("that", "0")
                self.tokenizer.advance()
            # subrutine call
            elif self.tokenizer.tokens[self.tokenizer.currentToken +1] == '(' or self.tokenizer.tokens[self.tokenizer.currentToken +1] == '.':
                self.compileSubRoutineCall()
            # varname
            else:
                varname = self.tokenizer.identifier()
                varkind = self.symbolTable.kindOf(varname)
                if varkind == "field":
                    self.vmWriter.writePush("this", self.symbolTable.indexOf(varname))
                elif varkind == "var":
                    self.vmWriter.writePush("local", self.symbolTable.indexOf(varname))
                elif varkind == "arg":
                    self.vmWriter.writePush("argument", self.symbolTable.indexOf(varname))
                elif varkind == "static":
                    self.vmWriter.writePush("static", self.symbolTable.indexOf(varname))
                self.tokenizer.advance()

        elif self.tokenizer.tokenType() == 1 and self.tokenizer.symbol() == '(':
            # ( expression )
            self.tokenizer.advance()
            self.CompileExpression()
            self.tokenizer.advance()
        else:
            #unary!!!
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            self.CompileTerm()
            if op == "-":
                self.vmWriter.writeArithmetic("neg")
            elif op == "~":
                self.vmWriter.writeArithmetic("not")

    def compileSubRoutineCall(self):
        # subroutineName  | (className | varName)
        identifier = self.tokenizer.identifier()
        self.tokenizer.advance()
        #no "." only name
        if self.tokenizer.symbol() == '(':
            # ( expressionList ) -- subroutine of type method
            self.tokenizer.advance()
            self.vmWriter.writePush("pointer", "0")
            argnum = self.CompileExpressionList()
            self.vmWriter.writeCall(self.classname + "." + identifier, str(argnum +1))

            self.tokenizer.advance()
        else:
            # . -- class.function or var.method
            self.tokenizer.advance()
            # subroutineName
            subname = self.tokenizer.identifier()
            self.tokenizer.advance()

            self.tokenizer.advance()
            if identifier in self.symbolTable.classtable or identifier in self.symbolTable.subroutinetable:
                # varname!!!
                if identifier in self.symbolTable.subroutinetable:
                    if self.symbolTable.kindOf(identifier) == "var":
                        self.vmWriter.writePush("local", self.symbolTable.indexOf(identifier))
                    else:
                        self.vmWriter.writePush("argument", self.symbolTable.indexOf(identifier))
                else:
                    if self.symbolTable.kindOf(identifier) == "static":
                        self.vmWriter.writePush("static", self.symbolTable.indexOf(identifier))
                    else:
                        self.vmWriter.writePush("this", self.symbolTable.indexOf(identifier))


                argnum = self.CompileExpressionList()
                identifierclass = self.symbolTable.typeOf(identifier)
                self.vmWriter.writeCall(identifierclass + "." + subname, str(argnum +1))
            else:
                argnum = self.CompileExpressionList()
                self.vmWriter.writeCall(identifier + "." + subname, str(argnum))
            self.tokenizer.advance()

    def CompileExpressionList(self):
        # (expression
        i = 0
        if self.isTerm():
            i += 1
            # (, expression)
            self.CompileExpression()
            while self.tokenizer.symbol() == ',':
                i+= 1
                self.tokenizer.advance()
                self.CompileExpression()
        return i

    def isTerm(self):
        if self.tokenizer.tokenType() == 3 or self.tokenizer.tokenType() == 4:
            return True
        if self.tokenizer.tokenType() == 0 and self.tokenizer.keyWord() in keyword_const:
            return True
        if self.tokenizer.tokenType() == 1 and self.tokenizer.symbol() == '(' :
            return True
        if self.tokenizer.tokenType() == 1 and (self.tokenizer.symbol() == '-' or self.tokenizer.symbol() == '~'):
            return True
        if self.tokenizer.tokenType() == 2:
            return True
        return False

    def compileType(self):
        if self.tokenizer.tokenType() == 0:
            typen = self.tokenizer.keyWord()
        else:
            typen = self.tokenizer.identifier()
        self.tokenizer.advance()
        return typen

