# -*- coding: utf-8 -*-
from flask import g, render_template, jsonify, flash, request, abort, redirect


def index(page, **kwargs):
	return render_template('pages/home/admin/index.html', page=page, **kwargs)
