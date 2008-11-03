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

// Define these
// var popupName;
// var textareaName;
// var comidas;
// var paga;
// var miembros;
// var textHeight;
// var suggestionsPerPage;

var index = 0;
var numberOfSuggestions;
var selectedSuggestion;
var currentSuggestions;

var empty = new Array();
var ignore = new Array();

function keyDown(event) {
	var popup = document.getElementById(popupName);
	
	switch(event.keyCode) {
	case KEY_DOWN:
		if (index < numberOfSuggestions - 1) {
			index++;
			showSuggestions();
		}
		if (popup.style.display != 'none') {
			return false;
		}
		break;
	case KEY_UP:
		if (index > 0) {
			index--;
			showSuggestions();
		}
		if (popup.style.display != 'none') {
			return false;
		}
		break;
	case KEY_ENTER:
	//case KEY_SPACE:
	case KEY_COLON:
	case KEY_COMMA:		
		if (popup.style.display != 'none') {
			return false;
		}
		break;
	case KEY_ESC:
		popup.style.display = 'none';
		break;
	}
}

function keyUp(event) {
	var popup = document.getElementById(popupName);
	
	switch(event.keyCode) {
	case KEY_DOWN:
	case KEY_UP:
		break;
	case KEY_ENTER:
	//case KEY_SPACE:
	case KEY_COMMA:
	case KEY_COLON:		
		if (popup.style.display != 'none') {
			replace(event.keyCode);
			if (event.keyCode == KEY_ENTER) {
				popup.style.display = 'none';
			} else {
				evaluateShowSuggestions();
			}			
			return false;
		} else {
			evaluateShowSuggestions();
		}
		break;
	case KEY_LEFT:
	case KEY_RIGHT:
		popup.style.display = 'none';
		break;
	case KEY_DOLLAR:
		appendPrice();
		break;
	case KEY_ESC:
		break;
	default:
		evaluateShowSuggestions();
		break;
	}
}

function evaluateShowSuggestions() {
	index = 0;		
	currentSuggestions = getCurrentSuggestions();
	showSuggestions();
}

function hideSuggestions() {
	var popup = document.getElementById(popupName);
	popup.style.display = 'none';
}

function showSuggestions() {
	var popup = document.getElementById(popupName);
	var prefix = getPrefix().toLowerCase();
	
	popup.innerHTML = '';
	
	numberOfSuggestions = 0;
	for(var i = 0; i < currentSuggestions.length; i++) {
		if (prefix.length < currentSuggestions[i].length && startsWith(currentSuggestions[i].toLowerCase(), prefix) && !contains(ignore, currentSuggestions[i])) {
			var s = currentSuggestions[i];
			if (currentSuggestions == comidas) {
				s += "<i> ... $" + precios[s] + "</i>";
			}
			if (numberOfSuggestions == index) {
				popup.innerHTML += '<span style="color:blue;font-weight:bold;">' + s + '</style>';
				selectedSuggestion = currentSuggestions[i];
			} else {
				popup.innerHTML += s;
			}
			popup.innerHTML += '<br/>';
			numberOfSuggestions++;
		}
	}
	
	if (numberOfSuggestions > 0) {
		popup.style.display = '';
		if (numberOfSuggestions > suggestionsPerPage) {
			popup.style.height = (textHeight * suggestionsPerPage) + "px";
		} else {
			popup.style.height = (textHeight * numberOfSuggestions) + "px";
		}
		popup.scrollTop = textHeight * index - (suggestionsPerPage % 2 == 0 ? suggestionsPerPage / 2 : (suggestionsPerPage - 1) / 2) * textHeight;
	} else {
		popup.style.display = 'none';
	}
}

