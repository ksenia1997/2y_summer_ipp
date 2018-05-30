<?php
$parse_error = 21;


//XML
$xml = xmlwriter_open_memory();
xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_set_indent($xml, 1);
xmlwriter_set_indent_string($xml, "    ");



// Control of arguments 
if ($argc > 2) {
	fwrite(STDERR, "Should be only two arguments or STDIN.\n");
	exit(10);
}
else{
	if($argc == 2) {
		if(($argv[0] == "parse.php") && ($argv[1] == "--help")) {
			print(" Implementation of language IPPcode18\n Take a code from stdin and check if it is lexical and syntaxical correct and write to stdout XML representation of this code.\n 10 is error in arguments\n 21 is parse error\n");
			exit(0);			
		}

		else {
			print($argv[1]);
			fwrite(STDERR, "Expected '--help'.\n");
			exit(10);

		}
	}
}

function count_of_arguments($words, $count){
	global $parse_error;
	if (count($words) - 1 != $count) {
		fwrite(STDERR, "Bad count of arguments\n");
		exit($parse_error);
	}
}


//Function var

function variable($var, $count, $parse_error, $var_match){
	global $xml;
	# <var> match
	xmlwriter_start_element($xml, "arg1");
	xmlwriter_start_attribute($xml, "type");

	if (preg_match($var_match, $var)) {
		xmlwriter_text($xml, "var");
	}
	else {
		fwrite(STDERR, "Error in variable number 1 line:" . $count . "\n");
		exit($parse_error);
		}
	xmlwriter_end_attribute($xml);
	xmlwriter_text($xml, $var);
	xmlwriter_end_element($xml);

}

// Function symb 
function symb($parse_error, $var_match, $symbol, $bool_match, $string_match, $int_match, $counter, $number) {
	global $xml;

	if (preg_match($var_match, $symbol)) {
		xmlwriter_text($xml, "var");
		xmlwriter_end_attribute($xml);
		xmlwriter_text($xml, $symbol);
		}
				
	else {
		$prom_cont = explode("@", $symbol);
		xmlwriter_text($xml, $prom_cont[0]);
		// Bool match
		if ($prom_cont[0] == "bool" && preg_match($bool_match, $prom_cont[1])) {
			xmlwriter_end_attribute($xml);

		}
		

		// Str match
		else if (($prom_cont[0] == "string") && ((preg_match($string_match, $prom_cont[1], $matches) == 0) || ($prom_cont[1] == ""))) {
			xmlwriter_end_attribute($xml);

		}
		
		// Int match
		else if (($prom_cont[0] == "int") && preg_match($int_match, $prom_cont[1])) {
			xmlwriter_end_attribute($xml);

		}
		else {
			fwrite(STDERR, "Error in variable number " . $number . " line:" . $counter . "\n");
			exit($parse_error);
		}
		xmlwriter_text($xml, $prom_cont[1]);					
					
	}
	xmlwriter_end_element($xml);


}

// Function type
function type($parse_error, $symbol, $bool_match, $string_match, $int_match, $counter){
	global $xml;

	$prom_cont = explode("@", $symbol);
	xmlwriter_text($xml, "type");
	// Bool match
	if ($prom_cont[0] == "bool" && preg_match($bool_match, $prom_cont[1])) {
		xmlwriter_end_attribute($xml);
	}
		
	// Str match
	else  if (($prom_cont[0] == "string") && ((preg_match($string_match, $prom_cont[1]) == 0) || $prom_cont[1] == "")) {
		xmlwriter_end_attribute($xml);
	}
		
	// Int match
	else if (($prom_cont[0] == "int") && preg_match($int_match, $prom_cont[1])) {
		xmlwriter_end_attribute($xml);
	}
	else {
		fwrite(STDERR, "Error in variable number 2 line:" . $counter . "\n");
		exit($parse_error);
	}
	xmlwriter_text($xml, $prom_cont[1]);	

	xmlwriter_end_element($xml);

}

// Function label
function label($parse_error, $symbol, $label_match, $counter) {
	global $xml;

	if(preg_match($label_match, $symbol)) {
		xmlwriter_text($xml, "label");
	}
	else {
		fwrite(STDERR, "Bad label line:" . $counter . "\n");
		exit($parse_error);
	}

}

