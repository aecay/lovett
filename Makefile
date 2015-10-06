.PHONY: doc doc-clean doc-push doc-local

doc:
	rm -rf doc/build
	SPHINX_APIDOC_OPTIONS=members,undoc-members,private-members sphinx-apidoc -o doc/build/api --separate --private lovett lovett/tests
	emacs -Q --script doc/org/export-doc.el

doc-push: doc-html
	[ -d /tmp/lovett-doc-git ] || git clone git@github.com:aecay/lovett.git /tmp/lovett-doc-git
	export PWD=`pwd`
	cd /tmp/lovett-doc-git; \
	git checkout master;
	git pull; \
	git checkout docs ; \
	git merge master; \
	mkdir -p doc-built
	cp -r doc/build/* /tmp/lovett-doc-git/doc-built
	cp doc/conf.py /tmp/lovett-doc-git/doc-built
	cd /tmp/lovett-doc-git; \
	git add doc-built; \
	git commit -m "Autobuild documentation"; \
	git push

doc-html: doc
	cp doc/conf.py doc/build
	sphinx-build -b html doc/build doc/html
