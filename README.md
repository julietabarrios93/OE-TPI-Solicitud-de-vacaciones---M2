# TPI Organización Empresarial - Solicitud de Vacaciones M2

## Descripción del proyecto

Este repositorio contiene el desarrollo del Trabajo Práctico Integrador de la materia Organización Empresarial.

El proyecto consiste en un simulador de chatbot desarrollado en Python para automatizar parte del proceso de solicitud y validación de vacaciones del personal de M2.

El chatbot permite validar datos del colaborador, consultar archivos CSV como base de datos simulada, controlar saldo disponible, detectar posibles conflictos de cobertura y registrar únicamente las vacaciones aprobadas.

## Proceso seleccionado

Solicitud y validación de vacaciones del personal de M2 mediante chatbot.

El proceso comienza cuando un colaborador inicia una solicitud de vacaciones e informa su legajo, fecha de inicio y cantidad de días solicitados. Luego, el sistema valida la información y determina si la solicitud puede aprobarse, rechazarse o derivarse a Recursos Humanos.

## Alcance del sistema

El sistema permite:

* Validar si el legajo ingresado existe.
* Verificar si el colaborador se encuentra activo.
* Validar el formato de la fecha solicitada.
* Validar que la cantidad de días sea numérica y mayor a cero.
* Verificar si el colaborador tiene días disponibles suficientes.
* Consultar vacaciones ya aprobadas para detectar posibles conflictos de cobertura.
* Solicitar aprobación del responsable si existe superposición.
* Registrar vacaciones aprobadas.
* Actualizar el saldo de días disponibles del colaborador.

El sistema no incluye liquidación de sueldos ni registración contable posterior.

## Estructura del repositorio

```text
OE-TPI-Solicitud-de-vacaciones---M2/
├── main.py
├── README.md
├── .gitignore
├── data/
│   ├── colaboradores.csv
│   ├── vacaciones_aprobadas.csv
│   └── reglas.csv
├── bpmn/
│   ├── AS-IS_Vacaciones_M2.jpg
│   └── TO-BE_Vacaciones_M2.jpg
└── capturas/
    ├── camino_feliz.png
    ├── saldo_insuficiente.jpg
    ├── legajo_inexistente.jpg
    └── conflicto_cobertura.jpg
```

## Archivos principales

### main.py

Contiene el programa principal del chatbot.

Fue desarrollado con una estructura básica de Python:

* `import csv`
* funciones simples
* listas de diccionarios
* condicionales `if / else`
* ciclos `for`
* manejo de errores con `try / except`

### data/colaboradores.csv

Contiene los datos de los colaboradores.

Campos principales:

* `legajo`
* `nombre`
* `area`
* `proyecto_obra`
* `estado`
* `dias_disponibles`
* `responsable`

Este archivo se utiliza para validar el legajo, el estado del colaborador, el área, el proyecto u obra, los días disponibles y el responsable asignado.

Cuando una solicitud queda aprobada, el programa actualiza este archivo descontando los días solicitados del campo `dias_disponibles`.

### data/vacaciones_aprobadas.csv

Contiene únicamente las vacaciones aprobadas.

Campos principales:

* `id_solicitud`
* `legajo`
* `fecha_inicio`
* `dias_solicitados`
* `fecha_fin`
* `estado`
* `observacion`

Este archivo se consulta para detectar posibles conflictos de cobertura. También se actualiza cuando una nueva solicitud queda aprobada.

Las solicitudes rechazadas o derivadas no se guardan en este archivo porque no generan una ausencia real.

### data/reglas.csv

Contiene las reglas de negocio que documentan la lógica del proceso.

Ejemplos de reglas:

* Validar colaborador.
* Validar estado activo.
* Validar fecha.
* Validar saldo.
* Validar cobertura.
* Registrar aprobación.

## Cómo ejecutar el programa

Para ejecutar el chatbot, se debe abrir una terminal en la carpeta principal del repositorio y escribir:

```bash
python main.py
```

No es necesario instalar librerías externas, ya que el programa utiliza únicamente módulos estándar de Python.

## Pruebas sugeridas

### Camino feliz sin conflicto

Datos de prueba:

```text
Legajo: 1025
Fecha: 20/08/2026
Días: 3
```

Resultado esperado:

```text
Estado final: APROBADA
```

