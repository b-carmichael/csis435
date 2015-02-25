import sys
import pprint

import pycparser
import mksymtab
import mk3ac

def assign_registers(the_3ac,funct_info):
	names_of_locals = funct_info.offsets_of_locals.keys()
	result = {}
	counter = 0
	for name in names_of_locals:
		if name == "L5":
			result[name] = "$t0"
		else:
			result[name] = "$s"+str(counter)
			counter = counter + 1
	#for label, operation, destination, operand1, operand2 in the_3ac:
	return result

op_to_asm = {
	"*":	("mult",3),
	"unconditional_branch":	("j",1)
	}

def process_3ac(the_3ac,funct_info):
	register_assignments = assign_registers(the_3ac,funct_info)
	def handle_possible_immediate(operand):
		"return (immediate?,text)"
		try:
			if str(int(operand)) == str(operand):
				return (True,str(operand))
			else:
				assert(False)
		except ValueError:
			return (False,register_assignments[operand])
		
	result = ""
	for label, operation, destination, operand1, operand2 in the_3ac:
		if label is None:
			pass
		else:
			result += "\n"
			result += str(label)
			result += ":"
		if operation == "":
			pass
		else:
			result += "\t"
			if operation in ["conditional_branch","call","return"]:
				result += str(operation)+" "+str(destination)+" "+str(operand1)+" "+str(operand2)+"""
"""
			elif operation in ["="]:
				is_immediate, s = handle_possible_immediate(operand1)
				if is_immediate:
					result += "li	"+register_assignments[destination]+", "+str(operand1)+"""
"""
				else:
					result += "move	"+register_assignments[destination]+", "+register_assignments[operand1]+"""
"""
			elif operation in ["<="]:
				result += "slt	"+register_assignments[destination]+", "+register_assignments[operand2]+", 				"+register_assignments[operand1]+"""
	"""
				result += "not	"+register_assignments[destination]+", "+register_assignments[destination]+"""
	"""
			elif operation in ["+"]:
				is_immediate, s = handle_possible_immediate(operand1)
				if is_immediate:
					result += "addi	"+register_assignments[destination]+", "+register_assignments[operand2]+", "+operand1+"""
"""
				else:
					is_immediate, s = handle_possible_immediate(operand2)
					if is_immediate:
						
						result += "addi	"+register_assignments[destination]+", "+register_assignments[operand1]+", "+str(operand2)+"""
	"""
					else:
						result += "add	"+register_assignments[destination]+", "+register_assignments[operand1]+", 				"+register_assignments[operand2]+"""
	"""
			else:
				asm, num_args = op_to_asm[operation]
				labels = [key for key, value in funct_info.the_symbol_table.values[funct_info.name].items() if isinstance(value,mk3ac.Label)]
				def keep_if_label(x):
					if (x in labels):
						return x
					else:
						return register_assignments[x]
				result += asm+" "+", ".join([keep_if_label(item) for item in [destination,operand1,operand2][:num_args]])+"""
"""

	return (result)

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
		result = 1;
		for (j = 1; j <= i; j++) {
			result = result * j;
		};
		putint(result);
	};
	return 0;
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
        if key == "putint":
            continue
        print key
        result = makeFunctionInformation(st,key)
        pprint.pprint(result.args)
        print result.size_of_locals
        pprint.pprint(result.offsets_of_locals)
        pprint.pprint(result.return_type)
        print result.body
        print process_3ac(result.body,result)
        
    

