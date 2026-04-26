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

def rendimiento_vs_media_posicion(id_admin: int) -> list:
    """
    Compara los goles y asistencias de cada jugador
    con la media de los jugadores de su misma posición.
    Útil para detectar quién destaca dentro de su rol.
    """

    df = query(f"""
        SELECT jugador AS nombre, posicion,
               goles, asistencias, partidos_jugados
        FROM Futbol
        WHERE id_admin = {id_admin}
    """)

    media = df.groupby("posicion")[["goles", "asistencias"]].transform("mean")

    df["media_goles_posicion"]       = media["goles"].round(2)
    df["media_asistencias_posicion"] = media["asistencias"].round(2)

    df["diff_goles"]       = (df["goles"]       - df["media_goles_posicion"]).round(2)
    df["diff_asistencias"] = (df["asistencias"] - df["media_asistencias_posicion"]).round(2)

    return df.to_dict(orient="records")


def ranking_goleadores(id_admin: int) -> list:
    """
    Devuelve el ranking de jugadores ordenados por goles totales.
    Incluye su posición, equipo y asistencias para tener
    una visión completa de su aportación ofensiva.
    """

    df = query(f"""
        SELECT jugador AS nombre, posicion, equipo,
               goles AS goles_totales,
               asistencias AS asistencias_totales,
               partidos_jugados AS partidos_totales
        FROM Futbol
        WHERE id_admin = {id_admin}
        ORDER BY goles_totales DESC
    """)

    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")


def estadisticas_por_equipo(id_admin: int) -> list:
    """
    Agrupa las estadísticas de todos los jugadores por equipo.
    Permite ver qué equipo es más goleador, más disciplinado
    o genera más asistencias en conjunto.
    """

    df = query(f"""
        SELECT equipo,
               SUM(goles) AS goles_totales,
               SUM(asistencias) AS asistencias_totales,
               SUM(partidos_jugados) AS partidos_totales,
               SUM(tarjetas_amarillas) AS tarjetas_amarillas,
               SUM(tarjetas_rojas) AS tarjetas_rojas,
               COUNT(id_jugador) AS num_jugadores
        FROM Futbol
        WHERE id_admin = {id_admin}
        GROUP BY equipo
        ORDER BY goles_totales DESC
    """)

    df["goles_por_jugador"] = (df["goles_totales"] / df["num_jugadores"]).round(2)

    return df.to_dict(orient="records")


def eficiencia_goleadora(id_admin: int) -> list:
    """
    Calcula los goles por partido jugado de cada jugador.
    Solo incluye jugadores con al menos 5 partidos para
    que el dato sea estadísticamente representativo.
    """

    df = query(f"""
        SELECT jugador AS nombre, posicion,
               goles AS goles_totales,
               partidos_jugados AS partidos_totales
        FROM Futbol
        WHERE id_admin = {id_admin}
        AND partidos_jugados >= 5
        ORDER BY goles_totales DESC
    """)

    # Goles por partido: un valor de 0.5 significa 1 gol cada 2 partidos
    df["goles_por_partido"] = (df["goles_totales"] / df["partidos_totales"]).round(2)
    df = df.sort_values("goles_por_partido", ascending=False)

    return df.to_dict(orient="records")


# EMPLEADOS

def distribucion_salarial_por_cargo(id_admin: int) -> list:
    """
    Calcula media, mediana y desviación típica del salario
    real agrupado por cargo. El coeficiente de variación
    indica qué cargos tienen más desigualdad salarial.
    """

    df = query(f"""
        SELECT cargo AS nombre_cargo, salario_real
        FROM Empleados
        WHERE id_admin = {id_admin}
    """)

    resumen = df.groupby("nombre_cargo")["salario_real"].agg(
        media             = "mean",
        mediana           = "median",
        desviacion_tipica = "std",
        minimo            = "min",
        maximo            = "max",
        total_empleados   = "count"
    ).round(2)

    # Cuanto más alto, más desigualdad salarial en ese cargo
    resumen["coef_variacion_%"] = (
        (resumen["desviacion_tipica"] / resumen["media"]) * 100
    ).round(2)

    return resumen.reset_index().to_dict(orient="records")


