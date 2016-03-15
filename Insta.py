# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import request, g, render_template, json, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room
from contextlib import closing
from werkzeug import secure_filename
from flask import Flask
from flask_jsglue import JSGlue
import zipfile
from io import BytesIO
import time

# configuration
DATABASE = '/tmp/insta.db'
DEBUG = True
SECRET_KEY = 'LKDNF(ln3r(sj3r9JIWJ(j(JP#!N(J@91-93jn'
USERNAME = 'admin'
PASSWORD = 'default'

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
SCREEN_TOTAL = 2

jsglue = JSGlue(app)

socketio = SocketIO(app)

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


def insert(table, fields=(), values=()):
    # g.db is the database connection
    cur = g.db.cursor()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    g.db.commit()
    id = cur.lastrowid
    cur.close()
    return id


@app.route('/')
def root():
    return render_template('index.html')


def add_file(file, img_type):
    # TODO: add error handling if file not there
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config[img_type], filename)
        file.save(path)


@app.route('/store/<img_type>/<insta_id>', methods=['POST'])
def store(img_type, insta_id=None):
    file = request.files['file']
    filename = file.filename
    # TODO: notify javascript to continue labelling as ignore if error
    delete(insta_id)
    add_file(file, img_type)
    if img_type == 'like':
        insert('active', ('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id))
    insert('ids', ('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id))
    return json.dumps({'status': 'OK'})


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        insta_id = filename.split('.')[0]  # Assumes that the filename stays the same
        img_type = 'edited_super'
        image = query_db('select * from active where filename = ?', [filename], one=True)
        if image is None:
            add_file(file, img_type)
            row_id = insert('active',('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id)) - 1
            print row_id
            room = row_id % SCREEN_TOTAL
            print room
            image = {'img_type': img_type, 'filename': filename}
            return jsonify({'image': image, 'room': room})
        return jsonify({'error': 'File already exists'})
    else:
        return render_template('upload.html')


@socketio.on('upload complete', namespace='/slides')
def upload_complete(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    emit('new-slide', data['image'], room=int(data['room']))


@app.route('/download/')
def download():
    files = [open(os.path.join(app.config['super'], f)) for f in os.listdir(app.config['super']) if os.path.isfile(os.path.join(app.config['super'], f))]
    if(len(files)):
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for individualFile in files:
                data = zipfile.ZipInfo(os.path.basename(individualFile.name))
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(data, individualFile.read())
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='super_likes.zip', as_attachment=True)
    else:
        return render_template('error.html', message='No files')


def get_filename_from_id(insta_id):
    image = query_db('select img_type, filename from ids where insta_id = ?', [insta_id], one=True)
    path = None
    if image is not None:
        path = os.path.join(app.config[image['img_type']], image['filename'])
    return path


def remove_file(path):
    if path is not None:
        try:
            os.remove(path)
            return True
        except:
            return False
    return False


@app.route('/delete/<insta_id>', methods=['DELETE'])
def delete(insta_id):
    path = get_filename_from_id(insta_id)
    exists = remove_file(path)
    if exists:
        query_db('delete from active where insta_id = ?', [insta_id])
        query_db('delete from ids where insta_id = ?', [insta_id])
        g.db.commit()
    return json.dumps({'status': 'OK'})


def delete_file_with_name(path, filename):
    exists = remove_file(path)
    if exists:
        query_db('delete from active where filename = ?', [filename])
        query_db('delete from ids where filename = ?', [filename])
        g.db.commit()
    return json.dumps({'status': 'OK'})


@app.route('/check_id/<insta_id>')
def check_id(insta_id):
    id_val = query_db('select img_type from ids where insta_id = ?', [insta_id], one=True)
    if id_val is None:
        id_val = 'delete'
    else:
        id_val = id_val[0]
    return jsonify({'idValue': id_val})


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


@socketio.on('joined', namespace='/slides')
def joined(data):
    room = int(data['room'])
    join_room(room)

# TODO: make uploading unique i.e. no duplicates

if __name__ == '__main__':
    init_db()
    socketio.run(app)
