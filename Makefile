

book:
	gitbook build
	cp -R _book/* ./docs

words:
	wc -w `find . -name '*.md'`
