# -*- coding: utf-8 -*-
import cgi


def sanitize_input_text(txt, allowed_tags=['br', 'i']):
    """
    Apply sanitization to input text.

    :param txt: string The user input text.
    :param allowed_tags: string Sanitized text.
    :return:
    """
    txt = cgi.escape(txt)

    # allow only the <br>
    for t in allowed_tags:
        beg = txt.find('&lt;' + t)
        while beg >= 0:
            # restore the excaped <tag
            txt = txt.replace('&lt;' + t, '<' + t, 1)
            end = txt.find('&gt;', beg)
            # restore the > at the end
            txt = txt[:end] + '>' + txt[end + 4:]

            # search for a close tag </tag>
            begc = txt.find('&lt;/' + t + '&gt;', end)
            if begc >= 0:
                # restore the close tag
                txt = txt[:begc] + '</' + t + '>' + txt[begc + 5 + len(t) + 4:]

            beg = txt.find('&lt;' + t, beg)

    return txt
