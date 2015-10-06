.PHONY: doc doc-clean doc-push doc-local

doc:
	rm -rf doc/build
	SPHINX_APIDOC_OPTIONS=members,undoc-members,private-members sphinx-apidoc -o doc/build/api --separate --private lovett lovett/tests
	emacs -Q --script doc/org/export-doc.el

doc-clean:
	rm -r doc-out

doc-push:
	git clone https://github.com/aecay/lovett.git doc-git
	cd doc-git
	git config user.name "Travis CI"
	git config user.email "aaronecay+travis@gmail.com"
	git checkout docs
	rm -r *
	cp ../doc/build/* .
	cp ../doc/conf.py .
	git add .
	git commit -m "Autobuild documentation"
	git push "https://${GH_TOKEN}@${GH_REF}" > /dev/null

doc-local: doc
	cp doc/conf.py doc/build
	sphinx-build -b html doc/build doc/html
