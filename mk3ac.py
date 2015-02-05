import pycparser # the C parser written in Python
import sys # so we can access command-line args
import pprint # so we can pretty-print our output

import mksymtab

import itertools

label_generator = itertools.count()

class Label(object):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
	pass

class CodeBuilder(pycparser.c_ast.NodeVisitor):
    def __init__(self,function_name,symbol_table):
        self.the_code = []
        self.the_symbol_table = symbol_table
        self.the_function_name = function_name
        self.expression_stack = []
    def add(self,operation,destination,source1,source2,label=None):
        self.the_code.append((label,operation,destination,source1,source2))
    def genLabel(self,scope="local",**kwargs):
        # do stuff here with symbol table
        the_label = "L"+str(label_generator.next())
        self.the_symbol_table.values[the_label] = Label(**kwargs)
        return the_label
    def start_visit(self,node):
        self.the_symbol_table.values.path.append(self.the_function_name)
        self.visit(node)
        del self.the_symbol_table.values.path[-1]
        assert(0 == len(self.the_symbol_table.values.path))
    def visit_Compound(self,node):
        self.generic_visit(node)
    def visit_Assignment(self,node):
        self.generic_visit(node)
        rvalue = self.expression_stack.pop()
        lvalue = self.expression_stack.pop()
        self.add("=",lvalue,rvalue,"")
        self.expression_stack.append(lvalue)
    def visit_ID(self,node):
        self.expression_stack.append(node.name)
    def visit_Constant(self,node):
        self.expression_stack.append(node.value)
    def visit_Return(self,node):
        self.generic_visit(node)
        self.add("return",self.expression_stack.pop(),"","")
    def visit_BinaryOp(self,node):
        self.generic_visit(node)
        operand1 = self.expression_stack.pop()
        operand2 = self.expression_stack.pop()
        destination = self.genLabel("local")
        self.add(node.op,destination,operand1,operand2)
        self.expression_stack.append(destination)
    def visit_UnaryOp(self,node):
        self.generic_visit(node)
        operand1 = self.expression_stack.pop()
        destination = self.genLabel("local")
        if node.op == "p++":
            self.add("+",operand1,operand1,1)
            self.expression_stack.append(operand1)
        else:
            self.add(node.op,destination,operand1,"")
            self.expression_stack.append(destination)
    def visit_For(self,node):
        init, cond, next, stmt = node.init, node.cond, node.next, node.stmt
        self.visit(init)
        junk = self.expression_stack.pop()        
        top_of_loop = self.genLabel()
        bottom_of_loop = self.genLabel()
        self.add("","","","",label=top_of_loop)
        self.visit(cond)
        conditional = self.expression_stack.pop()
        self.add("conditional_branch",bottom_of_loop,conditional,"")
        self.visit(stmt)
        junk = self.expression_stack.pop()        
        self.visit(next)
        junk = self.expression_stack.pop()
        self.add("unconditional_branch",top_of_loop,"","")
        self.add("","","","",label=bottom_of_loop)
        
        

if __name__ == "__main__":
    if len(sys.argv) > 1:    # optionally support passing in some code as a command-line argument
        code_to_parse = sys.argv[1]
    else: # this can not handle the typedef and struct below correctly. Need to work on it.
        code_to_parse = """
int foo(int a, int b) {
    int x;
    int y;
    return (x+y);
};
int bar(int c, int d) {
    int y;
    int z;
};
test() {};
int sum_of_squares(int x) {
	int i;
	int result;
	result = 0;
	for (i = 1; i <= x; i++) {
		result = result + i*i;
	};
	return result;
};
"""
    cparser = pycparser.c_parser.CParser()
    parsed_code = cparser.parse(code_to_parse)
    parsed_code.show()
    st = mksymtab.makeSymbolTable(parsed_code)
    #pprint.pprint(st.values.values)
    #pprint.pprint(st.types.values)
    functions = (dict(st.functions()))
    #pprint.pprint(st.values.path)
    for key,value in functions.items():
    	print key
    	body = value["{}"]
    	body.show()
    	cb = CodeBuilder(key,st)
    	cb.start_visit(body)
    	pprint.pprint(cb.the_code)
    	#pprint.pprint(st.values.values)
    	#pprint.pprint(st.types.values)
    