def ranking_salarial(id_admin: int) -> list:
    """
    Devuelve todos los empleados ordenados de mayor a menor
    salario, incluyendo su cargo y posición en el ranking
    dentro de su propio cargo.
    """

    df = query(f"""
        SELECT empleado AS nombre, cargo AS nombre_cargo,
               salario_real AS salario_real_medio
        FROM Empleados
        WHERE id_admin = {id_admin}
    """)

    df = df.sort_values("salario_real_medio", ascending=False).head(25)

    df["ranking_global"] = range(1, len(df) + 1)

    df["ranking_en_cargo"] = df.groupby("nombre_cargo")["salario_real_medio"] \
                               .rank(ascending=False, method="min").astype(int)

    df["total_en_cargo"] = df.groupby("nombre_cargo")["nombre_cargo"] \
                             .transform("count")

    return df.to_dict(orient="records")


def comparativa_salario_real_vs_base(id_admin: int) -> list:
    """
    Compara el salario de cada empleado con la media salarial
    de su cargo. Detecta quién cobra significativamente
    más o menos que sus compañeros de puesto.
    """

    df = query(f"""
        SELECT empleado AS nombre, cargo AS nombre_cargo,
               salario_real AS salario_real_medio
        FROM Empleados
        WHERE id_admin = {id_admin}
    """)

    # Media del cargo como referencia de comparación
    df["salario_medio_cargo"] = df.groupby("nombre_cargo")["salario_real_medio"] \
                                  .transform("mean").round(2)

    # Positivo = cobra más que la media de su cargo
    # Negativo = cobra menos que la media de su cargo
    df["diferencia"] = (df["salario_real_medio"] - df["salario_medio_cargo"]).round(2)
    df["diferencia_%"] = (
        (df["diferencia"] / df["salario_medio_cargo"]) * 100
    ).round(2)

    return df.to_dict(orient="records")


def antiguedad_media_por_cargo(id_admin: int) -> list:
    """
    Calcula la antigüedad media en años de los empleados
    agrupada por cargo. Permite ver si los cargos más altos
    tienen empleados más veteranos.
    """

    df = query(f"""
            SELECT cargo AS nombre_cargo, fecha_contratacion
            FROM Empleados
            WHERE id_admin = {id_admin}
        """)

    # Especificamos el formato exacto para evitar el error
    df["fecha_contratacion"] = pd.to_datetime(df["fecha_contratacion"],
                                              format="mixed")

    hoy = pd.Timestamp.today()
    df["antiguedad_anos"] = ((hoy - df["fecha_contratacion"])
                             .dt.days / 365.25).round(2)

    resumen = df.groupby("nombre_cargo")["antiguedad_anos"].agg(
        antiguedad_media="mean",
        antiguedad_maxima="max",
        antiguedad_minima="min",
        total_empleados="count"
    ).round(2)

    return resumen.reset_index().to_dict(orient="records")


def distribucion_empleados_por_cargo(id_admin: int) -> list:
    """
    Cuenta cuántos empleados hay en cada cargo y qué
    porcentaje representa sobre el total de la plantilla.
    """

    df = query(f"""
        SELECT cargo AS nombre_cargo,
               COUNT(id_empleado) AS total_empleados,
               AVG(salario_real) AS salario_base
        FROM Empleados
        WHERE id_admin = {id_admin}
        GROUP BY cargo
        ORDER BY total_empleados DESC
    """)

    total = df["total_empleados"].sum()
    df["porcentaje_%"] = (df["total_empleados"] / total * 100).round(2)

    # Coste total estimado: salario medio × número de empleados
    df["coste_total_cargo"] = (df["salario_base"] * df["total_empleados"]).round(0)

    return df.to_dict(orient="records")


# CONCIERTOS

