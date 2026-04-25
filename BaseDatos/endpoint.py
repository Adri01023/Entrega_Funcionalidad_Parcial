import traceback
import hashlib
import json

from fastapi import FastAPI, Response, HTTPException, UploadFile, File, Depends, Query
from sqlalchemy import text
from datetime import datetime
from pydantic import BaseModel
from typing import Any
from fastapi.middleware.cors import CORSMiddleware

from Estadistica_Y_Graficas.estadisticas import *
from Estadistica_Y_Graficas.graficas import *
from Estadistica_Y_Graficas.importar import *
from BaseDatos.BaseDatos import engine

#MEJORAR COMMENTS -> CON DOCSTRINGS, mejor documentacion
class UserCreate(BaseModel):
    username: str
    password: str
    id_admin: int

class AdminCreate(BaseModel):
    username: str
    password: str

class HistorialCreate(BaseModel):
    id_consultor: int
    consulta: Any

class LoginData(BaseModel):
    username: str
    password: str

app = FastAPI(title="PyBusiness Analytics API")

# Permite que el frontend pueda comunicarse con este backend sin que el navegador bloquee las peticiones.
# CORS es una política de seguridad de los navegadores que restringe las solicitudes HTTP 
# entre distintos orígenes (dominio, puerto o protocolo).

#Configuración de desarrollo unicamente
app.add_middleware(
    CORSMiddleware,
    #Permite cualquier dominio
    allow_origins=["*"],  # en desarrollo
    #Permite el traspaso de credenciales por los endpoints
    allow_credentials=True,
    # Métodos HTTP permitidos (GET,POST,DELETE...)
    allow_methods=["*"],
    #Permite cabeceras HTTP
    allow_headers=["*"],
)

#Funciones
#OBTENER ADMINISTRADOR ACTUAL (FALTA POR IMPLEMENTAR)
def get_admin():
    return 1

 # Comprueba si existe al menos un administrador en la base de datos
def existe_admin():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as total FROM Administrador
        """)).fetchone()

        return result.total > 0

#Comprueba si se repite el nombre de un admin
def admin_existe_por_username(username: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 1 FROM Administrador WHERE usuario = :usuario
        """), {"usuario": username}).fetchone()

        return result is not None
    
# Comprueba si existe un administrador por su ID
def admin_existe_por_id(id_admin: int) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 1 FROM Administrador WHERE id_admin = :id_admin
        """), {"id_admin": id_admin}).fetchone()

        return result is not None

# Genera el hash SHA-256 de una contraseña en texto plano
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Inserta un nuevo administrador en la base de datos
def insertar_admin(username: str, password_hash: str):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO Administrador (usuario, contrasena)
            VALUES (:usuario, :contrasena)
        """), {
            "usuario": username,
            "contrasena": password_hash
        })
        conn.commit()

def insertar_usuario(id_admin: int, username: str, password_hash: str):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO Usuario (id_admin, usuario, contrasena)
            VALUES (:id_admin, :usuario, :contrasena)
        """), {
            "id_admin": id_admin,
            "usuario": username,
            "contrasena": password_hash
        })
        conn.commit()

# Comprueba si un usuario ya existe para un administrador concreto
def usuario_existe(id_admin: int, username: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 1 FROM Usuario 
            WHERE id_admin = :id_admin AND usuario = :usuario
        """), {
            "id_admin": id_admin,
            "usuario": username
        }).fetchone()

        return result is not None
    
# Determina la tabla destino en función de las columnas del dataset
def detectar_tabla(columnas: list[str]) -> str:
    if 'goles' in columnas or 'posicion' in columnas:
        return "Futbol"
    elif 'salario_base' in columnas:
        return "Empleados"
    elif 'entradas_vendidas' in columnas:
        return "Conciertos"
    elif 'recaudacion' in columnas:
        return "Cine"
    else:
        raise ValueError("Estructura no reconocida")
    
def procesar_empleados(df):
    df['fecha_contratacion'] = pd.to_datetime(df['fecha_contratacion'], errors='coerce')

    if df['fecha_contratacion'].isnull().any():
        raise ValueError("Fechas inválidas en 'fecha_contratacion'")

    df['fecha_contratacion'] = df['fecha_contratacion'].dt.strftime('%Y-%m-%d')
    return df

def existe_dataset(tabla: str, id_admin: int) -> bool:
    tablas_validas = {"Futbol", "Empleados", "Conciertos", "Cine"}

    if tabla not in tablas_validas:
        raise ValueError("Tabla no permitida")

    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT 1 FROM {tabla} WHERE id_admin = :id LIMIT 1"),
            {"id": id_admin}
        ).fetchone()

        return result is not None

#Cominenzo de endpoints

