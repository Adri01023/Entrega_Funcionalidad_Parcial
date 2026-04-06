from sqlalchemy import create_engine

from graficas import grafico_rendimiento_posicion

engine = create_engine("sqlite:///baseDatos.db")

from estadisticas import rendimiento_vs_media_posicion
resultado = rendimiento_vs_media_posicion()
print(resultado)

# Generamos el gráfico pasándole el resultado de la estadística
imagen = grafico_rendimiento_posicion(resultado)

# Guardamos los bytes en un fichero PNG para poder verlo
with open("grafico_rendimiento_posicion.png", "wb") as f:
    f.write(imagen)

print("Gráfico guardado como prueba_grafico.png")

# Empleados

from estadisticas import (
    distribucion_salarial_por_cargo,
    ranking_salarial,
    comparativa_salario_real_vs_base
)

from graficas import (
    grafico_distribucion_salarial,
    grafico_ranking_salarios,
    grafico_comparativa_vs_base
)

print("\n--- Distribución salarial por cargo ---")
datos_distribucion = distribucion_salarial_por_cargo()
for cargo in datos_distribucion:
    print(cargo)

imagen = grafico_distribucion_salarial(datos_distribucion)
with open("grafico_distribucion.png", "wb") as f:
    f.write(imagen)
print("Gráfico guardado como grafico_distribucion.png")


print("\n--- Ranking salarial por cargo ---")
datos_rankinkg = ranking_salarial()
for cargo in datos_rankinkg:
    print(cargo)

imagen = grafico_ranking_salarios(datos_rankinkg)
with open("grafico_ranking.png", "wb") as f:
    f.write(imagen)
print("Gráfico guardado como grafico_ranking.png")

print("\n--- Comparativa salario real vs base ---")
datos_comparativa = comparativa_salario_real_vs_base()
for empleado in datos_comparativa:
    print(empleado)

imagen = grafico_comparativa_vs_base(datos_comparativa)
with open("grafico_comparativa.png", "wb") as f:
    f.write(imagen)
print("Gráfico guardado como grafico_comparativa.png")