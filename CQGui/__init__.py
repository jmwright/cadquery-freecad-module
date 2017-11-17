class PrintHook:
    def __init__(self):
        import sys

        #self.origOut = None
        #sys.stdout = self
        #self.origOut = sys.__stdout__

    def write(self, text):
        import FreeCAD

        FreeCAD.Console.PrintMessage(text)

    #pass all other methods to __stdout__ so that we don't have to override them
    def __getattr__(self, name):
        return self.origOut.__getattr__(name)

PrintHook()
