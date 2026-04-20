# procesamiento/estadisticas.py

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///baseDatos.db")


def query(sql: str) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL y devuelve un DataFrame.
    Función interna, solo se usa dentro de este fichero.
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)

# FÚTBOL

def rendimiento_vs_media_posicion() -> list:
    """
    Compara los goles y asistencias de cada jugador
    con la media de los jugadores de su misma posición.
    Útil para detectar quién destaca dentro de su rol.
    """

    df = query("""
        SELECT j.nombre, j.posicion,
               e.goles, e.asistencias, e.partidos_jugados
        FROM EstadisticasJugador e
        JOIN Jugador j ON e.id_jugador = j.id_jugador
    """)

    # transform("mean") calcula la media por posición y la asigna
    # a cada fila para poder comparar cada jugador con su grupo
    media = df.groupby("posicion")[["goles", "asistencias"]].transform("mean")

    df["media_goles_posicion"]       = media["goles"].round(2)
    df["media_asistencias_posicion"] = media["asistencias"].round(2)

    # Positivo = rinde por encima de su posición
    # Negativo = rinde por debajo de su posición
    df["diff_goles"]       = (df["goles"]       - df["media_goles_posicion"]).round(2)
    df["diff_asistencias"] = (df["asistencias"] - df["media_asistencias_posicion"]).round(2)

    return df.to_dict(orient="records")

def ranking_goleadores() -> list:
    """
    Devuelve el ranking de jugadores ordenados por goles totales.
    Incluye su posición, equipo y asistencias para tener
    una visión completa de su aportación ofensiva.
    """

    df = query("""
        SELECT j.nombre, j.posicion, eq.nombre AS equipo,
               SUM(e.goles) AS goles_totales,
               SUM(e.asistencias) AS asistencias_totales,
               SUM(e.partidos_jugados) AS partidos_totales
        FROM EstadisticasJugador e
        JOIN Jugador j ON e.id_jugador = j.id_jugador
        JOIN Equipo eq ON e.id_equipo = eq.id_equipo
        GROUP BY e.id_jugador
        ORDER BY goles_totales DESC
    """)

    # Ranking global: posición de cada jugador entre todos
    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")


def estadisticas_por_equipo() -> list:
    """
    Agrupa las estadísticas de todos los jugadores por equipo.
    Permite ver qué equipo es más goleador, más disciplinado
    o genera más asistencias en conjunto.
    """

    df = query("""
        SELECT eq.nombre AS equipo,
               SUM(e.goles) AS goles_totales,
               SUM(e.asistencias) AS asistencias_totales,
               SUM(e.partidos_jugados) AS partidos_totales,
               SUM(e.tarjetas_amarillas) AS tarjetas_amarillas,
               SUM(e.tarjetas_rojas) AS tarjetas_rojas,
               COUNT(DISTINCT e.id_jugador) AS num_jugadores
        FROM EstadisticasJugador e
        JOIN Equipo eq ON e.id_equipo = eq.id_equipo
        GROUP BY e.id_equipo
        ORDER BY goles_totales DESC
    """)

    # Promedio de goles por jugador en cada equipo
    # Permite comparar equipos de distinto tamaño de forma justa
    df["goles_por_jugador"] = (df["goles_totales"] / df["num_jugadores"]).round(2)

    return df.to_dict(orient="records")


def eficiencia_goleadora() -> list:
    """
    Calcula los goles por partido jugado de cada jugador.
    Un jugador con pocos partidos pero muchos goles puede
    tener una eficiencia mayor que el máximo goleador.
    Solo incluye jugadores con al menos 5 partidos para
    que el dato sea estadísticamente representativo.
    """

    df = query("""
        SELECT j.nombre, j.posicion,
               SUM(e.goles) AS goles_totales,
               SUM(e.partidos_jugados) AS partidos_totales
        FROM EstadisticasJugador e
        JOIN Jugador j ON e.id_jugador = j.id_jugador
        GROUP BY e.id_jugador
        HAVING partidos_totales >= 5
        ORDER BY goles_totales DESC
    """)

    # Goles por partido: métrica de eficiencia real
    # Un valor de 0.5 significa 1 gol cada 2 partidos
    df["goles_por_partido"] = (df["goles_totales"] / df["partidos_totales"]).round(2)

    # Ordenamos por eficiencia, no por goles totales
    df = df.sort_values("goles_por_partido", ascending=False)

    return df.to_dict(orient="records")

