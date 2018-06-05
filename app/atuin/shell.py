# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.curdir)
import random
import readline
from pprint import pprint

terrys_quotes = [
		"Ripples of paradox spread out across the sea of causality.",
		"DON'T THINK OF IT AS DYING, said Death. JUST THINK OF IT AS LEAVING EARLY TO AVOID THE RUSH."
		"The sun rose slowly, as if it wasn't sure it was worth all the effort.",
		"The pen is mightier than the sword... if the sword is very short, and the pen is very sharp.",
		"Time passed, which, basically, is its job.",
		"Reality is not always what it seems, said Death. Anyway, if they don't want to see me, they certainly don't want to see you. These are aristocrats, boy. They're good at not seeing things.",
		"'And what would humans be without love?' - RARE, said Death.",
		"It wasn't blood in general he couldn't stand the sight of, it was just his blood in particular that was so upsetting.",
		
	]

print "\nFLASK-ATUIN - SCALEBOX Framework on python " + sys.version.split()[0]

from handler import app
from datastore import db

app.test_request_context().push()

for m in sys.argv[1:]:
	if os.path.isfile(m + "/models.py"):
		md = __import__(m + ".models")
		globals().update(vars(md.models))

print "\n{}\n".format(random.choice(terrys_quotes))

os.environ['PYTHONINSPECT'] = 'True'
