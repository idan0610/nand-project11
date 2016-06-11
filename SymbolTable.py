__author__ = 'daph.kaplan'
kind = {}
kind['STATIC'] = 1
kind['FIELD'] = 2
kind['ARG'] = 3
kind['VAR'] = 4

class SymbolTable:

    def __init__(self):
        self.classtable = {}
        self.subroutinetable = {}

        self.ClassCountStatic = 0
        self.ClassCountField = 0
        self.SubCountArg = 0
        self.SubCountVar = 0

    def startSubroutine(self):
        self.subroutinetable = {}
        self.SubCountArg = 0
        self.SubCountVar = 0

    def define(self, name, type, kind):
        if kind == "static":
            self.classtable[name] = (type ,kind, self.ClassCountStatic)
            self.ClassCountStatic += 1
        elif kind =="field":
            self.classtable[name] = (type ,kind, self.ClassCountField)
            self.ClassCountField += 1
        elif kind == "arg":
            self.subroutinetable[name] = (type ,kind, self.SubCountArg)
            self.SubCountArg += 1
        elif kind == "var":
            self.subroutinetable[name] = (type ,kind, self.SubCountVar)
            self.SubCountVar += 1


    def varCount(self, kind):
        if kind == "static":
            return self.ClassCountStatic
        elif kind =="field":
            return self.ClassCountField
        elif kind == "arg":
            return self.SubCountArg
        elif kind == "var":
            return self.SubCountVar

    def kindOf(self, name):

        if name in self.subroutinetable:
            return self.subroutinetable[name][1]
        elif name in self.classtable:
            return self.classtable[name][1]

    def typeOf(self,name):
        if name in self.subroutinetable:
            return self.subroutinetable[name][0]
        elif name in self.classtable:
            return self.classtable[name][0]

    def indexOf(self, name):

        if name in self.subroutinetable:
            return self.subroutinetable[name][2]
        elif name in self.classtable:
            return self.classtable[name][2]

