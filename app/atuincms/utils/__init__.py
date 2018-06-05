# -*- coding: utf-8 -*-
import re


def cc_to_pkg(name):
    """
    Convert a name from CamelCase convention to package_name convention.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def pkg_to_cc(name):
    """
    Convert a name from package_name convention to CamelCase convention.
    """
    return name.replace('_', ' ').title().replace(' ', '')
