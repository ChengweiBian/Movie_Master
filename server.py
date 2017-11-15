import os
from sqlalchemy import *
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash, url_for
from datetime import date

DATABASEURI = "postgresql://cb3331:515059@35.196.90.148/proj1part2"
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_object(__name__)

engine = create_engine(DATABASEURI)

# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

def convert(date):
  return 'None' if date==date.max else date


@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass



@app.route('/')
def index():
  
  data = {'type': 'home'}
  data['movie'] = {'id': None}
  # data['error'] = request.args.get('error', None)
  # print(session)
  
  return render_template('movie.html', data=data)



@app.route('/movie', methods=['POST', 'GET'])
def movie():
  data = {'type': 'searchMovie'}

  if request.method == "POST":
    movie_id = None
    name = request.form['name']
    cursor = g.conn.execute("SELECT movie_id FROM movie WHERE name ILIKE '{0}';".format(name))
    for i in cursor:
      movie_id = i[0]
    cursor.close()
    if not movie_id:
      flash('No result found!', 'search')
      return redirect('/')
    return redirect('/movie?movie_id={0}'.format(movie_id))

  movie_id = int(request.args.get('movie_id', None))
  cursor = g.conn.execute("SELECT * FROM movie WHERE movie_id = '{0}';".format(movie_id))
  for i in cursor:
    data['movie'] = {'id': i[0], 'name': i[1], 'overview': i[2], 'country': i[3], 'release_date': convert(i[4]), 'rate': i[5], 'poster': i[6], 'background': i[7]}
  cursor.close()

  cursor = g.conn.execute("SELECT ar.actor_id, ar.name, ar.profile FROM actor ar, act a WHERE a.actor_id = ar.actor_id AND a.movie_id = '{0}';".format(movie_id))
  data['actor'] = [{'id': i[0], 'name': i[1], 'profile': i[2]} for i in cursor]
  cursor.close()

  cursor = g.conn.execute("SELECT dr.director_id, dr.name, dr.profile FROM director dr, direct d WHERE d.director_id = dr.director_id AND d.movie_id = '{0}';".format(movie_id))
  data['director'] = [{'id': i[0], 'name': i[1], 'profile': i[2]} for i in cursor]
  cursor.close()

  cursor = g.conn.execute("SELECT author, content FROM review WHERE movie_id = '{0}';".format(movie_id))
  data['review'] = [{'author': i[0], 'content': i[1]} for i in cursor]
  cursor.close()

  cursor = g.conn.execute("SELECT g.name FROM genre g, belong b WHERE g.genre_id=b.genre_id AND b.movie_id='{0}';".format(movie_id))
  data['genre'] = [result[0] for result in cursor]
  cursor.close()

  cursor = g.conn.execute("SELECT c.name FROM company c, produce p WHERE c.company_id=p.company_id AND p.movie_id='{0}';".format(movie_id))
  data['company'] = [result[0] for result in cursor]
  cursor.close()

  if session.get('logged_in') and len(session.get('favorite')) > 0:
    if movie_id in [i['id'] for i in session.get('favorite')]:
      data['liked'] = True
    else:
      data['liked'] = False

  return render_template("movie.html", data=data)





@app.route('/director', methods=['POST', 'GET'])
def director():
  data = {'type': 'searchDirector'}

  if request.method == "POST":
    name = request.form['name']
    director_id = None
    cursor = g.conn.execute("SELECT director_id FROM director WHERE name ILIKE '{0}';".format(name))
    for i in cursor:
      director_id = i[0]
    cursor.close()
    if not director_id:
      flash('No result found!', 'search')
      return redirect('/')
    return redirect('/director?director_id={0}'.format(director_id))

  director_id = int(request.args.get('director_id'))
  cursor = g.conn.execute("SELECT * FROM director WHERE director_id = '{0}';".format(director_id))
  for i in cursor:
    data['person'] = {'id': i[0], 'name': i[1], 'place_of_birth': i[2], 'birthday': convert(i[3]), 'biography': i[4], 'profile': i[5]}
  cursor.close()

  cursor = g.conn.execute("SELECT m.movie_id, m.name, m.poster FROM movie m, direct d WHERE d.movie_id = m.movie_id AND d.director_id = '{0}';".format(director_id))
  data['movie'] = [{'id': i[0], 'name': i[1], 'poster': i[2]} for i in cursor]
  cursor.close()

  return render_template("movie.html", data=data)





