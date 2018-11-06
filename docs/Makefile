
.PHONY: book build copy clean

default: book

node_modules:
	yarn install

book: clean build copy

build: node_modules
	./node_modules/.bin/gitbook build

copy:
	cp -R ./_book/* .

clean:
	rm -rf _book
	rm -f *.html
	rm -rf part1
	rm -f search_index.json
	rm -rf gitbook

serve: node_modules
	./node_modules/.bin/gitbook serve
