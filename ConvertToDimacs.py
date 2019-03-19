import re
# SENT ::= DISJ | DISJ IMPOP SENT
# DISJ ::= CONJ{OROP CONJ}
# CONJ ::= LIT{ANDOP LIT}
# LIT ::= ATOM | NEGOP ATOM
# ATOM ::= VAR | LPAREN SENT RPAREN

records = {}
num_records = 0

def get_record(sentence):	
	global num_records
	global records

	principle_operator = get_principle_operator(sentence)
	while(principle_operator == -1 and not is_variable(sentence)):
		sentence = sentence[1:-1]
		principle_operator = get_principle_operator(sentence)

	key_value = ''
	for char in sentence:
		key_value += char

	if key_value in records:
		return records.get(key_value)
	num_records += 1
	records[key_value] = num_records
	return num_records

#	Returns the index of the principle operator of a sentence
#	Returns -1 if the sentence is an ATOM
def get_principle_operator(sentence):
	open_parentheses = 0
	principle_operator = -1
	i = 0
	for char in sentence:
		if (char == '('):
			open_parentheses += 1
		elif (char == ')'):
			open_parentheses -= 1
		elif (
			open_parentheses == 0 and
			char == '->'
			):
			return i

		#	One of {~,^,v} can be the principle operator only when -> is not the principle operator and
		#	it is the first of {~,^,v} to appear
		elif (
			open_parentheses == 0 and
			(char == '^' or char == 'v' or char == '~') and
			principle_operator == -1
			):
			principle_operator = i
		i+=1
	return principle_operator

#	Returns true if the sentence is 
def is_variable(sentence):
	if (len(sentence) == 1):
		return True
	return False

#	Given a sentence A -> B
#	Returns ~A v B
def implication_equiv(sentence):
	principle_operator = get_principle_operator(sentence)
	return ['~', '('] + sentence[:principle_operator] + [')', 'v'] + ['('] + sentence[principle_operator+1:] + [')']

#	Ai = Aj ^ Ak
#	Returns
#	Aj ^ Ak ->  Ai		== ~Aj v ~Ak v Ai
#	~Aj ^ ~Ak -> ~Ai	== Aj v Ak v ~Ai
#	~Aj ^ Ak -> ~Ai		== Aj v ~Ak v ~Ai
#	Aj ^ ~Ak -> ~Ai 	== ~Aj v Ak v ~Ai
def parse_conjunction(sentence):
	principle_operator = get_principle_operator(sentence)

	#left_sentece is Aj and right_sentence is Ak
	left_sentence = sentence[:principle_operator]
	right_sentence = sentence[principle_operator+1:]

	variable = 'A' + str(get_record(sentence))
	variable1 = 'A' + str(get_record(left_sentence))
	variable2 = 'A' + str(get_record(right_sentence))

	eq1 = ['~' + variable1, '~' + variable2, variable]
	eq2 = [variable1, variable2, '~' + variable]
	eq3 = [variable1, '~' + variable2, '~' + variable]
	eq4 = ['~' + variable1, variable2, '~' + variable]
	
	return [eq1, eq2, eq3, eq4] + parse_sentence(left_sentence) + parse_sentence(right_sentence)

#	Ai = Aj v Ak
#	Returns
#	Aj v Ak -> Ai		==	Aj,Ak,Ai
#	~Aj	v Ak -> Ai		==	Aj,~Ak,Ai
#	Aj v ~Ak -> Ai		==	~Aj,Ak,Ai
#	~Aj v ~Ak -> ~Ai	==	~Aj,~Ak,~Ai
def parse_disjunction(sentence):
	principle_operator = get_principle_operator(sentence)
	
	#left_sentece is Aj and right_sentence is Ak
	left_sentence = sentence[:principle_operator]
	right_sentence = sentence[principle_operator+1:]

	variable = 'A' + str(get_record(sentence))
	variable1 = 'A' + str(get_record(left_sentence))
	variable2 = 'A' + str(get_record(right_sentence))

	eq1 = [variable1, variable2, variable]	
	eq2 = [variable1, '~' + variable2, variable]
	eq3 = ['~' + variable1, variable2, variable]	
	eq4 = ['~' + variable1, '~' + variable2, '~' + variable]
	return [eq1, eq2, eq3, eq4] + parse_sentence(left_sentence) + parse_sentence(right_sentence)

