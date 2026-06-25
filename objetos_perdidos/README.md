# Sistema de Gestión de Objetos Perdidos - CFT Tarapacá

## Descripción del Proyecto
Plataforma web diseñada para la gestión, registro y recuperación de objetos perdidos dentro de las instalaciones del CFT Tarapacá. El sistema centraliza la información mediante una arquitectura que permite a la comunidad estudiantil reportar y buscar pertenencias, mientras que el personal administrativo mantiene un control total sobre el inventario y el estado de entrega de los artículos.

## Características Principales
* **Gestión Administrativa:** Panel restringido para administradores que permite visualizar el historial completo, editar información, modificar el estado de un objeto y gestionar eliminaciones de registros.
* **Motor de Búsqueda:** Funcionalidad implementada para realizar consultas rápidas mediante coincidencias parciales, optimizando la localización de objetos extraviados.
* **Adaptabilidad de Interfaz:** Sistema de navegación responsivo que permite alternar dinámicamente entre "Modo PC" y "Modo Tótem" para adaptarse a diversos dispositivos institucionales.
* **Módulo de Feedback (En desarrollo):** Sistema en fase de implementación diseñado para que los alumnos envíen sugerencias y puntuaciones. Esta característica permitirá al administrador recolectar métricas sobre la eficiencia del servicio y la satisfacción del usuario en futuras actualizaciones.

## Arquitectura Técnica
* **Backend:** Python utilizando el framework **Flask** para el manejo de rutas, sesiones y lógica de negocio.
* **Base de Datos:** **PostgreSQL** para la persistencia de datos, con conexión gestionada mediante `psycopg`.
* **Frontend:** Estructura basada en **HTML5** y **CSS3**, utilizando **Bootstrap** para el diseño de componentes y **FontAwesome** para la iconografía.
* **Control de Estado:** Uso de `session` en Flask para gestionar la autenticación de administradores y la persistencia de preferencias de visualización.

## Estructura del Proyecto
- `app.py`: Archivo principal con la lógica de rutas y control de la aplicación.
- `conexion.py`: Módulo de conexión con la base de datos PostgreSQL.
- `templates/`: Carpeta que contiene todas las interfaces (HTML) del sistema.