# Arquitectura MVP

## 1. Objetivo del sistema

Construir una aplicacion de escritorio local para una docente, optimizada para captura rapida de calificaciones, consulta de promedios y deteccion temprana de riesgo academico.

## 2. Principios arquitectonicos

- Offline first real: toda la operacion vive en SQLite local.
- UI reactiva: la vista responde a cambios inmediatos sin flujos complejos.
- Logica fuera de la interfaz: calculos, validaciones y reglas viven en `services/`.
- Escalabilidad simple: crecer por modulos, no por capas ceremoniales.
- Reutilizacion visual: los widgets comunes viven en `ui/widgets/`.

## 3. Capas recomendadas

### `ui/`

Responsable de:

- ventanas
- navegacion
- tablas editables
- formularios
- estados visuales

No debe encargarse de:

- calculos de promedio
- reglas de negocio
- SQL embebido en widgets

### `services/`

Responsable de:

- promedio por categoria
- promedio final ponderado
- validacion de porcentajes
- deteccion de alumnos en riesgo
- coordinacion entre repositorios y UI

### `database/`

Responsable de:

- conexion SQLite
- inicializacion de esquema
- repositorios CRUD por modulo
- respaldo y restauracion de base local

### `models/`

Responsable de:

- entidades tipadas
- DTOs internos
- estructuras para tablas y filtros

## 4. Modulos funcionales del MVP

### Modulo de grupos

- alta, edicion y baja de grupos
- configuracion general del grupo
- minimo aprobatorio por grupo

### Modulo de alumnos

- CRUD de alumnos
- estado activo/inactivo
- notas breves por alumno

### Modulo de evaluacion

- categorias activables
- porcentaje por categoria
- actividades por categoria
- validacion de suma total igual a 100%

### Modulo de calificaciones

- captura tipo grid
- edicion por celda
- guardado automatico
- navegacion por teclado

### Modulo de analitica ligera

- promedio por alumno
- promedio grupal
- aprobados y reprobados
- alumnos en riesgo

## 4.1 Operacion y soporte local

- La base principal vive en `data/aulatrack.db`.
- Los logs de la app se guardan en `data/logs/aulatrack.log`.
- Los errores no controlados deben registrarse en log y mostrar un mensaje claro al usuario.
- Antes de cambios masivos o importaciones grandes, se recomienda crear respaldo desde la app.

## 5. Flujo general de la app

1. La maestra crea un grupo.
2. Agrega alumnos al grupo.
3. Configura categorias y porcentajes.
4. Crea actividades dentro de cada categoria.
5. Captura calificaciones en la tabla principal.
6. La app recalcula promedios en tiempo real.
7. El dashboard y los indicadores de riesgo se actualizan automaticamente.

## 6. Vista principal recomendada

Usar una ventana principal con sidebar y area de trabajo:

- `Dashboard`
- `Grupos`
- `Calificaciones`
- `Configuracion`

La vista mas importante debe ser `Calificaciones`, porque ahi vive el flujo diario.

## 7. Wireframes basicos

### Ventana principal

```text
+----------------------------------------------------------------------------------+
| Sidebar                    | Barra superior / contexto                           |
| - Dashboard                | Grupo: 2B Primaria   Materia: Matematicas          |
| - Grupos                   |----------------------------------------------------|
| - Calificaciones           |                                                    |
| - Configuracion            | Area de trabajo principal                          |
|                            |                                                    |
+----------------------------------------------------------------------------------+
```

### Vista de grupos

```text
+----------------------------------------------------------------------------------+
| Grupos                                              [ Nuevo grupo ]              |
| Lista / tabla de grupos                                                         |
|----------------------------------------------------------------------------------|
| Nombre | Grado | Materia | Ciclo | Min aprobatorio | Alumnos | Acciones         |
+----------------------------------------------------------------------------------+
```

### Vista de calificaciones

```text
+----------------------------------------------------------------------------------+
| Grupo: 2B Primaria     Periodo: Parcial 1       [ Nueva actividad ]              |
| Categorias: Examenes 40 | Tareas 30 | Proyecto 20 | Participacion 10            |
|----------------------------------------------------------------------------------|
| Alumno        | Ex1 | Ex2 | T1 | T2 | Proy1 | Part1 | Promedio | Riesgo         |
| Ana Lopez     | 8   | 9   | 10 | 9  | 8     | 10    | 8.85     | Normal         |
| Luis Perez    | 5   |     | 6  | 4  | 5     | 7     | 5.30     | En riesgo      |
+----------------------------------------------------------------------------------+
```

