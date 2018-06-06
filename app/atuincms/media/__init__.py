# -*- coding: utf-8 -*-
import cgi

def sanitize_input_text(txt):
    """
    Apply sanitization to input text.
    :param txt: string The user input text.
    :return: string Sanitized text.
    """
    txt = cgi.escape(txt)

    # allow only the <br>
    txt = txt.replace('&lt;br&gt;', '<br>')
    return txt
