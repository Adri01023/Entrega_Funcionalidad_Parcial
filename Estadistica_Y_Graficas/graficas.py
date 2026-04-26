# procesamiento/graficas.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Patch
import io

matplotlib.use("Agg")


def guardar_grafico():
    """
    Guarda el gráfico actual en memoria y lo devuelve como bytes.
    """
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return buffer.read()


# FÚTBOL

def grafico_rendimiento_posicion(datos):
    """
    Barras agrupadas con la media de goles y asistencias
    por posición.

    Parámetros:
        datos → resultado de rendimiento_vs_media_posicion()
    """

    df = pd.DataFrame(datos)
    print("Columnas disponibles:", df.columns.tolist())
    # Agrupamos por posición cogiendo el primer valor de la media
    # ya que todos los jugadores de la misma posición tienen la misma
    resumen = df.groupby("posicion")[
        ["media_goles_posicion", "media_asistencias_posicion"]
    ].first()

    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(resumen))
    ancho = 0.35

    ax.bar([i - ancho/2 for i in x], resumen["media_goles_posicion"],
           width=ancho, label="Media goles", color="steelblue")
    ax.bar([i + ancho/2 for i in x], resumen["media_asistencias_posicion"],
           width=ancho, label="Media asistencias", color="orange")

    ax.set_title("Rendimiento medio por posición")
    ax.set_xlabel("Posición")
    ax.set_ylabel("Media")
    ax.set_xticks(list(x))
    ax.set_xticklabels(resumen.index, rotation=45, ha="right")
    ax.legend()

    return guardar_grafico()


def grafico_ranking_goleadores(datos):
    """
    Barras horizontales con los top 10 goleadores.
    El color diferencia goles de asistencias.

    Parámetros:
        datos → resultado de ranking_goleadores()
    """

    df = pd.DataFrame(datos)

    # Nos quedamos con el top 10 para que sea legible
    df = df.head(10)

    # Ordenamos de menor a mayor para que el primero quede arriba
    df = df.sort_values("goles_totales", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Barras de goles y asistencias apiladas horizontalmente
    # stacked permite ver la contribución total de cada jugador
    ax.barh(df["nombre"], df["goles_totales"],
            label="Goles", color="steelblue")
    ax.barh(df["nombre"], df["asistencias_totales"],
            left=df["goles_totales"], label="Asistencias", color="orange")

    ax.set_title("Top 10 goleadores (goles + asistencias)")
    ax.set_xlabel("Total")
    ax.legend()

    return guardar_grafico()


def grafico_estadisticas_por_equipo(datos):
    """
    Barras agrupadas con goles, asistencias y tarjetas
    por equipo. Permite comparar el rendimiento colectivo.

    Parámetros:
        datos → resultado de estadisticas_por_equipo()
    """

    df = pd.DataFrame(datos)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # twinx() crea un segundo eje Y para las tarjetas
    # ya que sus valores son mucho menores que goles y asistencias
    ax2 = ax1.twinx()

    x = range(len(df))
    ancho = 0.25

    # Goles y asistencias en el eje izquierdo
    ax1.bar([i - ancho for i in x], df["goles_totales"],
            width=ancho, label="Goles", color="steelblue", alpha=0.8)
    ax1.bar([i for i in x], df["asistencias_totales"],
            width=ancho, label="Asistencias", color="orange", alpha=0.8)

    # Tarjetas en el eje derecho para que sean visibles
    ax2.bar([i + ancho for i in x], df["tarjetas_amarillas"],
            width=ancho, label="Tarjetas amarillas", color="gold", alpha=0.8)

    ax1.set_title("Estadísticas por equipo")
    ax1.set_xlabel("Equipo")
    ax1.set_ylabel("Goles / Asistencias")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["equipo"], rotation=45, ha="right")

    ax2.set_ylabel("Tarjetas amarillas", color="goldenrod")
    ax2.tick_params(axis="y", labelcolor="goldenrod")

    # Combinamos leyendas de ambos ejes en una sola
    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, etiquetas1 + etiquetas2, loc="upper right")

    return guardar_grafico()