# EMPLEADOS

def distribucion_salarial_por_cargo() -> list:
    """
    Calcula media, mediana y desviación típica del salario
    real agrupado por cargo. El coeficiente de variación
    indica qué cargos tienen más desigualdad salarial.
    """

    df = query("""
        SELECT c.nombre_cargo, se.salario_real
        FROM SalarioEmpleado se
        JOIN Empleado e ON se.id_empleado = e.id_empleado
        JOIN Cargo c ON e.id_cargo = c.id_cargo
    """)

    # agg() calcula varias estadísticas a la vez por cargo
    resumen = df.groupby("nombre_cargo")["salario_real"].agg(
        media             = "mean",
        mediana           = "median",
        desviacion_tipica = "std",
        minimo            = "min",
        maximo            = "max",
        total_empleados   = "count"
    ).round(2)

    # Coeficiente de variación = (std / media) * 100
    # Cuanto más alto, más desigualdad salarial en ese cargo
    resumen["coef_variacion_%"] = (
        (resumen["desviacion_tipica"] / resumen["media"]) * 100
    ).round(2)

    # reset_index() convierte el índice en columna normal
    return resumen.reset_index().to_dict(orient="records")


def ranking_salarial() -> list:
    """
    Devuelve todos los empleados ordenados de mayor a menor
    salario real, incluyendo su cargo, salario base y
    posición en el ranking dentro de su propio cargo.
    """

    df = query("""
        SELECT e.nombre, e.apellido,
               c.nombre_cargo, c.salario_base,
               AVG(se.salario_real) as salario_real_medio
        FROM Empleado e
        JOIN Cargo c ON e.id_cargo = c.id_cargo
        JOIN SalarioEmpleado se ON se.id_empleado = e.id_empleado
        GROUP BY e.id_empleado
    """)

    df = df.sort_values("salario_real_medio", ascending=False)

    # Ranking global entre todos los empleados
    df["ranking_global"] = range(1, len(df) + 1)

    # Ranking dentro del mismo cargo
    df["ranking_en_cargo"] = df.groupby("nombre_cargo")["salario_real_medio"] \
                               .rank(ascending=False, method="min").astype(int)

    # Cuántos compañeros tiene en su mismo cargo
    df["total_en_cargo"] = df.groupby("nombre_cargo")["nombre_cargo"] \
                             .transform("count")

    # Diferencia en euros respecto al salario base del cargo
    df["diferencia_vs_base"] = (df["salario_real_medio"] - df["salario_base"]).round(2)

    return df.to_dict(orient="records")


def comparativa_salario_real_vs_base() -> list:
    """
    Compara el salario medio real de cada empleado con el
    salario base de su cargo. Detecta quién cobra
    significativamente más o menos de lo establecido.
    """

    df = query("""
        SELECT e.id_empleado, e.nombre, e.apellido,
               c.nombre_cargo, c.salario_base,
               AVG(se.salario_real) as salario_real_medio
        FROM Empleado e
        JOIN Cargo c ON e.id_cargo = c.id_cargo
        JOIN SalarioEmpleado se ON se.id_empleado = e.id_empleado
        GROUP BY e.id_empleado
    """)

    # Diferencia absoluta en euros
    df["diferencia"] = (df["salario_real_medio"] - df["salario_base"]).round(2)

    # Positivo = cobra más de lo marcado por el cargo
    # Negativo = cobra menos de lo marcado por el cargo
    df["diferencia_%"] = (
        (df["diferencia"] / df["salario_base"]) * 100
    ).round(2)

    return df.to_dict(orient="records")