#Endpoint necesario para el login de cualquier user
@app.post("/login")
def login(data: LoginData):
    # Genera el hash SHA-256 de la contraseña introducida para compararla con la almacenada
    contrasena_hash = hash_password(data.password)

    with engine.connect() as conn:
        # Buscar en Administrador
        admin = conn.execute(text("""
            SELECT id_admin, usuario FROM Administrador
            WHERE usuario = :usuario AND contrasena = :contrasena
        """), {
            "usuario": data.username,
            "contrasena": contrasena_hash
        }).fetchone()

        # Si se encuentra un administrador con esas credenciales, se devuelve su información
        if admin:
            return {
                "id_admin": admin.id_admin,
                "username": admin.usuario,
                "es_admin": True
            }

        # Buscar en Usuario
        user = conn.execute(text("""
            SELECT id_user, usuario, id_admin FROM Usuario
            WHERE usuario = :usuario AND contrasena = :contrasena
        """), {
            "usuario": data.username,
            "contrasena": contrasena_hash
        }).fetchone()

        #Lo mismo que admin con user
        if user:
            return {
                "id_user": user.id_user,
                "username": user.usuario,
                "id_admin": user.id_admin,
                "es_admin": False
            }

    #Se devuelve excepción http en caso de no encontrar ningun usuario correcto
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
#CREACION DE USUARIOS (ADMINISTRADOR Y BASE)
#Sirve para determinar si hay al menos un usuario en la BBDD
#En caso de no haberlo otorga permisos de admin al primer user creado.
@app.get("/usuarios/hay-admin")
def hay_admin():
    return {"hay_admin": existe_admin()}

