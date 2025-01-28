TITLE Project 6    (Proj6_lawste.asm)

; Author: Stefan Law
; Last Modified: 03/16/2024
; Project Number: 6                 Due Date: 03/17/2024
; Description: x86/MASM program that demos I/O operations including string handling/parsing, traversing arrays, and converting 
; strings containing numeric data to the equivalent integer or float and vice versa. 

INCLUDE Irvine32.inc

; macro definitions

; ---------------------------------------------------------------------------------
; Name: mGetString
;
; Prompts user for input by printing a prompt string using Irvine WriteString, then 
; then stores keyboard input as a string using ReadString and storing it in 
; supplied memory address
;
; Preconditions: all arguments are required, requires Irvine32 library
;
; Receives:
; promptAddress = address of prompt string
; inputStorage = address where input string will be stored
; bufferLength = max input string length
; bytesRead = address where value placed into EAX by ReadString (number of bytes read) will be stored
;
; returns: bytesRead (value stored at this address) and input string (stored in inputStorage)
; ---------------------------------------------------------------------------------
mGetString MACRO promptAddress:REQ, inputStorage:REQ, bufferLength:REQ, bytesRead:REQ
	
	;preserve registers
	PUSH	EDX
	PUSH	ECX
	PUSH	EAX
	PUSH	EDI

	;display prompt string using Irvine WriteString
	MOV		EDX,			promptAddress
	call	WriteString

	;get user's keyboard input into inputStorage using Irvine ReadString
	MOV		EDX,			inputStorage
	MOV		ECX,			bufferLength
	call	ReadString		;input string should now be stored at address specified by inputStorage

	;store number of bytes read
	MOV		EDI,			bytesRead
	MOV		[EDI],			EAX

	;restore registers
	POP		EDI
	POP		EAX
	POP		ECX
	POP		EDX

ENDM

; ---------------------------------------------------------------------------------
; Name: mDisplayString
;
; Displays a provided string
;
; Preconditions: outputStringAddress is required, requires Irvine32 library
;
; Receives:
;outputStringAddress = memory address for string to be printed
;
; returns: none
; ---------------------------------------------------------------------------------
mDisplayString MACRO outputStringAddress:REQ

	; print string stored in memory location using Irvine WriteString
	PUSH	EDX
	MOV		EDX,		outputStringAddress
	call	WriteString
	POP		EDX

ENDM



	; constant definitions
	;*********************
	ARRAYSIZE = 10
	INT_STRINGSIZE = 13
	; max 32-bit integer is 10 chars, plus possible sign char and null-terminator char, extra cushion character to detect under/overflow input
	FLT_STRINGSIZE = 50
	; 32 bit range for REAL4 is  1.175 x 10^(-38) to 3.403 x 10^38; must account for decimal point char, sign char, 
	;null terminator char, and preceding zero(s) along with extra cushion to detect under/overflow input
	MAX_INT_POSITIVE = 2147483647 ; for reference
	MAX_INT_NEGATIVE = -2147483648
	
	;values of ASCII chars
	;*********************
	ASCII_ZERO = 48
	ASCII_NINE = 57
	ASCII_PLUS = 43
	ASCII_MINUS = 45
	ASCII_DECIMAL_POINT = 46

.data

	;assorted variables to be stored in memory
	bytesIn				SDWORD		?
	inputStr			BYTE		INT_STRINGSIZE DUP (?)
	outputStr			BYTE		INT_STRINGSIZE DUP (?)
	floatInputStr		BYTE		FLT_STRINGSIZE DUP (?)
	floatOutputStr		BYTE		FLT_STRINGSIZE DUP (?)
	inputNum			SDWORD		?
	numArray			SDWORD		ARRAYSIZE DUP (?)
	sum					SDWORD		0
	avg					SDWORD		?
	inputFloat			REAL4		? 
	floatSum			REAL4		?
	floatAvg			SDWORD		?
	floatArray			REAL4		ARRAYSIZE DUP (?)


	;assorted strings for prompts
	programTitle		BYTE		"					Captain IO: Project 6 low-level IO demo",13,10,0
	programAuthor		BYTE		"							by Stefan Law",13,10,0
	extra1				BYTE		"**EC: Number each line of user input and display a running subtotal of the user's valid numbers.",13,10,0
	extra2				BYTE		"**EC: Implement procedures ReadFloatVal and WriteFloatVal for floating point values, using the FPU",13,10,0
	intPrompt			BYTE		". Please enter a signed integer: ",0
	floatPrompt			BYTE		". Please enter a signed float number: ",0
	description1		BYTE		"This program will save 10 input signed integers and display them along with their sum and truncated average.",13,10,0
	description2		BYTE		"Input numbers must be small enough to be represented as 32 bit SDWORD.",13,10,0
	description3		BYTE		"Now we will do the same with floating point numbers.",13,10,"Input numbers must be small enough to be represented as 32-bit REAL4",13,10,0
	farewell			BYTE		"Ta ta for now!",0
	errorInt			BYTE		"ERROR: You did not enter a signed integer or integer is too big.",13,10,0
	errorFlt			BYTE		"ERROR: You did not enter a signed float or your number is too big",13,10,0
	tryAgain			BYTE		". Please try another number: ",0
	numDisplay			BYTE		"You entered the following numbers: ",13,10,0
	commaSpace			BYTE		", ",0
	sumDisplay			BYTE		"The calculated sum of these numbers is: ",0
	avgDisplay			BYTE		"The truncated average of these numbers is: ",0
	runDisplay			BYTE		"The running total of numbers entered so far is: ",0
	asterisks			BYTE		"*****************************************************************************************************************",13,10,0
	decimalPoint		BYTE		".",0


