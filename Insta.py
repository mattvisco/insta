# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, json, jsonify, send_from_directory
from contextlib import closing
from werkzeug import secure_filename
# from juggernaut import Juggernaut

# configuration
DATABASE = '/tmp/insta.db'
DEBUG = True
SECRET_KEY = 'LKDNF(ln3r(sj3r9JIWJ(j(JP#!N(J@91-93jn'
USERNAME = 'admin'
PASSWORD = 'default'
# JUGGERNAUT_DRIVER = 'http://127.0.0.1:5000/application.js'  # TODO: figure out how to run juggernaut

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('INSTA_SETTINGS', silent=True)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LIKES_FOLDER = os.path.join(APP_ROOT, 'static/like/')
SUPER_FOLDER = os.path.join(APP_ROOT, 'static/super/')
EDITED_SUPER_FOLDER = os.path.join(APP_ROOT, 'static/edited_super/')
app.config['like'] = LIKES_FOLDER
app.config['super'] = SUPER_FOLDER
app.config['edited_super'] = EDITED_SUPER_FOLDER
SCREEN_TOTAL = 7

# jug = Juggernaut()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()
    g.db.row_factory = sqlite3.Row

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/store/<img_type>/<insta_id>', methods=['POST'])
def store(img_type, insta_id=None):
    file = request.files['file']
    # TODO: add error handling if file not there
    # TODO: notify javascript to continue labelling as ignore - maybe pop up message
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config[img_type], filename)
        file.save(path)
    delete(insta_id)
    if img_type == 'like' or img_type == 'edited_super':
        g.db.execute('insert into active (img_type, filename, insta_id) values (?, ?, ?)',
                 [img_type, filename, insta_id])
    if img_type is not 'edited_super':
        g.db.execute('insert into ids (img_type, filename, insta_id) values (?, ?, ?)',
                 [img_type, filename, insta_id])
    g.db.commit()
    return json.dumps({'status': 'OK'})

@app.route('/upload_super', methods=['GET', 'POST'])
def upload_super():
    if request.method == 'POST':
        # TODO: talk to andrew and sitrak about if we want insta_id, does it matter?
        # Assumes that the filename stays the same
        insta_id = request.files['file'].filename.split('.')[0]
        store('edited_super')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

def remove_file(insta_id):
    image = query_db('select img_type, filename from ids where insta_id = ?', [insta_id], one=True)
    if image is not None:
        path = os.path.join(app.config[image['img_type']], image['filename'])
        os.remove(path)
        return True
    return False

@app.route('/delete/<insta_id>', methods=['DELETE'])
def delete(insta_id):
    exists = remove_file(insta_id)
    if exists:
        query_db('delete from active where insta_id = ?', [insta_id])
        query_db('delete from ids where insta_id = ?', [insta_id])
        g.db.commit()
    return json.dumps({'status':'OK'})

@app.route('/check_id/<insta_id>')
def check_id(insta_id):
    id_val = query_db('select img_type from ids where insta_id = ?', [insta_id], one=True)
    if id_val is None:
        id_val = 'delete'
    else:
        id_val = id_val[0]
    return jsonify({'idValue': id_val})

@app.route('/get_super/')
def get_super():
    return send_from_directory(app.config['super'])

@app.route('/slideshow/<index>')
def slideshow(index):
    index = int(index)
    all_images = query_db('select img_type, filename from active order by id ASC')
    if len(all_images) == 0:
        return render_template('error.html', message='No images yoo')
    elif index >= len(all_images):
        message = 'Not enough images to start at index: ' + str(index)
        return render_template('error.html', message=message)
    images = []
    while index < len(all_images):
        images.append(all_images[index])
        index += SCREEN_TOTAL
    return render_template('slideshow.html', images=images)

def send_new_paste_notifications(id, image):
    """Notifies clients about new slideshow."""
    jug.publish('paste-replies:%d' % id, image)

#     TODO: figure out a way to watch for special super_like uploads
# ToDo: super like will be edited then stored into "edited-super", once it is uploaded it will need to notify one screen
# TODO: ask andrew about the case where super_like is uploaded and then needs to be removed - if they keep filename the same it'll be easy

if __name__ == '__main__':
    init_db()
    app.run(debug=DEBUG)