El sistema registra la vacación aprobada en `vacaciones_aprobadas.csv` y descuenta los días en `colaboradores.csv`.

### Saldo insuficiente

Datos de prueba:

```text
Legajo: 1030
Fecha: 25/08/2026
Días: 20
```

Resultado esperado:

```text
Estado final: RECHAZADA
```

El sistema informa que no hay saldo suficiente y no actualiza las bases.

### Legajo inexistente

Datos de prueba:

```text
Legajo: 9999
```

Resultado esperado:

```text
Estado final: DERIVADA_RRHH
```

El sistema deriva la consulta a Recursos Humanos y no actualiza las bases.

### Colaborador inactivo

Datos de prueba:

```text
Legajo: 1051
```

Resultado esperado:

```text
Estado final: DERIVADA_RRHH
```

El sistema informa que el colaborador no está activo y deriva la consulta a Recursos Humanos.

### Conflicto de cobertura

Para probar este caso, se debe ingresar una fecha que ya exista en `vacaciones_aprobadas.csv` para un colaborador de la misma área o proyecto.

Resultado esperado:

```text
Estado final: PENDIENTE_APROBACION
```

Luego el sistema solicita una decisión simulada del responsable.

Si el responsable responde `si`, la solicitud queda:

```text
Estado final: APROBADA
```

Si el responsable responde `no`, la solicitud queda:

```text
Estado final: RECHAZADA
```

## Criterio de actualización de bases

El sistema solo actualiza las bases cuando la solicitud queda aprobada.

| Situación                           | Actualiza vacaciones_aprobadas.csv | Actualiza colaboradores.csv |
| ----------------------------------- | ---------------------------------- | --------------------------- |
| Legajo inexistente                  | No                                 | No                          |
| Colaborador inactivo                | No                                 | No                          |
| Fecha inválida                      | No                                 | No                          |
| Días inválidos                      | No                                 | No                          |
| Saldo insuficiente                  | No                                 | No                          |
| Sin conflicto de cobertura          | Sí                                 | Sí                          |
| Conflicto aprobado por responsable  | Sí                                 | Sí                          |
| Conflicto rechazado por responsable | No                                 | No                          |

## Relación con BPMN

El repositorio incluye los diagramas BPMN del proceso:

* AS-IS: representa el proceso actual, donde la solicitud se realiza mediante canales informales y las validaciones dependen de Recursos Humanos.
* TO-BE: representa el proceso propuesto con chatbot, validaciones automáticas, consulta a bases de datos y derivación en casos que requieren intervención humana.

## Máquina de estados

El chatbot utiliza estados para representar el avance de la conversación.

Estados principales:

* `INICIO`
* `ESPERANDO_LEGAJO`
* `VALIDANDO_COLABORADOR`
* `ESPERANDO_FECHA`
* `ESPERANDO_DIAS`
* `VALIDANDO_SALDO`
* `VALIDANDO_COBERTURA`
* `PENDIENTE_APROBACION`
* `APROBADA`
* `RECHAZADA`
* `DERIVADA_RRHH`
* `FINALIZADA`

Estos estados permiten explicar cómo el bot conserva el contexto del proceso y decide cuál es el siguiente paso.

## Capturas

La carpeta `capturas/` contiene evidencias de ejecución del programa:

* camino feliz;
* saldo insuficiente;
* legajo inexistente;
* conflicto de cobertura.

Estas capturas se utilizan como evidencia del funcionamiento del simulador.

## Archivo .gitignore

El archivo `.gitignore` se utiliza para evitar subir archivos temporales generados por Python.

Contenido utilizado:

```gitignore
__pycache__/
```

## Uso de inteligencia artificial

La inteligencia artificial fue utilizada como apoyo para:

* ordenar ideas del proceso;
* comparar alternativas de automatización;
* revisar coherencia entre BPMN y código;
* definir reglas de negocio;
* mejorar la redacción del informe;
* estructurar la máquina de estados.

El contenido fue revisado y adaptado al contexto de M2.

## Seguridad del Personal Access Token

El Personal Access Token de GitHub debe tratarse como una contraseña.

No debe publicarse en:

* el código fuente;
* el README;
* las capturas;
* los commits;
* los archivos del repositorio.

## Autora

Nair Julieta Barrios
Tecnicatura Universitaria en Programación
Universidad Tecnológica Nacional
Materia: Organización Empresarial
