
.PHONY: docs

docs:
	rm -r ./docs/source -f
	rm -r ./docs/_templates -f
	rm -r ./docs/_build -f
	sphinx-apidoc -o ./docs/source ./checksum_dict

mypyc:
	mypyc checksum_dict/_utils.py checksum_dict/base.py checksum_dict/default.py --strict --pretty --disable-error-code unused-ignore --disable-error-code import-not-found --install-types 