.code

; ---------------------------------------------------------------------------------
; Name: main
;
; The main procedure has 4 separate blocks for demonstrating and testing the
; mDisplayString/mGetString macros along with the Read and Write procedures
; for integer and float values. A set of 10 float values will be obtained 
; for each type as a string, then converted to proper type and stored in an 
; array, before being printed back out as strings along with their sum
; and truncated average. 
;
; Preconditions: none
;
; Postconditions: 
;		-all memory variables declared in .data will be altered by user input and procedures
;
; Receives: 
;		-programTitle/programAuthor: strings used in introduction section
;		-extra1/extra2: strings used to call out additions to program for extra credit
;		-intPrompt/floatPrompt: CLI strings to prompt user for input
;		-description1/2/3: strings that describe the flow of the program to the user
;		-farewell: string to be printed at termination of program
;		-errorInt/errorFlt/tryagain: strings used in handlind erroneous input and reprompting user for input
;       -xxxDisplay, decimalPoint, commaSpace: strings used for describing output to user
;		-asterisks: string used for formatting
;
; Returns: As described above, ALL global variables will be altered by this program, dependent on user input. The 
; program and procedures are written such that these variables can be reused without reinitializing. 
; ---------------------------------------------------------------------------------
main PROC

	; print program title/author/instructions
	PUSH			OFFSET		programTitle
	PUSH			OFFSET		programAuthor 
	PUSH			OFFSET		extra1
	PUSH			OFFSET		extra2
	PUSH			OFFSET		description1
	PUSH			OFFSET		description2
	CALL			Intro
	CALL			Crlf

	;***********************************************************;
	;test loop for obtaining 10 integers from user using ReadVal;
	;will also print running sum to screen						;
	;***********************************************************;

	;initialize loop counter to address and step through array
	;EBX will be used to number individual prompt lines
	MOV				ECX,		ARRAYSIZE
	MOV				EDI,		OFFSET	numArray
	MOV				EBX,		1
	
_testLoop:
	;obtain input as string and convert to numeric form, then store in memory variable

	;push param for running count of input
	PUSH			OFFSET		outputStr
	PUSH			EBX
	;push params for messages and num storage
	PUSH			OFFSET		errorInt
	PUSH			OFFSET		tryAgain
	PUSH			OFFSET		inputNum
	;push params for mGetString macro
	PUSH			OFFSET		intPrompt
	PUSH			OFFSET		inputStr
	PUSH			INT_STRINGSIZE
	PUSH			OFFSET		bytesIn
	CALL			ReadVal

	;transfer input stored in memory by ReadVal to nth element of array, then step to next array cell
	MOV				EAX,		inputNum
	MOV				[EDI],		EAX
 	ADD				EDI,		4

	;add input to running sum and display
	ADD				sum,		EAX
	PUSH			OFFSET		runDisplay
	CALL			PrintSingleLine
	
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			sum
	CALL			WriteVal
	CALL			Crlf

	;increment input count
	INC				EBX

	LOOP			_testLoop

	;***********************************************************;
	;integer input loop is complete; start integer display loop ;									;
	;***********************************************************;

	; display the stored integers by looping through array and sending value of each cell to WriteVal
	CALL			Crlf
	PUSH			OFFSET		numDisplay
	CALL			PrintSingleLine

	
	MOV				ECX,		ARRAYSIZE
	MOV				ESI,		OFFSET numArray