@app.route('/actor', methods=['POST', 'GET'])
def actor():
  data = {'type': 'searchActor'}

  if request.method == "POST":
    name = request.form['name']
    actor_id = None
    print(name)
    cursor = g.conn.execute("SELECT actor_id FROM actor WHERE name ILIKE '{0}';".format(name))
    for i in cursor:
      actor_id = i[0]
    cursor.close()
    if not actor_id:
      flash('No result found!', 'search')
      return redirect('/')
    return redirect('/actor?actor_id={0}'.format(actor_id))

  actor_id = int(request.args.get('actor_id'))
  cursor = g.conn.execute("SELECT * FROM actor WHERE actor_id = '{0}';".format(actor_id))
  for i in cursor:
    data['person'] = {'id': i[0], 'name': i[1], 'place_of_birth': i[2], 'birthday': convert(i[3]), 'biography': i[4], 'profile': i[5]}
  cursor.close()
  print(data)

  cursor = g.conn.execute("SELECT m.movie_id, m.name, m.poster FROM movie m, act a WHERE a.movie_id = m.movie_id AND a.actor_id = '{0}';".format(actor_id))
  data['movie'] = [{'id': i[0], 'name': i[1], 'poster': i[2]} for i in cursor]
  cursor.close()

  return render_template("movie.html", data=data)





@app.route('/signup', methods=['POST'])
def signup():
  error = None
  username = request.form["username"]
  password = request.form["password"]

  cursor = g.conn.execute("SELECT * FROM users WHERE username = '{0}';".format(username))
  rows = list(cursor)
  cursor.close()

  if len(rows) != 0:
    error = 'Username already exists!'
  else:
    try:
      g.conn.execute(text("INSERT INTO users VALUES ('{0}', '{1}');".format(username, password)))
      session['logged_in'] = True
      session['username'] = username
      flash('You were logged in')
      return redirect('/')
    except:
      error = 'Invalid password!'

  return render_template("movie.html", error=error)





@app.route('/login', methods=['POST'])
def login():
  username = request.form["username"]
  password = request.form["password"]
  action = request.form['action']

  cursor = g.conn.execute("SELECT * FROM users WHERE username = '{0}';".format(username))
  rows = list(cursor)
  cursor.close()

  if action == 'login':
    if len(rows) == 0:
      flash('Invalid username!', 'login')
    elif rows[0][1] != password:
      flash('Invalid password!', 'login')
    else:
      session['logged_in'] = True
      session['username'] = username
      cursor = g.conn.execute("SELECT m.movie_id, m.name, m.poster FROM movie m, likes l WHERE l.movie_id = m.movie_id AND l.username = '{0}';".format(username))
      session['favorite'] = [{'id': i[0], 'name': i[1], 'poster': i[2]} for i in cursor]
      cursor.close()
      return redirect(request.referrer)
  else:
    if len(rows) != 0:
      flash('Username already exists!', 'login')
    else:
      try:
        g.conn.execute(text("INSERT INTO users VALUES ('{0}', '{1}');".format(username, password)))
        session['logged_in'] = True
        session['username'] = username
        session['favorite'] = []
        return redirect(request.referrer)
      except:
        flash('Invalid password!', 'login')

  return redirect(request.referrer+'#login')





@app.route('/logout')
def logout():
    # movie_id = request.args.get('movie_id', None)
    # session['logged_in'] = False
    session.clear()
    # flash('You were logged out')
    # return redirect('/movie?movie_id={0}'.format(movie_id))
    return redirect(request.referrer)





@app.route('/addFavorite')
def addFavorite():
    movie_id = int(request.args.get('movie_id', None))
    try:
      print("INSERT INTO likes VALUES ('{0}', {1});".format(session['username'], movie_id))
      engine.execute("INSERT INTO likes VALUES ('{0}', {1});".format(session['username'], movie_id))
    except:
      print('Error when insert into table Likes!')

    cursor = g.conn.execute("SELECT movie_id, name, poster FROM movie WHERE movie_id = {0};".format(movie_id))
    for i in cursor:
      session['favorite'].append({'id': i[0], 'name': i[1], 'poster': i[2]})
    cursor.close()
    return redirect(request.referrer+'#about')





@app.route('/deleteFavorite')
def deleteFavorite():
    movie_id = int(request.args.get('movie_id', None))
    try:
      # print("INSERT INTO likes VALUES ('{0}', {1});".format(session['username'], movie_id))
      engine.execute("DELETE FROM likes WHERE username = '{0}' AND movie_id = {1};".format(session['username'], movie_id))
    except:
      print('Error when insert into table Likes!')

    session['favorite'] = [i for i in session['favorite'] if i.get('id') != movie_id]
    return redirect(request.referrer+'#about')





if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)

  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)
    #session['logged_in'] = False

  run()
