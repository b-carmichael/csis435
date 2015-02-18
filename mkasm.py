import sys
import pprint

import pycparser
import mksymtab
import mk3ac

# WORK HERE
def space_needed_on_stack_and_offsets(st,func_name):
    some_function = st.values[func_name]
    space_so_far = 0
    struct_like_type = []
    for key,value in some_function.items():
        if key == "...":
            pass
        elif key == "return":
            pass
        elif isinstance(value,mk3ac.Label):
            pass
        else:
            struct_like_type.append((key,value))
    return dict(st.offsets_and_types_of_elements(struct_like_type))

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
    pprint.pprint(st.values.values)
    mk3ac.make3ac(st)
    pprint.pprint(st.values.values)

