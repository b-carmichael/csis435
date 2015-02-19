import sys
import pprint

import pycparser
import mksymtab
import mk3ac

def process_3ac(the_3ac):
	result = ""
	print (the_3ac)

# WORK HERE
class FunctionInformation(object):
    def __init__(self,st):
        self.the_symbol_table = st
        
	
def space_needed_on_stack_and_offsets(st,func_name):
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
            result.body = process_3ac(value)
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
        result = space_needed_on_stack_and_offsets(st,key)
        pprint.pprint(result.args)
        print result.size_of_locals
        pprint.pprint(result.offsets_of_locals)
        pprint.pprint(result.return_type)
        pprint.pprint(result.body)
        
    

