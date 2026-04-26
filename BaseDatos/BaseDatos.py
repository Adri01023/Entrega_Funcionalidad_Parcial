import os
from sqlalchemy import create_engine, text

# Ruta del archivo actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Subir a carpeta superior (TFG)
ROOT_DIR = os.path.dirname(BASE_DIR)

# Ruta final de la BD
db_path = os.path.join(ROOT_DIR, "baseDatos.db")

db_existed = os.path.exists(db_path)

engine = create_engine(f"sqlite:///{db_path.replace('\\', '/')}")

# DEBUG BUENO
print("RUTA ACTUAL (cwd):", os.getcwd())
print("RUTA DEL SCRIPT:", BASE_DIR)
print("RUTA PROYECTO:", ROOT_DIR)
print("RUTA REAL BD:", db_path)
print("EXISTE BD:", os.path.exists(db_path))
print("EXISTE BD (ANTES):", db_existed)

with engine.connect() as conn:


    conn.execute(text("PRAGMA foreign_keys = ON"))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Administrador (
        id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        contrasena TEXT NOT NULL
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Usuario (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        id_admin INTEGER NOT NULL,
        usuario TEXT NOT NULL,
        contrasena TEXT NOT NULL,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS Historial (
            id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER,
            id_admin INTEGER,
            tipo_consultor TEXT NOT NULL,
            consulta TEXT NOT NULL,
            fecha DATE NOT NULL,
            FOREIGN KEY (id_user) REFERENCES Usuario(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin) ON DELETE CASCADE
        )
        """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Futbol (
        id_jugador INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo TEXT NOT NULL,
        jugador TEXT NOT NULL,
        posicion TEXT NOT NULL,
        partidos_jugados INTEGER NOT NULL,
        asistencias INTEGER NOT NULL,
        goles INTEGER NOT NULL,
        tarjetas_amarillas INTEGER NOT NULL,
        tarjetas_rojas INTEGER NOT NULL,
        id_admin INTEGER NOT NULL,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Empleados (
        id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado TEXT NOT NULL,
        departamento TEXT NOT NULL,
        cargo TEXT NOT NULL,
        salario_base REAL NOT NULL,
        salario_real REAL NOT NULL,
        fecha_contratacion DATE NOT NULL,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Conciertos (
        id_concierto INTEGER PRIMARY KEY AUTOINCREMENT,
        cantante TEXT NOT NULL,
        nacionalidad TEXT NOT NULL,
        fecha_nac DATE NOT NULL,
        concierto TEXT,
        num_canciones INTEGER NOT NULL,
        duracion INTEGER NOT NULL,
        recinto TEXT NOT NULL,
        pais TEXT NOT NULL,
        continente TEXT NOT NULL,
        max_entradas INTEGER NOT NULL,
        entradas_vendidas INTEGER NOT NULL,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Cine (
        id_pelicula INTEGER PRIMARY KEY AUTOINCREMENT,
        pelicula TEXT NOT NULL,
        genero TEXT NOT NULL,
        duracion INTEGER NOT NULL,
        presupuesto INTEGER NOT NULL,
        recaudacion INTEGER NOT NULL,
        director TEXT NOT NULL,
        fecha_nac_director DATE NOT NULL,
        actor_protagonista TEXT NOT NULL,
        fecha_nac_prota DATE NOT NULL,
        id_admin INTEGER NOT NULL,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admin)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))
    conn.commit()
    """
    rows = conn.execute(text("SELECT * FROM Administrador")).fetchall()

    print("ADMINS:", rows)
    """
    if not db_existed:
        print("Base de datos creada por primera vez")
    else:
        print("Base de datos ya existía")

