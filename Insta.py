# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import request, g, render_template, json, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room
from contextlib import closing
from werkzeug import secure_filename
from flask import Flask
from flask.ext.basicauth import BasicAuth
from flask_jsglue import JSGlue
import zipfile
from io import BytesIO
import time

#pycURL imports
import pycurl
import re
import StringIO
import string

# configuration
DATABASE = '/tmp/insta.db'
DEBUG = True
SECRET_KEY = 'LKDNF(ln3r(sj3r9JIWJ(j(JP#!N(J@91-93jn'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('INSTA_SETTINGS', silent=True)
app.config['BASIC_AUTH_USERNAME'] = 'emojimilan'
app.config['BASIC_AUTH_PASSWORD'] = 'circlecracker'

basic_auth = BasicAuth(app)

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

def get_instas(query = '', id = ''):

    # Login and crawling for #bestview(->to be changed for #emojimilan in final)

    # request instagram login
    b = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://instagram.com/accounts/login/?force_classic_login')
    c.setopt(pycurl.REFERER, 'https://instagram.com/accounts/login/?force_classic_login')
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.COOKIEFILE, 'cookiess.txt')
    c.setopt(pycurl.COOKIEJAR, 'cookiess.txt')
    page = c.perform()
    c.close()
    # preg_match that doesn't really work
    links = re.findall('<input type="hidden" name="csrfmiddlewaretoken" value="([A-z0-9]{32})"/>', b.getvalue())

    # Log into instagram using username+password(-> need to get one from students or whoever) and token retrieved in Links
    # (I actually hard coded the token, since my re.findall didn't work)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://instagram.com/accounts/login/?force_classic_login')
    c.setopt(pycurl.REFERER, 'https://instagram.com/accounts/login/?force_classic_login')
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.POST, True)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(pycurl.POSTFIELDS, "csrfmiddlewaretoken=336ce9019884103a0a3a87dd639c1803&username=[instalia.larinascente]&password=[circlecrackers]")
    c.setopt(pycurl.COOKIEFILE, 'cookiess.txt')
    c.setopt(pycurl.COOKIEJAR, 'cookiess.txt')
    page = c.perform()
    c.close()
    # retrieve 'search for #bestview tag' page and store images data in b object
    c = pycurl.Curl()
    if query is '':
        url = 'https://www.instagram.com/explore/tags/bestview/'
    else:
        url = 'https://www.instagram.com/explore/tags/bestview/?' + query + '=' + id
    c.setopt(pycurl.URL, str(url))
    c.setopt(pycurl.REFERER, 'https://instagram.com/')
    c.setopt(pycurl.HTTPHEADER, [
            'Accept-Language: en-US,en;q=0.8',
            'User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
            'Accept: */*',
            'X-Requested-With: XMLHttpRequest',
            'Connection: keep-alive'
            ])
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.SSL_VERIFYPEER, False)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(pycurl.COOKIEFILE, 'cookiess.txt')
    c.setopt(pycurl.COOKIEJAR, 'cookiess.txt')
    page = c.perform()
    c.close()

    # print the values from b into string variables and parse them
    rawpage = b.getvalue()
    firstsplit = rawpage.split('window._sharedData')
    displaysrc = firstsplit[3].split('"display_src":"')
    displayID = firstsplit[3].split(',"id":"')

    displaysrc_length = len(displaysrc)-8 # The last 7 images are redundant because of instas "Top Post Section"

    # store raw src to be split
    raw_src = []

    # store ID's
    list_ID = []

    for i in range(1,displaysrc_length):
        rawsrc = displaysrc[i].split('?ig_cache_key')
        rawID = displayID[i].split('","display_src"')
        raw_src.append(rawsrc[0])
        list_ID.append(rawID[0])

    raw_src_length = len(raw_src)-1

    # store real src URLs
    list_src = []

    # store [[ID, SRC]] to be used in index template
    the_list = []

    for src in range(0, raw_src_length):
        srcreplaced = raw_src[src].replace("\/", "/")
        list_src.append(srcreplaced)
        tmp_list = [srcreplaced, list_ID[src]]
        the_list.append(tmp_list)
    min_id = list_ID[0]
    max_id = list_ID[raw_src_length-1]
    return the_list, min_id, max_id

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
@basic_auth.required
def root():
    the_list, min_id, max_id = get_instas()
    return render_template('index.html', src=the_list, prev=min_id, next=max_id)

@app.route('/next/<id>')
@basic_auth.required
def next(id):
    the_list, min_id, max_id = get_instas('max_id', id)
    return render_template('index.html', src=the_list, prev=min_id, next=max_id)


def add_file(file, img_type):
    # TODO: add error handling if file not there
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config[img_type], filename)
        file.save(path)


@app.route('/store/<img_type>/<insta_id>', methods=['POST'])
@basic_auth.required
def store(img_type, insta_id=None):
    file = request.files['file']
    filename = file.filename
    # TODO: notify javascript to continue labelling as ignore if error
    delete(insta_id)
    add_file(file, img_type)
    insert('ids', ('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id))
    if img_type == 'like':
        row_id = insert('active', ('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id))
        room = row_id % SCREEN_TOTAL
        image = {'img_type': img_type, 'filename': filename}
        return jsonify({'socket': True, 'data': {'image': image, 'room': room}})
    return jsonify({'socket': False})


@app.route('/upload/', methods=['GET', 'POST'])
@basic_auth.required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        insta_id = filename.split('.')[0]  # Assumes that the filename stays the same
        img_type = 'edited_super'
        image = query_db('select * from active where filename = ?', [filename], one=True)
        if image is None:
            add_file(file, img_type)
            row_id = insert('active',('img_type', 'filename', 'insta_id'), (img_type, filename, insta_id))
            room = row_id % SCREEN_TOTAL
            image = {'img_type': img_type, 'filename': filename}
            return jsonify({'image': image, 'room': room})
        return jsonify({'error': 'File already exists'})
    else:
        return render_template('upload.html')


@app.route('/download/')
@basic_auth.required
def download():
    files = [open(os.path.join(app.config['super'], f)) for f in os.listdir(app.config['super']) if os.path.isfile(os.path.join(app.config['super'], f))]
    if len(files):
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for individualFile in files:
                remove_file(individualFile.name)
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
@basic_auth.required
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

@socketio.on('send-image', namespace='/slides')
def send_image(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    emit('new-slide', data['image'], room=int(data['room']))

@socketio.on('received', namespace='/slides')
def receieved(data):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    emit('image-received', data, broadcast=True)

init_db()

if __name__ == '__main__':
    socketio.run(app, port=15408)  # Remove port number to run locally