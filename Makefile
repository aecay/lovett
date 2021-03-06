.PHONY: doc doc-clean doc-push doc-local

doc:
	rm -rf doc/build
	SPHINX_APIDOC_OPTIONS=members,undoc-members,private-members sphinx-apidoc -o doc/build/api --separate --private lovett lovett/tests
	emacs -Q --script doc/org/export-doc.el
	cp doc/conf.py doc/build
	cp -r doc/static doc/build
	sphinx-build -b html doc/build doc/html

test:
	nosetests --with-coverage --cover-package=lovett --cover-html --cover-branches
