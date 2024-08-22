TAB = '\t'
BACK = '\x08'
ENTER = '\r'
DELETE = '\x7f'
ESCAPE = '\x1b'
PASTE = '\x16'
COPY = '\x03'
SPACE = ' '

LOWERCASE_ALPHABET = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
'''The lowercase latin alphabet'''
UPPERCASE_ALPHABET = {'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'}
'''The uppercase latin alphabet'''
ALPHABET = LOWERCASE_ALPHABET.union(UPPERCASE_ALPHABET)
NUMBERS = {'1','2','3','4','5','6','7','8','9','0','.'}
'''Numbers 1-9 including "." '''
SYMBOLS = {',','`','~','!','@','#','$','%','^','&','*','(',')','_','+','-','=','{','}','[',']','|','\\',';',':','"','<','>','.','?','/','`',"'"}
FILENAME_VALID = ALPHABET.union(NUMBERS, SYMBOLS, {" ",}).difference({'<','>','|','/','\\','*',':','?','"'}) 
'''File name accepted characters'''
REGULAR = ALPHABET.union(NUMBERS,SYMBOLS, {SPACE,})