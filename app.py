import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date, datetime

# Configurar adaptadores y convertidores de fechas para SQLite
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("DATE", lambda s: date.fromisoformat(s.decode("utf-8")))
sqlite3.register_converter("DATETIME", lambda s: datetime.fromisoformat(s.decode("utf-8")))

# Archivos para almacenar usuarios y profesionales
USUARIOS_CSV = "usuarios.csv"
PROFESIONALES_CSV = "profesionales.csv"

# Conectar a la base de datos SQLite
DB_NAME = 'salud_mental.db'

# Función para obtener la conexión a la base de datos (CRUCIAL)
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Para acceder a los datos por nombre de columna
    return conn

def crear_tablas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contrasenia TEXT NOT NULL);
    ''')
    
    # Crear tabla de pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT NOT NULL,
            apellido TEXT NOT NULL,
            nombre TEXT NOT NULL,
            genero TEXT,
            fecha_nacimiento DATE,
            edad_actual INTEGER,
            ciudad TEXT,
            domicilio TEXT,
            telefono TEXT,
            email TEXT,
            protocolo_activado BOOLEAN,
            protocolo TEXT,
            fecha_derivacion DATE,
            profesional_derivante TEXT,
            observaciones_clinicas TEXT,
            profesional TEXT,
            especialidad TEXT,
            tipo_atencion TEXT,
            fecha_turno DATE,
            hora_turno TIME,
            turno_confirmado BOOLEAN);
    ''')
    
    conn.commit()
    conn.close()

def cargar_usuarios():
    if os.path.exists(USUARIOS_CSV):
        return pd.read_csv(USUARIOS_CSV)
    else:
        return pd.DataFrame(columns=["usuario", "contrasenia"])

def cargar_profesionales():
    if os.path.exists(PROFESIONALES_CSV):
        return pd.read_csv(PROFESIONALES_CSV)
    else:
        return pd.DataFrame(columns=["nombre"])

def guardar_usuario(usuario, contrasenia):
    df = cargar_usuarios()
    nuevo_usuario_df = pd.DataFrame({"usuario": [usuario], "contrasenia": [contrasenia]})
    df = pd.concat([df, nuevo_usuario_df], ignore_index=True)
    df.to_csv(USUARIOS_CSV, index=False)

def verificar_usuario(usuario, contrasenia):
    df = cargar_usuarios()
    return not df[(df["usuario"] == usuario) & (df["contrasenia"] == contrasenia)].empty