def ranking_cantantes_por_actividad(id_admin: int) -> list:
    """
    Ranking de cantantes por número de conciertos realizados
    y duración total de sus conciertos.
    """

    df = query(f"""
        SELECT Cantante AS cantante,
               COUNT(*) AS total_conciertos,
               SUM(duracion) AS duracion_total_minutos,
               COUNT(DISTINCT concierto) AS total_giras,
               AVG(num_canciones) AS media_canciones_por_gira
        FROM Conciertos
        WHERE id_admin = {id_admin}
        GROUP BY Cantante
        ORDER BY total_conciertos DESC
    """)

    df["ranking"] = range(1, len(df) + 1)
    df["media_canciones_por_gira"] = df["media_canciones_por_gira"].round(2)

    return df.to_dict(orient="records")


def distribucion_conciertos_por_continente(id_admin: int) -> list:
    """
    Agrupa los conciertos por continente donde se celebran
    (no por nacionalidad del cantante) para ver en qué
    parte del mundo hay más actividad musical.
    """

    df = query(f"""
        SELECT continente,
               COUNT(*) AS total_conciertos,
               COUNT(DISTINCT cantante) AS cantantes_distintos,
               COUNT(DISTINCT recinto) AS recintos_distintos
        FROM Conciertos
        WHERE id_admin = {id_admin}
        GROUP BY continente
        ORDER BY total_conciertos DESC
    """)

    total = df["total_conciertos"].sum()
    df["porcentaje_%"] = (df["total_conciertos"] / total * 100).round(2)

    return df.to_dict(orient="records")


def recintos_mas_demandados(id_admin: int) -> list:
    """
    Ranking de recintos que acogen más conciertos.
    Incluye el país y los cantantes distintos que han
    actuado en cada recinto.
    """

    df = query(f"""
        SELECT recinto, pais, continente,
               COUNT(*) AS total_conciertos,
               COUNT(DISTINCT Cantante) AS cantantes_distintos
        FROM Conciertos
        WHERE id_admin = {id_admin}
        GROUP BY recinto
        ORDER BY total_conciertos DESC
    """)

    df = df.head(10)
    df["ranking"] = range(1, len(df) + 1)

    return df.to_dict(orient="records")


def ocupacion_media_por_cantante(id_admin: int) -> list:
    """
    Calcula el porcentaje de ocupación medio por cantante.
    (entradas_vendidas / max_entradas * 100)
    Mide quién llena más los recintos donde actúa.
    """

    df = query(f"""
        SELECT Cantante AS cantante,
               AVG(CAST(entradas_vendidas AS FLOAT)
                   / max_entradas * 100) AS ocupacion_media,
               SUM(entradas_vendidas) AS entradas_totales,
               COUNT(*) AS total_conciertos
        FROM Conciertos
        WHERE id_admin = {id_admin}
        GROUP BY Cantante
        ORDER BY ocupacion_media DESC
    """)

    df["ocupacion_media"] = df["ocupacion_media"].round(2)

    return df.to_dict(orient="records")


def rentabilidad_por_gira(id_admin: int) -> list:
    """
    Calcula el ratio de conciertos por gira de cada cantante.
    Un ratio alto significa que exprime bien cada gira,
    lo que es directamente rentable para el promotor.
    """

    df = query(f"""
        SELECT Cantante AS cantante,
               concierto AS nombre_gira,
               num_canciones,
               duracion,
               COUNT(*) AS conciertos_en_gira
        FROM Conciertos
        WHERE id_admin = {id_admin}
        GROUP BY Cantante, concierto
    """)

    resumen = df.groupby("cantante").agg(
        total_giras          = ("nombre_gira", "count"),
        conciertos_por_gira  = ("conciertos_en_gira", "mean"),
        duracion_media_gira  = ("duracion", "mean"),
        canciones_media_gira = ("num_canciones", "mean")
    ).round(2)

    resumen = resumen.sort_values("conciertos_por_gira", ascending=False)

    return resumen.reset_index().to_dict(orient="records")


# PELÍCULAS

