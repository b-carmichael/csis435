"""
	Does register assignment stuff

	When a local is accessed, generates code to bring it from the stack into a register

	When a local is written to, generates code to then write it back to the stack

	$t1 gets operand1
	$t2 gets operand2
	$t3 has the destination
	$t4 gets immediates
"""
class VariableAccess(object):
	def __init__(self,funct_info):
		self.offsets_of_locals = funct_info.offsets_of_locals
	def code_to_load(self,operand,register):
		offset = self.offsets_of_locals[operand]
		return """lw """+register+", "+str(offset)+"""($sp)		# """+str(operand)
	def code_to_store(self,destination,which_register):
		offset = self.offsets_of_locals[destination]
		return """sw """+which_register+", "+str(offset)+"""($sp)		# """+str(destination)
	def register_for(self,arg):
		if arg == "generic_load":
			return "$t5"
		else:
			assert(False)
			
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

