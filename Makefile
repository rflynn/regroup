# vim: set ts=8 noet:

test: venv/bin/nosetests
	./venv/bin/python setup.py --quiet test

venv/bin/nosetests: venv

venv: requirements.txt
	test -d venv || virtualenv -p python3 venv
	venv/bin/pip install -U pip
	venv/bin/pip install -r requirements.txt
	-@touch venv  # update timestamp

clean:
	$(RM) -r venv

distclean: clean

.PHONY: test clean distclean
