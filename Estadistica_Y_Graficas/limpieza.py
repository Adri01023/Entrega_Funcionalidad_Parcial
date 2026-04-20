import pandas as pd


def eliminar_filas_vacias(df):
    """
    Elimina las filas donde TODAS las columnas están vacías.
    """
    return df.dropna(how="all")


def eliminar_duplicados(df):
    """
    Elimina filas completamente duplicadas.
    """
    return df.drop_duplicates()


def limpiar_nombres_columnas(df):
    """
    Elimina espacios en blanco al inicio y al final
    de los nombres de las columnas.
    Ej: "  ventas " → "ventas"
    """
    df.columns = df.columns.str.strip()
    return df


def limpiar_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Función principal que aplica toda la limpieza en orden
    y devuelve el DataFrame limpio junto con un informe
    de los cambios realizados.

    Esta es la función que Diego llamará desde su endpoint.

    Devuelve:
        df_limpio → DataFrame ya limpiado
        informe   → diccionario con resumen de cambios
    """
    filas_antes = len(df)

    df = limpiar_nombres_columnas(df)
    df = eliminar_filas_vacias(df)
    df = eliminar_duplicados(df)

    filas_despues = len(df)

    # Informe con los cambios realizados
    informe = {
        "filas_originales": filas_antes,
        "filas_eliminadas": filas_antes - filas_despues,
        "filas_resultantes": filas_despues,
        "columnas": list(df.columns)
    }

    return df, informe