# Añadiendo el framewoprk Flask
from flask import Flask
# Importando la plantilla HTML(index.html), recepciona la info, redireccionar y mostrar la info
from flask import render_template, request, redirect, session
# Importando la libreria Flask Mysql para la conexion a la DB
from flaskext.mysql import MySQL
# Libreria para controlar el tiempo si archivos tienen el mismo nombre pero son diferentes
from datetime import datetime
# Accedendo a la informacion de archivos(imagenes en este caso)
from flask import send_from_directory
import os

# Creando la aplicacion
app=Flask(__name__)
# Variable de Sesion
app.secret_key="Web.py_flask"
# Creando la conexion a la DB
mysql=MySQL()
# Usuario y contraseña
app.config['MYSQL_DATABASE_HOST'] = 'localhost' # Direccion
app.config['MYSQL_DATABASE_USER'] = 'root'  # Usuario
app.config['MYSQL_DATABASE_PASSWORD'] = ''  # Contraseña
app.config['MYSQL_DATABASE_DB'] = 'sitio_libros' # Nombre Base de Datos
# Inicializando la aplicacion
mysql.init_app(app)

# Creando la ruta de acceso para poder acceder a la URL(/) - Servidor
@app.route('/')
# Mostrara un index
def inicio():
    # Retornara en la ruta y buscara el archivo index.html
    return render_template('sitio/index.html')

# Accediendo a la ruta de la IMAGEN y agregamos una nueva ruta<imagen> a la imagen
@app.route('/imagenes/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/imagenes'),imagen)


# Añadiendo los estilos de CSS
@app.route('/css/<estiloscss>')
def estilos(estiloscss):
    return send_from_directory(os.path.join('templates/sitio/css'), estiloscss)



# Navegacion en la web
# EN ARCHIVOS CARPETA SITIO
@app.route('/libros')
def libros():# Conexion con la DB
    conexion=mysql.connect()
    # Realizando la consulta a la DB de datos actualizados en la tabla
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")    # Y ejecutamos la consulta
    libros=cursor.fetchall()    # Se recupera toda la info de la DB
    conexion.commit()   # Se realiza la instruccion SQL
    return render_template('sitio/libros.html', libros=libros)  # Pasando los valores de libro


@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')


# EN ARCHIVOS CARPETA admin
@app.route('/admin/')
def admin_index():
    # Si no existe login en la sesion
    if not 'login' in session:
        # Si no existe se redireccionara al login
        return redirect('/admin/login')
    return render_template('admin/index.html')

@app.route('/admin/login')
def login():
    return render_template('admin/login.html')
# Obteniendo la indormacion del formulario
@app.route('/admin/login', methods=['POST'])
def login_form():
    _usuario=request.form['txtUsuario']
    _contrasena=request.form['tstPassword']
    # Comparativa de forma estatica(sin consultar en la DB)
    if _usuario=="admin" and _contrasena=="123":
        # Se crearan variables de sesion
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect('/admin')    # Retornando la direccion del admin
    return render_template('admin/login.html', mensaje="Acceso denegado")


# Cerrando sesion
@app.route('/admin/cerrar')
def cerrar_sesion():
    session.clear() # Limpiando las sesiones
    return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():
    
    # Bloqueo de usuarios si no existen 
    # Si no existe login en la sesion
    if not 'login' in session:
        # Si no existe se redireccionara al login
        return redirect('/admin/login')
    
    # Conexion con la DB
    conexion=mysql.connect()
    # Realizando la consulta a la DB de datos actualizados en la tabla
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")    # Y ejecutamos la consulta
    libros=cursor.fetchall()    # Se recupera toda la info de la DB
    conexion.commit()   # Se realiza la instruccion SQL
    print(libros) # Se imprimira libros en caso de que exista la conexion
    return render_template('admin/libros.html', libros=libros)  # Pasando los valores de libro


# Recibiendo la informacion con el metodo POST
# Creacion de la ruta que redireccionara toda la informacion en /admin/libros/guardar
@app.route('/admin/libros/guardar', methods=['POST'])
def admin_guardar_libros():
    # Bloqueando los accesos
    # Si no existe login en la sesion
    if not 'login' in session:
        # Si no existe se redireccionara al login
        return redirect('/admin/login')
    
    # Asignando nombres a los valores ingresados
    _nombre=request.form['txtNombre']
    _imagen=request.files['txtImagen']
    _url=request.form['txtURL']
    
    # Tiempo actual
    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')    # Año-Hora-Mes-
    # Condicion si esque existe una imagen y si es diferente al vacio
    if _imagen.filename!="":
        # Entonces se le agregara nuevo nombre + Nombre imagen
        nuevoNombre=horaActual+"_"+_imagen.filename
        # Guardaremos la imagen en una ruta temporal(templates/sitio/imagenes)
        _imagen.save("templates/sitio/imagenes/"+nuevoNombre)
    
    
    # Consultas SQL para ingresar registros
    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre, nuevoNombre, _url)  # Añadiedno los valores ingresados en el FORM
    
    # Conectandolo a la DB
    conexion=mysql.connect()
    cursor=conexion.cursor()    # Almacenando la informacion despues de la conexion
    cursor.execute(sql, datos)    # Ejecutando la consulta y remplazando por los datos ingresados
    conexion.commit()   # Se realiza la instruccion SQL
    
    print(_nombre)
    print(_imagen)
    print(_url)
    return redirect('/admin/libros')


# Accion borrar datos de la tabla libros
@app.route('/admin/libros/borrar', methods=['POST'])
# DEfinimos la funcion
def admin_borrar_libros():
    # Bloqueando los accesos
    # Si no existe login en la sesion
    if not 'login' in session:
        # Si no existe se redireccionara al login
        return redirect('/admin/login')
    
    
    # Recibimos el ID
    _id=request.form['txtID']
    print(_id)  # Imprimimos el resultado
    
    # Conexion con la DB
    conexion=mysql.connect()
    # Realizando la consulta a la DB de datos actualizados en la tabla
    cursor=conexion.cursor()
    # Y ejecutamos la consulta para remplazar(_id) por (=%s), es decir estara recuperando el ID
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s", (_id))
    libro=cursor.fetchall()    # Se recupera toda la info de la DB
    conexion.commit()   # Se realiza la instruccion SQL
    print(libro) # Se imprimira libros en caso de que exista la conexion
    
    # Si existe la imagen en la ruta, se convertira en string tomando la posicion(0)
    if os.path.exists("templates/sitio/imagenes/"+str(libro[0][0])):
        # Si existe esa imagen se borrara
        os.unlink("templates/sitio/imagenes/"+str(libro[0][0]))

    # Accion para eliminar de informacion
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM `libros` WHERE id=%s", (_id))
    conexion.commit()
    
    return redirect('/admin/libros')


# Si name es = a main , se estara corriendo la aplicacion
if __name__ == '__main__':
    # Se iniciara la aplicacion
    app.run(debug=True)