#Endpoint solo para cuando no hay ningun administrador
@app.post("/usuarios/crear-admin")
def crear_admin(data: AdminCreate):
    try:
        # Solo permite crear admin si NO existe ninguno
        if existe_admin():
            raise HTTPException(status_code=403, detail="Ya existe un administrador")

        # Evita duplicados
        if admin_existe_por_username(data.username):
            raise HTTPException(status_code=400, detail="El admin ya existe")

        # Crear admin
        password_hash = hash_password(data.password)
        insertar_admin(data.username, password_hash)

        return {"msg": "Primer ADMIN creado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#Este es el endpoint que se usa en la creacion de nuevos admin desde el panel 
# de configuracion de un admin
@app.post("/usuarios/crear-admin-secure")
def crear_admin_secure(user: AdminCreate):
    try:
        if admin_existe_por_username(user.username):
            raise HTTPException(status_code=400, detail="El admin ya existe")

        password_hash = hash_password(user.password)
        insertar_admin(user.username, password_hash)

        return {"msg": "Nuevo ADMIN creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/usuarios/crear-usuario")
def crear_usuario(data: UserCreate):
    try:
        # Validar admin
        if not admin_existe_por_id(data.id_admin):
            raise HTTPException(status_code=400, detail="El admin no existe")

        # Evitar duplicados
        if usuario_existe(data.id_admin, data.username):
            raise HTTPException(status_code=400, detail="Ese usuario ya existe para este administrador")

        password_hash = hash_password(data.password)
        insertar_usuario(data.id_admin, data.username, password_hash)

        return {"msg": "Usuario creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/datasets-disponibles")
def datasets_disponibles(id_admin: int):
    return {
        "futbol": existe_dataset("Futbol", id_admin),
        "empleados": existe_dataset("Empleados", id_admin),
        "conciertos": existe_dataset("Conciertos", id_admin),
        "cine": existe_dataset("Cine", id_admin),
    }

#SUBIR ARCHIVOS
@app.post("/subir-archivo")
async def importar_ficheros(
    file: UploadFile = File(...),
    id_admin: int = Query(...)
):
    try:
        # Leer contenido del archivo
        contenido = await file.read()

        # Convertir a DataFrame usando tu función de importación
        df = importar_fichero(file.filename, contenido)

        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        print(df.dtypes)
        print(df.head())

        # Validación obligatoria
        if 'id_admin' not in df.columns:
            raise ValueError("El fichero debe incluir la columna 'id_admin'")

        # Sobrescribir id_admin con el del usuario autenticado
        df['id_admin'] = id_admin

        columnas = df.columns.tolist()

        tabla = detectar_tabla(columnas)

        # Lógica específica SOLO para empleados
        if tabla == "Empleados":
            df = procesar_empleados(df)

        with engine.begin() as conn:
            df.to_sql(tabla, con=conn, if_exists="append", index=False)

        return {
            "nombre_archivo": file.filename,
            "filas": len(df),
            "tabla": tabla
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# FÚTBOL
@app.get("/futbol/rendimiento")
def get_rendimiento(id_admin: int = Depends(get_admin)):
    return rendimiento_vs_media_posicion(id_admin)

@app.get("/futbol/rendimiento/grafico")
def get_grafico_rendimiento(id_admin: int = Depends(get_admin)):
    datos = rendimiento_vs_media_posicion(id_admin)
    return Response(content=grafico_rendimiento_posicion(datos), media_type="image/png")

@app.get("/futbol/goleadores")
def get_goleadores(id_admin: int = Depends(get_admin)):
    return ranking_goleadores(id_admin)

@app.get("/futbol/goleadores/grafico")
def get_grafico_goleadores(id_admin: int = Depends(get_admin)):
    datos = ranking_goleadores(id_admin)
    return Response(content=grafico_ranking_goleadores(datos), media_type="image/png")

@app.get("/futbol/equipos")
def get_equipos(id_admin: int = Depends(get_admin)):
    return estadisticas_por_equipo(id_admin)

@app.get("/futbol/equipos/grafico")
def get_grafico_equipos(id_admin: int = Depends(get_admin)):
    datos = estadisticas_por_equipo(id_admin)
    return Response(content=grafico_estadisticas_por_equipo(datos), media_type="image/png")

@app.get("/futbol/eficiencia")
def get_eficiencia(id_admin: int = Depends(get_admin)):
    return eficiencia_goleadora(id_admin)

@app.get("/futbol/eficiencia/grafico")
def get_grafico_eficiencia(id_admin: int = Depends(get_admin)):
    datos = eficiencia_goleadora(id_admin)
    return Response(content=grafico_eficiencia_goleadora(datos), media_type="image/png")

# EMPLEADOS
@app.get("/empleados/distribucion")
def get_distribucion(id_admin: int = Depends(get_admin)):
    return distribucion_salarial_por_cargo(id_admin)

@app.get("/empleados/distribucion/grafico")
def get_grafico_distribucion(id_admin: int = Depends(get_admin)):
    datos = distribucion_salarial_por_cargo(id_admin)
    return Response(content=grafico_distribucion_salarial(datos), media_type="image/png")

@app.get("/empleados/ranking-salarial")
def get_ranking_salarial(id_admin: int = Depends(get_admin)):
    return ranking_salarial(id_admin)

@app.get("/empleados/ranking-salarial/grafico")
def get_grafico_ranking_salarial(id_admin: int = Depends(get_admin)):
    datos = ranking_salarial(id_admin)
    return Response(content=grafico_ranking_salarios(datos), media_type="image/png")

@app.get("/empleados/comparativa-base")
def get_comparativa(id_admin: int = Depends(get_admin)):
    return comparativa_salario_real_vs_base(id_admin)

@app.get("/empleados/comparativa-base/grafico")
def get_grafico_comparativa(id_admin: int = Depends(get_admin)):
    datos = comparativa_salario_real_vs_base(id_admin)
    return Response(content=grafico_comparativa_vs_base(datos), media_type="image/png")

@app.get("/empleados/antiguedad")
def get_antiguedad(id_admin: int = Depends(get_admin)):
    return antiguedad_media_por_cargo(id_admin)

@app.get("/empleados/antiguedad/grafico")
def get_grafico_antiguedad(id_admin: int = Depends(get_admin)):
    datos = antiguedad_media_por_cargo(id_admin)
    return Response(content=grafico_antiguedad_por_cargo(datos), media_type="image/png")

@app.get("/empleados/estructura-plantilla")
def get_estructura(id_admin: int = Depends(get_admin)):
    return distribucion_empleados_por_cargo(id_admin)

@app.get("/empleados/estructura-plantilla/grafico")
def get_grafico_estructura(id_admin: int = Depends(get_admin)):
    datos = distribucion_empleados_por_cargo(id_admin)
    return Response(content=grafico_distribucion_empleados(datos), media_type="image/png")

# CONCIERTOS
@app.get("/conciertos/actividad")
def get_actividad_cantantes(id_admin: int = Depends(get_admin)):
    return ranking_cantantes_por_actividad(id_admin)

@app.get("/conciertos/actividad/grafico")
def get_grafico_actividad(id_admin: int = Depends(get_admin)):
    datos = ranking_cantantes_por_actividad(id_admin)
    return Response(content=grafico_ranking_cantantes(datos), media_type="image/png")

@app.get("/conciertos/continentes")
def get_conciertos_continente(id_admin: int = Depends(get_admin)):
    return distribucion_conciertos_por_continente(id_admin)

@app.get("/conciertos/continentes/grafico")
def get_grafico_continentes(id_admin: int = Depends(get_admin)):
    datos = distribucion_conciertos_por_continente(id_admin)
    return Response(content=grafico_distribucion_por_continente(datos), media_type="image/png")

@app.get("/conciertos/recintos-top")
def get_recintos(id_admin: int = Depends(get_admin)):
    return recintos_mas_demandados(id_admin)

@app.get("/conciertos/recintos-top/grafico")
def get_grafico_recintos(id_admin: int = Depends(get_admin)):
    datos = recintos_mas_demandados(id_admin)
    return Response(content=grafico_recintos_mas_demandados(datos), media_type="image/png")

@app.get("/conciertos/ocupacion")
def get_ocupacion(id_admin: int = Depends(get_admin)):
    return ocupacion_media_por_cantante(id_admin)

@app.get("/conciertos/ocupacion/grafico")
def get_grafico_ocupacion(id_admin: int = Depends(get_admin)):
    datos = ocupacion_media_por_cantante(id_admin)
    return Response(content=grafico_ocupacion_por_cantante(datos), media_type="image/png")

@app.get("/conciertos/rentabilidad-giras")
def get_rentabilidad_giras(id_admin: int = Depends(get_admin)):
    return rentabilidad_por_gira(id_admin)

@app.get("/conciertos/rentabilidad-giras/grafico")
def get_grafico_rentabilidad_giras(id_admin: int = Depends(get_admin)):
    datos = rentabilidad_por_gira(id_admin)
    return Response(content=grafico_rentabilidad_giras(datos), media_type="image/png")

# PELÍCULAS
@app.get("/peliculas/rentabilidad")
def get_rentabilidad(id_admin: int = Depends(get_admin)):
    return rentabilidad_peliculas(id_admin)

@app.get("/peliculas/rentabilidad/grafico")
def get_grafico_rentabilidad_pelis(id_admin: int = Depends(get_admin)):
    datos = rentabilidad_peliculas(id_admin)
    return Response(content=grafico_rentabilidad_peliculas(datos), media_type="image/png")

@app.get("/peliculas/generos")
def get_generos(id_admin: int = Depends(get_admin)):
    return generos_mas_rentables(id_admin)

@app.get("/peliculas/generos/grafico")
def get_grafico_generos(id_admin: int = Depends(get_admin)):
    datos = generos_mas_rentables(id_admin)
    return Response(content=grafico_generos_rentables(datos), media_type="image/png")

@app.get("/peliculas/directores")
def get_directores(id_admin: int = Depends(get_admin)):
    return directores_mas_taquilleros(id_admin)

@app.get("/peliculas/directores/grafico")
def get_grafico_directores(id_admin: int = Depends(get_admin)):
    datos = directores_mas_taquilleros(id_admin)
    return Response(content=grafico_directores_taquilleros(datos), media_type="image/png")

@app.get("/peliculas/perdidas")
def get_perdidas(id_admin: int = Depends(get_admin)):
    return peliculas_mayor_perdida(id_admin)

@app.get("/peliculas/perdidas/grafico")
def get_grafico_perdidas(id_admin: int = Depends(get_admin)):
    datos = peliculas_mayor_perdida(id_admin)
    return Response(content=grafico_peliculas_mayor_perdida(datos), media_type="image/png")

@app.get("/peliculas/impacto-actores")
def get_actores(id_admin: int = Depends(get_admin)):
    return impacto_actores_en_recaudacion(id_admin)

@app.get("/peliculas/impacto-actores/grafico")
def get_grafico_actores(id_admin: int = Depends(get_admin)):
    datos = impacto_actores_en_recaudacion(id_admin)
    return Response(content=grafico_impacto_actores(datos), media_type="image/png")

@app.post("/historial")
def guardar_historial(data: HistorialCreate):
    try:
        # Convertir la consulta a string para almacenarla en la base de datos.
        # Se serializa a JSON.
        consulta_str = (
            json.dumps(data.consulta)
            if not isinstance(data.consulta, str)
            else data.consulta
        )

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO Historial (id_consultor, consulta, fecha)
                VALUES (:id_consultor, :consulta, :fecha)
            """), {
                "id_consultor": data.id_consultor,
                "consulta": consulta_str,
                "fecha": datetime.utcnow()
            })

        return {"msg": "ok"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/historial")
 # Obtiene el historial del usuario ordenado por fecha descendente
def obtener_historial(id_consultor: int):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT consulta, fecha
            FROM Historial
            WHERE id_consultor = :id
            ORDER BY fecha DESC
        """), {"id": id_consultor}).fetchall()

    salida = []

    # Se recorre el resultado para transformar la consulta almacenada
    for r in result:
        try:
            # Intenta convertir el texto almacenado a JSON
            consulta = json.loads(r.consulta) 
        except:
            # Si falla, se devuelve el contenido tal cual
            consulta = r.consulta  # fallback

        salida.append({
            "consulta": consulta,
            "fecha": r.fecha
        })

    return salida

@app.delete("/historial")
# Elimina todo el historial asociado a un usuario en la BBDD.
def borrar_historial(id_consultor: int):
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM Historial
            WHERE id_consultor = :id
        """), {"id": id_consultor})

    return {"msg": "historial eliminado"}