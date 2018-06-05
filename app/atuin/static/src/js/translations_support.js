function _t(textToTranslate) {
	if (TRANSLATIONS[textToTranslate]) {
		return TRANSLATIONS[textToTranslate];
	}
	return textToTranslate;
}