# Entrega de Funcionalidad Parcial

Parte Estadística y Gráficas:

Estructura:
  
  estadisticas.py -> contiene las formulas estadísticas aplicadas a los datos
  
  graficas.py -> contiene el código para la creación de diversos gráficos.
  
  main.py -> aplica dichas formulas estadísticas a los datos contenidos en la base de datos baseDatos.db (debe estar en el mismo directorio al ejecutarse este archivo además genera los reespectivos gráficos en formato png


Parte de Dashboard (frontend):

Estructura:

/graphs -> Contiene como imágenes algunos placeholders creados por nuestra apliación para ser empleados en nuestro frontend de forma temporal.

/icons -> Contiene los iconos empleados en nuestra página como imágenes vectoriales.

dashboard.html -> Archivo principal html que contiene nuestra página.

dashboard.css -> Hoja de estilos empleada por nuestro html principal.

Se emplean imágenes como gráficos como placeholder al depender la integración de APIs REST pendientes de ser completamente implementadas.

Base de datos:

  creacionBaseDaatos.py -> crea una sola base de datos con las tablas relacionadas de conciertos, cine, empresa y futbol y las rellena con unos cuantos datos de cada uno 
