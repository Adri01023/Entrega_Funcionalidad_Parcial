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


# Parte Futbol

def rendimiento_vs_media_posicion() -> list:
    """
    Compara los goles y asistencias de cada jugador
    con la media de los jugadores de su misma posición.
    """

    df = query("""
        SELECT j.nombre, j.posicion,
               e.goles, e.asistencias, e.partidos_jugados
        FROM EstadisticasJugador e
        JOIN Jugador j ON e.id_jugador = j.id_jugador
    """)

    # media por posicion
    media = df.groupby("posicion")[["goles", "asistencias"]].transform("mean")

    df["media_goles_posicion"]       = media["goles"].round(2)
    df["media_asistencias_posicion"] = media["asistencias"].round(2)

    # Positivo = rinde por encima de su posición
    # Negativo = rinde por debajo de su posición
    df["diff_goles"] = (df["goles"] - df["media_goles_posicion"]).round(2)
    df["diff_asistencias"] = (df["asistencias"] - df["media_asistencias_posicion"]).round(2)

    return df.to_dict(orient="records")

# Parte Empleados

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

    # calcula varias estadísticas a la vez por cargo
    resumen = df.groupby("nombre_cargo")["salario_real"].agg(
        media             = "mean",
        mediana           = "median",
        desviacion_tipica = "std",
        minimo            = "min",
        maximo            = "max",
        total_empleados   = "count"
    ).round(2)

    # cuanto más alto el coeficiente, más desigualdad salarial
    resumen["coef_variacion_%"] = ((resumen["desviacion_tipica"] / resumen["media"]) * 100).round(2)

    # convertir indice en columnas
    return resumen.reset_index().to_dict(orient="records")


def ranking_salarial() -> list:
    """
    Devuelve todos los empleados ordenados de mayor a menor
    salario real, incluyendo su cargo, salario base y
    posición en el ranking dentro de su propio cargo.
    Útil para ver quién cobra más y cómo se sitúa
    respecto a sus compañeros de puesto.
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

    # Ordenamos de mayor a menor salario real
    df = df.sort_values("salario_real_medio", ascending=False)

    df["ranking_global"] = range(1, len(df) + 1)

    # Ranking dentro del cargo: posición entre compañeros del mismo puesto
    # rank() asigna posiciones dentro de cada grupo
    df["ranking_en_cargo"] = df.groupby("nombre_cargo")["salario_real_medio"] \
                               .rank(ascending=False, method="min").astype(int)

    # Cuántos empleados hay en su mismo cargo
    df["total_en_cargo"] = df.groupby("nombre_cargo")["nombre_cargo"] \
                             .transform("count")

    # Diferencia en euros respecto al salario base
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