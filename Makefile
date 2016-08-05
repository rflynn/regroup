# vim: set ts=8 noet:

test: venv/bin/nosetests
	venv/bin/nosetests --nocapture tests/

venv/bin/nosetests: requirements.txt
	[[ -d venv ]] || { virtualenv -p python3 venv 2>/dev/null || python3 -m venv venv; }
	venv/bin/pip install -r requirements.txt

.PHONY: test clean distclean