def cargar_datos_usuarios(dni, apellido, nombre, genero, fecha_nacimiento, edad_actual, ciudad, domicilio, telefono, email, protocolo_activado, protocolo_nombre, fecha_derivacion, profesional_derivante, observaciones_clinicas):
    st.write("Intentando obtener conexión a la base de datos (cargar_datos_usuarios)...")
    conn = get_db_connection()
    st.write("Conexión obtenida (cargar_datos_usuarios).")
    cursor = conn.cursor()
    try:
        st.write(f"Intentando insertar datos: DNI={dni}, Apellido={apellido}, Nombre={nombre}, fecha_nacimiento={fecha_nacimiento}, edad_actual={edad_actual}, ciudad={ciudad}, domicilio={domicilio}, telefono={telefono}, email={email}, protocolo_activado={protocolo_activado}, protocolo={protocolo_nombre}, fecha_derivacion={fecha_derivacion}, profesional_derivante={profesional_derivante}, observaciones_clinicas={observaciones_clinicas}")
        sql = """
            INSERT INTO pacientes (dni, apellido, nombre, genero, fecha_nacimiento, edad_actual, ciudad, domicilio, telefono, email, protocolo_activado, protocolo, fecha_derivacion, profesional_derivante, observaciones_clinicas) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (dni, apellido, nombre, genero, str(fecha_nacimiento), edad_actual, ciudad, domicilio, telefono, email, protocolo_activado, protocolo_nombre, str(fecha_derivacion), profesional_derivante, observaciones_clinicas)
        cursor.execute(sql, valores)
        conn.commit()
        st.write("Datos insertados correctamente (cargar_datos_usuarios).")
        st.success("Datos cargados exitosamente")
    except sqlite3.Error as e:
        st.error(f"Error al cargar los datos: {e}")
        st.write(f"Error técnico (cargar_datos_usuarios): {e}") # Imprime el error completo
    finally:
        conn.close()
        st.write("Conexión cerrada (cargar_datos_usuarios).")

def asignar_turno_paciente(dni, profesional, especialidad, tipo_atencion, fecha_turno, hora_turno, turno_confirmado):
    st.write("Intentando obtener conexión a la base de datos (asignar_turno_paciente)...")
    conn = get_db_connection()
    st.write("Conexión obtenida (asignar_turno_paciente).")
    cursor = conn.cursor()
    try:
        st.write(f"Intentando asignar turno: DNI={dni}, profesional={profesional}, especialidad={especialidad}, tipo_atencion={tipo_atencion}, fecha_turno={fecha_turno}, hora_turno={hora_turno}, turno_confirmado={turno_confirmado}")
        sql = """
            UPDATE pacientes 
            SET profesional=?, especialidad=?, tipo_atencion=?, fecha_turno=?, hora_turno=?, turno_confirmado=? 
            WHERE dni=?
        """
        valores = (profesional, especialidad, tipo_atencion, fecha_turno, hora_turno, turno_confirmado, dni)
        cursor.execute(sql, valores)
        conn.commit()
        st.write("Turno asignado correctamente (asignar_turno_paciente).")
        st.success("Turno asignado exitosamente.")
    except sqlite3.Error as e:
        st.error(f"Ocurrió un error al asignar el turno: {e}")
        st.write(f"Error técnico (asignar_turno_paciente): {e}") # Imprime el error completo
    finally:
        conn.close()
        st.write("Conexión cerrada (asignar_turno_paciente).")
        
def obtener_todos_los_pacientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    records = cursor.fetchall()
    conn.close()
    return pd.DataFrame([dict(row) for row in records]) # Corrección para convertir a DataFrame

def buscar_pacientes_sin_turnos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE turno_confirmado IS NULL OR turno_confirmado = '' OR turno_confirmado = 0")
    records = cursor.fetchall()
    conn.close()
    return pd.DataFrame([dict(row) for row in records]) # Corrección para convertir a DataFrame
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Crear tablas si no existen
crear_tablas()

# Página de inicio (login o registro)
def login():
    st.title("Acceso al Sistema")
    
    if not st.session_state.logged_in:
        # Registro de Nuevo Usuario
        with st.container():
            st.subheader("Registro de Nuevo Usuario")
            
            nuevo_usuario = st.text_input("Nuevo Usuario")
            nueva_contrasenia = st.text_input("Nueva Contraseña" , type="password")
            
            if st.button("Registrarse"):
                if nuevo_usuario and nueva_contrasenia:
                    try:
                        guardar_usuario(nuevo_usuario , nueva_contrasenia)
                        st.success("Usuario registrado exitosamente.")
                    except sqlite3.IntegrityError:
                        st.error("El usuario ya existe.... Elige otro.")
                else:
                    st.error("Por favor completa todos los campos.")
        
        # Formulario de inicio de sesión
        st.subheader("Iniciar Sesión")
        
        usuario_input = st.text_input("Usuario")
        contrasenia_input = st.text_input("Contraseña" , type="password")
        
        if st.button("Iniciar Sesión"):
            if verificar_usuario(usuario_input , contrasenia_input):
                st.session_state.logged_in = True  # Establecer estado de inicio de sesión
                st.session_state.usuario_actual = usuario_input  # Guardar usuario actual
                st.success("Acceso concedido.")
                return True  # Permitir acceso a la aplicación
            else:
                st.error("Usuario o contraseña incorrectos.")
                
        return False  # Denegar acceso

if login() or st.session_state.logged_in:
    
    st.sidebar.title("Navegación")
    
    pagina_seleccionada = st.sidebar.radio("Selecciona una página:" , ["Inicio" , "Carga de Usuarios" , "Buscar Paciente"])
    
    if pagina_seleccionada == "Inicio":
        st.title("Bienvenido al Sistema de Salud Mental")

        
    
    elif pagina_seleccionada == "Carga de Usuarios":
        with st.form("formulario_usuarios" , clear_on_submit=True):
            
            dni = st.text_input("DNI")
            apellido = st.text_input("Apellido")
            nombre = st.text_input("Nombre")
            genero = st.selectbox("Género" , options=["Masculino" , "Femenino"] , index=0)
            
            fecha_nacimiento = st.date_input("Fecha de nacimiento")  # Mantener formato original
            
            edad_actual = st.number_input("Edad actual" , min_value=0)
            ciudad = st.text_input("Ciudad donde vive")
            domicilio = st.text_input("Domicilio")

            telefono = st.text_input("Teléfono (obligatorio)", placeholder="Ingrese su teléfono")  
            
            email = st.text_input("Email")  
            
            protocolo_activado = st.radio("¿Existe algún protocolo activado?" , ("Sí" , "No"))
            
            if protocolo_activado == "Sí":
                protocolo_nombre = st.text_input("¿Qué protocolo se ha activado?")
                
            else:
                protocolo_nombre = None
            
             # Fecha de derivación manteniendo el formato original
            fecha_derivacion=st.date_input("Fecha de derivación")  
            profesional_derivante=st.text_input("Profesional derivante del Ministerio de Seguridad")  
            observaciones_clinicas=st.text_area("Observaciones clínicas al momento de la derivación")  
            
            submit_button_usuarios=st.form_submit_button("Cargar Usuario")

            if submit_button_usuarios:
                 if not dni or not apellido or not nombre or not email or not telefono:
                     st.error ("Por favor completa todos los campos obligatorios (DNI, Apellido, Nombre y Email).")
                 elif edad_actual < 0:
                     st.error ("La edad actual no puede ser negativa.")
                 elif fecha_nacimiento > pd.Timestamp.now().date():
                     st.error ("La fecha de nacimiento no puede ser posterior a la fecha actual.")
                 else:
                     try:
                         cargar_datos_usuarios(dni or "", apellido or "", nombre or "", genero or "", 
                                               fecha_nacimiento or None ,
                                               edad_actual or 0 ,
                                               ciudad or "" ,
                                               domicilio or "" ,
                                               telefono or "" ,
                                               email or "",
                                               protocolo_activado == "Sí",
                                               protocolo_nombre or "" ,
                                               fecha_derivacion or None ,
                                               profesional_derivante or "" ,
                                               observaciones_clinicas or "")
                         # Mensaje de éxito
                         st.success ("Datos cargados exitosamente.")
                         
                     except Exception as e:
                         st.error(f"Ocurrió un error al cargar los datos: {e}")

    
    elif pagina_seleccionada == "Buscar Paciente":
        
        # Botón para buscar paciente por DNI
        search_dni=st.text_input ("Buscar paciente por DNI:")
        
        if search_dni:
            
            all_users_df=obtener_todos_los_pacientes()
            
            filtered_users_df=all_users_df[all_users_df['dni'] == search_dni]
            
            if filtered_users_df.empty:
                st.warning(f"No se encontraron pacientes con el DNI: {search_dni}.")
                
            else:
                # Mostrar todos los datos del paciente
                patient_data_displayed_dict=filtered_users_df.iloc[0].to_dict()  # Mostrar solo el primer resultado
                
                df_patient_info=pd.DataFrame([patient_data_displayed_dict])  # Mostrar en una tabla
                
                # Mostrar en una tabla
                st.write(df_patient_info)

        # Botón para ver pacientes sin turnos
        if st.button ("Ver Pacientes Sin Turnos"):
            sin_turnos_df=buscar_pacientes_sin_turnos()
            
            if not sin_turnos_df.empty:
                st.subheader ("Pacientes sin turnos")
                st.dataframe(sin_turnos_df)
            else:
                st.info ("En este momento no hay pacientes sin turnos otorgados.")

        # Formulario para asignar turnos
        with st.form ("formulario_asignar_turno" , clear_on_submit=True):
            dni_turno=st.text_input ("DNI del Paciente (para asignar turno)")
            profesionales_df=cargar_profesionales ()
            profesional=st.selectbox ("Profesional" , profesionales_df["nombre"] if not profesionales_df.empty else [])
            especialidad=st.selectbox ("Especialidad" , ["Psicología" ,"Psiquiatría"])
            tipo_atencion=st.selectbox ("Tipo de Atención" , ["Evaluación Inicial" ,"Seguimiento"])
            
            fecha_turno=st.date_input ("Fecha del Turno")  # Mantener formato original

            hora_turno_obj=datetime.strptime ('10:00' ,"%H:%M").time()  # Hora fija a las 10 AM
            turno_confirmado=st.radio ("¿Turno Confirmado?" , ["Sí" ,"No"], index=0)  
            
            submit_turno=st.form_submit_button ("Asignar Turno")

            if submit_turno:
                try :
                    asignar_turno_paciente(dni_turno , profesional , especialidad , tipo_atencion ,
                                            fecha_turno ,
                                            hora_turno_obj.strftime("%H:%M:%S") ,
                                            turno_confirmado)  
                    # Mensaje dentro del bloque try para asegurar que se muestra correctamente.
                    st.success ("Turno asignado exitosamente.")
                except Exception as e:
                    # Manejo del error dentro del bloque except.
                    st.error(f"Ocurrió un error al asignar el turno : {e}")

