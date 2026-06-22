from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import os, logging
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
import paho.mqtt.client as mqtt
import ssl

logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]
app.config['PERMANENT_SESSION_LIFETIME'] = 180
mysql = MySQL(app)

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        if not request.form.get("usuario"):
            return "el campo usuario es obligatorio"
        elif not request.form.get("password"):
            return "el campo contraseña es obligatorio"

        passhash = generate_password_hash(request.form.get("password"), method='scrypt', salt_length=16)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (usuario, hash) VALUES (%s,%s)", (request.form.get("usuario"), passhash[17:]))
        
        if mysql.connection.affected_rows():
            flash('Se agregó un usuario')
            logging.info("se agregó un usuario")
        
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    return render_template('registrar.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form.get("usuario"):
            return "el campo usuario es obligatorio"
        elif not request.form.get("password"):
            return "el campo contraseña es obligatorio"

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario LIKE %s", (request.form.get("usuario"),))
        rows = cur.fetchone()
        
        if rows:
            if check_password_hash('scrypt:32768:8:1$' + rows[2], request.form.get("password")):
                session.permanent = True
                session["user_id"] = request.form.get("usuario")
                logging.info("se autenticó correctamente")
                cur.close()
                return redirect(url_for('index'))
            else:
                flash('usuario o contraseña incorrecto')
        else:
            flash('usuario o contraseña incorrecto')
            
        cur.close()
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/')
@require_login
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nodos')
    datos = cur.fetchall()
    cur.close()
    return render_template('index.html', nodos=datos)

@app.route('/add_nodo', methods=['POST'])
@require_login
def add_nodo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mac = request.form['mac']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO nodos (mac, nombre) VALUES (%s,%s)", (mac, nombre))
        
        if mysql.connection.affected_rows():
            flash('Se agregó un dispositivo')
            logging.info("se agregó un dispositivo")
            mysql.connection.commit()
            
        cur.close()
    return redirect(url_for('index'))

@app.route('/borrar/<string:id>', methods=['GET'])
@require_login
def borrar_nodo(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM nodos WHERE id = %s', (id,))
    
    if mysql.connection.affected_rows():
        flash('Se eliminó un dispositivo')
        logging.info("se eliminó un dispositivo")
        mysql.connection.commit()
        
    cur.close()
    return redirect(url_for('index'))

@app.route('/editar/<id>', methods=['GET'])
@require_login
def conseguir_nodo(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM nodos WHERE id = %s', (id,))
    datos = cur.fetchone()
    cur.close()
    return render_template('editar-nodo.html', nodo=datos)

@app.route('/actualizar/<id>', methods=['POST'])
@require_login
def actualizar_nodo(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        mac = request.form['mac']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE nodos SET mac=%s, nombre=%s WHERE id=%s", (mac, nombre, id))
        
        if mysql.connection.affected_rows():
            flash('Se actualizó un dispositivo')
            logging.info("se actualizó un dispositivo")
            mysql.connection.commit()
            
        cur.close()
    return redirect(url_for('index'))

@app.route('/control', methods=['GET', 'POST'])
@require_login
def control():
    cur = mysql.connection.cursor()
    cur.execute("SELECT mac FROM nodos")
    nodos = [row[0] for row in cur.fetchall()] 
    cur.close()

    if request.method == 'POST':
        nodo = request.form.get('nodo')
        accion = request.form.get('accion')
        
        client = mqtt.Client()
        client.tls_set(cert_reqs=ssl.CERT_NONE) 
        client.username_pw_set(os.environ["MQTT_USR"], os.environ["MQTT_PASS"])
        client.connect(os.environ["SERVIDOR"], int(os.environ["PUERTO_MQTTS"]))

        if accion == 'destello':
            msg = client.publish(f"{nodo}/destello", "1")
            msg.wait_for_publish()
            flash(f"Comando de destello enviado al nodo {nodo}")
            logging.info(f"Destello enviado a {nodo}")
            
        elif accion == 'setpoint':
            valor = request.form.get('setpoint_val')
            if valor:
                msg = client.publish(f"{nodo}/setpoint", valor)
                msg.wait_for_publish()
                flash(f"Setpoint {valor} enviado al nodo {nodo}")
                logging.info(f"Setpoint {valor} enviado a {nodo}")
        
        client.disconnect()
        return redirect(url_for('control'))

    return render_template('control.html', nodos=nodos)

@app.route("/logout")
@require_login
def logout():
    logging.info("el usuario {} cerró su sesión".format(session.get("user_id")))
    session.clear()
    return redirect(url_for('index'))