def antiguedad_media_por_cargo() -> list:
    """
    Calcula la antigüedad media en años de los empleados
    agrupada por cargo. Permite ver si los cargos más altos
    tienen empleados más veteranos, lo que puede indicar
    si la empresa promociona internamente o contrata fuera.
    """

    df = query("""
        SELECT c.nombre_cargo,
               e.fecha_contratacion
        FROM Empleado e
        JOIN Cargo c ON e.id_cargo = c.id_cargo
    """)

    # Convertimos la fecha a datetime para poder operar con ella
    df["fecha_contratacion"] = pd.to_datetime(df["fecha_contratacion"])

    # Calculamos los años de antigüedad de cada empleado
    # restando su fecha de contratación a la fecha actual
    hoy = pd.Timestamp.today()
    df["antiguedad_años"] = ((hoy - df["fecha_contratacion"])
                             .dt.days / 365.25).round(2)

    # Agrupamos por cargo y calculamos estadísticas de antigüedad
    resumen = df.groupby("nombre_cargo")["antiguedad_años"].agg(
        antiguedad_media  = "mean",
        antiguedad_maxima = "max",
        antiguedad_minima = "min",
        total_empleados   = "count"
    ).round(2)

    return resumen.reset_index().to_dict(orient="records")


def distribucion_empleados_por_cargo() -> list:
    """
    Cuenta cuántos empleados hay en cada cargo y qué
    porcentaje representa sobre el total de la plantilla.
    Útil para ver si la estructura organizativa es equilibrada
    o si hay demasiado peso en algún nivel jerárquico.
    """

    df = query("""
        SELECT c.nombre_cargo, c.salario_base,
               COUNT(e.id_empleado) AS total_empleados
        FROM Cargo c
        LEFT JOIN Empleado e ON e.id_cargo = c.id_cargo
        GROUP BY c.id_cargo
        ORDER BY total_empleados DESC
    """)

    # Porcentaje que representa cada cargo sobre el total
    total = df["total_empleados"].sum()
    df["porcentaje_%"] = (df["total_empleados"] / total * 100).round(2)

    # Coste total de la plantilla por cargo
    # (salario base × número de empleados)
    df["coste_total_cargo"] = df["salario_base"] * df["total_empleados"]

    return df.to_dict(orient="records")

# CONCIERTO

def ranking_cantantes_por_actividad() -> list:
    """
    Ranking de cantantes por número de conciertos realizados
    y duración total de sus giras.
    Permite ver quién tiene más actividad en directo.
    """

    df = query("""
        SELECT ca.nombre AS cantante,
               COUNT(co.id_concierto) AS total_conciertos,
               SUM(g.duracion) AS duracion_total_minutos,
               COUNT(DISTINCT g.id_gira) AS total_giras,
               AVG(g.num_canciones) AS media_canciones_por_gira
        FROM Conciertos co
        JOIN Cantante ca ON co.id_cantante = ca.id_cantante
        JOIN Gira g ON co.id_gira = g.id_gira
        GROUP BY co.id_cantante
        ORDER BY total_conciertos DESC
    """)

    # Ranking por actividad total
    df["ranking"] = range(1, len(df) + 1)
    df["media_canciones_por_gira"] = df["media_canciones_por_gira"].round(2)

    return df.to_dict(orient="records")


def distribucion_conciertos_por_continente() -> list:
    """
    Agrupa los conciertos por continente para ver
    en qué parte del mundo hay más actividad musical.
    """

    df = query("""
        SELECT p.continente,
               COUNT(co.id_concierto) AS total_conciertos,
               COUNT(DISTINCT co.id_cantante) AS cantantes_distintos,
               COUNT(DISTINCT co.id_recinto) AS recintos_distintos
        FROM Conciertos co
        JOIN Recinto r ON co.id_recinto = r.id_recinto
        JOIN Pais p ON r.id_pais = p.id
        GROUP BY p.continente
        ORDER BY total_conciertos DESC
    """)

    # Porcentaje del total de conciertos que representa cada continente
    total = df["total_conciertos"].sum()
    df["porcentaje_%"] = (df["total_conciertos"] / total * 100).round(2)

    return df.to_dict(orient="records")


def recintos_mas_demandados() -> list:
    """
    Ranking de recintos que acogen más conciertos.
    Incluye el país y los cantantes distintos que han
    actuado en cada recinto.
    """

    df = query("""
        SELECT r.nombre AS recinto, p.nombre AS pais, p.continente,
               COUNT(co.id_concierto) AS total_conciertos,
               COUNT(DISTINCT co.id_cantante) AS cantantes_distintos
        FROM Conciertos co
        JOIN Recinto r ON co.id_recinto = r.id_recinto
        JOIN Pais p ON r.id_pais = p.id
        GROUP BY co.id_recinto
        ORDER BY total_conciertos DESC
    """)

    # Nos quedamos con el top 10 más demandados
    df = df.head(10)
    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")


