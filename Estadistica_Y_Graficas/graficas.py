# procesamiento/graficos.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io

# Usamos un backend sin interfaz gráfica porque las imágenes
# se generan en memoria y se devuelven como respuesta HTTP,
# no se muestran en pantalla
matplotlib.use("Agg")


def guardar_grafico() -> bytes:
    """
    Guarda el gráfico actual de matplotlib en memoria
    y lo devuelve como bytes para enviarlo por la API.
    Función interna, no la llama Diego directamente.
    """

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    # liberamos memoria cerrando la figura
    plt.close()
    # volvemos al inicio del buffer para poder leerlo
    buffer.seek(0)
    return buffer.read()


# Parte futbol
def grafico_rendimiento_posicion(datos):
    """
    Gráfico de barras agrupadas que muestra los goles
    y asistencias medias por posición.

    Parámetros:
        datos → resultado de rendimiento_vs_media_posicion()
    """

    df = pd.DataFrame(datos)

    # Calculamos la media por posición para el gráfico
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


def grafico_progresion_jugador(datos):
    """
    Gráfico de líneas que muestra la evolución de goles
    y asistencias de un jugador temporada a temporada.

    Parámetros:
        datos → resultado de progresion_jugador()
    """

    df = pd.DataFrame(datos["temporadas"])

    # Etiqueta para el eje X: "2020/2021", "2021/2022"...
    df["temporada"] = df["anio_inicio"].astype(str) + "/" + df["anio_fin"].astype(str)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df["temporada"], df["goles"],
            marker="o", label="Goles", color="steelblue")
    ax.plot(df["temporada"], df["asistencias"],
            marker="o", label="Asistencias", color="orange")

    ax.set_title(f"Progresión del jugador {datos['id_jugador']}")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("Cantidad")
    ax.legend()
    plt.xticks(rotation=45, ha="right")

    return guardar_grafico()


# Parte Empleados

def grafico_distribucion_salarial(datos):
    """
    Gráfico de barras para media y mediana por cargo.
    La desviación típica usa un segundo eje Y propio porque
    sus valores son mucho más pequeños que los salarios y
    en el mismo eje quedaría aplastada y sin poder apreciarse.

    Parámetros:
        datos → resultado de distribucion_salarial_por_cargo()
    """

    df = pd.DataFrame(datos)

    # fig y dos ejes: ax1 para salarios, ax2 para desviación típica
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # twinx() crea un segundo eje Y que comparte el mismo eje X
    ax2 = ax1.twinx()

    x = range(len(df))
    ancho = 0.3

    # Media y mediana en el eje izquierdo (ax1)
    ax1.bar([i - ancho/2 for i in x], df["media"],
            width=ancho, label="Media", color="steelblue", alpha=0.8)
    ax1.bar([i + ancho/2 for i in x], df["mediana"],
            width=ancho, label="Mediana", color="orange", alpha=0.8)

    # Desviación típica en el eje derecho (ax2)
    # plot() en lugar de bar() para diferenciarla visualmente
    ax2.plot(list(x), df["desviacion_tipica"],
             marker="D", color="green", linewidth=2,
             markersize=8, label="Desviación típica", linestyle="--")

    # Configuramos el eje izquierdo
    ax1.set_title("Distribución salarial por cargo")
    ax1.set_xlabel("Cargo")
    ax1.set_ylabel("Salario (€)", color="black")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["nombre_cargo"], rotation=45, ha="right")

    # Configuramos el eje derecho
    ax2.set_ylabel("Desviación típica (€)", color="green")
    ax2.tick_params(axis="y", labelcolor="green")

    # Combinamos las leyendas de ambos ejes en una sola
    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1 + lineas2, etiquetas1 + etiquetas2, loc="upper left")

    return guardar_grafico()


def grafico_ranking_salarios(datos: list) -> bytes:
    """
    Gráfico de barras horizontales que muestra todos los empleados
    ordenados de mayor a menor salario real, con colores por cargo.
    Permite ver de un vistazo quién cobra más y en qué cargo está.

    Parámetros:
        datos → resultado de comparativa_salario_real_vs_base()
    """

    df = pd.DataFrame(datos)

    # Ordenamos de mayor a menor salario real
    df = df.sort_values("salario_real_medio", ascending=True)

    # Asignamos un color distinto a cada cargo automáticamente
    # Para que cada cargo tenga siempre el mismo color en el gráfico
    cargos_unicos = df["nombre_cargo"].unique()
    paleta = ["steelblue", "orange", "green", "red", "purple"]
    color_por_cargo = {cargo: paleta[i % len(paleta)]
                       for i, cargo in enumerate(cargos_unicos)}
    colores = [color_por_cargo[cargo] for cargo in df["nombre_cargo"]]

    # El tamaño del gráfico se adapta al número de empleados
    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.4)))

    ax.barh(df["nombre"] + " " + df["apellido"],
            df["salario_real_medio"], color=colores)

    ax.set_title("Ranking salarial de empleados por cargo")
    ax.set_xlabel("Salario real medio (€)")

    # Creamos la leyenda manualmente para que aparezca un color por cargo
    from matplotlib.patches import Patch
    leyenda = [Patch(color=color_por_cargo[cargo], label=cargo)
               for cargo in cargos_unicos]
    ax.legend(handles=leyenda, loc="lower right")

    return guardar_grafico()

def grafico_comparativa_vs_base(datos: list) -> bytes:
    """
    Gráfico de barras horizontales que muestra la diferencia
    porcentual entre el salario real y el salario base.
    Verde = cobra más, rojo = cobra menos.

    Para que sea legible con datasets grandes, mostramos solo
    los 10 empleados que más se alejan del salario base de su
    cargo, que son los más interesantes de analizar.

    Parámetros:
        datos → resultado de comparativa_salario_real_vs_base()
    """

    df = pd.DataFrame(datos)

    # Ordenamos por valor absoluto
    df["diferencia_abs"] = df["diferencia_%"].abs()
    df = df.sort_values("diferencia_abs", ascending=False)

    # Nos quedamos solo con los 10 más extremos
    df = df.head(10)

    # Volvemos a ordenar por diferencia real para que el gráfico
    # quede con los negativos abajo y los positivos arriba
    df = df.sort_values("diferencia_%", ascending=True)

    colores = ["green" if v >= 0 else "red" for v in df["diferencia_%"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(df["nombre"] + " " + df["apellido"],
            df["diferencia_%"], color=colores)

    # Línea vertical en 0 para ver quién está por encima y por debajo
    ax.axvline(x=0, color="black", linewidth=0.8)

    ax.set_title("Top 10 empleados con mayor diferencia\nsalario real vs salario base del cargo")
    ax.set_xlabel("Diferencia (%)")

    return guardar_grafico()