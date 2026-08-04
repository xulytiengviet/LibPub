.PHONY: prepare build test clean serve

prepare:
	python3 scripts/prepare_sources.py --write-back

build: prepare
	python3 scripts/build.py --output output

test:
	python3 -m unittest discover -s tests -v

serve: build
	python3 -m http.server 8000 --directory output

clean:
	rm -rf .libpub dist output
