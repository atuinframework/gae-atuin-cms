# -*- coding: utf-8 -*-
from flask.blueprints import Blueprint
from flask import g, abort, render_template, jsonify, request

from google.appengine.ext import ndb, blobstore

from atuin.auth import login_role_required
from markdown import markdown

from . import sanitize_input_text

bp = Blueprint('atuincms.media.admin', __name__)


@bp.route('admin/atuincms/media/images/get-upload-url')
@login_role_required("ADMIN")
def get_image_upload_url():
    page_key_us = request.args['page_key_us']
    image_id = request.args['image_id']

    # create upload url with above parameters
    upload_url = blobstore.create_upload_url(
        g.lurl_for(
            'atuincms.pages.admin.page_image',
            page_key_us=page_key_us,
            image_id=image_id
        )
    )
    return jsonify(result='ok', url=upload_url)


@bp.route('admin/atuincms/media/texts/convert-md-to-html', methods=['POST'])
@login_role_required("ADMIN")
def text_md_to_html():
    text = request.form['text']
    text = sanitize_input_text(text)
    return markdown(text)
