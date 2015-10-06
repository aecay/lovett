.PHONY: doc doc-clean doc-push doc-local

doc:
	rm -rf doc/build
	SPHINX_APIDOC_OPTIONS=members,undoc-members,private-members sphinx-apidoc -o doc/build/api --separate --private lovett lovett/tests
	emacs -Q --script doc/org/export-doc.el

doc-push: doc-html
	cp -r doc/build/* ../lovett-docs/doc-built
	cp doc/conf.py ../lovett-docs/doc-built
	cd ../lovett-docs; \
	git fetch --all; \
	git merge --no-edit master; \
	git add doc-built; \
	git commit -m "Autobuild docs"; \
	git push

doc-html: doc
	cp doc/conf.py doc/build
	sphinx-build -b html doc/build doc/html
