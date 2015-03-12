import sys
import pprint

import pycparser
import mksymtab
import mk3ac

import compiler_builtins
import mkregassign

class AssemblyGenerator(object):
	def __init__(self,funct_info):
		self.funct_info = funct_info
		self.labels = [key for key, value in funct_info.the_symbol_table.values[funct_info.name].items() if isinstance(value,mk3ac.Label)]
		self.current_asm = []
		self.writeback_asm = []
		self.register_assignments = mkregassign.VariableAccess(funct_info)
	def handle_possible_immediate(self,operand):
		"return (immediate?,text)"
		try:
			if str(int(operand)) == str(operand):
				return (True,str(operand))
			else:
				assert(False)
		except ValueError:
			return (False,operand)
	def handle_operand(self,operand,register,mode):
		try:
			if operand[0] == "$":
				# this is already a register
				assert(mode == "read")
				self.current_asm.append("	move	"+str(register)+", "+str(operand))				
				return register
		except:
			pass
		x = operand
		if (x in self.labels):
			return x
		else:
			is_immediate, s = self.handle_possible_immediate(x)
			if is_immediate:
				self.current_asm.append("	li	"+str(register)+", "+str(s))
				return register
			else:
				try:
					if mode == "read":
						self.current_asm.append("	"+self.register_assignments.code_to_load(x,register))
					elif mode == "write":
						self.writeback_asm.append("	"+self.register_assignments.code_to_store(x,register))
					else:
						assert(False)
				except KeyError:
					return x
				return register
	def clear_writeback(self):
		self.current_asm.extend(self.writeback_asm)
		self.writeback_asm = []
	
	def make_asm_text(self,operation,args,comments=None,label=None):
		result = ""
		if label is None:
			result += "	"
		else:
			result += str(label)
			result += ":	"
		if operation == "":
			pass
		else:
			result += operation
			result += " "
			def mode_if(x):
				if x == 0:
					return "write"
				else:
					return "read"
			result += ", ".join([self.handle_operand(item,"$t"+str(index),mode_if(index)) for index, item in enumerate(args)])
		if comments is None:
			pass
		else:
			result += "		#"+str(comments)
		self.current_asm.append(result)
		self.clear_writeback()

op_to_asm = {
	"unconditional_branch":	("j",lambda x:x),
	"conditional_branch": ("bne",lambda x:("$0",x[1],x[0])),
	"=":("move",lambda x:x),
	"+":("add",lambda x:x)
	}

def arg_filter(x):
	if x is "":
		return False
	elif x is None:
		return False
	else:
		return x

def process_3ac(the_3ac,funct_info):
	ag = AssemblyGenerator(funct_info)	
	# right at the start of the function, we need to adjust $sp appropriately
	# comments=str(operation)+" "+str(destination)+", "+str(operand1)+", "+str(operand2)
	ag.make_asm_text("add",["$sp","$sp",-1*funct_info.size_of_locals])
	for label, operation, destination, operand1, operand2 in the_3ac:
		if operation in op_to_asm:
			asm_op, permutation = op_to_asm[operation]
			ag.make_asm_text(asm_op,
				permutation(filter(arg_filter,[destination,operand1,operand2])),
				label=label,
				comments=str(operation)+" "+str(destination)+", "+str(operand1)+", "+str(operand2)
			)
		else:
			if operation == "":
				ag.make_asm_text("",[],label=label)
			elif operation in ["call"]:
				if operand2 != '':
				    ag.handle_operand(operand2,"$a0","read")
				ag.make_asm_text("jal",[operand1],label=label)
				ag.handle_operand(destination,"$v0","write")
				ag.clear_writeback()
			elif operation in ["return"]:
				ag.handle_operand(destination,"$v0","read")
				ag.make_asm_text("jr",["$ra"],label=label)
			elif operation in ["<="]:
				ag.make_asm_text("slt",[
					destination,
					operand1,
					operand2
					],label=label,comments="slt "+str(destination)+", "+str(operand1)+", "+str(operand2))
				ag.make_asm_text("add",["$t3","$0",1],comments="put 1 into $t3")
				ag.make_asm_text("sub",[destination,"$t3",destination],comments="subtract destination of the slt from 1 to negate")
			elif operation in ["*"]:
				ag.make_asm_text("mult",[
					ag.handle_operand(operand1,"$t0","read"),
					ag.handle_operand(operand2,"$t1","read")
					],label=label,comments=str(operation)+" "+str(destination)+", "+str(operand1)+", "+str(operand2))
				ag.make_asm_text("mflo",[destination])
			else:
				pprint.pprint(operation)
				assert(False)
	return ("\n".join(ag.current_asm))

# WORK HERE
class FunctionInformation(object):
    def __init__(self,st):
        self.the_symbol_table = st
        
	
def makeFunctionInformation(st,func_name):
    result = FunctionInformation(st)
    some_function = st.values[func_name]
    result.name = func_name
    struct_like_type = []
    for key,value in some_function.items():
        if key == "...":
            result.args = value
        elif key == "return":
            result.return_type = value
        elif isinstance(value,mk3ac.Label):
            pass
        elif key == "{}":
            #result.body = process_3ac(value)
            result.body = value
            pass
        else:
            struct_like_type.append((key,value))
    struct_like_type.append(("","int"))
    result.offsets_of_locals = {}
    for name, info in st.offsets_and_types_of_elements(struct_like_type):
        offset, type = info
        if name == "":
            result.size_of_locals = offset
        else:
            result.offsets_of_locals[name] = offset
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:    # optionally support passing in some code as a command-line argument
        code_to_parse = sys.argv[1]
    else: # this can not handle the typedef and struct below correctly. Need to work on it.
        code_to_parse = """
int main()
{
	int i;
	int j;
	int result;
	for(i = 1; i <=6; i++) {
		getint();
		result = 1;
		for (j = 1; j <= i; j++) {
			putint(result);
			result = result * j;
		};
		putint(result);
	};
	exit();
	return 0;
}
"""
	if False:
	    code_to_parse = """
int main()
{
	int i;
	int j;
	int result;
	int zero;
	zero = 0;
	j = 9;
	result = 1;
	for (i = 1; i <= j; i++) {
		putint(i);
		putint(zero);
		putint(zero);
		putint(result);
		putint(zero);
		putint(zero);
		putint(zero);
		result = result * j;
	};
	exit();
}
"""
    cparser = pycparser.c_parser.CParser()
    parsed_code = cparser.parse(code_to_parse)
    parsed_code.show()
    st = mksymtab.makeSymbolTable(parsed_code)
    mk3ac.make3ac(st)
    functions = (dict(st.functions()))
    pprint.pprint(st.values.values)
    for key,value in functions.items():
        if key in compiler_builtins.function_names():
            continue
        print key
        result = makeFunctionInformation(st,key)
        pprint.pprint(result.args)
        print result.size_of_locals
        pprint.pprint(result.offsets_of_locals)
        pprint.pprint(result.return_type)
        pprint.pprint(result.body)
        asm = process_3ac(result.body,result)
        asm = """
.text
main:
"""+asm+compiler_builtins.code()
        with open("output.s","w") as f:
            f.write(asm)