def rentabilidad_peliculas(id_admin: int) -> list:
    """
    Calcula el ratio de rentabilidad de cada película.
    Ratio = recaudacion / presupuesto
    Un ratio menor que 1.0 significa pérdidas.
    """

    df = query(f"""
        SELECT Pelicula AS titulo, duracion, presupuesto, recaudacion
        FROM Cine
        WHERE presupuesto > 0
        AND id_admin = {id_admin}
        ORDER BY recaudacion DESC
    """)

    df["ratio_rentabilidad"] = (df["recaudacion"] / df["presupuesto"]).round(2)
    df["beneficio"] = (df["recaudacion"] - df["presupuesto"])

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


def generos_mas_rentables(id_admin: int) -> list:
    """
    Calcula la recaudación media, el presupuesto medio y el
    ratio de rentabilidad medio agrupado por género.
    Permite ver qué tipo de película genera más dinero.
    """

    df = query(f"""
        SELECT genero,
               AVG(recaudacion) AS recaudacion_media,
               AVG(presupuesto) AS presupuesto_medio,
               COUNT(*) AS total_peliculas,
               AVG(duracion) AS duracion_media
        FROM Cine
        WHERE id_admin = {id_admin}
        GROUP BY genero
        ORDER BY recaudacion_media DESC
    """)

    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"] = df["recaudacion_media"].round(2)
    df["presupuesto_medio"] = df["presupuesto_medio"].round(2)
    df["duracion_media"]    = df["duracion_media"].round(2)

    return df.to_dict(orient="records")


def directores_mas_taquilleros(id_admin: int) -> list:
    """
    Ranking de directores por recaudación media de sus películas.
    Incluye el número de películas dirigidas para que el dato
    sea más representativo.
    """

    df = query(f"""
        SELECT director,
               COUNT(*) AS peliculas_dirigidas,
               AVG(recaudacion) AS recaudacion_media,
               AVG(presupuesto) AS presupuesto_medio,
               SUM(recaudacion) AS recaudacion_total
        FROM Cine
        WHERE id_admin = {id_admin}
        GROUP BY director
        ORDER BY recaudacion_media DESC
    """)

    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"] = df["recaudacion_media"].round(2)
    df["presupuesto_medio"] = df["presupuesto_medio"].round(2)
    df["recaudacion_total"] = df["recaudacion_total"].round(2)
    df["ranking"]           = range(1, len(df) + 1)

    return df.to_dict(orient="records")


def peliculas_mayor_perdida(id_admin: int) -> list:
    """
    Identifica las películas con mayor pérdida económica
    en términos absolutos (euros perdidos).
    """

    df = query(f"""
            SELECT Pelicula AS titulo, presupuesto, recaudacion, duracion
            FROM Cine
            WHERE presupuesto > 0
            AND id_admin = {id_admin}
        """)

    df["perdida"] = df["recaudacion"] - df["presupuesto"]

    # Usamos recuperacion_pct en lugar de recuperacion_%
    # para evitar problemas al pasar por JSON
    df["recuperacion_pct"] = (
            (df["recaudacion"] / df["presupuesto"]) * 100
    ).round(2)

    df = df[df["perdida"] < 0]
    df = df.sort_values("perdida", ascending=True)

    return df.to_dict(orient="records")


def impacto_actores_en_recaudacion(id_admin: int) -> list:
    """
    Calcula la recaudación media de las películas en las que
    ha participado cada actor protagonista.
    Solo incluye actores con al menos 2 películas.
    """

    df = query(f"""
        SELECT actor_protagonista AS actor,
               COUNT(*) AS total_peliculas,
               AVG(recaudacion) AS recaudacion_media,
               AVG(presupuesto) AS presupuesto_medio,
               SUM(recaudacion) AS recaudacion_total
        FROM Cine
        WHERE id_admin = {id_admin}
        GROUP BY actor_protagonista
        ORDER BY recaudacion_media DESC
    """)

    df["ratio_rentabilidad"] = (
        df["recaudacion_media"] / df["presupuesto_medio"]
    ).round(2)

    df["recaudacion_media"] = df["recaudacion_media"].round(2)
    df["presupuesto_medio"] = df["presupuesto_medio"].round(2)
    df["recaudacion_total"] = df["recaudacion_total"].round(2)
    df["ranking"]           = range(1, len(df) + 1)

    return df.to_dict(orient="records")