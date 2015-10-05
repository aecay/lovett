.PHONY: doc doc-clean

doc:
	rm -rf doc/*.rst doc/api
	SPHINX_APIDOC_OPTIONS=members,undoc-members,private-members sphinx-apidoc -o doc/api --separate --private lovett lovett/tests
	emacs -Q --script doc/org/export-doc.el
	sphinx-build -b html doc doc-out

doc-clean:
	rm -r doc-out
