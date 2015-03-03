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
			if operation in ["call"]:
				if operand2 != '':
				    result += "\tmove\t$a0, "+register_assignments[operand2]+"""
"""
				result += "\tjal\t"+str(operand1)+"""
"""
				result += "\tmove\t"+register_assignments[destination]+", $v0"+"""
"""
			elif operation in ["return"]:
				is_immediate, s = handle_possible_immediate(destination)
				if is_immediate:
					result += "\tli\t$t1, "+s+"""
"""
					destination = "$t1"
				else:
					result += "\tmove\t$t1, "+register_assignments[destination]+"""
"""	
				result += """\tmove\t$v0, $t1
"""
				result += """\tjr $ra
"""			
			elif operation in ["="]:
				is_immediate, s = handle_possible_immediate(operand1)
				if is_immediate:
					result += "\tli	"+register_assignments[destination]+", "+str(operand1)+"""
"""
				else:
					result += "\tmove	"+register_assignments[destination]+", "+register_assignments[operand1]+"""
"""
			elif operation in ["<="]:
				is_immediate1, s1 = handle_possible_immediate(operand1)
				if is_immediate1:
					result += "\tli	"+register_assignments[destination]+", "+str(s1)+"""
"""
					operand1 = destination
	
				is_immediate2, s2 = handle_possible_immediate(operand2)
				if is_immediate2:
					result += "\tli	"+register_assignments[destination]+", "+str(s2)+"""
"""
					operand2 = destination

				result += "\tslt	"+register_assignments[destination]+", "+register_assignments[operand2]+", "+register_assignments[operand1]+"""
"""
				result += "\taddi	$t2, $0, 1"+"""
"""
				result += "\tsub	"+register_assignments[destination]+", $t2, "+register_assignments[destination]+"""
"""
			elif operation in ["+"]:
				is_immediate, s = handle_possible_immediate(operand1)
				if is_immediate:
					result += "\taddi	"+register_assignments[destination]+", "+register_assignments[operand2]+", "+operand1+"""
"""
				else:
					is_immediate, s = handle_possible_immediate(operand2)
					if is_immediate:
						
						result += "\taddi	"+register_assignments[destination]+", "+register_assignments[operand1]+", "+str(operand2)+"""
"""
					else:
						result += "\tadd	"+register_assignments[destination]+", "+register_assignments[operand1]+", 				"+register_assignments[operand2]+"""
"""
			elif operation in ["*"]:
				is_immediate1, s1 = handle_possible_immediate(operand1)
				if is_immediate1:
					result += "\tli	"+register_assignments[destination]+", "+str(s1)+"""
"""
					operand1 = destination
	
				is_immediate2, s2 = handle_possible_immediate(operand2)
				if is_immediate2:
					result += "\tli	"+register_assignments[destination]+", "+str(s2)+"""
"""
					operand2 = destination

				result += "\tmult\t"+register_assignments[operand1]+", "+register_assignments[operand2]+"""
"""
				result += "\tmflo\t"+register_assignments[destination]+"""
"""
			elif operation in ["conditional_branch"]:
				result += "\tbne\t$0, "+register_assignments[operand1]+", "+destination+"""
"""				
			else:
				asm, num_args = op_to_asm[operation]
				labels = [key for key, value in funct_info.the_symbol_table.values[funct_info.name].items() if isinstance(value,mk3ac.Label)]
				def keep_if_label(x):
					if (x in labels):
						return x
					else:
						return register_assignments[x]
				result += "\t"+asm+"\t"+", ".join([keep_if_label(item) for item in [destination,operand1,operand2][:num_args]])+"""
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
			putint(result);
			result = result * j;
		};
		putint(result);
	};
	exit();
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
        if key in ["putint","exit"]:
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
"""+asm+"""
puts:
        li      $v0, 4                  # load appropriate system call code into register $v0;
                                        # code for printing string is 4
        syscall                         # call operating system to perform print operation
        jr      $ra

getint:
        li      $v0, 5                  # load appropriate system call code into register $v0;
                                        # code for reading integer is 5
        syscall
        jr      $ra

putint:
        li      $v0, 1                  # load appropriate system call code into register $v0;
                                        # code for printing integer is 1
        syscall
        jr      $ra
exit:
        li      $v0, 10                 # system call code for exit = 10
        syscall                         # call operating sys
"""
        with open("output.s","w") as f:
            f.write(asm)