def ocupacion_media_por_cantante() -> list:
    """
    Calcula el porcentaje de ocupación medio por cantante.
    (entradas_vendidas / capacidad_recinto * 100)
    Mide quién llena más los recintos donde actúa.
    """

    df = query("""
        SELECT ca.nombre AS cantante,
               AVG(CAST(co.entradas_vendidas AS FLOAT)
                   / r.capacidad * 100) AS "ocupacion_media",
               SUM(co.entradas_vendidas) AS entradas_totales,
               COUNT(co.id_concierto) AS total_conciertos
        FROM Conciertos co
        JOIN Cantante ca ON co.id_cantante = ca.id_cantante
        JOIN Recinto r ON co.id_recinto = r.id_recinto
        GROUP BY co.id_cantante
        ORDER BY ocupacion_media DESC
    """)

    df["ocupacion_media"] = df["ocupacion_media"].round(2)

    return df.to_dict(orient="records")

def rentabilidad_por_gira() -> list:
    """
    Calcula el ratio de conciertos por gira de cada cantante.
    Un ratio alto significa que exprime bien cada gira,
    lo que es directamente rentable para el promotor.
    También incluye la duración media y canciones medias
    por gira para valorar la intensidad del trabajo.
    """

    df = query("""
        SELECT ca.nombre AS cantante,
               g.nombre_gira,
               g.num_canciones,
               g.duracion,
               COUNT(co.id_concierto) AS conciertos_en_gira
        FROM Conciertos co
        JOIN Cantante ca ON co.id_cantante = ca.id_cantante
        JOIN Gira g ON co.id_gira = g.id_gira
        GROUP BY co.id_cantante, co.id_gira
    """)

    # Agrupamos por cantante para obtener sus medias globales
    resumen = df.groupby("cantante").agg(
        total_giras            = ("nombre_gira", "count"),
        conciertos_por_gira    = ("conciertos_en_gira", "mean"),
        duracion_media_gira    = ("duracion", "mean"),
        canciones_media_gira   = ("num_canciones", "mean")
    ).round(2)

    # Ordenamos por conciertos por gira descendente
    resumen = resumen.sort_values("conciertos_por_gira", ascending=False)

    return resumen.reset_index().to_dict(orient="records")

# PELÍCULAS

def rentabilidad_peliculas() -> list:
    """
    Calcula el ratio de rentabilidad de cada película.
    Ratio = recaudacion / presupuesto

    Un ratio de 2.0 significa que ganó el doble de lo invertido.
    Un ratio menor que 1.0 significa pérdidas.
    """

    df = query("""
        SELECT titulo, duracion, presupuesto, recaudacion
        FROM Pelicula
        WHERE presupuesto > 0
        ORDER BY recaudacion DESC
    """)

    # Ratio de rentabilidad: cuánto se ganó por cada euro invertido
    df["ratio_rentabilidad"] = (df["recaudacion"] / df["presupuesto"]).round(2)

    # Beneficio absoluto en euros
    df["beneficio"] = (df["recaudacion"] - df["presupuesto"])

    # Clasificamos la película según su rentabilidad
    def clasificar(ratio):
        if ratio >= 3:
            return "Muy rentable"
        elif ratio >= 1.5:
            return "Rentable"
        elif ratio >= 1:
            return "Rentabilidad baja"
        else:
            return "Pérdidas"

    df["clasificacion"] = df["ratio_rentabilidad"].apply(clasificar)

    return df.sort_values("ratio_rentabilidad",
                          ascending=False).to_dict(orient="records")