def grafico_eficiencia_goleadora(datos):
    """
    Barras horizontales con los goles por partido de cada jugador.
    Solo muestra los top 10 más eficientes.

    Parámetros:
        datos → resultado de eficiencia_goleadora()
    """

    df = pd.DataFrame(datos)

    # Top 10 más eficientes
    df = df.head(10)
    df = df.sort_values("goles_por_partido", ascending=True)

    # Color degradado según eficiencia: más rojo = más eficiente
    # Normalizamos entre 0 y 1 para el mapa de colores
    norm = plt.Normalize(df["goles_por_partido"].min(),
                         df["goles_por_partido"].max())
    colores = plt.cm.RdYlGn(norm(df["goles_por_partido"]))

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.barh(df["nombre"], df["goles_por_partido"], color=colores)

    # Añadimos el valor exacto al final de cada barra
    for barra, valor in zip(barras, df["goles_por_partido"]):
        ax.text(barra.get_width() + 0.01, barra.get_y() + barra.get_height()/2,
                f"{valor}", va="center", fontsize=9)

    ax.set_title("Top 10 jugadores más eficientes (goles por partido)")
    ax.set_xlabel("Goles por partido")

    return guardar_grafico()

# EMPLEADOS

def grafico_distribucion_salarial(datos):
    """
    Barras para media y mediana por cargo con segundo eje
    para la desviación típica, que tiene escala diferente.

    Parámetros:
        datos → resultado de distribucion_salarial_por_cargo()
    """

    df = pd.DataFrame(datos)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    x = range(len(df))
    ancho = 0.3

    ax1.bar([i - ancho/2 for i in x], df["media"],
            width=ancho, label="Media", color="steelblue", alpha=0.8)
    ax1.bar([i + ancho/2 for i in x], df["mediana"],
            width=ancho, label="Mediana", color="orange", alpha=0.8)

    # Desviación típica como línea en el eje derecho
    ax2.plot(list(x), df["desviacion_tipica"],
             marker="D", color="green", linewidth=2,
             markersize=8, label="Desviación típica", linestyle="--")

    ax1.set_title("Distribución salarial por cargo")
    ax1.set_xlabel("Cargo")
    ax1.set_ylabel("Salario (€)")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["nombre_cargo"], rotation=45, ha="right")

    ax2.set_ylabel("Desviación típica (€)", color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, etiquetas1 + etiquetas2, loc="upper left")

    return guardar_grafico()


