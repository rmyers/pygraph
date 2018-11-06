

book:
	$(MAKE) -C docs book

serve:
	$(MAKE) -C docs serve

words:
	wc -w `find . -name "*.md" -not -path "./docs/node_modules/*"`
