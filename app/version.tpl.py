# -*- coding: utf-8 -*-
version = (0, 0, 1)
date = (5, 6, 2018)

string = "{}.{}.{}".format(*version)
date_string = '{}.{}.{}'.format(*date)

full_string = ' - '.join((string, date_string))
