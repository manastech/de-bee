var KEY_DOWN = 40;
var KEY_UP = 38;
var KEY_RIGHT = 39;
var KEY_LEFT = 37;
var KEY_ENTER = 13;
var KEY_SPACE = 32;
var KEY_COMMA = 188;
var KEY_COLON = 59;
var KEY_ESC = 27;
var KEY_DOLLAR = 52;

function getCaret(node) {
	return node.selectionStart;
}

function setCaret(node, pos) {
	node.selectionStart = pos;
	node.selectionEnd = pos;
}

function startsWith(string, prefix) {
	if (prefix.length > string.length) {
		return false;
	}
	
	for(var i = 0; i < prefix.length; i++) {
		if (string[i] != prefix[i]) {
			return false;
		}
	}
	
	return true;
}

function contains(haystack, needle) {
	for(var i = 0; i < haystack.length; i++) {
		if (haystack[i].toLowerCase() == needle.toLowerCase()) {
			return true;
		}
	}
	return false;
}

function isWhitespace(c) {
	return c == ' ' || c == '\n' || c == '\t';
}

function trim(cadena) {
	for(var i=0; i<cadena.length; )
	{
		if(isWhitespace(cadena.charAt(i)))
			cadena=cadena.substring(i+1, cadena.length);
		else
			break;
	}

	for(var i=cadena.length-1; i>=0; i=cadena.length-1)
	{
		if(isWhitespace(cadena.charAt(i)))
			cadena=cadena.substring(0,i);
		else
			break;
	}
	
	return cadena;
}