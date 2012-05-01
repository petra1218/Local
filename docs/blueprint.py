#-*- coding:utf-8 -*-
from flask import Blueprint
from flask import render_template
from flask import url_for, redirect, send_file, request
from flask import abort
from models import Doc
from database import db_session
import os

HOME_PAGES = ['index.html', 'index.htm', 'default.html', 'default.htm']

docs = Blueprint('docs', __name__, url_prefix='/docs',
        template_folder='templates', static_folder='static')

@docs.route('/', methods=['GET'])
def index():
    docs = Doc.query.all()
    return render_template('docs/index.html', docs=docs)

@docs.route('/', methods=['POST'])
def add():
    name = request.form.get('name')
    alias = request.form.get('slug')
    path = request.form.get('path')
    doc = Doc(name, path, alias)
    db_session.add(doc)
    db_session.commit()
    return redirect(url_for('.index'))

@docs.route('/<slug>/', methods='DELETE')
def remove(slug):
    return redirect(url_for('index'))

@docs.route('/<slug>/')
@docs.route('/<slug>/<path:filename>')
def view(slug, filename=''):
    doc = db_session.query(Doc).filter_by(slug=slug).first()
    print '###############################', doc
    if doc:
        doc_file = os.path.join(doc.path, filename)
        if os.path.isfile(doc_file):
            return send_file(doc_file)
        elif os.path.isdir(doc_file):
            if filename and not filename.endswith('/'):
                return redirect(url_for('.view', slug=slug, filename=filename+'/'))
            else:
                for page in HOME_PAGES:
                    if os.path.exists(os.path.join(doc_file, page)):
                        return redirect(url_for('.view', slug=slug, filename=filename + page))
    abort(404)

@docs.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