def grafico_ranking_salarios(datos):
    """
    Barras horizontales con todos los empleados ordenados
    por salario, con colores distintos por cargo.

    Parámetros:
        datos → resultado de ranking_salarial()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("salario_real_medio", ascending=True)

    cargos_unicos = df["nombre_cargo"].unique()
    paleta = ["steelblue", "orange", "green", "red", "purple"]
    color_por_cargo = {cargo: paleta[i % len(paleta)]
                       for i, cargo in enumerate(cargos_unicos)}
    colores = [color_por_cargo[cargo] for cargo in df["nombre_cargo"]]

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.4)))

    ax.barh(df["nombre"],
            df["salario_real_medio"], color=colores)

    ax.set_title("Ranking salarial de empleados por cargo")
    ax.set_xlabel("Salario real medio (€)")

    leyenda = [Patch(color=color_por_cargo[cargo], label=cargo)
               for cargo in cargos_unicos]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()


def grafico_comparativa_vs_base(datos):
    """
    Barras horizontales con la diferencia porcentual entre
    salario real y base. Verde = cobra más, rojo = cobra menos.
    Muestra solo el top 10 que más se aleja para que sea legible.

    Parámetros:
        datos → resultado de comparativa_salario_real_vs_base()
    """

    df = pd.DataFrame(datos)

    # Ordenamos por valor absoluto y cogemos los 10 más extremos
    df["diferencia_abs"] = df["diferencia_%"].abs()
    df = df.sort_values("diferencia_abs", ascending=False).head(10)
    df = df.sort_values("diferencia_%", ascending=True)

    colores = ["green" if v >= 0 else "red" for v in df["diferencia_%"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(df["nombre"],
            df["diferencia_%"], color=colores)
    ax.axvline(x=0, color="black", linewidth=0.8)

    ax.set_title("Top 10 empleados con mayor diferencia\nsalario real vs salario base del cargo")
    ax.set_xlabel("Diferencia (%)")

    return guardar_grafico()

def grafico_antiguedad_por_cargo(datos):
    """
    Barras horizontales con la antigüedad media por cargo.
    Incluye barras de error para mostrar el rango
    entre la antigüedad mínima y máxima.

    Parámetros:
        datos → resultado de antiguedad_media_por_cargo()
    """

    df = pd.DataFrame(datos)

    if df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No hay datos disponibles",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
        return guardar_grafico()

    df = df.sort_values("antiguedad_media", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.barh(df["nombre_cargo"], df["antiguedad_media"],
                     color="steelblue", alpha=0.8)

    for barra, valor in zip(barras, df["antiguedad_media"]):
        ax.text(barra.get_width() + 0.1,
                barra.get_y() + barra.get_height() / 2,
                f"{valor} años", va="center", fontsize=9)

    ax.set_title("Antiguedad media por cargo\n(con rango minimo-maximo)")
    ax.set_xlabel("Antiguedad (años)")

    return guardar_grafico()


def grafico_distribucion_empleados(datos):
    """
    Doble gráfico: tarta con el porcentaje de empleados
    por cargo y barras con el coste total por cargo.
    Usa los mismos colores en ambos gráficos para que
    sea fácil relacionar cada cargo entre las dos vistas.

    Parámetros:
        datos → resultado de distribucion_empleados_por_cargo()
    """

    df = pd.DataFrame(datos)

    # Definimos un diccionario de colores por cargo para que
    # coincidan exactamente en la tarta y en las barras
    paleta = ["steelblue", "orange", "green", "red", "purple"]
    color_por_cargo = {cargo: paleta[i % len(paleta)]
                       for i, cargo in enumerate(df["nombre_cargo"])}

    colores_ordenados = [color_por_cargo[c] for c in df["nombre_cargo"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfico de tarta con el porcentaje de empleados por cargo
    ax1.pie(df["total_empleados"],
            labels=df["nombre_cargo"],
            autopct="%1.1f%%",
            colors=colores_ordenados,
            startangle=90)
    ax1.set_title("Distribución de empleados\npor cargo")

    # Barras con el coste total por cargo usando los mismos colores
    df_sorted = df.sort_values("coste_total_cargo", ascending=True)
    colores_barras = [color_por_cargo[c] for c in df_sorted["nombre_cargo"]]

    ax2.barh(df_sorted["nombre_cargo"],
             df_sorted["coste_total_cargo"],
             color=colores_barras)

    # Valor exacto al final de cada barra
    for i, valor in enumerate(df_sorted["coste_total_cargo"]):
        ax2.text(valor + 100, i, f"{valor:,.0f}€",
                 va="center", fontsize=9)

    ax2.set_title("Coste total de plantilla\npor cargo")
    ax2.set_xlabel("Coste total (€)")

    plt.tight_layout()

    return guardar_grafico()

# CONCIERTOS

def grafico_ranking_cantantes(datos):
    """
    Barras apiladas con el número de conciertos y giras
    por cantante. Permite ver quién tiene más actividad.

    Parámetros:
        datos → resultado de ranking_cantantes_por_actividad()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("total_conciertos", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Barras apiladas: conciertos divididos por número de giras
    # para ver la proporción de conciertos por gira
    ax.barh(df["cantante"], df["total_conciertos"],
            label="Total conciertos", color="steelblue")
    ax.barh(df["cantante"], df["total_giras"],
            label="Total giras", color="orange", alpha=0.7)

    # Añadimos el número exacto al final de cada barra
    for i, (conciertos, giras) in enumerate(
            zip(df["total_conciertos"], df["total_giras"])):
        ax.text(conciertos + 0.2, i, str(conciertos),
                va="center", fontsize=9, color="steelblue")

    ax.set_title("Ranking de cantantes por actividad")
    ax.set_xlabel("Total")
    ax.legend()

    return guardar_grafico()


def grafico_distribucion_por_continente(datos):
    """
    Gráfico de tarta que muestra el porcentaje de conciertos
    por continente. Incluye número de cantantes y recintos.

    Parámetros:
        datos → resultado de distribucion_conciertos_por_continente()
    """

    df = pd.DataFrame(datos)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfico de tarta con el porcentaje por continente
    colores = ["steelblue", "orange", "green", "red", "purple"]
    ax1.pie(df["total_conciertos"], labels=df["continente"],
            autopct="%1.1f%%", colors=colores[:len(df)],
            startangle=90)
    ax1.set_title("Distribución de conciertos\npor continente")

    # Barras con cantantes y recintos distintos por continente
    x = range(len(df))
    ancho = 0.35
    ax2.bar([i - ancho/2 for i in x], df["cantantes_distintos"],
            width=ancho, label="Cantantes distintos", color="steelblue")
    ax2.bar([i + ancho/2 for i in x], df["recintos_distintos"],
            width=ancho, label="Recintos distintos", color="orange")

    ax2.set_title("Diversidad por continente")
    ax2.set_xlabel("Continente")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df["continente"], rotation=45, ha="right")
    ax2.legend()

    plt.tight_layout()

    return guardar_grafico()


