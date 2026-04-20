import pandas as pd
import io


def importar_csv(contenido: bytes) -> pd.DataFrame:
    """
    Recibe el contenido de un fichero CSV
    y devuelve el respectivo DataFrame.
    """
    return pd.read_csv(io.BytesIO(contenido))


def importar_excel(contenido: bytes) -> pd.DataFrame:
    """
    Recibe el contenido de un fichero Excel (.xlsx o .xls)
    y devuelve el respectivo DataFrame.
    """
    return pd.read_excel(io.BytesIO(contenido))


def importar_json(contenido: bytes) -> pd.DataFrame:
    """
    Recibe el contenido de un fichero JSON
    y devuelve un DataFrame de pandas.
    """
    return pd.read_json(io.BytesIO(contenido))


def importar_fichero(nombre: str, contenido: bytes) -> pd.DataFrame:
    """
    Función principal que detecta automáticamente el tipo de fichero
    por su extensión y llama a la función correspondiente.

    Esta es la función que Diego llamará desde su endpoint.

    Parámetros:
        nombre    → nombre del fichero (ej: "ventas.csv")
        contenido → contenido binario del fichero

    Devuelve:
        DataFrame con los datos del fichero

    Lanza:
        ValueError si el formato no está soportado
    """
    nombre = nombre.lower()

    if nombre.endswith(".csv"):
        return importar_csv(contenido)

    elif nombre.endswith(".xlsx") or nombre.endswith(".xls"):
        return importar_excel(contenido)

    elif nombre.endswith(".json"):
        return importar_json(contenido)

    else:
        raise ValueError(
            f"Formato no soportado: '{nombre}'. Usa CSV, Excel o JSON."
        )