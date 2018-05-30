import sys
import os
import re
import xml.etree.ElementTree as ET
from collections import deque
import time
#from pprint import pprint as pprint

#error outputs:
# 52 error in semantic checks of input code IPPcode18
# 53 bad types of operands
# 54 doesn't exist variable but label exists
# 55 doesn't exist label
# 56 missing value
# 57 div 0
# 58 error in string

#Array of instructions
array_of_instr = ["MOVE", "CREATEFRAME",	"PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT",
	"READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "DPRINT", "BREAK"]

#the second argument on stdin
param1 = sys.argv[1]

if param1 == "--help":
	print("The program retrieves the XML representation of the program from the specified file and interprets this program using standard input and output.")  
	print("You can use parametr '--source=file' for input XML file.")

elif param1[0:9] == "--source=":
	adress_file = param1[9:]

else:
	sys.stderr.write('Error in a parametr.\n')
	sys.exit(10)

#Regex
var_match = "^(GF|TF|LF)@([^\W()\d]|[$_&%*\-]){1}([^\W]|[$_&%*\-])*$"
bool_match = "^(true|false)$"
int_match = "^(-|\+){0,1}[0-9]+$"
string_match = "^(\\\[0-9]{3}|\d|$|&|;|<|>|[^\W|\t|\r|\'|\"|\s])*$"
label_match = "^([^\W()\d]|[$_&%*\-]){1}([^\W]|[$_&%*\-])*$"
dec_match = "^(\\\[0-9]{3})*$"

#Control XML representation
class Parsing_class():
	
	def __init__(self, adress_file):
		self.file = adress_file
		self.tree = ET.parse(adress_file)
		self.root = self.tree.getroot()
		self.parsed_file = None
		self.opcode = None
		
		
	def parse_me(self):
		self.parsed_file = {} #save information about instructions  (order like key, { instruction  {arg, (type and value)}})
		
		#If tag is a "program" at the beginning and at the ending tags
		if(self.root.tag != "program"):
			sys.stderr.write('Semantic error. Expected tag \'program\' \n')
			exit(31)

		#If tag "language" is correct
		if(self.root.keys()[0] != "language"):
			sys.stderr.write('Semantic error. Tag "language" isn\'t correct.\n')
			exit(31)

		#If language is IPPcode18
		if(self.root.attrib['language'] != "IPPcode18"):
			sys.stderr.write('Semantic error. Atttibute in the first line should be \'IPPcode18\'.\n')
			exit(32)

		#save orders to the list 
		self.LIST_order=[]
		#Key for dictionary
		self.counter = 0
		for self.child in self.root:
			if int(self.child.attrib['order']) in self.LIST_order:
				sys.stderr.write('This order has already existed.\n')
				exit(32)

			self.LIST_order.append(int(self.child.attrib['order']))
	
			count_of_argument = 0

			#If after tag any text after tag
			if(self.child.text.strip() != ""):
				sys.stderr.write('Semantic error. Broken structure.\n')
				exit(31)
			#If not instruction	
			if self.child.tag != "instruction":
				sys.stderr.write('Semantic error.\n')
				exit(31) 

			#if doesn't exist instruction
			if self.child.attrib['opcode'] not in array_of_instr:
				sys.stderr.write('Doesn\'t exist instruction.\n')
				exit(32)
			
			#Save instruction to the dictionary
			self.parsed_file[int(self.child.attrib['order'])] = {"instr": self.child.attrib['opcode'] }
		
			#control of elements (argumenty)
			for self.element in self.child:
				if(count_of_argument > 3):
					sys.stderr.write('Bad count of arguments.\n')
					exit(52)
				else:
					count_of_argument += 1

				if self.element.tag in self.parsed_file[int(self.child.attrib['order'])]:
					sys.stderr.write('This number of argument has already existed.\n')
					exit(52)
				else:
					#print(self.element.attrib['type'])
					#print(self.element.tag, ":", self.element.text)
					self.parsed_file[int(self.child.attrib['order'])][self.element.tag] = self.element.attrib['type'], self.element.text
			self.counter += 1	

parsing = Parsing_class(adress_file)
parsing.parse_me()

ORDER = parsing.LIST_order[:]

#control the count of the arguments in each instruction 
class Process_instructions():
	#print("Its in class DONE:", parsing.parsed_file)
	
	def Count_of_arguments(self):
		while (len(ORDER) != 0):
			i = ORDER[0]
			del ORDER[0]
			
			instr = parsing.parsed_file[i]['instr']
			
			#print("INSTR: ", parsing.parsed_file[i], "\n")

			#Instructions without arguments
			if(instr == "CREATEFRAME") or ( instr == "PUSHFRAME") or (instr == "POPFRAME") or (instr == "RETURN") or (instr == "BREAK"):
				if len(parsing.parsed_file[i]) > 1:
					sys.stderr.write('Mustn\'t be arguments.\n')
					exit(31)
			#Instructions with one argument
			elif (instr == "DEFVAR") or (instr == "CALL") or (instr == "PUSHS") or (instr == "POPS") or (instr == "WRITE") or (instr == "LABEL") or (instr == "JUMP") or (instr == "DPRINT"):
				if len(parsing.parsed_file[i]) > 2:
					sys.stderr.write('Expected one argument.\n')
					exit(31)
				if 'arg1'not in parsing.parsed_file[i]:
					sys.stderr.write('Expected "arg1" as an argument.\n')
					exit(31)
			#Instructions with two arguments		
			elif (instr == "MOVE") or (instr == "INT2CHAR") or (instr == "READ") or (instr == "STRLEN") or (instr == "TYPE") or ( instr == "NOT"):
				if len(parsing.parsed_file[i]) > 3:
					sys.stderr.write('Expected two argument.\n')
					exit(31)
				if ('arg1' not in parsing.parsed_file[i]) or ('arg2' not in parsing.parsed_file[i]) :
					sys.stderr.write('Expected "arg1" and "arg2" as an argument.\n')
					exit(31)
			#Instructions with three arguments
			else:	
				if len(parsing.parsed_file[i]) > 4:
					sys.stderr.write('Expected three argument.\n')
					exit(31)
				if ('arg1' not in parsing.parsed_file[i]) or ('arg2' not in parsing.parsed_file[i]) or ('arg3' not in parsing.parsed_file[i]):
					sys.stderr.write('Expected "arg1" and "arg2" as an argument.\n')
					exit(31)
		

Check_count_of_arg = Process_instructions()
Check_count_of_arg.Count_of_arguments()

#Control if values in this types are correct
def Matching_arg(type, arg):
	
	#When value is empty
	if (type != "string") and (arg == None):
		sys.stderr.write('Missing value.\n')
		exit(56)
	#if value of type var is correct 
	if (type == "var"):
		compiling = re.compile(var_match, re.IGNORECASE | re.UNICODE)
		var = re.match(var_match, arg)
		if var == None:
			sys.stderr.write('Bad value of argument. Type: var\n')
			exit(52)
	#if value of type int is correct 
	elif (type == "int"):
		compiling = re.compile(int_match, re.IGNORECASE | re.UNICODE)
		integer = re.match(int_match, arg)
		if integer == None:
			sys.stderr.write('Bad value of argument. Type: int\n')
			exit(52)
	#if value of type bool is correct 
	elif(type == "bool"):
		compiling = re.compile(bool_match, re.IGNORECASE | re.UNICODE)
		boolean = re.match(bool_match, arg)
		if boolean == None:
			sys.stderr.write('Bad value of argument. Type: bool.\n')
			exit(52)	
	#if value of type string is correct 
	elif(type == "string"):

		compiling = re.compile(string_match, re.IGNORECASE | re.UNICODE)
		string = re.match(string_match, arg)
		if string == None:
			sys.stderr.write('Bad value of argument. Type: string.\n')
			exit(52)
	#if value of type label is correct 
	elif(type == "label"):
		compiling = re.compile(label_match, re.IGNORECASE | re.UNICODE)
		label = re.match(label_match, arg)
		if label == None:
			sys.stderr.write('Bad value of argument. Type: label.\n')
			exit(52)
	#Type dousn't exist
	else:
		sys.stderr.write('This type doesn\'t exist.\n')
		exit(52)

#Control if variable is in frame
def Control_var(var_key, TF_list, LF_list, GF_list):
	#Temporary frame
	if var_key[0:2] == "TF" :
		if TF_list == None:
			sys.stderr.write('Temporary frame doesn\'t exist.\n')
			exit(55)
		else:
			if var_key[3:] not in TF_list:
				sys.stderr.write('This variable doesn\'t exist.\n')
				exit(54)
	#Local frame				
	elif var_key[0:2] == "LF":
		if len(LF_list) == 0:
			sys.stderr.write('Local frame doesn\'t exist.\n')
			exit(55)
		else:
			if var_key[3:] not in LF_list:
				sys.stderr.write('This variable doesn\'t exist.\n')
				exit(54)
	#Global frame						
	else:
		if var_key[3:] not in GF_list:

			sys.stderr.write('This variable doesn\'t exist.\n')
			exit(54)

#Function for instructions ADD, SUB, MUL, IDIV to control the second and the third arguments of type var, should contain inside type int.
def Control_first_arg(value_of_var, TF_list, LF_list, GF_list):
	#For Temporary frame
	if value_of_var[0:2] == "TF" :

		if TF_list == None:
			sys.stderr.write('Temporary frame doesn\'t exist.\n')
			exit(55)
		else:
			if value_of_var[3:] not in TF_list:
				sys.stderr.write('This variable doesn\'t exist.\n')
				exit(54)

			if TF_list[value_of_var[3:]] == None:
				sys.stderr.write('This variable doesn\'t have a value.\n')
				exit(56)

			if TF_list[value_of_var[3:]][0] != "int":
				sys.stderr.write('Bad type of the second variable in instruction.\n')
				exit(53)
			else:
				operand = int(TF_list[value_of_var[3:]][1])
	#For Local frame			
	elif value_of_var[0:2] == "LF":

		if len(LF_list) == 0:
			sys.stderr.write('Local frame doesn\'t exist.\n')
			exit(55)
		else:
			if value_of_var[3:] not in LF_list:
				sys.stderr.write('This variable doesn\'t exist.\n')
				exit(54)

			if LF_list[value_of_var[3:]] == None:
				sys.stderr.write('This variable doesn\'t have a value.\n')
				exit(56)

			if LF_list[value_of_var[3:]][0] != "int":
				sys.stderr.write('Bad type of the second variable in instruction.\n')
				exit(53)
			else:
				operand = int(LF_list[value_of_var[3:]][1])
	#For Global frame
	else:

		if value_of_var[3:] not in GF_list:
			sys.stderr.write('This variable doesn\'t exist.\n')
			exit(54)
		if GF_list[value_of_var[3:]] == None:
			sys.stderr.write('This variable doesn\'t have a value.\n')
			exit(56)
		if GF_list[value_of_var[3:]][0] != "int":
			sys.stderr.write('Bad type of the second variable in instruction.\n')
			exit(53)
		else:
			operand = int(GF_list[value_of_var[3:]][1])
	return operand

#Save all labels to dictionary (List of labels)
LABEL_list = {}

#Control at the beginning all labels and write it to LABEL_list
def Control_label():
 	
	Order_list = parsing.LIST_order[:] #Numbers of instructions
	Order_list.sort()
	control_order=0
			
	while(len(Order_list) != 0):
		it = Order_list[0]
		del Order_list[0]
		control_order += 1
		
		if it != control_order:
			sys.stderr.write('Bad number of the order.\n')
			exit(31)

		instuct = parsing.parsed_file[it]['instr']

		if instuct == "LABEL":
			type_of_arg1 = parsing.parsed_file[it]['arg1'][0]
			var_key = parsing.parsed_file[it]['arg1'][1]

			if(type_of_arg1 == "label"):
				Matching_arg("label", var_key)
				if 	var_key in LABEL_list:
					sys.stderr.write('This label has already existed.\n')
					exit(52)
				else:
					LABEL_list[var_key] = (it)

			else:
				sys.stderr.write('Expected type "label" in the argument in instruction LABEL.\n')
				exit(53)

#Process all functions
def Controlling():
	GF_list = {} #List of variables in Global frame
	TF_list = None #List of variables in Temporary frame
	LF_list = {} #List of variables in Local frame
	stack = [] #List of values in data stack
	CALL_list = [] #List of labels what are in instruction CALL
	counter_LF = 0 #for saving tamporary frames
	#print("LABEL_list: ", LABEL_list)
	LIST_order = parsing.LIST_order[:] #Numbers of instructions
	LIST_order.sort()
	i = 1
	counter_of_instruction = 0 #For print in instruction BREAK 
	while (i <= len(LIST_order) ):
	
		instruction = parsing.parsed_file[i]['instr']
		
		#Work with frames and functions
		
		if(instruction == "MOVE"):
		
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			
			#First arg
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
			else:
				sys.stderr.write('Expected type "var" in the first argument in instruction MOVE.\n')
				exit(53)
			
			#Second arg
			if(type_of_arg2 == "var"):
				Matching_arg("var", value_of_var)
				#print("LF VAR: ", LF_list[counter_LF-1][value_of_var[3:]][0])
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				
				if value_of_var[0:2] == "LF":
					if (LF_list[counter_LF-1][value_of_var[3:]] == None):
						sys.stderr.write('Not initialized variable in the second argument in instruction MOVE.\n')
						exit(56)
					type_of_arg2 = LF_list[counter_LF-1][value_of_var[3:]][0]
					value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
				
				elif value_of_var[0:2] == "TF":
					if (TF_list[value_of_var[3:]] == None):
						sys.stderr.write('Not initialized variable in the second argument in instruction MOVE.\n')
						exit(56)
					type_of_arg2 = TF_list[value_of_var[3:]][0]
					value_of_var = TF_list[value_of_var[3:]][1]

				else: 
					
					if (GF_list[value_of_var[3:]] == None):
						sys.stderr.write('Not initialized variable in the second argument in instruction MOVE.\n')
						exit(56)
					type_of_arg2 = GF_list[value_of_var[3:]][0]
					value_of_var = GF_list[value_of_var[3:]][1]

			elif (type_of_arg2 == "int") or (type_of_arg2 == "bool"):
				Matching_arg(type_of_arg2, value_of_var)
			elif (type_of_arg2 == "string"):
				if value_of_var == None:
					value_of_var = ""
				Matching_arg(type_of_arg2, value_of_var)
			else:
				sys.stderr.write('Expected other type in the second argument in instruction MOVE.\n')
				exit(53)

			#Save to the right frame 
			if var_key[0:2] == "GF":
				GF_list[var_key[3:]] = type_of_arg2, value_of_var
			elif var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = type_of_arg2, value_of_var
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = type_of_arg2, value_of_var
			else:
				sys.stderr.write('Bad frame of var in instruction MOVE.\n')
				exit(53)

		if(instruction == "CREATEFRAME"):
			TF_list = {}
			
		
		if(instruction == "PUSHFRAME"):
			if TF_list == None:
				sys.stderr.write('Temporary frame doesn\'t exist.\n')
				exit(55)
			else:
				LF_list[counter_LF] = TF_list
				counter_LF += 1
				TF_list = None
				

		if(instruction == "POPFRAME"):
			if len(LF_list) == 0:
				sys.stderr.write('Local frame is empty.\n')
				exit(55)
			else:
				TF_list = LF_list[counter_LF-1]
				del LF_list[counter_LF-1]
				counter_LF -= 1

		if(instruction == "DEFVAR"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)	
							
				if var_key[0:2] == "TF" :
					if TF_list == None:
						sys.stderr.write('Temporary frame doesn\'t exist.\n')
						exit(55)
					else:
						if var_key[3:] in TF_list:
							sys.stderr.write('This variable has already existed.\n')
							exit(59)
						else:
							TF_list[var_key[3:]] = None;
				
				elif var_key[0:2] == "LF":
					if len(LF_list) == 0:
						sys.stderr.write('Local frame doesn\'t exist.\n')
						exit(55)
					else:
						if var_key[3:] in LF_list[counter_LF-1]:
							sys.stderr.write('This variable has already existed.\n')
							exit(59)
						else:
							LF_list[counter_LF-1][var_key[3:]] = None;
				else:
					if var_key[3:] in GF_list:
						sys.stderr.write('This variable has already existed.\n')
						exit(59)
					else:
						GF_list[var_key[3:]]=None;


			else:
				sys.stderr.write('Expected type "var" in the argument in instruction DEFVAR.\n')
				exit(53)
		
		if(instruction == "CALL"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			
			if(type_of_arg1 == "label"):
				Matching_arg("label", var_key)
				if 	var_key not in LABEL_list:
					sys.stderr.write('This label doesn\'t exist.\n')
					exit(54)

				else:
					CALL_list.append(i)
					i = int(LABEL_list[var_key]-1)
					

			else:
				sys.stderr.write('Expected type "label" in the argument in instruction CALL.\n')
				exit(53)

		if (instruction == "RETURN"):
			if (len(CALL_list) == 0):
				sys.stderr.write('Expected instruction CALL before RETURN\n')
				exit(56)
			else:
				i = int(CALL_list.pop())
		
		#Data stack	
		if (instruction == "PUSHS"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			if (type_of_arg1 == "var"):
				Matching_arg(type_of_arg1, var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					type_of_arg1 = TF_list[var_key[3:]][0]
					var_key = TF_list[var_key[3:]][1]
				elif var_key[0:2] == "LF":
					type_of_arg1 = LF_list[counter_LF-1][var_key[3:]][0]
					var_key = LF_list[counter_LF-1][var_key[3:]][1]
				else:
					type_of_arg1 = GF_list[var_key[3:]][0]
					var_key = GF_list[var_key[3:]][1]
				stack.append(type_of_arg1)
				stack.append(var_key)
			elif (type_of_arg1 == "string"):
				if var_key == None:
					var_key = ""
				Matching_arg(type_of_arg1, var_key)
				stack.append(type_of_arg1)
				stack.append(var_key)
			elif (type_of_arg1 == "bool") or (type_of_arg1 == "int"):
				Matching_arg(type_of_arg1, var_key)
				stack.append(type_of_arg1)
				stack.append(var_key)
			else:
				sys.stderr.write('Expected other type in the argument in instruction PUSHS.\n')
				exit(53)

		if (instruction == "POPS"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			if len(stack) == 0:
				sys.stderr.write('Stack is empty.\n')
				exit(56)
			
			if type_of_arg1 == "var":
				Matching_arg("var", var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				var_stack = stack.pop()
				type_stack = stack.pop()
				if var_key[0:2] == "GF":
					GF_list[var_key[3:]] = type_stack, var_stack	
				elif var_key[0:2] == "LF":
					LF_list[counter_LF-1][var_key[3:]] = type_stack, var_stack
				else:
					TF_list[var_key[3:]] = type_stack, var_stack
			else:
				sys.stderr.write('Expected other type in the argument in instruction POPS.\n')
				exit(53)
		#Arithmetic, relational, bool and conversion instructions 
		if (instruction == "ADD"):
			
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction ADD.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)
				
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand1 = int(value_of_var)


			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction ADD.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)
			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction ADD.\n')
				exit(53)


			result = operand1 + operand2
			if var_key[0:2] == "GF":
				GF_list[var_key[3:]] = "int", result
			elif var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			else:
				TF_list[var_key[3:]] = "int", result

		if (instruction == "SUB"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction SUB.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)
				
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand1 = int(value_of_var)


			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction SUB.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)
				
			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction SUB.\n')
				exit(53)

			result = operand2 - operand1
			if var_key[0:2] == "GF":
				GF_list[var_key[3:]] = "int", result
			elif var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			else:
				TF_list[var_key[3:]] = "int", result

			
		if (instruction == "MUL"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction MUL.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)
				
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand1 = int(value_of_var)


			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction MUL.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)
				
			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction MUL.\n')
				exit(53)

			result = operand2 * operand1
			if var_key[0:2] == "GF":
				GF_list[var_key[3:]] = "int", result
			elif var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			else:
				TF_list[var_key[3:]] = "int", result

		if (instruction == "IDIV"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction IDIV.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)
				
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand1 = int(value_of_var)


			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction IDIV.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)

			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction IDIV.\n')
				exit(53)

			if operand2 == 0:
				sys.stderr.write('Div by 0. Instruction IDIV.\n')
				exit(57)
			result = operand1 // operand2
			if var_key[0:2] == "GF":
				GF_list[var_key[3:]] = "int", result
			elif var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			else:
				TF_list[var_key[3:]] = "int", result

		if (instruction == "LT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction LT.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction LT.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction LT.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction LT.\n')
				exit(53)

			#Second and third arguments
			#Type int
			if ((type_of_arg2 == "int") or  (type_of_arg2 == "var")) and ((type_of_arg3 == "int") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if value_of_var < value_of_arg:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] = "bool", "true"
					else:
						GF_list[var_key[3:]] = "bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] = "bool", "false"
					else:
						GF_list[var_key[3:]] = "bool", "false"
					
			
			#Type bool
			elif ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
					else:	
						Control_var(value_of_arg, TF_list, LF_list, GF_list)
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if (value_of_var == "false") and (value_of_arg == "true"):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] = "bool", "true"
					else:

						GF_list[var_key[3:]] = "bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] = "bool", "false"
			#Type string
			elif ((type_of_arg2 == "string")  or (type_of_arg2 == "var")) and ((type_of_arg3 == "string") or (type_of_arg3 == "var")):
				if (type_of_arg2 == "string"):
					if value_of_var == None:
						value_of_var = ""
				if (type_of_arg3 == "string"):
					if value_of_arg == None:
						value_of_arg = ""
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction LT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if (len(value_of_var) < len(value_of_arg)):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] = "bool", "true"
					else:
						GF_list[var_key[3:]] = "bool", "true"
				
				elif (len(value_of_var) == len(value_of_arg)):
					iterator = 0
					while(iterator < len(value_of_arg)):
						if (ord(value_of_var[iterator]) < ord(value_of_arg[iterator])):
							iterator = len(value_of_arg)
							if var_key[0:2] == "TF":
								TF_list[var_key[3:]] = "bool", "true"
							elif var_key[0:2] == "LF":
								LF_list[counter_LF-1][var_key[3:]] = "bool", "true"
							else:
								GF_list[var_key[3:]] = "bool", "true"
						elif (ord(value_of_var[iterator]) > ord(value_of_arg[iterator])):
							iterator = len(value_of_arg)
							if var_key[0:2] == "TF":
								TF_list[var_key[3:]] = "bool", "false"
							elif var_key[0:2] == "LF":
								LF_list[counter_LF-1][var_key[3:]] = "bool", "false"
							else:
								GF_list[var_key[3:]] = "bool", "false"
						else: 
							if iterator == (len(value_of_arg)-1):
								if var_key[0:2] == "TF":
									TF_list[var_key[3:]] ="bool", "false"
								elif var_key[0:2] == "LF":
									LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
								else:
									GF_list[var_key[3:]] ="bool", "false"
						iterator += 1 
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] = "bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] = "bool", "false"
					else:
						GF_list[var_key[3:]] = "bool", "false"

			else:
				sys.stderr.write('Expected the same types of the second and the third arguments LT.\n')
				exit(53)

		if (instruction == "GT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction GT.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction GT.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction GT.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction GT.\n')
				exit(53)

			#Second and third arguments
			#Type int
			if ((type_of_arg2 == "int") or (type_of_arg2 == "var")) and ((type_of_arg3 == "int") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if value_of_var > value_of_arg:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
					
			
			#Type bool
			elif ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if (value_of_var == "true") and (value_of_arg == "false"):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
			#Type string
			elif ((type_of_arg2 == "string")  or (type_of_arg2 == "var")) and ((type_of_arg3 == "string") or (type_of_arg3 == "var")):
				if (type_of_arg2 == "string"):
					if value_of_var == None:
						value_of_var = ""
				if type_of_arg3 == "string":
					if value_of_arg == None:
						value_of_arg = ""
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction GT.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if (len(value_of_var) > len(value_of_arg)):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				elif (len(value_of_var) == len(value_of_arg)):
					iterator = 0
					while(iterator < len(value_of_arg)):
						if (ord(value_of_var[iterator]) > ord(value_of_arg[iterator])):
							iterator = len(value_of_arg)
							if var_key[0:2] == "TF":
								TF_list[var_key[3:]] ="bool", "true"
							elif var_key[0:2] == "LF":
								LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
							else:
								GF_list[var_key[3:]] ="bool", "true"
						elif (ord(value_of_var[iterator]) < ord(value_of_arg[iterator])):
							iterator = len(value_of_arg)
							if var_key[0:2] == "TF":
								TF_list[var_key[3:]] ="bool", "false"
							elif var_key[0:2] == "LF":
								LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
							else:
								GF_list[var_key[3:]] ="bool", "false"
						else: 
							if iterator == (len(value_of_arg)-1):
								if var_key[0:2] == "TF":
									TF_list[var_key[3:]] ="bool", "false"
								elif var_key[0:2] == "LF":
									LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
								else:
									GF_list[var_key[3:]] ="bool", "false"
						
						iterator += 1

				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"

			else:
				sys.stderr.write('Expected the same types of the second and the third arguments GT.\n')
				exit(53)
			
		if (instruction == "EQ"):

			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction EQ.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction EQ.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction EQ.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction EQ.\n')
				exit(53)

			#Second and third arguments
			#Type int
			if ((type_of_arg2 == "int") or (type_of_arg2 == "var")) and ((type_of_arg3 == "int") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if value_of_var == value_of_arg:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
					
			
			#Type bool
			elif ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else: 
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if ((value_of_var == "true") and (value_of_arg == "true")) or ((value_of_var == "false") and (value_of_arg == "false")):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
			#Type string
			elif ((type_of_arg2 == "string")  or (type_of_arg2 == "var")) and ((type_of_arg3 == "string") or (type_of_arg3 == "var")):
				if type_of_arg2 == "string":
					if value_of_var == None:
						value_of_var = ""
				if type_of_arg3 == "string":
					if value_of_arg == None:
						value_of_arg = ""
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction EQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		


				if (len(value_of_var) == len(value_of_arg)):
					iterator = 0
					while(iterator < len(value_of_arg)):
						if (ord(value_of_var[iterator]) == ord(value_of_arg[iterator])):
							if iterator == (len(value_of_arg) -1):
								if var_key[0:2] == "TF":
									TF_list[var_key[3:]] ="bool", "true"
								elif var_key[0:2] == "LF":
									LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
								else:
									GF_list[var_key[3:]] ="bool", "true"
					
						else: 
							iterator = (len(value_of_arg)-1)
							if iterator == (len(value_of_arg)-1):
								if var_key[0:2] == "TF":
									TF_list[var_key[3:]] ="bool", "false"
								elif var_key[0:2] == "LF":
									LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
								else:
									GF_list[var_key[3:]] ="bool", "false"
						
						iterator += 1

				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"

			else:
				sys.stderr.write('Expected the same types in the second and the third arguments EQ.\n')
				exit(53)
			
		if (instruction == "AND"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction AND.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction AND.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction AND.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction AND.\n')
				exit(53)

			#Type bool      The second and third arguments
			if ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else: 
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction AND.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if ((value_of_var == "true") and (value_of_arg == "true")) or ((value_of_var == "false") and (value_of_arg == "false")):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "false"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"

			else:
				sys.stderr.write('Expected type "bool" in the argument in instruction AND.\n')
				exit(53)
			
		if (instruction == "OR"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction OR.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction OR.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction OR.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction OR.\n')
				exit(53)

			#Type bool      The second and third arguments
			if ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction OR.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if ((value_of_var == "false") and (value_of_arg == "false")):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "falsse"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"

			else:
				sys.stderr.write('Expected type "bool" in the argument in instruction OR.\n')
				exit(53)
			
		if (instruction == "NOT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction NOT.\n')
						exit(53)
				elif var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction NOT.\n')
						exit(53)
				else:
					if GF_list[var_key[3:]][0] != "bool":
						sys.stderr.write('Expected type "bool" in the first argument in instruction NOT.\n')
						exit(53)
			else:
				sys.stderr.write('Expected type "var" in the argument in instruction NOT.\n')
				exit(53)

			#Type bool Second argument

			if ((type_of_arg2 == "bool") or (type_of_arg2 == "var")):
				Matching_arg(type_of_arg2, value_of_var)

				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)

					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction NOT.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction NOT.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction NOT.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]

				if (value_of_var == "true"):
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "falsse"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "false"
					else:
						GF_list[var_key[3:]] ="bool", "false"
				else:
					if var_key[0:2] == "TF":
						TF_list[var_key[3:]] ="bool", "true"
					elif var_key[0:2] == "LF":
						LF_list[counter_LF-1][var_key[3:]] ="bool", "true"
					else:
						GF_list[var_key[3:]] ="bool", "true"

			else:
				sys.stderr.write('Expected type "bool" in the argument in instruction NOT.\n')
				exit(53)
		
		if (instruction == "INT2CHAR"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction INT2CHAR.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand = int(value_of_var)

			else:
				sys.stderr.write('Expected type "var" or "int" in the argument in instruction INT2CHAR.\n')
				exit(53)

			if (operand < 0) or (operand > 1114111):
				sys.stderr.write('Out of range. Instruction INT2CHAR.\n')
				exit(58)
			
			operand = chr(operand)
			
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "string", operand
			elif  var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "string", operand
			else:
				GF_list[var_key[3:]] = "string", operand

		if (instruction == "STRI2INT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction STRI2INT.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					Control_var(value_of_var, TF_list, LF_list, GF_list)
				if value_of_var[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRI2INT.\n')
						exit(53)
					else:
						operand1 = LF_list[counter_LF-1][value_of_var[3:]][1]
				elif value_of_var[0:2] == "TF":
					if TF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRI2INT.\n')
						exit(53)
					else:
						operand1 = TF_list[value_of_var[3:]][1]
				else:
					if GF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRI2INT.\n')
						exit(53)
					else:
						operand1 = GF_list[value_of_var[3:]][1]

				
			elif type_of_arg2 == "string":
			
				if value_of_var == None:
					value_of_var = ""
				
				Matching_arg("string", value_of_var)
				operand1 = value_of_var

			else:
				sys.stderr.write('Expected type "var" or "string" in the second argument in instruction STRI2INT.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)
			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the third argument in instruction STRI2INT.\n')
				exit(53)

			if -len(operand1)<= operand2 < len(operand1): 
				result = ord(operand1[operand2])
			else:
				sys.stderr.write('Index out of range in instruction STRI2INT.\n')
				exit(58)
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "int", result
			else:
				GF_list[var_key[3:]] = "int", result
		#Input - output instructions
		if (instruction == "READ"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]

			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction READ.\n')
				exit(53)

			#Second argument  TYPE {BOOL, STRING, INT}
			if(type_of_arg2 == "type"):
				if value_of_var == "int":
					res_in = input()
					compiling = re.compile(int_match, re.IGNORECASE | re.UNICODE)
					integer = re.match(int_match, res_in)
					if integer == None:
						res_in = 0
				elif value_of_var == "string":
					res_in = input()
					compiling = re.compile(string_match, re.IGNORECASE | re.UNICODE)
					string = re.match(string_match, res_in)
					if string == None:
						res_in = ""

				elif value_of_var == "bool":
					res_in = input()
					res_in = res_in.lower()
					compiling = re.compile(bool_match, re.IGNORECASE | re.UNICODE)
					boolean = re.match(bool_match, res_in)
					if boolean == None:
						res_in = "false"
				else:
					sys.stderr.write('Expected values are "string" or "int" or "bool" in the second argument in instruction READ.\n')
					exit(53)
			else:
				sys.stderr.write('Expected type "type" in the second argument in instruction READ.\n')
				exit(53)

			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = value_of_var, res_in
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = value_of_var, res_in
			else:
				GF_list[var_key[3:]] = value_of_var, res_in

		if (instruction == "WRITE"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			Write_list = {}
			if(type_of_arg1 == "var"):

				Matching_arg(type_of_arg1, var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				
				if var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] == "string":
						string = LF_list[counter_LF-1][var_key[3:]][1]
						iterat = 0	
						while(iterat < len(string)):
							if string[iterat] == '\\':
								if string[iterat+1:iterat+4].isdigit():
									string = string[0:iterat] + chr(int(string[iterat+1:iterat+4])) + string[iterat+4:]							
						
						print(string)
					else:
						print(LF_list[counter_LF-1][var_key[3:]][1])
				elif var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] == "string":
						
						string = TF_list[var_key[3:]][1]
						iterat = 0	
						while(iterat < len(string)):
							if string[iterat] == '\\':
								if string[iterat+1:iterat+4].isdigit():
									string = string[0:iterat] + chr(int(string[iterat+1:iterat+4])) + string[iterat+4:]

							iterat += 1
						
						print(string)
					else:
						print(TF_list[var_key[3:]][1])
				else:
					if GF_list[var_key[3:]][0] == "string":

						string = GF_list[var_key[3:]][1]
						iterat = 0	
						while(iterat < len(string)):
							if string[iterat] == '\\':
								if string[iterat+1:iterat+4].isdigit():
									string = string[0:iterat] + chr(int(string[iterat+1:iterat+4])) + string[iterat+4:]

							iterat += 1
						
						print(string)
						
					else:
						print(GF_list[var_key[3:]][1])

			elif (type_of_arg1 == "int") or (type_of_arg1 == "bool"): 
				Matching_arg(type_of_arg1, var_key)
				print(var_key)
							
			elif  (type_of_arg1 == "string"):
				if var_key == None:
					var_key = ""

				it = 0
				while(it < len(var_key)):
					if var_key[it:it+4] == "&lt;":
						var_key = var_key[0:it] + "<" + var_key[it+4:]
					if var_key[it:it+4] == "&gt;":
						var_key = var_key[0:it] + ">" + var_key[it+4:]
					if var_key[it:it+5] == "&amp;":
						var_key = var_key[0:it] + "&" + var_key[it+5:]
					it +=1
				#print("VAR: ", var_key)

				Matching_arg(type_of_arg1, var_key)
				string = var_key
				iterat = 0	
				while(iterat < len(string)):
					if string[iterat] == '\\':
						if string[iterat+1:iterat+4].isdigit():
							string = string[0:iterat] + chr(int(string[iterat+1:iterat+4])) + string[iterat+4:]
					iterat += 1
						
				print(string)

			else:
				sys.stderr.write('Expected other type in the first argument in instruction WRITE.\n')
				exit(53)
			
		if (instruction == "CONCAT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg(type_of_arg1, var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
			else:
				sys.stderr.write('Expected other type in the first argument in instruction CONCAT.\n')
				exit(53)
			#Second argument
			if (type_of_arg2 == "var"):
				Matching_arg(type_of_arg2, value_of_var) 
				if counter_LF != 0:
					Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					Control_var(value_of_var, TF_list, LF_list, GF_list)
				if value_of_var[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
				elif value_of_var[0:2] == "TF":
					if TF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_var = TF_list[value_of_var[3:]][1]
				else:

					if GF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_var = GF_list[value_of_var[3:]][1]

			elif (type_of_arg2 == "string"):
				if value_of_var == None:
					value_of_var = ""
				Matching_arg("string", value_of_var)
			else:
				sys.stderr.write('Expected other type in the second argument in instruction CONCAT.\n')
				exit(53)
			#Third argument
			if (type_of_arg3 == "var"):
				Matching_arg(type_of_arg3, value_of_arg) 
				if counter_LF != 0:
					Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					Control_var(value_of_arg, TF_list, LF_list, GF_list)
				if value_of_arg[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the third argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
				elif value_of_arg[0:2] == "TF":
					if TF_list[value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the third argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_arg = TF_list[value_of_arg[3:]][1]
				else:

					if GF_list[value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the trhird argument in instruction CONCAT.\n')
						exit(53)
					else:
						value_of_arg = GF_list[value_of_arg[3:]][1]

			elif (type_of_arg3 == "string"):
				if value_of_arg == None:
					value_of_arg = ""
				Matching_arg("string", value_of_arg)
			else:
				sys.stderr.write('Expected other type in the third argument in instruction CONCAT.\n')
				exit(53)
			result = value_of_var + value_of_arg
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "string", result
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "string", result 
			else:
				GF_list[var_key[3:]] = "string", result 


		if (instruction == "STRLEN"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg(type_of_arg1, var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
			else:
				sys.stderr.write('Expected other type in the first argument in instruction STRLEN.\n')
				exit(53)
			#Second argument
			if (type_of_arg2 == "var"):
				Matching_arg(type_of_arg2, value_of_var)
				if counter_LF != 0:
					Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					Control_var(value_of_var, TF_list, LF_list, GF_list)
				if value_of_var[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRLEN.\n')
						exit(53)
					else:
						result = len(LF_list[counter_LF-1][value_of_var[3:]][1])
				elif value_of_var[0:2] == "TF":
					if TF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRLEN.\n')
						exit(53)
					else:
						result = len(TF_list[value_of_var[3:]][1])
				else:
					if GF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction STRLEN.\n')
						exit(53)
					else:
						result = len(GF_list[value_of_var[3:]][1])

			elif type_of_arg2 == "string":
				if value_of_var == None:
					result = 0
				else:
					result = len(value_of_var)
			else:
				sys.stderr.write('Expected other type in the second argument in instruction STRLEN.\n')
				exit(53)
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "int", result
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "int", result
			else:
				GF_list[var_key[3:]] = "int", result

		if (instruction == "GETCHAR"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction GETCHAR.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					Control_var(value_of_var, TF_list, LF_list, GF_list)
				if value_of_var[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction GETCHAR.\n')
						exit(53)
					else:
						operand1 = LF_list[counter_LF-1][value_of_var[3:]][1]
				elif value_of_var[0:2] == "TF":
					if TF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction GETCHAR.\n')
						exit(53)
					else:
						operand1 = TF_list[value_of_var[3:]][1]
				else:
					if GF_list[value_of_var[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction GETCHAR.\n')
						exit(53)
					else:
						operand1 = GF_list[value_of_var[3:]][1]

				
			elif type_of_arg2 == "string":
				if value_of_var == None:
					value_of_var = ""
				Matching_arg("string", value_of_var)
				operand1 = value_of_var

			else:
				sys.stderr.write('Expected type "var" or "string" in the second argument in instruction GETCHAR.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				if counter_LF != 0:
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
				else: 
					operand2 = Control_first_arg(value_of_arg, TF_list, LF_list, GF_list)
			
			elif type_of_arg3 == "int":
				Matching_arg("int", value_of_arg)
				operand2 = int(value_of_arg)

			else:
				sys.stderr.write('Expected type "var" or "int" in the third argument in instruction GETCHAR.\n')
				exit(53)

			if -len(operand1)<= operand2 < len(operand1): 
				result = operand1[operand2]
			else:
				sys.stderr.write('Index out of range in instruction GETCHAR.\n')
				exit(58)
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "string", result
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "string", result
			else:
				GF_list[var_key[3:]] = "string", result
		
		if (instruction == "SETCHAR"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "LF":
					if LF_list[counter_LF-1][var_key[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the first argument in instruction SETCHAR.\n')
						exit(53)
					else: 
						var_res = LF_list[counter_LF-1][var_key[3:]][1]
				elif var_key[0:2] == "TF":
					if TF_list[var_key[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the first argument in instruction SETCHAR.\n')
						exit(53)
					else: 
						var_res = TF_list[var_key[3:]][1]
				else: 
					if GF_list[var_key[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the first argument in instruction SETCHAR.\n')
						exit(53)
					else: 
						var_res = GF_list[var_key[3:]][1]

			else:
				sys.stderr.write('Expected type "var" in the first argument in instruction SETCHAR.\n')
				exit(53)

			#Second argument
			if type_of_arg2 == "var":
				Matching_arg("var", value_of_var)
				if counter_LF != 0:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
				else:
					operand1 = Control_first_arg(value_of_var, TF_list, LF_list, GF_list)

				
			elif type_of_arg2 == "int":
				Matching_arg("int", value_of_var)
				operand1 = int(value_of_var)

			else:
				sys.stderr.write('Expected type "var" or "int" in the second argument in instruction SETCHAR.\n')
				exit(53)

			#Third argument
			if type_of_arg3 == "var":
				Matching_arg("var", value_of_arg)
				

				if value_of_arg[0:2] == "LF":
					if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction SETCHAR.\n')
						exit(53)
					else:
						operand2 = LF_list[counter_LF-1][value_of_arg[3:]][1]
				elif value_of_arg[0:2] == "TF":
					if TF_list[value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction SETCHAR.\n')
						exit(53)
					else:
						operand2 = TF_list[value_of_arg[3:]][1]
				else:
					if GF_list[value_of_arg[3:]][0] != "string":
						sys.stderr.write('Expected type "string" in the second argument in instruction SETCHAR.\n')
						exit(53)
					else:
						operand2 = GF_list[value_of_arg[3:]][1]		
				
			elif type_of_arg3 == "string":
				if value_of_arg == None:
					value_of_arg = ""
				Matching_arg("string", value_of_arg)
				operand2 = value_of_arg

			else:
				sys.stderr.write('Expected type "var" or "string" in the third argument in instruction SETCHAR.\n')
				exit(53)

			if -len(var_res)<= operand1 < len(var_res): 
				var_res = var_res[0:operand1] + operand2[0] + var_res[operand1+1:] 
			else:
				sys.stderr.write('Index out of range in instruction SETCHAR.\n')
				exit(58)
			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "string", var_res
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "string", var_res
			else:
				GF_list[var_key[3:]] = "string", var_res
		#Type instruction 	
		if (instruction == "TYPE"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			
			#First argument
			if(type_of_arg1 == "var"):
				Matching_arg("var", var_key)				
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)

			else:
				sys.stderr.write('Expected type "var" in the argument in instruction TYPE.\n')
				exit(53)

			#Second argument
			if (type_of_arg2 == "var"):
				Matching_arg("var", value_of_var)
				if value_of_var[0:2] == "LF":
					if value_of_var[3:] not in LF_list[counter_LF-1]:
						result = ""
					else:
						result = LF_list[counter_LF-1][value_of_var[3:]][0]
				elif value_of_var[0:2] == "TF":
					if value_of_var[3:] not in TF_list:
						result = ""
					else:
						result = TF_list[value_of_var[3:]][0]
				else:
				
					if value_of_var[3:] not in GF_list:
						result = ""
					else:
						result = GF_list[value_of_var[3:]][0]
				
			elif (type_of_arg2 == "int"): 
				Matching_arg("int", value_of_var)
				result = "int"
			elif (type_of_arg2 == "string"):
				if value_of_var == None:
					value_of_var = ""
				Matching_arg("string", value_of_var)
				result = "string"
			elif (type_of_arg2 == "bool"):
				Matching_arg("bool", value_of_var)
				result = "bool"
			
			else: 
				sys.stderr.write('Expected other type in the argument in instruction TYPE.\n')
				exit(53)

			if var_key[0:2] == "LF":
				LF_list[counter_LF-1][var_key[3:]] = "string", result
			elif var_key[0:2] == "TF":
				TF_list[var_key[3:]] = "string", result
			else:
				GF_list[var_key[3:]] = "string", result
		#Instructions for controlling the program
		if (instruction == "LABEL"):
			pass
		if (instruction == "JUMP"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			
			if(type_of_arg1 == "label"):
				Matching_arg("label", var_key)
				if 	var_key not in LABEL_list:
					sys.stderr.write('This label doesn\'t exist.\n')
					exit(54)

				else:
					i = int(LABEL_list[var_key]-1)	

			else:
				sys.stderr.write('Expected type "label" in the argument in instruction JUMP.\n')
				exit(53)
		if (instruction == "JUMPIFEQ"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			#First argument
			
			if(type_of_arg1 == "label"):
				Matching_arg("label", var_key)
				if 	var_key not in LABEL_list:
					sys.stderr.write('This label doesn\'t exist.\n')
					exit(54)

			else:
				sys.stderr.write('Expected type "label" in the argument in instruction JUMPIFEQ.\n')
				exit(53)

			#Second and third arguments
			#Type int
			if ((type_of_arg2 == "int") or (type_of_arg2 == "var")) and ((type_of_arg3 == "int") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0: 
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else: 
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if value_of_var == value_of_arg:
					i = int(LABEL_list[var_key]-1)						
			
			#Type bool
			elif ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0: 
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if ((value_of_var == "true") and (value_of_arg == "true")) or ((value_of_var == "false") and (value_of_arg == "false")):
					i = int(LABEL_list[var_key]-1)	
		
			#Type string
			elif ((type_of_arg2 == "string")  or (type_of_arg2 == "var")) and ((type_of_arg3 == "string") or (type_of_arg3 == "var")):
				
				if type_of_arg2 == "string":
					if value_of_var == None:
						value_of_var = ""
				if type_of_arg3 == "string":
					if value_of_arg == None:
						value_of_arg = ""

				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				
				if type_of_arg2 == "var":
					if counter_LF != 0 :
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:	
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if (len(value_of_var) == len(value_of_arg)):
					iterator = 0
					while(iterator < len(value_of_arg)):
						if (ord(value_of_var[iterator]) == ord(value_of_arg[iterator])):
							if iterator == (len(value_of_arg)-1):
								i = int(LABEL_list[var_key]-1)

							iterator += 1
					
						else: 
							iterator = len(value_of_arg)


			else:
				sys.stderr.write('Expected the same types in the second and the third arguments JUMPIFEQ.\n')
				exit(53)
		
		if (instruction == "JUMPIFNEQ"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			type_of_arg2 = parsing.parsed_file[i]['arg2'][0]
			value_of_var = parsing.parsed_file[i]['arg2'][1]
			type_of_arg3 = parsing.parsed_file[i]['arg3'][0]
			value_of_arg = parsing.parsed_file[i]['arg3'][1]
			#First argument
			
			if(type_of_arg1 == "label"):
				Matching_arg("label", var_key)
				if 	var_key not in LABEL_list:
					sys.stderr.write('This label doesn\'t exist.\n')
					exit(54)

			else:
				sys.stderr.write('Expected type "label" in the argument in instruction JUMPIFNEQ.\n')
				exit(53)

			#Second and third arguments
			#Type int
			if ((type_of_arg2 == "int") or (type_of_arg2 == "var")) and ((type_of_arg3 == "int") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)	
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "int":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		

				if value_of_var != value_of_arg:
					i = int(LABEL_list[var_key]-1)						
			
			#Type bool
			elif ((type_of_arg2 == "bool") or (type_of_arg2 == "var")) and ((type_of_arg3 == "bool") or (type_of_arg3 == "var")):
				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "bool":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]	

				if ((value_of_var == "false") and (value_of_arg == "true")) or ((value_of_var == "true") and (value_of_arg == "false")):
					i = int(LABEL_list[var_key]-1)	
		
			#Type string
			elif ((type_of_arg2 == "string")  or (type_of_arg2 == "var")) and ((type_of_arg3 == "string") or (type_of_arg3 == "var")):
				
				if type_of_arg2 == "string":
					if value_of_var == None:
						value_of_var = ""
				if type_of_arg3 == "string":
					if value_of_arg == None:
						value_of_arg = ""

				Matching_arg(type_of_arg2, value_of_var)
				Matching_arg(type_of_arg3, value_of_arg)
				
				if type_of_arg2 == "var":
					if counter_LF != 0:
						Control_var(value_of_var, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_var, TF_list, LF_list, GF_list)
					if value_of_var[0:2] == "TF":
						if TF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = TF_list[value_of_var[3:]][1]
					elif value_of_var[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = LF_list[counter_LF-1][value_of_var[3:]][1]
					else:
						if GF_list[value_of_var[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_var = GF_list[value_of_var[3:]][1]
					
				if type_of_arg3 == "var":
					if counter_LF != 0:
						Control_var(value_of_arg, TF_list, LF_list[counter_LF-1], GF_list)
					else:
						Control_var(value_of_arg, TF_list, LF_list, GF_list)	
					if value_of_arg[0:2] == "TF":
						if TF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = TF_list[value_of_arg[3:]][1]
					elif value_of_arg[0:2] == "LF":
						if LF_list[counter_LF-1][value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = LF_list[counter_LF-1][value_of_arg[3:]][1]
					else:
						if GF_list[value_of_arg[3:]][0] != "string":
							sys.stderr.write('Expected the same types in the second and third arguments in instruction JUMPIFNEQ.\n')
							exit(53)
						else:
							value_of_arg = GF_list[value_of_arg[3:]][1]		


				if (len(value_of_var) == len(value_of_arg)):
					iterator = 0
					while(iterator < len(value_of_arg)):
						if (ord(value_of_var[iterator]) == ord(value_of_arg[iterator])):
							
							iterator += 1
					
						else: 
							i = int(LABEL_list[var_key]-1)
				else:
					i = int(LABEL_list[var_key]-1)
			else:
				sys.stderr.write('Expected the same types in the second and the third arguments JUMPIFNEQ.\n')
				exit(53)
		#Tuning instructions
		if (instruction == "DPRINT"):
			type_of_arg1 = parsing.parsed_file[i]['arg1'][0]
			var_key = parsing.parsed_file[i]['arg1'][1]
			if type_of_arg1 == "var":
				Matching_arg("var", var_key)
				if counter_LF != 0 :
					Control_var(var_key, TF_list, LF_list[counter_LF-1], GF_list)
				else:	
					Control_var(var_key, TF_list, LF_list, GF_list)
				if var_key[0:2] == "LF":
					string = ""
					string += str(LF_list[counter_LF-1][var_key[3:]][1])
					string += "\n"
					sys.stderr.write(string)
				elif var_key[0:2] == "TF":
					string = ""
					string += str(TF_list[var_key[3:]][1])
					string += "\n"
					sys.stderr.write(string)
				else:
					string = ""
					string += str(GF_list[var_key[3:]][1])
					string += "\n"
					sys.stderr.write(string)
				
			elif type_of_arg1 == "int":
				Matching_arg("int", var_key)
				string = ""
				string += str(var_key)
				string += "\n"
				sys.stderr.write(string)

			elif type_of_arg1 == "bool":
				Matching_arg("bool", var_key)
				string = ""
				string += str(var_key)
				string += "\n"
				sys.stderr.write(string)
			
			elif type_of_arg1 == "string":
				if var_key == None:
					var_key = ""
				Matching_arg("string", var_key)
				string = ""
				string += str(var_key)
				string += "\n"
				sys.stderr.write(string)
			else:
				sys.stderr.write('Expected other type in the argument in instruction DPRINT.\n')
				exit(53)


		if (instruction == "BREAK"):
			string = ""
			string +="Count of instruction: "
			string += str(counter_of_instruction)
			string += "\n"
			string += "Global frame: "
			string += str(GF_list)
			string += "\n"
			string += "Lokal frame: "
			if counter_LF != 0:
				string += str(LF_list[counter_LF-1])
			else:
				string += "None"
			string += "\n"
			string += "Temporary frame: "
			string += str(TF_list)
			string += "\n"
			sys.stderr.write(string)
		i +=1
		counter_of_instruction += 1

Control_label()
Controlling()

