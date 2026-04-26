import { useEffect, useState } from "react";
import "./App.css";
import "./dashboard.css";
import * as XLSX from "xlsx";

// Pendiente mover a otros modulos e importar componentes. Crear hooks
// https://www.w3schools.com/react/react_hooks.asp
// https://legacy.reactjs.org/docs/hooks-custom.html

//Dirección de nuestro endpoint que nos permite la conexión entre frontend y backend
const BASE_URL = "http://127.0.0.1:8000";

// http://localhost:8000/empleados/distribucion/grafico

/*
// Array que contiene los graficos de prueba con sus url correspondientes
const graficos = [
  // Fútbol
  {
    nombre: "Rendimiento vs Media Posición",
    url: "/futbol/rendimiento/grafico",
  },
  { nombre: "Ranking Goleadores", url: "/futbol/goleadores/grafico" },
  { nombre: "Estadísticas por Equipo", url: "/futbol/equipos/grafico" },
  { nombre: "Eficiencia Goleadora", url: "/futbol/eficiencia/grafico" },

  // Empleados
  {
    nombre: "Distribución Salarial por Cargo",
    url: "/empleados/distribucion/grafico",
  },
  { nombre: "Ranking Salarial", url: "/empleados/ranking-salarial/grafico" },
  {
    nombre: "Comparativa Salario Real vs Base",
    url: "/empleados/comparativa-base/grafico",
  },
  {
    nombre: "Antigüedad Media por Cargo",
    url: "/empleados/antiguedad/grafico",
  },
  {
    nombre: "Estructura de Plantilla",
    url: "/empleados/estructura-plantilla/grafico",
  },

  // Conciertos
  {
    nombre: "Ranking Cantantes por Actividad",
    url: "/conciertos/actividad/grafico",
  },
  {
    nombre: "Distribución de Conciertos por Continente",
    url: "/conciertos/continentes/grafico",
  },
  {
    nombre: "Recintos Más Demandados",
    url: "/conciertos/recintos-top/grafico",
  },
  {
    nombre: "Ocupación Media por Cantante",
    url: "/conciertos/ocupacion/grafico",
  },
  {
    nombre: "Rentabilidad por Gira",
    url: "/conciertos/rentabilidad-giras/grafico",
  },

  // Películas
  { nombre: "Rentabilidad Películas", url: "/peliculas/rentabilidad/grafico" },
  { nombre: "Géneros Más Rentables", url: "/peliculas/generos/grafico" },
  {
    nombre: "Directores Más Taquilleros",
    url: "/peliculas/directores/grafico",
  },
  { nombre: "Películas con Mayor Pérdida", url: "/peliculas/perdidas/grafico" },
  {
    nombre: "Impacto Actores en Recaudación",
    url: "/peliculas/impacto-actores/grafico",
  },
];
*/

// Datasets que contienen todos los gráficos
const datasets = [
  {
    id: "futbol",
    nombre: "Fútbol",
    graficos: [
      {
        nombre: "Rendimiento vs Media Posición",
        url: "/futbol/rendimiento/grafico",
      },
      { nombre: "Ranking Goleadores", url: "/futbol/goleadores/grafico" },
      { nombre: "Estadísticas por Equipo", url: "/futbol/equipos/grafico" },
      { nombre: "Eficiencia Goleadora", url: "/futbol/eficiencia/grafico" },
    ],
  },
  {
    id: "empleados",
    nombre: "Empleados",
    graficos: [
      {
        nombre: "Distribución Salarial por Cargo",
        url: "/empleados/distribucion/grafico",
      },
      {
        nombre: "Ranking Salarial",
        url: "/empleados/ranking-salarial/grafico",
      },
      {
        nombre: "Comparativa Salario Real vs Base",
        url: "/empleados/comparativa-base/grafico",
      },
      {
        nombre: "Antigüedad Media por Cargo",
        url: "/empleados/antiguedad/grafico",
      },
      {
        nombre: "Estructura de Plantilla",
        url: "/empleados/estructura-plantilla/grafico",
      },
    ],
  },
  {
    id: "conciertos",
    nombre: "Conciertos",
    graficos: [
      {
        nombre: "Ranking Cantantes por Actividad",
        url: "/conciertos/actividad/grafico",
      },
      {
        nombre: "Distribución de Conciertos por Continente",
        url: "/conciertos/continentes/grafico",
      },
      {
        nombre: "Recintos Más Demandados",
        url: "/conciertos/recintos-top/grafico",
      },
      {
        nombre: "Ocupación Media por Cantante",
        url: "/conciertos/ocupacion/grafico",
      },
      {
        nombre: "Rentabilidad por Gira",
        url: "/conciertos/rentabilidad-giras/grafico",
      },
    ],
  },
  {
    id: "cine",
    nombre: "Cine",
    graficos: [
      {
        nombre: "Rentabilidad Películas",
        url: "/peliculas/rentabilidad/grafico",
      },
      { nombre: "Géneros Más Rentables", url: "/peliculas/generos/grafico" },
      {
        nombre: "Directores Más Taquilleros",
        url: "/peliculas/directores/grafico",
      },
      {
        nombre: "Películas con Mayor Pérdida",
        url: "/peliculas/perdidas/grafico",
      },
      {
        nombre: "Impacto Actores en Recaudación",
        url: "/peliculas/impacto-actores/grafico",
      },
    ],
  },
];