### Dashboard

```text
+----------------------------------------------------------------------------------+
| Promedio grupal | Aprobados | En riesgo | Actividades pendientes                |
|----------------------------------------------------------------------------------|
| Grafico simple por categoria o barras de rendimiento                            |
| Lista discreta de alumnos que requieren atencion                                |
+----------------------------------------------------------------------------------+
```

## 8. Componentes PySide6 recomendados

### Para navegacion y layout

- `QMainWindow`: contenedor principal
- `QStackedWidget`: cambio de vistas sin abrir ventanas extra
- `QFrame`: paneles visuales reutilizables
- `QSplitter`: opcional para vista lista + detalle

### Para tablas editables

- `QTableView`: mejor opcion para rendimiento y control fino
- `QAbstractTableModel`: modelo principal para gradebook
- `QStyledItemDelegate`: edicion personalizada de celdas
- `QSortFilterProxyModel`: filtros y orden sin romper el modelo base

Evitaria `QTableWidget` para la tabla principal de calificaciones. Sirve para prototipos, pero se vuelve mas rigido y menos escalable.

## 9. Recomendacion de arquitectura para la tabla estilo Excel

- Filas = alumnos
- Columnas = actividades
- Columnas finales fijas = promedio, pendientes, riesgo
- Un `GradebookTableModel` controla datos
- Un delegate numerico valida rangos y acelera captura
- Atajos:
  - `Enter`: guarda y baja
  - `Tab`: guarda y avanza
  - flechas: navegacion
  - `Ctrl+C` y `Ctrl+V`: copiar y pegar rangos simples

## 10. Sistema visual recomendado

### Direccion visual

- base neutra
- acento azul suave o verde grisaceo
- bordes tenues
- sombras minimas
- jerarquia por espaciado, no por saturacion

### Tokens sugeridos

- fondo principal: `#F6F7F9`
- panel: `#FFFFFF`
- borde: `#E2E6EA`
- texto principal: `#1F2933`
- texto secundario: `#6B7280`
- acento: `#2563EB`
- exito: `#1F8A5B`
- alerta suave: `#B7791F`
- riesgo suave: `#C05666`

### Modo oscuro

- fondo: `#111318`
- panel: `#171A21`
- borde: `#2B3240`
- texto: `#EEF2F7`
- acento: `#6EA8FE`

### Reglas de consistencia

- radio de 10 a 14 px
- espaciado base de 8 px
- titulos 18 a 24 px
- cuerpo 13 a 14 px
- tablas con altura comoda de fila

## 11. Roadmap por fases

### Fase 1. Base tecnica

- estructura del proyecto
- conexion SQLite
- tema visual
- ventana principal

### Fase 2. Datos maestros

- CRUD de grupos
- CRUD de alumnos
- CRUD de categorias

### Fase 3. Gradebook

- actividades
- tabla editable
- guardado automatico
- validacion numerica

### Fase 4. Calculos y riesgo

- promedio por categoria
- promedio final ponderado
- reglas de riesgo
- etiquetas visuales

### Fase 5. Dashboard y pulido UX

- tarjetas de resumen
- filtros
- accesos rapidos
- mejoras visuales

### Fase 6. Estabilidad

- pruebas de servicios
- datos demo
- backup local
- exportacion basica a CSV o Excel si luego la necesitas

## 12. Recomendaciones UX para captura rapida

- dejar la tabla principal como centro del trabajo diario
- minimizar modales
- usar panel lateral o drawer para editar actividad o alumno
- autoguardado silencioso con confirmacion discreta
- duplicar actividad desde otra existente
- permitir pegar bloques desde Excel
- recordar ultimo grupo abierto
- usar encabezados congelados para no perder contexto
- permitir resaltar celdas vacias o pendientes con tonos suaves
- mostrar promedio y riesgo sin exigir clic adicional

## 13. Decision tecnica clave

Para este producto, la inversion correcta esta en:

- un buen modelo de tabla
- una UX de teclado impecable
- un sistema visual consistente

No en complejidad arquitectonica innecesaria.
