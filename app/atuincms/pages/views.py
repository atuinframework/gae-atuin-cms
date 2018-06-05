# -*- coding: utf-8 -*-
from flask import g, render_template, redirect, flash, request, abort


def render_page(page, **kwargs):
    return render_template('atuincms/pages/base.html', **kwargs)
