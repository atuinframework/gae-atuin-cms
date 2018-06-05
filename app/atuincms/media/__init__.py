# -*- coding: utf-8 -*-
import bleach


def sanitize_input_text(txt):
    """
    Apply sanitization to input text.
    :param txt: string The user input text.
    :return: string Sanitized text.
    """
    txt = bleach.clean(txt, tags=['br'])
    txt = bleach.linkify(txt)
    return txt
