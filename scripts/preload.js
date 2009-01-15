var preloadedImages = new Array();

if (document.images) {
	preloadTabImages("home");
	preloadTabImages("mygroups");
	preloadTabImages("Actions");
	preloadTabImages("balance");
	preloadTabImages("History");
	preloadTabImages("home");
	preloadTabImages("InvitePeople");
	preloadTabImages("mygroups");
	preloadTabImages("properties");
}

function preloadTabImages(name) {
	preloadImage("s_" + name + "_OFF.gif");
	preloadImage("s_" + name + "_ON.gif");
	preloadImage("s_" + name + "_OVER.gif");
}