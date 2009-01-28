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
	var start = 0;
	if (document.selection) {
		start = getRangeOffsetIE(node, document.selection.createRange());
	} else {
		start = node.selectionStart;
	}
	return start;
}

function getRangeOffsetIE( node, r ) {
  var end = Math.abs( r.duplicate().moveEnd('character', -1000000) );
  // find the anchor element's offset
  var range = r.duplicate();
  r.collapse( false );
  var parentElm = range.parentElement();
  var children = parentElm.getElementsByTagName('*');
  for (var i = children.length - 1; i >= 0; i--) {
    range.moveToElementText( children[i] );
    if ( range.inRange(r) ) {
      parentElm = children[i];
      break;
    }
  }
  range.moveToElementText( parentElm );
  var toReturn = end - Math.abs( range.moveStart('character', -1000000) );
  
  for(var i = toReturn; i >= 0; i--) {
    if (node.value.charCodeAt(i) == 13 || node.value.charCodeAt(i + 1) == 13) {
      toReturn++;
    }
  }
  
  return toReturn;
}


function setCaret(node, pos) {
	if (node.createTextRange) {
		var range = node.createTextRange(); 
        range.move("character", pos); 
        range.select(); 
	} else {
		node.selectionStart = pos;
		node.selectionEnd = pos;
	}
}

function startsWith(string, prefix) {
	if (prefix.length > string.length) {
		return false;
	}
	
	for(var i = 0; i < prefix.length; i++) {
		if (string.charAt(i) != prefix.charAt(i)) {
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
	return c == ' ' || c == '\n' || c == '\t' || c == '\r';
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