def grafico_recintos_mas_demandados(datos):
    """
    Barras horizontales con los recintos que más conciertos
    acogen. El color diferencia dinámicamente por país.

    Parámetros:
        datos → resultado de recintos_mas_demandados()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("total_conciertos", ascending=True)

    # Asignamos un color distinto a cada país dinámicamente
    # para que todos los países tengan su propio color
    paises_unicos = df["pais"].unique()
    paleta = ["steelblue", "orange", "green", "red",
              "purple", "brown", "pink", "gray",
              "cyan", "magenta"]
    color_por_pais = {pais: paleta[i % len(paleta)]
                      for i, pais in enumerate(paises_unicos)}
    colores = [color_por_pais[pais] for pais in df["pais"]]

    fig, ax = plt.subplots(figsize=(12, 7))

    barras = ax.barh(df["recinto"], df["total_conciertos"], color=colores)

    # Número de conciertos y artistas al final de cada barra
    for barra, cantantes in zip(barras, df["cantantes_distintos"]):
        ax.text(barra.get_width() + 0.3,
                barra.get_y() + barra.get_height() / 2,
                f"{int(barra.get_width())} conciertos ({cantantes} artistas)",
                va="center", fontsize=8)

    ax.set_title("Top 10 recintos más demandados")
    ax.set_xlabel("Total conciertos")

    # Leyenda con todos los países presentes en el top 10
    leyenda = [Patch(color=color_por_pais[pais], label=pais)
               for pais in paises_unicos]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()


def grafico_ocupacion_por_cantante(datos):
    """
    Barras horizontales con el porcentaje medio de ocupación
    por cantante. Verde si supera el 80%, naranja si supera
    el 60%, rojo si está por debajo.

    Parámetros:
        datos → resultado de ocupacion_media_por_cantante()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("ocupacion_media", ascending=True)

    # Color según nivel de ocupación
    def color_ocupacion(valor):
        if valor >= 80:
            return "green"
        elif valor >= 60:
            return "orange"
        else:
            return "red"

    colores = [color_ocupacion(v) for v in df["ocupacion_media"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(df["cantante"], df["ocupacion_media"], color=colores)

    # Línea vertical en el 80% como referencia de "lleno"
    ax.axvline(x=80, color="green", linestyle="--",
               linewidth=1, label="80% ocupación (referencia)")

    # Añadimos el porcentaje exacto al final de cada barra
    for i, valor in enumerate(df["ocupacion_media"]):
        ax.text(valor + 0.5, i, f"{valor}%", va="center", fontsize=9)

    ax.set_title("Ocupación media de recintos por cantante")
    ax.set_xlabel("Ocupación media (%)")
    ax.set_xlim(0, 110)
    ax.legend()

    leyenda = [Patch(color="green", label="≥ 80% (excelente)"),
               Patch(color="orange", label="60-80% (bueno)"),
               Patch(color="red", label="< 60% (bajo)")]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()

def grafico_rentabilidad_giras(datos):
    """
    Barras horizontales con los conciertos medios por gira
    de cada cantante. El color es relativo a la media del
    dataset para que siempre haya distinción visual.

    Parámetros:
        datos → resultado de rentabilidad_por_gira()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("conciertos_por_gira", ascending=True)

    # Usamos colores relativos a la media del dataset
    # para que siempre haya distinción visual independientemente
    # de los valores absolutos
    media = df["conciertos_por_gira"].mean()

    def color_relativo(valor):
        if valor >= media * 1.2:
            return "green"
        elif valor >= media * 0.8:
            return "orange"
        else:
            return "red"

    colores = [color_relativo(v) for v in df["conciertos_por_gira"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.barh(df["cantante"], df["conciertos_por_gira"],
                     color=colores)

    # Media como línea de referencia vertical
    ax.axvline(x=media, color="black", linestyle="--",
               linewidth=1, label=f"Media ({media:.1f})")

    # Duración y canciones al final de cada barra
    for barra, duracion, canciones in zip(
            barras, df["duracion_media_gira"], df["canciones_media_gira"]):
        ax.text(barra.get_width() + 0.05,
                barra.get_y() + barra.get_height() / 2,
                f"{duracion:.0f} min | {canciones:.0f} canciones",
                va="center", fontsize=8)

    ax.set_title("Conciertos medios por gira por cantante\n"
                 "(mayor valor = gira más rentable)")
    ax.set_xlabel("Conciertos por gira")
    ax.legend()

    leyenda = [Patch(color="green",  label="Por encima de la media (+20%)"),
               Patch(color="orange", label="En torno a la media"),
               Patch(color="red",    label="Por debajo de la media (-20%)")]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()

# PELÍCULAS

def grafico_rentabilidad_peliculas(datos):
    """
    Gráfico de barras horizontales con el ratio de rentabilidad
    de cada película. El color indica si es rentable o no.
    Muestra solo el top 10 más rentable y el top 5 con pérdidas.

    Parámetros:
        datos → resultado de rentabilidad_peliculas()
    """

    df = pd.DataFrame(datos)

    # Top 10 más rentables y top 5 con peores pérdidas
    top_rentables = df.nlargest(10, "ratio_rentabilidad")
    peores        = df[df["ratio_rentabilidad"] < 1].nsmallest(5, "ratio_rentabilidad")
    df            = pd.concat([peores, top_rentables])
    df            = df.sort_values("ratio_rentabilidad", ascending=True)

    # Verde si rentable, rojo si pérdidas
    colores = ["green" if v >= 1 else "red" for v in df["ratio_rentabilidad"]]

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.4)))

    barras = ax.barh(df["titulo"], df["ratio_rentabilidad"], color=colores)

    # Línea vertical en 1.0 = punto de equilibrio (ni gana ni pierde)
    ax.axvline(x=1, color="black", linestyle="--",
               linewidth=1, label="Punto de equilibrio (ratio = 1)")

    # Valor exacto al final de cada barra
    for barra, valor in zip(barras, df["ratio_rentabilidad"]):
        ax.text(barra.get_width() + 0.05,
                barra.get_y() + barra.get_height() / 2,
                f"x{valor}", va="center", fontsize=9)

    ax.set_title("Rentabilidad de películas\n(recaudación / presupuesto)")
    ax.set_xlabel("Ratio de rentabilidad")
    ax.legend()

    leyenda = [Patch(color="green", label="Rentable (ratio ≥ 1)"),
               Patch(color="red",   label="Pérdidas (ratio < 1)")]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()


def grafico_generos_rentables(datos):
    """
    Gráfico de barras agrupadas con recaudación media y
    presupuesto medio por género, con segundo eje para
    el ratio de rentabilidad.

    Parámetros:
        datos → resultado de generos_mas_rentables()
    """

    df = pd.DataFrame(datos)
    df = df.sort_values("recaudacion_media", ascending=False)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    x = range(len(df))
    ancho = 0.35

    # Recaudación y presupuesto en el eje izquierdo
    ax1.bar([i - ancho/2 for i in x], df["recaudacion_media"],
            width=ancho, label="Recaudación media", color="steelblue", alpha=0.8)
    ax1.bar([i + ancho/2 for i in x], df["presupuesto_medio"],
            width=ancho, label="Presupuesto medio", color="orange", alpha=0.8)

    # Ratio de rentabilidad en el eje derecho como línea
    ax2.plot(list(x), df["ratio_rentabilidad"],
             marker="D", color="green", linewidth=2,
             markersize=8, label="Ratio rentabilidad", linestyle="--")

    # Línea de referencia en ratio = 1
    ax2.axhline(y=1, color="red", linestyle=":",
                linewidth=1, label="Punto de equilibrio")

    ax1.set_title("Géneros más rentables")
    ax1.set_xlabel("Género")
    ax1.set_ylabel("Importe (€)")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["genero"], rotation=45, ha="right")

    ax2.set_ylabel("Ratio rentabilidad", color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, etiquetas1 + etiquetas2, loc="upper right")

    return guardar_grafico()


def grafico_directores_taquilleros(datos):
    """
    Gráfico de barras horizontales con los directores ordenados
    por recaudación media. El tamaño del punto indica el número
    de películas dirigidas.

    Parámetros:
        datos → resultado de directores_mas_taquilleros()
    """

    df = pd.DataFrame(datos)

    # Top 10 directores más taquilleros
    df = df.head(10)
    df = df.sort_values("recaudacion_media", ascending=True)

    # Color según ratio de rentabilidad
    def color_ratio(ratio):
        if ratio >= 3:
            return "green"
        elif ratio >= 1.5:
            return "steelblue"
        elif ratio >= 1:
            return "orange"
        else:
            return "red"

    colores = [color_ratio(r) for r in df["ratio_rentabilidad"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.barh(df["director"], df["recaudacion_media"], color=colores)

    # Número de películas y ratio al final de cada barra
    for barra, peliculas, ratio in zip(
            barras, df["peliculas_dirigidas"], df["ratio_rentabilidad"]):
        ax.text(barra.get_width() + 0.5,
                barra.get_y() + barra.get_height() / 2,
                f"{peliculas} películas | x{ratio}",
                va="center", fontsize=8)

    ax.set_title("Top 10 directores por recaudación media")
    ax.set_xlabel("Recaudación media (€)")

    leyenda = [Patch(color="green",     label="Ratio ≥ 3 (muy rentable)"),
               Patch(color="steelblue", label="Ratio 1.5-3 (rentable)"),
               Patch(color="orange",    label="Ratio 1-1.5 (rentabilidad baja)"),
               Patch(color="red",       label="Ratio < 1 (pérdidas)")]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()

def grafico_peliculas_mayor_perdida(datos):
    """
    Barras horizontales con las películas que más dinero
    han perdido en términos absolutos.

    Parámetros:
        datos → resultado de peliculas_mayor_perdida()
    """

    df = pd.DataFrame(datos)

    # Si no hay películas con pérdidas mostramos mensaje
    if df.empty or "perdida" not in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No hay películas con pérdidas en los datos",
                ha="center", va="center", fontsize=14, color="gray")
        ax.axis("off")
        return guardar_grafico()

    # Los datos ya vienen filtrados desde estadisticas.py
    # solo ordenamos y cogemos el top 10
    df = df.sort_values("perdida", ascending=True).head(10)

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.5)))

    barras = ax.barh(df["titulo"], df["perdida"],
                     color="red", alpha=0.8)

    for barra, recuperacion in zip(barras, df["recuperacion_pct"]):
        ax.text(barra.get_width() - abs(barra.get_width()) * 0.05,
                barra.get_y() + barra.get_height() / 2,
                f"Recuperó {recuperacion}%",
                va="center", ha="right", fontsize=8, color="white")

    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.set_title("Top 10 películas con mayor pérdida económica")
    ax.set_xlabel("Pérdida (€)")

    return guardar_grafico()


def grafico_impacto_actores(datos):
    """
    Barras horizontales con los actores ordenados por
    recaudación media de sus películas. El color indica
    su ratio de rentabilidad.

    Parámetros:
        datos → resultado de impacto_actores_en_recaudacion()
    """

    df = pd.DataFrame(datos)

    # Top 10 actores con mayor recaudación media
    df = df.head(10)
    df = df.sort_values("recaudacion_media", ascending=True)

    def color_ratio(ratio):
        if ratio >= 3:
            return "green"
        elif ratio >= 1.5:
            return "steelblue"
        elif ratio >= 1:
            return "orange"
        else:
            return "red"

    colores = [color_ratio(r) for r in df["ratio_rentabilidad"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    barras = ax.barh(df["actor"], df["recaudacion_media"], color=colores)

    # Número de películas y ratio al final de cada barra
    for barra, peliculas, ratio in zip(
            barras, df["total_peliculas"], df["ratio_rentabilidad"]):
        ax.text(barra.get_width() + 0.5,
                barra.get_y() + barra.get_height() / 2,
                f"{peliculas} películas | x{ratio}",
                va="center", fontsize=8)

    ax.set_title("Top 10 actores por recaudación media\n"
                 "(mínimo 2 películas)")
    ax.set_xlabel("Recaudación media (€)")

    leyenda = [Patch(color="green",     label="Ratio ≥ 3 (muy rentable)"),
               Patch(color="steelblue", label="Ratio 1.5-3 (rentable)"),
               Patch(color="orange",    label="Ratio 1-1.5 (rentabilidad baja)"),
               Patch(color="red",       label="Ratio < 1 (pérdidas)")]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()

