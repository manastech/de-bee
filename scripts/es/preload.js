function preloadImage(src) {
	var img = new Image(100, 100);
	img.src = "/images/es/" + src;
	preloadedImages.push(img);
}