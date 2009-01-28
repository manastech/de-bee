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
var replaceKind;

var empty = new Array();
var ignore = new Array();
var currentFunction;

function bulk() {
	currentFunction = 'bulk';
	popupName = 'comandoPopup';
	textareaName = 'comando';
}

function cow() {
	currentFunction = 'cow';
	popupName = 'cowPopup';
	textareaName = 'cow';
}

function bulkKeyDown(event) {
	bulk();
	return keyDown(event);
}

function bulkKeyUp(event) {
	bulk();
	return keyUp(event);
}

function cowKeyDown(event) {
	cow();
	return keyDown(event);
}

function cowKeyUp(event) {
	cow();
	return keyUp(event);
}

function bulkEvaluateShowSuggestions() {
	bulk();
	return evaluateShowSuggestions();
}

function bulkHideSuggestions() {
	bulk();
	return hideSuggestions();
}

function cowEvaluateShowSuggestions() {
	cow();
	return evaluateShowSuggestions();
}

function cowHideSuggestions() {
	cow();
	return hideSuggestions();
}

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
			if (event.keyCode == KEY_ENTER && replaceKind != 'paga' && replaceKind != 'miembrosEnPaga') {
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

	//if (pos != text.length && !isWhitespace(text.charAt(pos))) {
	//	return empty;
	//}
	
	pos--;
	
	if (currentFunction == 'bulk') {
		thepaga = paga;
	} else {
		thepaga = razon;
	}
	
	while(pos >= 0) {
		if (text.charAt(pos) == ':') {
			if (pos >= thepaga[0].length) {
				for(var i = 0; i < thepaga[0].length; i++) {
					if (text.charAt(pos - (thepaga[0].length - i)).toLowerCase() != thepaga[0].charAt(i).toLowerCase()) {
						ignore = empty;
						replaceKind = 'comidas';
						return comidas;
					}
				}
				
				if (currentFunction == 'cow') {
					replaceKind = 'empty';
					return empty;
				}
				
				ignore = empty;
				replaceKind = 'miembrosEnPaga';
				return miembros;
			}
		} else if (text.charAt(pos) == '\n' || text.charCodeAt(pos) == 13 || text.charCodeAt(pos) == 10) {
			computeIgnore();
			replaceKind = 'miembros';
			return miembros;
		} else if (text.charAt(pos) == '$') {
			replaceKind = 'empty';
			return empty;
		}
		pos--;
	}
	
	ignore = empty;
	replaceKind = 'paga';
	return thepaga;
}

function computeIgnore() {
	var node = document.getElementById(textareaName);
	var text = node.value;
	
	ignore = new Array();
	
	var last = 0;
	for(var i = 0; i < text.length; i++) {
		if (text.charAt(i) == ':') {
			ignore.push(trim(text.substring(last, i)));
		} else if (text.charAt(i) == ',') {
			ignore.push(trim(text.substring(last, i)));
			last = i + 1;
		} else if (text.charAt(i) == '\n') {
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
	while(pos >= 0 && text.charAt(pos) != ':') {
		if (text.charAt(pos) == ',') {
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
		if ('0' <= item.charAt(0) && item.charAt(0) <= '9') {
			up = 10 * up + parseInt(item.charAt(0));
			item = item.substring(1);
		} else {
			break;
		}
	}
	
	var symbol = 0;
	if (item.length > 0 && (item.charAt(0) == '.' || item.charAt(0) == '/')) {
		symbol = item.charAt(0);
		item = item.substring(1);
		
		while(item.length > 0) {
			if ('0' <= item.charAt(0) && item.charAt(0) <= '9') {
				down = 10 * down + parseInt(item.charAt(0));
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
	
	while(pos >= 0 && !isWhitespace(text.charAt(pos))) {
		pos--;
	}
	
	var replacement = selectedSuggestion;
	
	if (keyCode == KEY_SPACE) {
		replacement += ' ';
	} else if (keyCode == KEY_ENTER) {
		if (replaceKind == 'paga' || replaceKind == 'miembros') {
			replacement += ': ';
		}
		if (replaceKind == 'miembros' && currentFunction == 'cow') {
			replacement += '$';
		}
		if (replaceKind == 'miembrosEnPaga') {
			if (!document.selection) {
				replacement += '\n';
			}
		}
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
	
	while(pos >= 0 && !isWhitespace(text.charAt(pos))) {
		prefix = text.charAt(pos) + prefix;
		pos--;
	}
	
	return prefix;
}