# Ai = ~Aj
# Returns
#	~Aj -> Ai == Aj v Ai
#	~~Aj -> ~Ai == ~Aj v ~Ai
def parse_negation(sentence):
	principle_operator = get_principle_operator(sentence)
	if (sentence[principle_operator+1] == '('):
		number_open_parentheses = 1
		i = 2
		
		while(number_open_parentheses != 0):
			if (sentence[principle_operator + i] == '('):
				number_open_parentheses += 1
			elif (sentence[principle_operator + i] == ')'):
				number_open_parentheses -= 1
			i += 1

		subsentence = sentence[principle_operator + 1:principle_operator+i]
		sub_principle_operator = get_principle_operator(subsentence)

		while(sub_principle_operator == -1 and not is_variable(subsentence)):
			subsentence = subsentence[1:-1]
			sub_principle_operator = get_principle_operator(subsentence)

		sub_principle_operator = get_principle_operator(subsentence)
		if (subsentence[sub_principle_operator] == '->'):
			return parse_sentence(['~','('] + subsentence[:sub_principle_operator] + [')', 'v'] + 
				subsentence[sub_principle_operator+1:] + sentence[principle_operator+i+1:])

		open_parentheses = 0
		for j in range(len(subsentence)):
			if (subsentence[j] == '('):
				open_parentheses += 1
			elif (subsentence[j] == ')'):
				open_parentheses -= 1
			elif (subsentence[j] == 'v' and open_parentheses == 0):
				subsentence[j] = '^';
			elif (subsentence[j] == '^' and open_parentheses == 0):
				subsentence[j] = 'v'
			elif (subsentence[j] == '~'):
				subsentence[j] = ''
			else:
				subsentence[j] = '~' + subsentence[j]

		return parse_sentence(['('] + subsentence + [')'] + sentence[principle_operator+i:])
	else:
		sentence[principle_operator + 1] = '~' + sentence[principle_operator + 1]
		return parse_sentence(sentence[principle_operator+1:])

#	sentence 	: The sentence to parse
#	i 			: The current variable (ie A1, A2, ... )
def parse_sentence(sentence):
	if (sentence == []):
		return []
	principle_operator = get_principle_operator(sentence)
	while(principle_operator == -1 and not is_variable(sentence)):
		if (sentence == []):
			return []
		sentence = sentence[1:-1]
		principle_operator = get_principle_operator(sentence)

	if (sentence[principle_operator] == '->'):
		sentence = implication_equiv(sentence)
		return parse_sentence(sentence)
	elif (sentence[principle_operator] == '^'):
		return parse_conjunction(sentence)
	elif (sentence[principle_operator] == 'v'):
		return parse_disjunction(sentence)
	elif (sentence[principle_operator] == '~'):
		return parse_negation(sentence)
	else:
		return []

def print_in_dimacs(sentences):
	global num_records;

	dimacs_sentences = [];
	output = 'p cnf ' + str(num_records) + ' ' + str(len(sentences) + 1) + '\n'
	pattern = re.compile('(~)*A(\d)+')

	for sentence in sentences:
		line = ''
		for char in sentence:
			matches = pattern.match(char)
			if len(str(matches.group(1))) % 2 != 0:
				line += '-' + matches.group(2) + ' '
			else:
				line += matches.group(2) + ' '
		line += '0\n'
		output += line

	output += '-1 0'
	print(output)

def main():
	equation = input('What is the equation?\n')

	#Initializing the sentence as a list of character
	sentence = []
	pattern = re.compile("\s*(?:(A\d+)|([\^v&()~])|(->))")
	scan = pattern.scanner(equation)
	while 1:
		m = scan.match()
		if not m:
			break
		x = (m.group(m.lastindex))
		sentence.append(x)

	sentences = parse_sentence(sentence)

	print_in_dimacs(sentences)

if __name__ == '__main__':
	main()