//Estructura de dato que alberga el tipo de objeto a almacenar en el historial
type HistorialItem =
  | {
      type: "grafica";
      url: string;
      nombre: string;
      hora: string;
      count: number;
    }
  | {
      type: "Fichero";
      nombre: string;
      hora: string;
      lineas: number;
      columnas: string[];
      numColumnas: number;
      extension: string;
    };

//Función por defecto para que funcione la app en react
function App() {
  // Constantes y UseStates de las gráficas y de las tablas/dataset a los que pertenece
  const [datasetActivo, setDatasetActivo] = useState(datasets[0].id);
  const [graficosActivos, setGraficosActivos] = useState<string[]>([]);
  const datasetSeleccionado = datasets.find((d) => d.id === datasetActivo);
  const [graficoExpandido, setGraficoExpandido] = useState<string | null>(null);
  const [mostrarChecks, setMostrarChecks] = useState(true);

  // Constantes de usuarios
  const [usuario, setUsuario] = useState<any | null>(() => {
    const saved = localStorage.getItem("usuario");
    return saved ? JSON.parse(saved) : null;
  });
  //const [modoAuth, setModoAuth] = useState<"login" | "register" | null>(null);
  const [nuevoUsuario, setNuevoUsuario] = useState("");
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [mensajeUsuario, setMensajeUsuario] = useState("");
  //const [mostrarCrearUsuario, setMostrarCrearUsuario] = useState(false);
  const [mostrarLogin, setMostrarLogin] = useState(false);
  const [hayAdmin, setHayAdmin] = useState<boolean | null>(null);
  const adminId = usuario?.id_admin || null;
  const esAdmin = usuario?.es_admin === true;

  //Datasets para mostrar en la sección de gráficas
  const [datasetsDisponibles, setDatasetsDisponibles] = useState<
    Record<string, boolean>
  >({});

  //UseStates para mostar un mensaje al subir un fichero
  const [mensajeUpload, setMensajeUpload] = useState<string>("");
  const [tipoMensajeUpload, setTipoMensajeUpload] = useState<
    "ok" | "error" | ""
  >("");

  //Se cargan los datasets disponibles para mostrar en las gráficas
  /*
  useEffect(() => {
    if (!usuario) return;

    fetch(`${BASE_URL}/datasets-disponibles?id_admin=${usuario.id_admin}`)
      .then((res) => res.json())
      .then((data) => {
        setDatasetsDisponibles(data);

        const primeroDisponible = datasets.find((d) => data[d.id]);

        if (primeroDisponible) {
          setDatasetActivo(primeroDisponible.id);
        }

        setGraficosActivos([]);
      })
      .catch(() => setDatasetsDisponibles({}));
  }, [usuario]);
  */

  const cargarDatasets = async () => {
    if (!usuario) return;

    try {
      const res = await fetch(
        `${BASE_URL}/datasets-disponibles?id_admin=${usuario.id_admin}`,
      );
      const data = await res.json();

      setDatasetsDisponibles(data);

      const primeroDisponible = datasets.find((d) => data[d.id]);

      if (primeroDisponible) {
        setDatasetActivo(primeroDisponible.id);
      }

      setGraficosActivos([]);
    } catch {
      setDatasetsDisponibles({});
    }
  };

  useEffect(() => {
    cargarDatasets();
  }, [usuario]);

  //UseEffect para ocultar el mensaje pasado X ms
  useEffect(() => {
    if (!mensajeUpload) return;

    const timeout = setTimeout(() => {
      setMensajeUpload("");
      setTipoMensajeUpload("");
    }, 4000);

    return () => clearTimeout(timeout);
  }, [mensajeUpload]);

  const getAdminId = () => {
    if (!usuario) return null;

    // Si es admin, usa su propio id
    if (usuario.es_admin) return usuario.id_admin;

    // Si es usuario normal, usa el id_admin asignado
    return usuario.id_admin;
  };

  useEffect(() => {
    if (!usuario) {
      // logout
      setDatasetsDisponibles({});
      setGraficosActivos([]);
      setDatasetActivo(datasets[0].id);
      return;
    }

    // login
    setGraficosActivos([]);
    setGraficoExpandido(null);
  }, [usuario]);

  //check si admin
  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await fetch(`${BASE_URL}/usuarios/hay-admin`);
        const data = await res.json();
        setHayAdmin(data.hay_admin);
      } catch {
        setHayAdmin(true); // fallback seguro
      }
    };

    checkAdmin();
  }, []);

  /*
  const crearUsuario = async () => {
    if (!usuario) {
      setMensajeUsuario("Debes iniciar sesión");
      return;
    }

    if (!esAdmin) {
      setMensajeUsuario("Solo los administradores pueden crear usuarios");
      return;
    }

    if (!nuevoUsuario || !nuevaPassword) {
      setMensajeUsuario("Completa todos los campos");
      return;
    }

    try {
      const check = await fetch(`${BASE_URL}/usuarios/hay-admin`);
      const checkData = await check.json();

      if (!checkData.hay_admin) {
        setMensajeUsuario(
          "No existe ningún administrador. Debes crear el primero desde el login",
        );
        return;
      }

      const response = await fetch(`${BASE_URL}/usuarios/crear-usuario`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: nuevoUsuario,
          password: nuevaPassword,
          id_admin: usuario.id_admin,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error creando usuario");
      }

      setMensajeUsuario("Usuario creado correctamente");
      setNuevoUsuario("");
      setNuevaPassword("");
    } catch (error: any) {
      setMensajeUsuario(error.message);
    }
  };
*/

  // crear nuevo usuario para admin
  const admin_crearUsuario = async () => {
    if (!usuario || !esAdmin) {
      setMensajeUsuario("No tienes permisos");
      return;
    }

    if (!nuevoUsuario || !nuevaPassword) {
      setMensajeUsuario("Completa todos los campos");
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/usuarios/crear-usuario`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: nuevoUsuario,
          password: nuevaPassword,
          id_admin: usuario.id_admin,
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail);

      setMensajeUsuario("Usuario creado correctamente");
      setNuevoUsuario("");
      setNuevaPassword("");
    } catch (err: any) {
      setMensajeUsuario(err.message);
    }
  };

  const crearPrimerAdmin = async () => {
    if (!nuevoUsuario || !nuevaPassword) {
      setMensajeUsuario("Completa todos los campos");
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/usuarios/crear-admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: nuevoUsuario,
          password: nuevaPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail);

      setMensajeUsuario("Primer admin creado correctamente");
      setHayAdmin(true);
    } catch (err: any) {
      setMensajeUsuario(err.message);
    }
  };

  const crearAdmin = async () => {
    if (!usuario || !esAdmin) {
      setMensajeUsuario("No tienes permisos para crear administradores");
      return;
    }

    if (!nuevoUsuario || !nuevaPassword) {
      setMensajeUsuario("Completa todos los campos");
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/usuarios/crear-admin-secure`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: nuevoUsuario,
          password: nuevaPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail);

      setMensajeUsuario("Admin creado correctamente");
      setNuevoUsuario("");
      setNuevaPassword("");
    } catch (err: any) {
      setMensajeUsuario(err.message);
    }
  };

  useEffect(() => {
    if (usuario) {
      localStorage.setItem("usuario", JSON.stringify(usuario));
    } else {
      localStorage.removeItem("usuario");
    }
  }, [usuario]);

  //Funciones de login
  //Login de pruebas
  // Función que realiza el login contra el backend
  // Envía usuario y contraseña,
  // guarda la sesión en estado y el localStorage para persistencia local
  const login = async () => {
    // Petición POST al endpoint de autenticación
    try {
      const res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // Se envían credenciales en el body
        body: JSON.stringify({
          username: nuevoUsuario,
          password: nuevaPassword,
        }),
      });

      const data = await res.json();

      // Si hay error en backend, se lanza excepción
      if (!res.ok) throw new Error(data.detail);

      //Guardamos los datos de usuario en el estado global para ser reutilizado
      setUsuario(data);
      setMostrarLogin(false);

      //Reset del formulario de login
      setNuevoUsuario("");
      setNuevaPassword("");
      setMensajeUsuario("");
      setHistorial([]);
      setGraficosActivos([]);
      setGraficoExpandido(null);

      setMostrarLogin(false); //quitamos boton de login
    } catch (err: any) {
      setMensajeUsuario(err.message); //Mostramos error en el login
    }
  };

  // Cierra la sesión del usuario actual
  // Limpia todos los estados relacionados con usuario y graficas/historial
  const logout = () => {
    setUsuario(null); //usuario to null -> Volver a Iniciar Sesion
    setNuevoUsuario("");
    setNuevaPassword("");
    setMensajeUsuario("");
    setHistorial([]);
    setGraficosActivos([]);
    setGraficoExpandido(null);
    setDatasetsDisponibles({});
  };

  //Si se presiona ESC -> Cerrar login
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMostrarLogin(false);
      }
    };

    window.addEventListener("keydown", handleEsc); //Añadimos evento

    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  /*  
  useEffect(() => {
    setAdminId(1);
  }, []);
  */

  // Setea por defecto la sección dashboard (Inicio)
  const [seccion, setSeccion] = useState("dashboard");
  // Seteamos el modo noche por defecto
  const [modo, setModo] = useState("noche");
  // Se guarda el archivo csv que sube el usuario, inicializado a null
  const [archivo, setArchivo] = useState<File | null>(null);

  /* useState con persistencia del historial */
  const [historial, setHistorial] = useState<HistorialItem[]>(() => {
    if (!usuario) return [];

    const key = usuario.es_admin
      ? `historial_admin_${usuario.id_admin}`
      : `historial_user_${usuario.id_user}`;

    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : [];
  });

  //Al cambiar de usuario se fuerza el reset
  useEffect(() => {
    setHistorial([]);

    if (!usuario) return;

    const key = usuario.es_admin
      ? `historial_admin_${usuario.id_admin}`
      : `historial_user_${usuario.id_user}`;

    const saved = localStorage.getItem(key);
    setHistorial(saved ? JSON.parse(saved) : []);
  }, [usuario]);

  // Bool para luego ocultar los botones de la gráfica en caso de no haber datos disponibles
  const hayDatosDisponibles = Object.values(datasetsDisponibles).some(Boolean);

  // Última gráfica consultada que solo puede ser de tipo grafica o null
  const [ultimaGrafica, setUltimaGrafica] = useState<Extract<
    HistorialItem,
    { type: "grafica" }
  > | null>(null);

  const getTipoArchivo = (ext: string) => {
    if (ext === "json") return "JSON";
    if (ext === "xls" || ext === "xlsx") return "EXCEL";
    return "CSV";
  };

  //Use effect cuando cambie el historial
  useEffect(() => {
    // Filtra solo los elementos de tipo "grafica"
    const graficasHistorial = historial.filter(
      (item): item is Extract<HistorialItem, { type: "grafica" }> =>
        item.type === "grafica",
    );

    if (graficasHistorial.length > 0) {
      const ultima = [...graficasHistorial].sort(
        (a, b) => new Date(b.hora).getTime() - new Date(a.hora).getTime(),
      )[0];

      setUltimaGrafica(ultima || null);
    } else {
      setUltimaGrafica(null);
    }
  }, [historial]);

  /* Evento que maneja el cambio de modo de los estilos entre modo día y noche */
  useEffect(() => {
    document.body.setAttribute("data-mode", modo);
  }, [modo]);

  /* Persistencia automática en localStorage */
  useEffect(() => {
    if (!usuario) return;

    const key = usuario.es_admin
      ? `historial_admin_${usuario.id_admin}`
      : `historial_user_${usuario.id_user}`;

    localStorage.setItem(key, JSON.stringify(historial));
  }, [historial, usuario]);

  /*
  //Vaciamos el historial al usuario ser null, si no retrievamos de local
  useEffect(() => {
    if (!usuario) {
      setHistorial([]);
      return;
    }
    const saved = localStorage.getItem(`historial_${usuario.id_admin}`);
    setHistorial(saved ? JSON.parse(saved) : []);
  }, [usuario]);
*/

  //Al loggear o cerrar session volvemos a inicio y cleareamos la pantalla
  useEffect(() => {
    if (usuario) {
      // LOGIN
      setSeccion("dashboard");
      setGraficosActivos([]);
      setGraficoExpandido(null);
    } else {
      // LOGOUT
      setSeccion("dashboard");
      setGraficosActivos([]);
      setGraficoExpandido(null);
    }
  }, [usuario]);

  //Devolvemos el primer grafico en el historial para mostrar la ultima grafica consultada
  // y limpiamos gráficas seleccionadas
  useEffect(() => {
    if (!usuario) return;
    // reset dataset al primero disponible
    setDatasetActivo(datasets[0].id);
    setGraficosActivos([]);
  }, [usuario]);

  /* Registrar gráfica en el historial */
  /*
  const registrarGrafica = (url: string) => {
    // Busca el gráfico en la lista de gráficos disponibles
    const grafica = graficos.find((g) => g.url === url);
    if (!grafica) return; //condicion de salida si grafica vacia

    const hora = new Date().toLocaleString(); //guardamos como string la fecha

    // Prev estado previo del historial
    setHistorial((prev) => {
      // Se busca si existe en el historial la gráfica con la misma url
      const existe = prev.find((h) => h.type === "grafica" && h.url === url);

      //Si existe se aumenta el contador
      if (existe && existe.type === "grafica") {
        return prev.map((h) =>
          //Operador ternario, si condicion falsa se devuelve el mismo objeto,
          // Si condicion verdadera, se devuelve el mismo objeto actualizando fecha y total+1
          h.type === "grafica" && h.url === url
            ? { ...h, count: h.count + 1, hora }
            : h,
        );
      }

      //En caso de no existir se devuelve un nuevo objeto al historial
      return [
        ...prev,
        {
          type: "grafica",
          url,
          nombre: grafica.nombre,
          hora,
          count: 1,
        },
      ];
    });
  };
*/

  /* Registrar gráfica en el historial */
  // Guarda la grafica consultada en el historial local y de la BBDD
  const registrarGrafica = async (url: string) => {
    //Obtenemos datos de la grafica
    const grafica = datasets
      .flatMap((d) => d.graficos) //obtenemos todas las graficas de datasets
      .find((g) => g.url === url); //devuelve el elemento que coincida en url

    //Condicion de salida si gráfica/user -> null
    if (!grafica || !usuario) return;

    const hora = new Date().toISOString(); //guardamos fecha en formato ISO

    //Persistencia backend
    await fetch(`${BASE_URL}/historial`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_consultor: usuario.es_admin ? usuario.id_admin : usuario.id_user,
        tipo_consultor: usuario.es_admin ? "admin" : "user",
        consulta: {
          type: "grafica",
          nombre: grafica.nombre,
          url: url,
        },
      }),
    });

    //Persistencia local
    setHistorial((prev) => {
      const existe = prev.find((h) => h.type === "grafica" && h.url === url);

      if (existe && existe.type === "grafica") {
        return prev.map((h) =>
          h.type === "grafica" && h.url === url
            ? { ...h, count: h.count + 1, hora }
            : h,
        );
      }

      //Si no existe se crea un nuevo elemento con contador 1
      return [
        ...prev,
        {
          type: "grafica",
          url,
          nombre: grafica.nombre,
          hora,
          count: 1,
        },
      ];
    });
  };

  // Carga historial desde backend al iniciar sesión
  // (se sobrescribe el local para mantener consistencia)
  useEffect(() => {
    if (!usuario) return;

    setHistorial([]);

    fetch(
      `${BASE_URL}/historial?id_consultor=${
        usuario.es_admin ? usuario.id_admin : usuario.id_user
      }&tipo_consultor=${usuario.es_admin ? "admin" : "user"}`,
    )
      .then((res) => res.json())
      .then((data) => {
        const mapped = data
          .map((item: any) => {
            const c = item.consulta;

            if (c.type === "grafica") {
              return {
                type: "grafica",
                nombre: c.nombre,
                url: c.url,
                hora: item.fecha,
                count: 1,
              };
            }

            if (c.type === "fichero") {
              return {
                type: "Fichero",
                nombre: c.nombre,
                hora: item.fecha,
                lineas: c.lineas,
                columnas: c.columnas,
                numColumnas: c.numColumnas,
                extension: c.extension,
              };
            }

            return null;
          })
          .filter(Boolean);

        setHistorial(mapped);
      });
  }, [usuario]);

  //formatea una string a formato ISO
  const formatearFecha = (iso: string) => {
    const fecha = new Date(iso);

    return fecha.toLocaleString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // La función comprueba que el archivo subido por el usuario sea un archivo con extensión csv
  // Evento de React nativo que se ejecuta al cambiar el valor del input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    //Operador de Encadenamiento Opcional que devuelve null. Evita excepción
    const file = e.target.files?.[0];
    if (!file) return; //si archivo null se sale de la funcion

    // Se obtiene la extensión del archivo falla si no contiene "."
    const extension = file.name.split(".").pop()?.toLowerCase();

    //Extensión check
    if (!["csv", "xls", "xlsx", "json"].includes(extension || "")) {
      alert("Formato no soportado. Usa CSV, XLS, XLSX o JSON");
      return;
    }

    setArchivo(file); //guardamos el archivo para que sea parseado posteriormente
  };

  // Se lee el fichero csv para guardar el total de lineas y columnas (campos)
  // Objeto nativo de JS File
  // Para las promesas -> https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise
  // Se lee el fichero csv para guardar el total de lineas y columnas (campos)
  // Objeto nativo de JS File
  // Para las promesas -> https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise
  /**
   * Lee un CSV y devuelve número de filas y columnas.
   * Falla si el formato no es válido.
   * @param file - Fichero
   * @returns - Sale si no es válido el fichero. O Resolve (Promises) si se completa con éxito.
   */
  const parseCSV = (file: File) =>
    // Se crea nueva promesa para la correcta ejecución de funciones asíncronas
    // Resolve y Reject son callbacks de exito y error en base al resultado de la ejecución del codigo
    new Promise<{ lineas: number; columnas: string[] }>((resolve, reject) => {
      // FileReader de JS
      const reader = new FileReader();

      //Metodo de FileReader que ejecuta el evento al acabar la carga del fichero
      reader.onload = (event) => {
        //Casting del resultado del fichero a String
        const text = event.target?.result as string;

        //Si fichero vacio rechazamos
        if (!text) return reject("Archivo vacío");

        // Filas divididas por retornos de carro, se eliminan filas vacias
        // y se borran espacios en blanco innecesarios con trim
        const rows = text
          .split("\n")
          .map((r) => r.trim())
          .filter((r) => r !== "");

        //Para las columnas ahora usamos la primera fila (cabecera del CSV)
        //Separamos por comas y limpiamos espacios en blanco
        const columnas = rows[0].split(",").map((c) => c.trim());

        //Devuelve un objeto con las lineas y columnas al acabar la ejecución de la promesa
        resolve({
          lineas: rows.length,
          columnas,
        });
      };

      reader.onerror = () => reject("Error leyendo archivo");

      reader.readAsText(file);
    });

  /**
   *Lee un JSON (array de objetos) y devuelve número de filas y columnas.
   * Falla si el formato no es válido.
   * @param file - Fichero
   * @returns - Sale si no es válido el fichero. O Resolve (Promises) si se completa con éxito.
   */
  const parseJSON = (file: File) =>
    new Promise<{ lineas: number; columnas: string[] }>((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        try {
          const text = event.target?.result as string;
          const data = JSON.parse(text);

          if (!Array.isArray(data)) {
            return reject("El JSON debe ser un array de objetos");
          }

          const columnas = data.length > 0 ? Object.keys(data[0]) : [];

          resolve({
            lineas: data.length,
            columnas,
          });
        } catch {
          reject("JSON inválido");
        }
      };

      reader.onerror = () => reject("Error leyendo JSON");

      reader.readAsText(file);
    });

  /**
   *Lee un archivo de Excel y devuelve número de filas y columnas.
   * Falla si el formato no es válido.
   * @param file - Fichero
   * @returns - Sale si no es válido el fichero. O Resolve (Promises) si se completa con éxito.
   */
  const parseExcel = (file: File) =>
    new Promise<{ lineas: number; columnas: string[] }>((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (event) => {
        try {
          const data = event.target?.result as ArrayBuffer;

          const workbook = XLSX.read(data, { type: "array" });
          const sheet = workbook.Sheets[workbook.SheetNames[0]];

          const json = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet);

          const columnas = json.length > 0 ? Object.keys(json[0]) : [];

          resolve({
            lineas: json.length,
            columnas,
          });
        } catch {
          reject("Error parseando Excel");
        }
      };

      reader.onerror = () => reject("Error leyendo Excel");

      reader.readAsArrayBuffer(file);
    });

  /*
  const uploadCSV = async () => {
    if (!archivo) return; // condicion de salida si archivo está en null

    try {
      //await pausa la ejecucion hasta que reciba respuesta de la funcion que parsea el fichero
      const { lineas, columnas } = await parseCSV(archivo);

      //crea un nuevo objeto de tipo HistorialItem para guardarlo
      const nuevaEntrada: HistorialItem = {
        type: "Fichero",
        nombre: archivo.name,
        hora: new Date().toLocaleString(),
        lineas,
        columnas,
      };

      // Se añade al historial previo la nueva entrada en un nuevo array
      // prev (haciendo spread) hace referencia al estado previo del historial
      setHistorial((prev) => [...prev, nuevaEntrada]);
      setArchivo(null);
    } catch (err) {
      console.error(err);
    }
  };
*/

  // Función asíncrona que permite no bloquear la ejecución del hilo principal en su llamada
  /**
   * Parsea y posteriormente sube el archivo del usuario si este es correcto.
   * Inicialmente detecta la extensión y después llama a las funciones de parseo correspondientes.
   * Una vez es correcto se manda al backend y guardamos en el historial (Local y Backend)
   * Guardamos en el historial el numero de filas y columnas del fichero.
   * @async
   * @returns - No devuelve, solo actualiza estados
   */
  const uploadFile = async () => {
    if (!archivo) return; // condicion de salida si archivo está en null

    // Obtenemos la extensión del archivo para determinar cómo parsearlo
    const extension = archivo.name.split(".").pop()?.toLowerCase(); //puede ser null el archivo

    if (!extension) {
      throw new Error("No se pudo determinar la extensión");
    }

    try {
      let result;

      // Según la extensión, llamamos al parser correspondiente
      if (extension === "csv") {
        //await pausa la ejecucion hasta que reciba respuesta de la funcion que parsea el fichero
        result = await parseCSV(archivo);
      } else if (extension === "json") {
        result = await parseJSON(archivo);
      } else if (extension === "xls" || extension === "xlsx") {
        result = await parseExcel(archivo);
      } else {
        throw new Error("Formato no soportado");
      }

      if (!result) {
        throw new Error("Error procesando el archivo");
      }

      // después de parsear el fichero localmente
      await sendFileToBackend(archivo);
      await cargarDatasets();

      const res = await fetch(`${BASE_URL}/historial`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_consultor: usuario.es_admin ? usuario.id_admin : usuario.id_user,
          tipo_consultor: usuario.es_admin ? "admin" : "user",
          consulta: {
            type: "fichero",
            nombre: archivo.name,
            lineas: result.lineas,
            columnas: result.columnas,
            numColumnas: result.columnas.length,
            extension,
          },
        }),
      });

      if (!res.ok) {
        throw new Error("Error guardando en historial");
      }

      //crea un nuevo objeto de tipo HistorialItem para guardarlo
      const nuevaEntrada: HistorialItem = {
        type: "Fichero",
        nombre: archivo.name,
        hora: new Date().toISOString(),
        lineas: result.lineas,
        columnas: result.columnas,
        numColumnas: result.columnas.length,
        extension,
      };

      // Se añade al historial previo la nueva entrada en un nuevo array
      // prev (haciendo spread) hace referencia al estado previo del historial
      setHistorial((prev) => [...prev, nuevaEntrada]);
      setMensajeUpload("Archivo subido correctamente");
      setTipoMensajeUpload("ok");
      setArchivo(null);
    } catch (err: any) {
      setMensajeUpload(err.message || "Error al subir el archivo");
      setTipoMensajeUpload("error");
    }
  };

  //Funcion que llama a hacer un clear del historial en la persistencia local y de BBDD
  const clearHistorial = async () => {
    if (!usuario) return;

    try {
      await fetch(
        `${BASE_URL}/historial?id_consultor=${
          usuario.es_admin ? usuario.id_admin : usuario.id_user
        }&tipo_consultor=${usuario.es_admin ? "admin" : "user"}`,
        {
          method: "DELETE",
        },
      );

      setHistorial([]);
      const key = usuario.es_admin
        ? `historial_admin_${usuario.id_admin}`
        : `historial_user_${usuario.id_user}`;

      localStorage.removeItem(key);
    } catch (err) {
      console.error("Error borrando historial", err);
    }
  };

  // <> agrupa varios elementos sin usar nuevo div
  // dentro de return, comentarios -> {/* */}
  // var === valor && -> Render condicional: https://react.dev/learn/conditional-rendering
  // true && algo → devuelve algo
  // false && algo → devuelve false (no renderiza nada)

  const sendFileToBackend = async (file: File) => {
    const adminId = getAdminId();

    if (!adminId) {
      throw new Error("adminId no definido");
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      `${BASE_URL}/subir-archivo?id_admin=${adminId}`,
      {
        method: "POST",
        headers: {
          id_admin: adminId,
        },
        body: formData,
      },
    );

    if (!response.ok) {
      throw new Error("Error enviando fichero al backend");
    }

    return await response.json();
  };

  return (
    <>
      <h1 id="titleDashboard">PyBusiness Analytics - Dashboard</h1>

      <div className="contenedor">
        <div className="logo">
          <img src="/icons/logo.svg" alt="Logo" className="logo-icon" />
        </div>

        <nav className="sidebar">
          <button
            className={`sidebar-item ${seccion === "dashboard" ? "active" : ""}`}
            onClick={() => setSeccion("dashboard")}
          >
            <img src="/icons/home.svg" alt="Home" className="icon" />
          </button>

          <button
            className={`sidebar-item ${seccion === "files" ? "active" : ""}`}
            onClick={() => setSeccion("files")}
          >
            <img src="/icons/folder.svg" alt="Files" className="icon" />
          </button>

          {esAdmin && (
            <button
              className={`sidebar-item ${seccion === "upload" ? "active" : ""}`}
              onClick={() => setSeccion("upload")}
            >
              <img src="/icons/upload.svg" alt="Subir" className="icon" />
            </button>
          )}

          <button
            className={`sidebar-item ${seccion === "charts" ? "active" : ""}`}
            onClick={() => setSeccion("charts")}
          >
            <img src="/icons/charts.svg" alt="Gráficas" className="icon" />
          </button>

          <button
            className={`sidebar-item ${seccion === "settings" ? "active" : ""}`}
            onClick={() => setSeccion("settings")}
          >
            <img
              src="/icons/settings.svg"
              alt="Configuración"
              className="icon"
            />
          </button>
        </nav>

        <div className="search-bar">
          <input
            id="search-input"
            name="search"
            type="text"
            placeholder="Buscar..."
            className="search-input"
          />
          <button className="search-button">
            <img src="/icons/search.svg" alt="Buscar" className="search-icon" />
          </button>
        </div>

        <div className="user-panel">
          {!usuario ? (
            <button
              className="login-button"
              onClick={() => setMostrarLogin(true)}
            >
              Iniciar sesión
            </button>
          ) : (
            <>
              <img
                src="/icons/user.svg"
                alt="Usuario"
                className="user-avatar"
              />

              <div className="user-info">
                <span className="user-name">{usuario.username}</span>
                <button className="logout-button" onClick={logout}>
                  Cerrar sesión
                </button>
              </div>
            </>
          )}
        </div>

        <main className="main-content">
          {/* DASHBOARD */}
          {seccion === "dashboard" && (
            <>
              <h1>Inicio</h1>

              {/* Si no null se obtiene de la misma manera que en charts */}
              {ultimaGrafica ? (
                <div className="last-graph">
                  <h2>Última gráfica consultada</h2>
                  <p>{ultimaGrafica.nombre}</p>
                  <img
                    src={`${BASE_URL}${ultimaGrafica.url}?id_admin=${adminId}`}
                    alt={ultimaGrafica.nombre}
                  />
                </div>
              ) : (
                <p>Aún no se ha consultado ninguna gráfica</p>
              )}
            </>
          )}

          {/* CHARTS */}
          {seccion === "charts" && (
            <>
              <h1>Gráficas</h1>

              {!hayDatosDisponibles ? (
                <p>Todavía no hay datos disponibles</p>
              ) : (
                <>
                  <button
                    className="toggle-checkboxes"
                    onClick={() => setMostrarChecks((prev) => !prev)}
                  >
                    {mostrarChecks ? "Ocultar filtros" : "Mostrar filtros"}
                  </button>

                  {/* BOTONES DATASET */}
                  <div className="dataset-buttons">
                    {datasets.map((d) => {
                      const disponible = datasetsDisponibles[d.id];

                      return (
                        <button
                          key={d.id}
                          className={`${datasetActivo === d.id ? "active" : ""} ${
                            !disponible ? "disabled" : ""
                          }`}
                          disabled={!disponible}
                          onClick={() => {
                            if (!disponible) return;
                            setDatasetActivo(d.id);
                            setGraficosActivos([]);
                          }}
                        >
                          {d.nombre}
                        </button>
                      );
                    })}
                  </div>

                  {/* CHECKBOXES */}
                  {datasetsDisponibles[datasetActivo] && (
                    <div
                      className={`checkbox-group ${
                        !mostrarChecks ? "hidden" : ""
                      }`}
                    >
                      {datasetSeleccionado?.graficos.map((g) => (
                        <label key={g.url}>
                          <input
                            type="checkbox"
                            checked={graficosActivos.includes(g.url)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setGraficosActivos((prev) => [...prev, g.url]);
                                registrarGrafica(g.url);
                              } else {
                                setGraficosActivos((prev) =>
                                  prev.filter((url) => url !== g.url),
                                );
                              }
                            }}
                          />
                          {g.nombre}
                        </label>
                      ))}
                    </div>
                  )}

                  {/* GRÁFICAS */}
                  <div className="graphs-container">
                    {graficosActivos.length === 0 ? (
                      <p>Selecciona una o más gráficas</p>
                    ) : datasetsDisponibles[datasetActivo] ? (
                      graficosActivos.map((url) => (
                        <div key={url} className="graph">
                          <img
                            src={`${BASE_URL}${url}?id_admin=${adminId}`}
                            alt="Gráfico"
                            onClick={() => setGraficoExpandido(url)}
                            className="clickable-graph"
                          />
                        </div>
                      ))
                    ) : (
                      <p>Dataset no disponible</p>
                    )}
                  </div>
                </>
              )}
            </>
          )}

          {/* ARCHIVOS (folder) */}
          {seccion === "files" && (
            <>
              <div className="files-header">
                <h1>Historial de gráficas</h1>
              </div>

              <div className="files-list">
                {/* Map recorre el array historial
                 Item se refiere al propio elemento y Idx a su índice */}
                {historial.map((item, idx) => {
                  if (item.type === "grafica") {
                    return (
                      <div key={idx} className="file-item">
                        <div className="file-left">
                          <strong>{item.nombre}</strong>
                          <p>Última consulta: {formatearFecha(item.hora)}</p>
                        </div>

                        <div className="file-right">
                          <span>x{item.count}</span>
                        </div>
                      </div>
                    );
                  }

                  {
                    /* Si no grafica, se asume que .csv */
                  }
                  return (
                    <div key={idx} className="file-item">
                      <div className="file-left">
                        <strong>{item.nombre}</strong>
                        <p>Añadido: {formatearFecha(item.hora)}</p>
                        <p>
                          Filas: {item.lineas} | Columnas: {item.numColumnas}
                        </p>

                        <p>Tipo: {item.extension?.toUpperCase()}</p>
                      </div>

                      <div className="file-right">
                        <span>{getTipoArchivo(item.extension)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <button className="upload-button" onClick={clearHistorial}>
                Limpiar historial
              </button>
            </>
          )}

          {/* UPLOAD */}
          {seccion === "upload" && esAdmin && (
            <>
              <h1>Subir archivos</h1>

              <div className="upload-box">
                <input
                  type="file"
                  accept=".csv,.xls,.xlsx,.json"
                  onChange={handleFileChange}
                />

                <button
                  className="upload-button"
                  onClick={uploadFile}
                  disabled={!archivo}
                >
                  Subir archivo
                </button>

                {mensajeUpload && (
                  <p className={`upload-message ${tipoMensajeUpload}`}>
                    {mensajeUpload}
                  </p>
                )}
              </div>
            </>
          )}

          {seccion === "upload" && !esAdmin && (
            <p>No tienes permisos para acceder a esta sección</p>
          )}

          {/* SETTINGS */}
          {seccion === "settings" && (
            <>
              <h1>Configuración</h1>

              <div className="settings-box">
                <label>Modo de visualización:</label>

                <select value={modo} onChange={(e) => setModo(e.target.value)}>
                  <option value="noche">Modo noche</option>
                  <option value="dia">Modo día</option>
                </select>
              </div>

              {esAdmin && (
                <div className="admin-panel">
                  <h2>Administración</h2>

                  <div className="admin-form">
                    <input
                      type="text"
                      placeholder="Nuevo usuario"
                      value={nuevoUsuario}
                      onChange={(e) => setNuevoUsuario(e.target.value)}
                    />

                    <input
                      type="password"
                      placeholder="Contraseña"
                      value={nuevaPassword}
                      onChange={(e) => setNuevaPassword(e.target.value)}
                    />

                    <div className="admin-buttons">
                      <button onClick={admin_crearUsuario} className="primary">
                        Crear usuario
                      </button>

                      <button onClick={crearAdmin} className="secondary">
                        Crear administrador
                      </button>
                    </div>
                  </div>

                  {mensajeUsuario && (
                    <p className="admin-message">{mensajeUsuario}</p>
                  )}
                </div>
              )}
            </>
          )}

          {/* OVERLAY FULLSCREEN */}
          {graficoExpandido && (
            <div
              className="fullscreen-overlay"
              onClick={() => setGraficoExpandido(null)}
            >
              <img
                src={`${BASE_URL}${graficoExpandido}?id_admin=${adminId}`}
                alt="Gráfico ampliado"
                className="fullscreen-image"
              />
            </div>
          )}

          {/* Overlay de Login */}
          {mostrarLogin && (
            <div
              className="modal-overlay"
              onClick={() => setMostrarLogin(false)}
            >
              <div className="modal-login" onClick={(e) => e.stopPropagation()}>
                <h2>Iniciar sesión</h2>

                <input
                  type="text"
                  placeholder="Usuario"
                  value={nuevoUsuario}
                  onChange={(e) => setNuevoUsuario(e.target.value)}
                />

                <input
                  type="password"
                  placeholder="Contraseña"
                  value={nuevaPassword}
                  onChange={(e) => setNuevaPassword(e.target.value)}
                />

                {hayAdmin ? (
                  <button onClick={login}>Entrar</button>
                ) : (
                  <button onClick={crearPrimerAdmin}>
                    Crear primer administrador
                  </button>
                )}

                <button
                  className="secondary"
                  onClick={() => setMostrarLogin(false)}
                >
                  Cancelar
                </button>

                {mensajeUsuario && <p>{mensajeUsuario}</p>}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}

export default App;
