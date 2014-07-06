import sublime, sublime_plugin
import re 

class RealTimeCommand(sublime_plugin.EventListener):
    def __init__(self):
        self.variables = {}
        self.operators = ["+", "-", "/", "*"]
        self.mouseDown = True

    def on_done(self, index):
        print (index)

    def handle_assignment(self, var, val):
        """Assigns a variable for the first time or a variable that has changed types"""
        if "'" in val or '"' in val:
            val = str(val.replace('"', "").replace("'", ""))

        elif val == 'True':
            val = True

        elif val == 'False':
            val  = False

        elif val == "[]":
            val = list()

        else: # int or float 
            try:
                if int(val) == float(val):
                    val = int(val)
            except:
                try:
                    val = float(val)
                except:
                    return

        self.variables[var] = val


    def handle_modification(self, var, val, op):
        """Handles operations conducted on an existing variable"""
        if (isinstance(self.variables[var], int) or isinstance(self.variables[var], float)) and str(self.variables[var] not in ["True", "False"]):
            if op:
                val = var + op + val
            val = val.replace(var, "self.variables[var]")
            self.variables[var] = eval(val)

        elif isinstance(self.variables[var], str):
            oldVal = val

            if op:
                val = var + op + val
            val = val.replace(var, "self.variables[var]")

            try:
                self.variables[var] = eval(val)
            except:
                if op:
                    self.variables[var] = "Error on line: " + var + op + "=" + oldVal + ". Check for type errors"
                else:
                    self.variables[var] = "Error on line: " + var + "=" + oldVal + ". Check for type errors"



    def on_selection_modified_async(self, view):
        selection = view.substr(view.word(view.sel()[0]))
        content = view.substr(sublime.Region(0, view.line(view.sel()[0]).end()))
        content = content.split("\n")

        self.mouseDown = not self.mouseDown

        if (self.mouseDown):
            for line in content:

                line = str(line.replace("\n", "").replace(" ", ""))
                line = re.sub('\s+', "", line)

                if line.startswith("#"):
                    continue

                if "=" in line and "==" not in line:  # assignment
                    line = line.split("=")
                    var = line[0]   # var being assigned
                    val = line[1]   # value assigned 
                    op = None # whether or not there is an operation +=, etc.
                    assign = True


                    # += or variant
                    if var[len(var) - 1] in self.operators:
                        if "//" in var:  # handle truncate
                            op = "//"
                        else:
                            op = var[len(var) - 1] # else it is one of *=, +=, -=, /=
                        var = var.replace(op, "")


                    if var in self.variables:
                        oldVal = val
                        val = val.replace(var, "self.variables[var]")
                        try:
                            if type(self.variables[var]) == type(eval(val)) or op != None: # type is the same as before
                                assign = False
                        except:
                            self.variables[var] = oldVal # issue with eval
                            #print("Unable to evaluate, please check types: " + oldVal )
                            break

                    # if a value for the variable is stored && type hasn't changed
                    if not assign:  
                        self.handle_modification(var, val, op)              
                    else: 
                        self.handle_assignment(var, val) # assign for first time or re-assign completely

            if selection in self.variables:
                print(selection + " = " + str(self.variables[selection]))
            #view.show_popup_menu([str(self.variables[selection])], self.on_done)