function getCurrentSuggestions() {
	var node = document.getElementById(textareaName);
	var pos = getCaret(node);
	var text = node.value;
	
	if (pos != text.length && !isWhitespace(text[pos])) {
		return empty;
	}
	
	pos--;
	
	while(pos >= 0) {
		if (text[pos] == ':') {
			if (pos >= paga[0].length) {
				for(var i = 0; i < paga[0].length; i++) {
					if (text[pos - (paga[0].length - i)].toLowerCase() != paga[0][i].toLowerCase()) {
						ignore = empty;
						return comidas;
					}
				}
				ignore = empty;
				return miembros;
			}
		} else if (text[pos] == '\n') {
			computeIgnore();
			return miembros;
		} else if (text[pos] == '$') {
			return empty;
		}
		pos--;
	}
	
	ignore = empty;
	return paga;
}

function computeIgnore() {
	var node = document.getElementById(textareaName);
	var text = node.value;
	
	ignore = new Array();
	
	var last = 0;
	for(var i = 0; i < text.length; i++) {
		if (text[i] == ':') {
			ignore.push(trim(text.substring(last, i)));
		} else if (text[i] == ',') {
			ignore.push(trim(text.substring(last, i)));
			last = i + 1;
		} else if (text[i] == '\n') {
			last = i + 1;
		}
	}
}

function appendPrice() {
	var node = document.getElementById(textareaName);
	var originalPos = getCaret(node);
	var pos = originalPos - 1;
	var text = node.value;
	var price = 3 + '';
	
	var items = new Array();
	var last = pos;
	while(pos >= 0 && text[pos] != ':') {
		if (text[pos] == ',') {
			items.push(trim(text.substring(pos + 1, last)));	
			last = pos;
		}
		pos--;
	}
	
	if (pos != last) {
		items.push(trim(text.substring(pos + 1, last)));	
	}
	
	var totalPrice = 0;
	for(var i = 0; i < items.length; i++) {
		var subPrice = calculatePrice(items[i]);
		if (subPrice == 0) {
			totalPrice = 0;
			break;
		} else {
			totalPrice += subPrice;
		}
	}
	
	if (totalPrice != 0) {
		totalPrice = Math.round(totalPrice * 100) / 100;		
		totalPrice += '';
		node.value = text.substring(0, originalPos) + totalPrice + text.substring(originalPos);
		setCaret(node, originalPos + totalPrice.length);
	}
}

function calculatePrice(item) {
	var up = 0;
	var down = 0;
	
	while(item.length > 0) {
		if ('0' <= item[0] && item[0] <= '9') {
			up = 10 * up + parseInt(item[0]);
			item = item.substring(1);
		} else {
			break;
		}
	}
	
	var symbol = 0;
	if (item.length > 0 && (item[0] == '.' || item[0] == '/')) {
		symbol = item[0];
		item = item.substring(1);
		
		while(item.length > 0) {
			if ('0' <= item[0] && item[0] <= '9') {
				down = 10 * down + parseInt(item[0]);
				item = item.substring(1);
			} else {
				break;
			}
		}
	}
	
	if (symbol == '.') {
		up = parseFloat(up + symbol + down);
	} else if (symbol == '/' && down != 0) {
		up /= down;
	}
	
	if (up == 0) {
		up = 1;
	}
	
	var val = precios[trim(item)];
	if (val) {
		return up * val;
	} else {
		return 0;
	}
}

function replace(keyCode) {
	var node = document.getElementById(textareaName);
	var originalPos = getCaret(node);
	var pos = originalPos - 1;
	var text = node.value;
	
	while(pos >= 0 && !isWhitespace(text[pos])) {
		pos--;
	}
	
	var replacement = selectedSuggestion;
	if (keyCode == KEY_SPACE) {
		replacement += ' ';
	} else if (keyCode == KEY_COMMA) {
		replacement += ', ';
	} else if (keyCode == KEY_COLON) {
		replacement += ': ';
	}
	
	var oldScrollTop = node.scrollTop;	
	node.value = text.substring(0, pos + 1) + replacement + text.substring(originalPos);
	setCaret(node, pos + replacement.length + 1);	
	node.scrollTop = oldScrollTop;
}

function getPrefix() {
	var node = document.getElementById(textareaName);
	var pos = getCaret(node) - 1;
	var text = node.value;
	var prefix = '';
	
	while(pos >= 0 && !isWhitespace(text[pos])) {
		prefix = text[pos] + prefix;
		pos--;
	}
	return prefix;
}

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