function main(){
	global $xml;
	global $parse_error;
	$counter = 0; //counter of lines
	$order = 0; // counter of instructions
	$started = FALSE;

	# Regex vars
	$var_match = "/^(?:GF|TF|LF)@[\p{L}_\-\$&%*][\w\p{L}\p{N}\p{Pd}\$&%*]*$/u";
	$bool_match = "/true|false/";
	$int_match = "/^(-|\+)?[0-9]+$/u";
	$string_match = "/\\\[0-9]{0,2}($|\p{L})|\s|\t|\r|\'|\"/u";
	$label_match = "/^[\p{L}_\-\$&%*][\w\p{L}\p{N}\p{Pd}\$&%*]*$/u";


	while($line = fgets(STDIN)) {
		$counter++;

		//delete comment
		if (strpos($line, "#") !== FALSE) {
			$line = substr($line, 0, strpos($line, "#")); 
		}

		$words = preg_split('/\s+/', $line, 0,  PREG_SPLIT_NO_EMPTY); //separate words


		if (!$words) {
			continue;
		}
		else {
			//control of the first line
			if ($started == FALSE) {
				if ($words[0] === ".IPPcode18" && count($words) == 1) {
					$started = TRUE;
					# Element 'program'
					xmlwriter_start_element($xml, "program");
					xmlwriter_start_attribute($xml, 'language');
					xmlwriter_text($xml, 'IPPcode18');
					xmlwriter_end_attribute($xml);
					
					continue;
				}
				else {
					fwrite(STDERR, "Doesn't '.IPPcode18' on the first line.\n");
					exit($parse_error);
				}

			}	
		
		}


		// start instruction
		xmlwriter_start_element($xml, "instruction");

		$order++;
		xmlwriter_start_attribute($xml, "order");
		xmlwriter_text($xml, $order);
		xmlwriter_end_attribute($xml);

		xmlwriter_start_attribute($xml, "opcode");
		xmlwriter_text($xml, strtoupper($words[0]));
		xmlwriter_end_attribute($xml);

		// Instructions 

		//PRACE S RAMCI, VOLANI FUNKCI
		if(strtoupper($words[0]) == "MOVE") {
			count_of_arguments($words, 2);
			#<var> match
			variable($words[1], $counter, $parse_error, $var_match);

			# <symb> match
			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);
			xmlwriter_end_element($xml);

		}

		else if((strtoupper($words[0]) == "CREATEFRAME") || (strtoupper($words[0]) == "PUSHFRAME") || (strtoupper($words[0]) == "POPFRAME") || (strtoupper($words[0]) == "RETURN")
		 || (strtoupper($words[0]) == "BREAK")) {
			count_of_arguments($words, 0);
			xmlwriter_end_element($xml);

		}

		else if(strtoupper($words[0]) == "DEFVAR") {
			count_of_arguments($words, 1);
			variable($words[1], $counter, $parse_error, $var_match);
			xmlwriter_end_element($xml);

		}

		else if(strtoupper($words[0]) == "CALL") {
			count_of_arguments($words, 1);
			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			label($parse_error, $words[1], $label_match, $counter);

			xmlwriter_end_attribute($xml);
			xmlwriter_text($xml, $words[1]);
			xmlwriter_end_element($xml);
			xmlwriter_end_element($xml);
		}

		//PRACE S DATOVYM ZASOBNIKEM

		else if (strtoupper($words[0]) == "PUSHS") {
			count_of_arguments($words, 1);
			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[1], $bool_match, $string_match, $int_match, $counter, 1);
			xmlwriter_end_element($xml);

		}

		else if(strtoupper($words[0]) == "POPS") {
			count_of_arguments($words, 1);
			variable($words[1], $counter, $parse_error, $var_match);
			xmlwriter_end_element($xml);
		}

		// Aritmetické, relační, booleovské a konverzní instrukce

		else if((strtoupper($words[0]) == "ADD") || (strtoupper($words[0]) == "SUB") || (strtoupper($words[0]) == "MUL") || (strtoupper($words[0]) == "IDIV") || (strtoupper($words[0]) == "LT") 
			|| (strtoupper($words[0]) == "GT") || (strtoupper($words[0]) == "EQ") || (strtoupper($words[0]) == "AND") || (strtoupper($words[0]) == "OR") || (strtoupper($words[0]) == "STRI2INT")) {

			count_of_arguments($words, 3);

			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);

			xmlwriter_start_element($xml, "arg3");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[3], $bool_match, $string_match, $int_match, $counter, 3);
			xmlwriter_end_element($xml);


		}

		else if ((strtoupper($words[0]) == "NOT") || (strtoupper($words[0]) == "INT2CHAR")){
			count_of_arguments($words, 2);
			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);
			xmlwriter_end_element($xml);
		}

		//VSTUPNE-VYSTUPNI INSTRUKCE

		else if (strtoupper($words[0]) == "READ") {
			count_of_arguments($words, 2);
			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			type($parse_error, $words[2], $bool_match, $string_match, $int_match, $counter);
			xmlwriter_end_element($xml);

		}

		else if(strtoupper($words[0]) == "WRITE") {
			count_of_arguments($words, 1);
			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[1], $bool_match, $string_match, $int_match, $counter, 1);
			xmlwriter_end_element($xml);

		}

		// PRACE S RETEZCI

		else if((strtoupper($words[0]) == "CONCAT") || (strtoupper($words[0]) == "GETCHAR") || (strtoupper($words[0]) == "SETCHAR")) {
			count_of_arguments($words, 3);
			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);

			xmlwriter_start_element($xml, "arg3");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[3], $bool_match, $string_match, $int_match, $counter, 3);
			xmlwriter_end_element($xml);

		}

		else if (strtoupper($words[0]) == "STRLEN") {
			count_of_arguments($words, 2);
			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);
			xmlwriter_end_element($xml);

		}

		// PRACE S TYPY

		else if (strtoupper($words[0]) == "TYPE") {
			count_of_arguments($words, 2);
			variable($words[1], $counter, $parse_error, $var_match);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);
			xmlwriter_end_element($xml);

		}

		// INSTRUKCE PRO RIZENI TOKU PROGRAMU
		else if ((strtoupper($words[0]) == "LABEL") || (strtoupper($words[0]) == "JUMP")) {
			count_of_arguments($words, 1);

			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			label($parse_error, $words[1], $label_match, $counter);

			xmlwriter_end_attribute($xml);
			xmlwriter_text($xml, $words[1]);
			xmlwriter_end_element($xml);
			xmlwriter_end_element($xml);
		}

		else if ((strtoupper($words[0]) == "JUMPIFEQ") || (strtoupper($words[0]) == "JUMPIFNEQ")) {
			count_of_arguments($words, 3);

			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			label($parse_error, $words[1], $label_match, $counter);

			xmlwriter_end_attribute($xml);
			xmlwriter_text($xml, $words[1]);
			xmlwriter_end_element($xml);

			xmlwriter_start_element($xml, "arg2");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[2], $bool_match, $string_match, $int_match, $counter, 2);

			xmlwriter_start_element($xml, "arg3");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[3], $bool_match, $string_match, $int_match, $counter, 3);	
			xmlwriter_end_element($xml);		

		}

		//LADICI INSTRUKCE
		else if (strtoupper($words[0]) == "DPRINT") {
			count_of_arguments($words, 1);
			xmlwriter_start_element($xml, "arg1");
			xmlwriter_start_attribute($xml, "type");

			symb($parse_error, $var_match, $words[1], $bool_match, $string_match, $int_match, $counter, 1);
			xmlwriter_end_element($xml);

		}

		// Not found instruction
		else {
			fwrite(STDERR, "Unknowm instruction line:" . $counter . "\n");
			exit($parse_error);
		}
		
	}

	// if empty file
	if($started == FALSE) {
		fwrite(STDERR, "Empty stdin or it contains only comments or white spaces. \n" );
		exit($parse_error);
	}

}

main();

xmlwriter_end_element($xml);
xmlwriter_end_document($xml);

echo xmlwriter_output_memory($xml);
?>