_outputLoop:
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			[ESI]
	CALL			WriteVal

	;formatting to add commas between printed values
	PUSH			OFFSET		commaSpace
	CALL			PrintSingleLine
	
	;increment ESI to next cell of array
	ADD				ESI,		4
	
	LOOP			_outputLoop

	;***********************************************************;
	;integer display loop is complete; display average and sum  ;
	;***********************************************************;
	
	CALL			Crlf
	CALL			Crlf

	;display sum
	PUSH			OFFSET		sumDisplay
	CALL			PrintSingleLine
	
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			sum
	CALL			WriteVal
	CALL			Crlf

	;display truncated average (average = sum // arraysize)
	PUSH			OFFSET		avgDisplay
	CALL			PrintSingleLine

	MOV				EAX,		sum
	CDQ
	MOV				EBX,		ARRAYSIZE
	IDIV			EBX

	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			EAX
	CALL			WriteVal
	CALL			Crlf

	;**************************************************************************************************************************
	;INTEGER PORTION DONE******************************************************************************************************
	;**************************************************************************************************************************

	; print asterisk divider and description of float portion
	CALL			Crlf
	PUSH			OFFSET		asterisks
	CALL			PrintSingleLine
	PUSH			OFFSET		asterisks
	CALL			PrintSingleLine
	CALL			Crlf
	PUSH			OFFSET		description3
	CALL			PrintSingleLine
	CALL			Crlf
	CALL			Crlf

	;**************************************************************;
	;test loop for obtaining 10 floats from user using ReadFloatVal;
	;**************************************************************;


	;address and step through each element of array
	MOV				ECX,		ARRAYSIZE
	MOV				EDI,		OFFSET	floatArray
	MOV				EBX,		1					;counter for user input
	
_testFloatLoop:
	;obtain input as string and convert to numeric form, store in memory variable
	;push param for output string before storage
	PUSH			OFFSET		floatOutputStr
	;push param for running count of input
	PUSH			EBX
	;push params for messages and num storage
	PUSH			OFFSET		errorFlt
	PUSH			OFFSET		tryAgain
	PUSH			OFFSET		inputFloat
	;push params for mGetString
	PUSH			OFFSET		floatPrompt
	PUSH			OFFSET		floatInputStr
	PUSH			FLT_STRINGSIZE
	PUSH			OFFSET		bytesIn 
	CALL			ReadFloatVal

	;transfer input stored in memory to nth element of array
	MOV				EAX,		inputFloat
	MOV				[EDI],		EAX
 	ADD				EDI,		4

	;add input to running sum and display
	FINIT
	FLD				inputFloat
	FLD				floatSum
	FADD			
	FSTP			floatSum

	PUSH			OFFSET		runDisplay
	CALL			PrintSingleLine
	
	PUSH			OFFSET		decimalPoint
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			OFFSET		floatInputStr
	PUSH			OFFSET		floatOutputStr
	PUSH			OFFSET		floatSum
	CALL			WriteFloatVal
	CALL			Crlf

	;increment input count
	INC				EBX

	DEC				ECX
	CMP				ECX,		0
	JNE			_testFloatLoop

	;***********************************************************;
	;float input loop is complete; start float display loop     ;
	;***********************************************************;

	; display the stored floats, their sum, and their truncated average (using WriteFloatVal)
	CALL			Crlf
	CALL			CRLF
	PUSH			OFFSET		numDisplay
	CALL			PrintSingleLine
	CALL			CRLF


	MOV				ECX,		ARRAYSIZE
	MOV				ESI,		OFFSET floatArray
_outputFloatLoop:
	PUSH			OFFSET		decimalPoint
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			OFFSET		floatInputStr
	PUSH			OFFSET		floatOutputStr
	PUSH			ESI
	CALL			WriteFloatVal

	;formatting
	PUSH			OFFSET		commaSpace
	CALL			PrintSingleLine
	
	;increment ESI to next cell of array
	ADD				ESI,		4
	
	LOOP			_outputFloatLoop
	
	;formatting
	CALL			Crlf
	CALL			Crlf

	;display sum
	PUSH			OFFSET		sumDisplay
	CALL			PrintSingleLine
	
	PUSH			OFFSET		decimalPoint
	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			OFFSET		floatInputStr
	PUSH			OFFSET		floatOutputStr
	PUSH			OFFSET		floatSum
	CALL			WriteFloatVal
	CALL			Crlf

	;display truncated average
	PUSH			OFFSET		avgDisplay
	CALL			PrintSingleLine

	MOV				inputNum,	ARRAYSIZE

	;calc average
	FLD				floatSum
	FILD			inputNum
	FDIV

	;truncate and display average
	FIST			floatAvg

	PUSH			OFFSET		inputStr
	PUSH			OFFSET		outputStr
	PUSH			floatAvg
	CALL			WriteVal
	CALL			Crlf

	;print good bye message
	PUSH			OFFSET		farewell
	CALL			PrintSingleLine

	Invoke ExitProcess,0	; exit to operating system
main ENDP

; ---------------------------------------------------------------------------------
; Name: ReadVal
;
; This procedure prompts the user to input a string containing an integer value and stores the string to memory using the
; mGetString macro. The string is validated for proper formatting and then parsed to an SDWORD integer using a simple algorithm.
; The number is also validated to ensure it can fit inside a 32-bit SDWORD. 
; The parsed integer is then stored at the provided input address. Each prompt is also individualy numbered, incrementing once 
; a validated value is received. 
;
; Preconditions:
;	-input value must be an integer (can have a leading +/- sign only, all other characters must be digits)
;	-input value must fit inside 32-bit SDWORD
;	-mGetString and mDisplayString macro must be defined, and Irvine32 library must be included
;
;
; Postconditions:
;	-global strings inputStr, outputStr are altered
;	-bytesIn and inputNum integer values are altered
;
; Receives: 
;	[EBP+40]:		outputStr (by reference, used for string copy/reversal)
;	[EBP+36]:		EBX		  (by value, used for input line count)
;	[EBP+32]:		errorInt  (by reference, prompt for error)
;	[EBP+28]:		tryAgain  (by reference, prompt for error)
;	[EBP+24]:		inputNum  (by reference, address for input value to be stored)
;	[EBP+20]:		intPrompt (by reference, prompt for input)
;	[EBP+16]:		inputStr  (by reference, address for input string to be stored)
;	[EBP+12]:		INT_STRINGSIZE (constant by value, max length of string buffer)
;	[EBP+8]:		bytesIn   (by reference, address for number of characters read in to be stored)
;
; Returns: 
;	-inputNum will contained parsed user integer input in SDWORD format
;	-bytesIn will contain number of characters read
; ---------------------------------------------------------------------------------
ReadVal PROC
	;build stack frame
	PUSH				EBP
	MOV					EBP,		ESP

	;preserve registers
	PUSH				EBX
	PUSH				ECX
	PUSH				EDX
	PUSH				ESI
	PUSH				EDI

_loopStart:
	;invoke mGetString macro to get user input in the form of a string of digits
	PUSH				[EBP+16]
	PUSH				[EBP+40]
	PUSH				[EBP+36]
	CALL				WriteVal
	mGetString			[EBP+20],[EBP+16],[EBP+12],[EBP+8]
_tryAgain:
	;set up registers for readLoop
	MOV					ESI,		[EBP+8]
	MOV					ECX,		[ESI]			;loop through length of string
	MOV					ESI,		[EBP+16]		;address of string to be read
	MOV					BH,			0				;BH will hold negative flag
	MOV					EDX,		0				;EDX will hold input number as we interpret string
	CLD

	;error check for null input
	CMP					ECX,		0
	JE					_error

_readLoop:
	;check if we are at beginning of string
	CMP					ESI,		[EBP+16]
	JNE					_pastFirstChar
	;must use LODSB/STOSB to get string[n] into AL
	LODSB
	;validate that user input is a valid number (no letters,symbols, etc)

	;check for negative or positive sign
	CMP					AL,			ASCII_MINUS
	JE					_setNegative
	CMP					AL,			ASCII_PLUS
	JE					_loopEnd
	JMP					_checks
	;If the user enters non-digits other than something which will indicate sign (e.g. �+� or �-�), or the number is too large for 32-bit registers, an error message should be displayed and the number should be discarded.
	;If the user enters nothing (empty input), display an error and re-prompt.
	;convert string of ASCII digits to numeric representation (type SDWORD)


_setNegative:
	INC					BH
	JMP					_loopEnd

_pastFirstChar:
	LODSB
_checks:
	CMP					AL,			ASCII_ZERO
	JL					_error
	CMP					AL,			ASCII_NINE
	JG					_error
	SUB					AL,			ASCII_ZERO

	CMP					BH,			1
	JE					_handleNegative

_handlePositive:
	;char is an ascii digit, so running total = (10 * num) + (ascii_num - 48)
	MOV					BL,			AL					;free up EAX for multiplicand storage
	MOV					EAX,		EDX		
	MOV					EDX,		10					;EDX is briefly free
	IMUL				EDX
	JO					_error							;check for overflow
	MOVZX				EDX,		BL
	ADD					EAX,		EDX	
	JO					_error
	MOV					EDX,		EAX


	JMP					_loopEnd

_handleNegative:
;char is an ascii digit, so running total = (10 * num) - (ascii_num - 48)
	MOV					BL,			AL					;free up EAX for multiplicand storage
	MOV					EAX,		EDX		
	MOV					EDX,		10					;EDX is briefly free
	IMUL				EDX
	JO					_error							;check for overflow
	MOVZX				EDX,		BL
	SUB					EAX,		EDX	
	JO					_error
	MOV					EDX,		EAX

	JMP					_loopEnd

_error:
	;display error messages and prompt for new input
	mDisplayString		[EBP+32]
	PUSH				OFFSET		inputStr
	PUSH				OFFSET		outputStr ;fix reference here
	PUSH				[EBP+36]
	CALL				WriteVal
	mGetString			[EBP+28],[EBP+16],[EBP+12],[EBP+8]
	JMP					_tryAgain

_loopEnd:
	DEC					ECX
	CMP					ECX,		0
	JE					_loopDone
	JMP					_readLoop

_loopDone:

	;store final value in a memory location
	MOV					EDI,		[EBP+24]
	MOV					[EDI],		EDX

	;restore registers
	POP					EDI
	POP					ESI
	POP					EDX
	POP					ECX
	POP					EBX

	
	;stack frame cleanup
	POP					EBP
	RET					36
ReadVal ENDP
; ---------------------------------------------------------------------------------
; Name: WriteVal
;
; This procedure writes a provided SDWORD 32-bit integer to the screen. It converts 
; the integer directlyfrom it's stored SDWORD value to an ASCII character string 
; representation which is stored, and then displayed using the mDisplayString macro.
; If the number is negative, its sign is also printed. 
;
; Preconditions:
;	-must receive a 32-bit SDWORD integer to be displayed
;	-mDisplayString macro bust be defined, and Irvine32 library must be included
;
;
; Postconditions:
;	-global strings inputStr, outputStr are altered
;	-number stored at num array + offset will be printed to screen
;
; Receives: 
;	[EBP+16]:		inputStr  (by reference, address for input string where parsed characters (in reverse) will be stored)
;	[EBP+12]:		outputStr (by reference, max length of string buffer)
;	[EBP+8]:		numArray + offset   (by reference, address for number to be displayed)
;
; Returns: 
;	-none
; ---------------------------------------------------------------------------------
WriteVal PROC
	LOCAL				divisor:SDWORD, quotient:SDWORD, remainder:BYTE

	;preserve registers
	PUSH				EAX
	PUSH				EBX
	PUSH				ECX
	PUSH				EDX
	PUSH				ESI
	PUSH				EDI

	;convert a numeric SDWORD to a string of ASCII digits
	MOV					EDI,		[EBP+16]
	MOV					ECX,		0

	;check if passed value is negative, if so add a negative sign, otherwise add a positive sign (set a flag and add at end of string)
	MOV					EAX,		[EBP+8]
	CDQ
	CLD
	CMP					EAX,		0
	JL					_negFlags
	MOV					BH,			0
	MOV					divisor,			10
_divisionLoop:
	;each ASCII character in number can be determined by dividing by 10 and writing remainder to string, starting with least significant digit
	IDIV				divisor
	MOV					quotient,	EAX
	MOV					remainder,	DL
	MOV					AL,			remainder
	CMP					AL,			0
	JL					_numFLip
_numFlipped:
	ADD					AL,			ASCII_ZERO
	STOSB				
	MOV					EAX,		quotient
	CDQ

	INC					ECX

	CMP					EAX,		0
	JNE					_divisionLoop

	;determine sign
	CMP					BH,			0
	JE					_signDone
	JMP					_negativeSign

_negativeSign:
	MOV					AL,			ASCII_MINUS
	STOSB
	INC					ECX

_signDone:


	;string will now contain reversed ASCII string, so reverse string by setting direction flag and copying backwards
	MOV					ESI,		EDI
	DEC					ESI
	MOV					EDI,		[EBP+12]

_reverseLoop:
	STD
	LODSB
	CLD
	STOSB

	LOOP				_reverseLoop

	;add a null terminator
	MOV					AL,			0
	STOSB

;invoke the mDisplayString macro to print the ASCII representation of the SDWORD value to output
	mDisplayString		[EBP+12]

	JMP					_procedureDone

_negFlags:
	MOV					BH,			1
	MOV					divisor,			-10
	JMP					_divisionLoop

_numFlip:
	NEG					AL
	JMP					_numFlipped

_procedureDone:
;restore registers
	POP					EDI
	POP					ESI
	POP					EDX
	POP					ECX
	POP					EBX
	POP					EAX

;stack frame cleanup
	RET					12

WriteVal ENDP
; ---------------------------------------------------------------------------------
; Name: ReadFloatVal
;
; This procedure prompts the user to input a string containing a 32-bit float value 
; and stores the string to memory using the mGetString macro. The string is validated 
; for proper formatting and then parsed to an Real4 float using a (not so) simple 
; algorithm and the FPU. This procedure has some limitations in the accuracy of the results 
; returned (which may be inherent to its use of the floating point format). The number is 
; also validated to ensure it can fit inside a 32-bit REAL4 by checking for underflow 
; and overflow after each arithmetic operation, by way of looking at the status word. 
; The parsed flot is then stored at the provided input address. Each prompt is also 
; individualy numbered, incrementing once a validated value is received. 
;
; Preconditions:
;	-input value must be an Real4 float (can have a leading +/- sign only, all other characters must be digits)
;	-input value can omit a leading 0 or include as many as desired
;   -input value can omit a decimal point for integers
;	-input value must fit inside 32-bit Real4
;	-mGetString and mDisplayString macro must be defined, and Irvine32 library must be included
;
; Postconditions:
;	-the FPU stack and control word is altered
;	-inputStr,OutputStr,floatInputStr, floatOutputStr are all altered
;	-the value stored at the floatArray cell address provided is updated with the REAL4 form of the provided input
;
; Receives: 
;	[EBP+40]:		outputStr (by reference, used for string copy/reversal)
;	[EBP+36]:		EBX		  (by value, used for input line count)
;	[EBP+32]:		errorFlt  (by reference, prompt for error)
;	[EBP+28]:		tryAgain  (by reference, prompt for error)
;	[EBP+24]:		inputFlt  (by reference, address for input value to be stored)
;	[EBP+20]:		fltPrompt (by reference, prompt for input)
;	[EBP+16]:		inputStr  (by reference, address for input string to be stored)
;	[EBP+12]:		FLT_STRINGSIZE (constant by value, max length of string buffer)
;	[EBP+8]:		bytesIn   (by reference, address for number of characters read in to be stored)
;
; Returns:
;		-input float value will be stored at address of inputFlt
; ---------------------------------------------------------------------------------
ReadFloatVal PROC
	LOCAL				ten:DWORD, decimal_flag:DWORD, parsed_float:REAL4, digit:WORD, status_flag:WORD, divisor:REAL4, control_word:WORD

	;preserve registers
	PUSH				EAX
	PUSH				EBX
	PUSH				ECX
	PUSH				ESI
	PUSH				EDI

	;initialize local variables used for parsing input string
	MOV					ten,					10
	MOV					decimal_flag,			0
	MOV					digit,					0
	MOV					status_flag,			0

	;initialize FPU and direction flag
	FINIT
	CLD

	;set precision mode to REAL4 in control word and round up; note this has been adapted from "SIMPLY FPU" by Raymond Filiatreault
	FSTCW				control_word
	FWAIT
	MOV					AX,				control_word
	XOR					AX,				0800h
	MOV					control_word,		AX
	FLDCW				control_word

	;initialize parsed_float
	FLDZ
	FSTP				parsed_float


	;get user input
_fltLoopStart:
	;invoke mGetString macro to prompt and get user input in the form of a string of digits
	PUSH				[EBP+16]
	PUSH				[EBP+40]
	PUSH				[EBP+36]
	CALL				WriteVal
	mGetString			[EBP+20],[EBP+16],[EBP+12],[EBP+8]

_fltTryAgain:
	;set up registers for readLoop
	MOV					ESI,		[EBP+8]
	MOV					ECX,		[ESI]			;loop through length of string, have to access pointer to a pointer
	MOV					ESI,		[EBP+16]		;address of string to be read
	MOV					BH,			0				;BH will hold negative flag
	FLDZ											;put 0.0 at ST(0)

	;error check for null input
	CMP					ECX,		0
	JE					_fltError

_readFltLoop:
	;check if we are at beginning of string
	CMP					ESI,		[EBP+16]
	JNE					_pastFirstFltChar
	
	;use LODSB/STOSB to get string[n] into AL, LODSB also increments ESI
	LODSB

	;now validate that user input is a valid number 
	;for floats we might have a sign or a decimal point at the first position, and we also need to check for chars that are not accepted
	;check for decimal
	CMP					AL,			ASCII_DECIMAL_POINT
	JE					_foundDecimal
	;check for negative or positive sign
	CMP					AL,			ASCII_MINUS
	JE					_setFltNegative
	CMP					AL,			ASCII_PLUS
	JE					_fltLoopEnd
	JMP					_fltChecks

_foundDecimal:
	;make sure a decimal point wasn't already parsed
	CMP					decimal_flag,	1
	JE					_fltError
	;set decimal flag and store integer portion of float
	MOV					decimal_flag,	1
	;initialize divisor to 10.0
	FILD				ten
	FST					divisor
	FSTP				ST(0)
	JMP					_fltLoopEnd

_setFltNegative:
	INC					BH
	JMP					_fltLoopEnd

_pastFirstFltChar:
	;use LODSB/STOSB to get string[n] into AL
	LODSB

_fltChecks:
	;validate formatting for chars past position zero
	CMP					AL,			ASCII_DECIMAL_POINT
	JE					_foundDecimal
	CMP					AL,			ASCII_ZERO
	JL					_fltError
	CMP					AL,			ASCII_NINE
	JG					_fltError
	;if passes checks, convert ASCII char to digit 
	SUB					AL,			ASCII_ZERO

	;determine if we need to go through integer or fraction algorithm
	CMP					decimal_flag,	1
	JE					_handleFltDec


_handleFltInt:
	;char is an ascii digit, so running total of integer portion of float = (10 * parsed_float) + (ascii_num - 48)
	MOVZX					AX,			AL				;store parsed digit in memory for FPU ops
	MOV						digit,		AX
	
	;10 * parsed_float
	FILD				DWORD PTR ten
	FLD					parsed_float
	FMUL
	
	;test for underflow/overflow
	FSTSW				status_flag						;note this procedure for testing underflow/overflow adapted from "SIMPLY FPU" by Raymond Filiatreault
	FWAIT
	TEST				status_flag,			1		;check I field/bit 0 of status word, which flags underflow/overflow
	JNZ					_fltError

	;(10 * parsed_float) + (ascii_num - 48)
 	FILD				WORD PTR digit
	FADD

	;test for underflow/overflow again
	FSTSW				status_flag						;note this procedure for testing underflow/overflow adapted from "SIMPLY FPU" by Raymond Filiatreault
	FWAIT
	TEST				status_flag,			1		;check 1's field/bit 0 of status word, which flags underflow/overflow
	JNZ					_fltError

	;ST(0) now contains results of above equation
	FSTP				parsed_float

	JMP					_fltLoopEnd

_handleFltDec:
	;parse each numeral to right of decimal point and divide by divisor, and add result to fraction placeholder, then multiply divisor by 10 before looking at next digit

	MOVZX					AX,			AL				;store parsed digit in memory for FPU ops
	MOV						digit,		AX

	FILD				digit
	FLD					divisor
	FDIV
	;error check
 	FSTSW				status_flag						;note this procedure for testing underflow/overflow adapted from "SIMPLY FPU" by Raymond Filiatreault
	FWAIT
	TEST				status_flag,			1		;check I field/bit 0 of status word, which flags underflow/overflow
	JNZ					_fltError
	;add digit to parsed number and error check again, then store
	FLD					parsed_float
	;add fraction to parsed_float
	FADD
	;error check
	FSTSW				status_flag						;note this procedure for testing underflow/overflow adapted from "SIMPLY FPU" by Raymond Filiatreault
	FWAIT
	TEST				status_flag,			1		;check 1's field/bit 0 of status word, which flags underflow/overflow
	JNZ					_fltError
	;store for next loop
	FST					parsed_float
	FSTP				ST(0)

	;update divisor by multiplying by ten
	FLD					divisor
	FILD				ten
	FMUL
	FST					divisor
	FSTP				ST(0)
	;repeat to end of input

	JMP					_fltLoopEnd


_fltError:
	;display error messages and prompt for new input
	mDisplayString		[EBP+32]
	PUSH				[EBP+16]
	PUSH				[EBP+40]
	PUSH				[EBP+36]
	CALL				WriteVal
	mGetString			[EBP+28],[EBP+16],[EBP+12],[EBP+8]
	JMP					_fltTryAgain

_fltLoopEnd:
	DEC					ECX
	CMP					ECX,		0
	JE					_fltLoopDone
	JMP					_readFltLoop

_fltLoopDone:
	
	;check for negative flag and change sign if needed
	CMP					BH,			1
	JNE					_notNegative
	FLD					parsed_float
	FCHS
	FST					parsed_float
	FSTP				ST(0)

_notNegative:
	;store final value in a memory location
	MOV					EDI,		[EBP+24]
	MOV					EAX,		parsed_float
	MOV					[EDI],		EAX

	;restore registers
	POP					EDI
	POP					ESI
	POP					ECX
	POP					EBX
	POP					EAX


	RET					36
ReadFloatVal ENDP
; ---------------------------------------------------------------------------------
; Name: WriteFloatVal
;
; This procedure takes a provided REAL4 Float value and parses it into a string of
; ASCII characters and appropriate sign/decimal point using FPU operations. The 
; integer portion is obtained by simple truncation of the stored number and casting
; and storing of this value into SDWORD format, followed by a call to ReadVal. The 
; decimal portion is obtained by subtracting the truncated integer portion from the 
; stored value and translating to ASCII, and individual digits are obtained by 
; multiplying by ten and translating the resultant integer poriton to ASCII. This 
;operation is repeated until we reach 0.0
;
; Preconditions:
;	-WriteVal, mDisplayString must be defined; IRVINE32 library must be include
;	-value provided to be written must be a REAL4 float stored in memory
;
;
; Postconditions: 
;	-the provided REAL4 float value is printed to the screen
;	-the FPU stack and control word is altered
;
; Receives:
;	[EBP+28]:		decimalPoint	(by reference, decimal point character to be printed)
;	[EBP+24]:		inputStr		(by reference, string array for parsing)
;	[EBP+20]:		outputStr		(by reference, string array for copying/reversal)
;	[EBP+16]:		floatInputStr  (by reference, not currently used)
;	[EBP+12]:		floatOutputStr (by reference, not currently used)
;	[EBP+8]:		number  (by reference, memory address where input float value is stored)
;
; Returns:
;	-none
; ---------------------------------------------------------------------------------
WriteFloatVal PROC
	LOCAL	output_int:DWORD, output_dec:REAL4, control_word:WORD, ten:DWORD, input_float:REAL4

	;preserve registers
	PUSH				EAX
	PUSH				ESI

	MOV					ESI,	[EBP+8]
	MOV					ten,			10

	;initialize FPU
	FINIT
	FLD					DWORD PTR[ESI]
	FSTP				input_float
	;set truncate mode in control word; note this has been adapted from "SIMPLY FPU" by Raymond Filiatreault
	FSTCW				control_word
	FWAIT
	MOV					AX,				control_word
	OR					AX,				0C00h
	MOV					control_word,		AX
	FLDCW				control_word

	
	;truncate integer portion, store locally, and print to screen
	FLD					input_float
	FISTP				output_int

	PUSH				[EBP+24]
	PUSH				[EBP+20]
	PUSH				output_int
	CALL				WriteVal

	;print decimal point
	PUSH				[EBP+28]
	CALL				PrintSingleLine
	

	;subtract integer portion to determine and store decimal portion
	;negative sign no longer needed, so run FABS on decimal portion
	FLD					input_float
	FILD				output_int
	FSUB
	FABS
	FSTP				output_dec

	FLD					output_dec
_decDisplayLoop:
	;Multiply decimal portion by 10 e.g., 0.22 -> 2.2
	FILD				ten
	FMUL
	;FIST result to local memory value e.g. 2.2 -> 2, ensuring truncate mode is set as above
	FIST				output_int
	;print digit to screen
	PUSH				[EBP+24]
	PUSH				[EBP+20]
	PUSH				output_int
	CALL				WriteVal
	;FILD to load digit, then subtract e.g 2.2 - 2.0 = 0.2
	FILD				output_int
	FSUB				

	;FCOMIP result to determine if we have reached termination of number (0.0)
	FLDZ
	FCOMIP				ST(0),ST(1)
	JZ					_decDisplayLoopDone

	JMP					_decDisplayLoop

_decDisplayLoopDone:

	;restore registers
	POP					ESI
	POP					EAX


	RET					24
WriteFloatVal ENDP
; ---------------------------------------------------------------------------------
; Name: Intro
;
; This procedure is used at the beginnign of main() to print the program title
; and author, a description of its functionality, and extra credit call outs
;
; Preconditions:
;	-mDisplay String must be defined and IRVINE32 library must be included
;
; Postconditions: 
;	-below information is formatted and printed to screen
;
; Receives:
;	[EBP+28]:		programTitle (by reference)
;	[EBP+24]:		programAuthor  (by reference)
;	[EBP+20]:		description1 (by reference)
;	[EBP+16]:		description2  (by reference)
;	[EBP+12]:		extra1 (by reference)
;	[EBP+8]:		extra2   (by reference)
;
; Returns:
;	-none
; ---------------------------------------------------------------------------------
Intro	PROC
	;build stack frame
	PUSH				EBP
	MOV					EBP,		ESP

	;print title/author/directions using mDisplayString
	mDisplayString		[EBP + 28]
	mDisplayString		[EBP + 24]
	CALL				crlf
	mDisplayString		[EBP + 12]
	mDisplayString		[EBP + 8]
	CALL				crlf

	;print extra credit callout
	mDisplayString		[EBP + 20]
	mDisplayString		[EBP + 16]

	;stack frame cleanup
	POP					EBP
	RET					24

Intro	ENDP
; ---------------------------------------------------------------------------------
; Name: PrintSingleLine
;
; 
; 
;
; Preconditions:
;	-mDisplayString must be defined and an address to a string to be printed must be provided
;
; Postconditions:
;	-the provided string is printed to the screen
;
; Receives: 
;	-[EBP+8] (reference to address of string to be printed)
;
; Returns:
;	-none
; ---------------------------------------------------------------------------------
PrintSingleLine	PROC
	;build stack frame
	PUSH				EBP
	MOV					EBP,		ESP

	;print PrintSingleLine meesage using mDisplayString
	mDisplayString		[EBP + 8]

	;stack frame cleanup
	POP					EBP
	RET					4

PrintSingleLine	ENDP

END main