def generos_mas_rentables() -> list:
    """
    Calcula la recaudación media, el presupuesto medio y el
    ratio de rentabilidad medio agrupado por género.
    Permite ver qué tipo de película genera más dinero.
    """

    df = query("""
        SELECT g.nombre AS genero,
               AVG(p.recaudacion) AS recaudacion_media,
               AVG(p.presupuesto) AS presupuesto_medio,
               COUNT(p.id_pelicula) AS total_peliculas,
               AVG(p.duracion) AS duracion_media
        FROM Pelicula p
        JOIN Pelicula_Genero pg ON p.id_pelicula = pg.id_pelicula
        JOIN Genero g ON pg.id_genero = g.id_genero
        GROUP BY g.id_genero
        ORDER BY recaudacion_media DESC
    """)

    # Ratio de rentabilidad medio por género
    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"] = df["recaudacion_media"].round(2)
    df["presupuesto_medio"] = df["presupuesto_medio"].round(2)
    df["duracion_media"]    = df["duracion_media"].round(2)

    return df.to_dict(orient="records")


def directores_mas_taquilleros() -> list:
    """
    Ranking de directores por recaudación media de sus películas.
    Incluye el número de películas dirigidas para que el dato
    sea más representativo (un director con 10 películas es
    más fiable que uno con solo 1).
    """

    df = query("""
        SELECT pe.nombre AS director,
               COUNT(pd.id_pelicula) AS peliculas_dirigidas,
               AVG(p.recaudacion) AS recaudacion_media,
               AVG(p.presupuesto) AS presupuesto_medio,
               SUM(p.recaudacion) AS recaudacion_total
        FROM Pelicula_Director pd
        JOIN Pelicula p ON pd.id_pelicula = p.id_pelicula
        JOIN Persona pe ON pd.id_persona = pe.id_persona
        GROUP BY pd.id_persona
        ORDER BY recaudacion_media DESC
    """)

    # Ratio de rentabilidad medio del director
    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"]  = df["recaudacion_media"].round(2)
    df["presupuesto_medio"]  = df["presupuesto_medio"].round(2)
    df["recaudacion_total"]  = df["recaudacion_total"].round(2)

    # Ranking global
    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")

def peliculas_mayor_perdida() -> list:
    """
    Identifica las películas con mayor pérdida económica
    en términos absolutos (euros perdidos).
    Para una productora esto es crítico: saber qué proyectos
    han sido los peores fracasos económicos ayuda a evitar
    patrones repetidos en futuras producciones.
    """

    df = query("""
        SELECT titulo, presupuesto, recaudacion, duracion
        FROM Pelicula
        WHERE presupuesto > 0
    """)

    # Pérdida absoluta en euros
    df["perdida"] = df["recaudacion"] - df["presupuesto"]

    # Ratio de recuperación: qué porcentaje del presupuesto se recuperó
    df["recuperacion_%"] = (
        (df["recaudacion"] / df["presupuesto"]) * 100
    ).round(2)

    # Nos quedamos solo con las que tienen pérdidas reales
    df = df[df["perdida"] < 0]

    # Ordenamos de mayor a menor pérdida absoluta
    df = df.sort_values("perdida", ascending=True)

    return df.to_dict(orient="records")


def impacto_actores_en_recaudacion() -> list:
    """
    Calcula la recaudación media de las películas en las que
    ha participado cada actor. Útil para decidir a quién
    contratar en un proyecto si se busca maximizar la
    recaudación en taquilla.
    Solo incluye actores con al menos 2 películas para
    que el dato sea estadísticamente representativo.
    """

    df = query("""
        SELECT pe.nombre AS actor,
               COUNT(r.id_pelicula) AS total_peliculas,
               AVG(p.recaudacion) AS recaudacion_media,
               AVG(p.presupuesto) AS presupuesto_medio,
               SUM(p.recaudacion) AS recaudacion_total
        FROM Reparto r
        JOIN Pelicula p ON r.id_pelicula = p.id_pelicula
        JOIN Persona pe ON r.id_persona = pe.id_persona
        GROUP BY r.id_persona
        HAVING total_peliculas >= 2
        ORDER BY recaudacion_media DESC
    """)

    # Ratio de rentabilidad medio de las películas del actor
    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"]  = df["recaudacion_media"].round(2)
    df["presupuesto_medio"]  = df["presupuesto_medio"].round(2)
    df["recaudacion_total"]  = df["recaudacion_total"].round(2)

    # Ranking por recaudación media
    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")