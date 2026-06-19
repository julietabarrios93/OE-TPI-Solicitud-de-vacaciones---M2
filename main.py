import csv

print("=== CHATBOT M2 - SOLICITUD DE VACACIONES ===")
print("Hola, voy a ayudarte a cargar una solicitud de vacaciones.")
print("")


# --------------------------------------------------
# FUNCIONES PARA LEER ARCHIVOS CSV
# --------------------------------------------------

def leer_colaboradores():
    colaboradores = []

    try:
        with open("data/colaboradores.csv", "r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                try:
                    fila["dias_disponibles"] = int(fila["dias_disponibles"])
                    colaboradores.append(fila)
                except ValueError:
                    print("Error: hay un dato inválido en días disponibles.")

    except FileNotFoundError:
        print("Error: no se encontró el archivo colaboradores.csv.")

    return colaboradores


def leer_vacaciones_aprobadas():
    vacaciones_aprobadas = []

    try:
        with open("data/vacaciones_aprobadas.csv", "r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                try:
                    fila["dias_solicitados"] = int(fila["dias_solicitados"])
                    vacaciones_aprobadas.append(fila)
                except ValueError:
                    print("Error: hay un dato inválido en días solicitados.")

    except FileNotFoundError:
        print("Error: no se encontró el archivo vacaciones_aprobadas.csv.")

    return vacaciones_aprobadas


# --------------------------------------------------
# FUNCIONES DE VALIDACIÓN
# --------------------------------------------------

def buscar_colaborador(colaboradores, legajo):
    for colaborador in colaboradores:
        if colaborador["legajo"] == legajo:
            return colaborador

    return None


def fecha_valida(fecha):
    try:
        partes = fecha.split("/")

        if len(partes) != 3:
            return False

        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])

        if dia < 1 or dia > 31:
            return False

        if mes < 1 or mes > 12:
            return False

        if anio < 2026:
            return False

        return True

    except ValueError:
        return False


def pedir_dias():
    try:
        dias = int(input("Bot: Ingresá la cantidad de días solicitados: "))

        if dias <= 0:
            return None

        return dias

    except ValueError:
        return None


def hay_superposicion(vacaciones_aprobadas, colaboradores, colaborador_actual, fecha_inicio):
    for vacacion in vacaciones_aprobadas:

        if vacacion["fecha_inicio"] == fecha_inicio:
            colaborador_ausente = buscar_colaborador(colaboradores, vacacion["legajo"])

            if colaborador_ausente is not None:
                misma_area = colaborador_ausente["area"] == colaborador_actual["area"]
                mismo_proyecto = colaborador_ausente["proyecto_obra"] == colaborador_actual["proyecto_obra"]

                if misma_area or mismo_proyecto:
                    return True

    return False


def generar_id_solicitud(vacaciones_aprobadas):
    numero = len(vacaciones_aprobadas) + 1
    return "SOL" + str(numero).zfill(3)


# --------------------------------------------------
# FUNCIONES PARA ACTUALIZAR BASES DE DATOS
# --------------------------------------------------

def guardar_vacacion_aprobada(nueva_vacacion):
    try:
        with open("data/vacaciones_aprobadas.csv", "a", encoding="utf-8", newline="") as archivo:
            campos = [
                "id_solicitud",
                "legajo",
                "fecha_inicio",
                "dias_solicitados",
                "fecha_fin",
                "estado",
                "observacion"
            ]

            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writerow(nueva_vacacion)

    except FileNotFoundError:
        print("Error: no se pudo actualizar la base de vacaciones aprobadas.")


def actualizar_dias_disponibles(colaboradores, legajo, dias_solicitados):
    try:
        for colaborador in colaboradores:
            if colaborador["legajo"] == legajo:
                colaborador["dias_disponibles"] = colaborador["dias_disponibles"] - dias_solicitados

        with open("data/colaboradores.csv", "w", encoding="utf-8", newline="") as archivo:
            campos = [
                "legajo",
                "nombre",
                "area",
                "proyecto_obra",
                "estado",
                "dias_disponibles",
                "responsable"
            ]

            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(colaboradores)

    except FileNotFoundError:
        print("Error: no se pudo actualizar la base de colaboradores.")


# --------------------------------------------------
# PROGRAMA PRINCIPAL
# --------------------------------------------------

colaboradores = leer_colaboradores()
vacaciones_aprobadas = leer_vacaciones_aprobadas()

estado_bot = "INICIO"


# --------------------------------------------------
# VALIDACIÓN DE LEGAJO
# --------------------------------------------------

estado_bot = "ESPERANDO_LEGAJO"
legajo_ingresado = input("Bot: Ingresá tu número de legajo: ")

estado_bot = "VALIDANDO_COLABORADOR"
colaborador = buscar_colaborador(colaboradores, legajo_ingresado)


if colaborador is None:
    estado_bot = "DERIVADA_RRHH"

    print("")
    print("Bot: No encontré ese legajo en la base de datos.")
    print("Bot: La consulta se deriva a Recursos Humanos.")
    print("Bot: No se actualiza la base de vacaciones aprobadas.")
    print("Estado final:", estado_bot)


else:
    # --------------------------------------------------
    # VALIDACIÓN DE ESTADO DEL COLABORADOR
    # --------------------------------------------------

    if colaborador["estado"] != "Activo":
        estado_bot = "DERIVADA_RRHH"

        print("")
        print("Bot: El colaborador no se encuentra activo.")
        print("Bot: La consulta se deriva a Recursos Humanos.")
        print("Bot: No se actualiza la base de vacaciones aprobadas.")
        print("Estado final:", estado_bot)


    else:
        print("")
        print("Bot: Hola", colaborador["nombre"])
        print("Bot: Área:", colaborador["area"])
        print("Bot: Proyecto/Obra:", colaborador["proyecto_obra"])
        print("Bot: Días disponibles:", colaborador["dias_disponibles"])


        # --------------------------------------------------
        # VALIDACIÓN DE FECHA
        # --------------------------------------------------

        estado_bot = "ESPERANDO_FECHA"
        fecha_inicio = input("Bot: Ingresá la fecha de inicio (DD/MM/AAAA): ")

        if not fecha_valida(fecha_inicio):
            estado_bot = "RECHAZADA"

            print("")
            print("Bot: La fecha ingresada no es válida.")
            print("Bot: La solicitud queda rechazada.")
            print("Bot: No se actualiza la base de vacaciones aprobadas.")
            print("Estado final:", estado_bot)


        else:
            # --------------------------------------------------
            # VALIDACIÓN DE CANTIDAD DE DÍAS
            # --------------------------------------------------

            estado_bot = "ESPERANDO_DIAS"
            dias_solicitados = pedir_dias()

            if dias_solicitados is None:
                estado_bot = "RECHAZADA"

                print("")
                print("Bot: La cantidad de días debe ser un número mayor a cero.")
                print("Bot: La solicitud queda rechazada.")
                print("Bot: No se actualiza la base de vacaciones aprobadas.")
                print("Estado final:", estado_bot)


            else:
                # --------------------------------------------------
                # VALIDACIÓN DE SALDO
                # --------------------------------------------------

                estado_bot = "VALIDANDO_SALDO"

                if dias_solicitados > colaborador["dias_disponibles"]:
                    estado_bot = "RECHAZADA"

                    print("")
                    print("Bot: No tenés saldo suficiente.")
                    print("Bot: Solicitaste", dias_solicitados, "días.")
                    print("Bot: Tenés disponibles", colaborador["dias_disponibles"], "días.")
                    print("Bot: La solicitud queda rechazada.")
                    print("Bot: No se actualiza la base de vacaciones aprobadas.")
                    print("Estado final:", estado_bot)


                else:
                    # --------------------------------------------------
                    # VALIDACIÓN DE COBERTURA
                    # --------------------------------------------------

                    estado_bot = "VALIDANDO_COBERTURA"

                    conflicto = hay_superposicion(
                        vacaciones_aprobadas,
                        colaboradores,
                        colaborador,
                        fecha_inicio
                    )

                    if conflicto:
                        estado_bot = "PENDIENTE_APROBACION"

                        print("")
                        print("Bot: Existe una posible superposición de cobertura.")
                        print("Bot: La solicitud requiere aprobación del responsable.")
                        print("Responsable:", colaborador["responsable"])

                        respuesta = input("Simulación: ¿El responsable aprueba la excepción? (si/no): ")

                        if respuesta.lower() == "si":
                            estado_bot = "APROBADA"
                            observacion = "Aprobada por excepción de cobertura"
                        else:
                            estado_bot = "RECHAZADA"

                            print("")
                            print("Bot: El responsable rechazó la excepción de cobertura.")
                            print("Bot: La solicitud queda rechazada.")
                            print("Bot: No se actualiza la base de vacaciones aprobadas.")
                            print("Estado final:", estado_bot)

                    else:
                        estado_bot = "APROBADA"
                        observacion = "Sin conflicto de cobertura"


                    # --------------------------------------------------
                    # REGISTRO SOLO SI LA SOLICITUD FUE APROBADA
                    # --------------------------------------------------

                    if estado_bot == "APROBADA":

                        nueva_vacacion = {
                            "id_solicitud": generar_id_solicitud(vacaciones_aprobadas),
                            "legajo": legajo_ingresado,
                            "fecha_inicio": fecha_inicio,
                            "dias_solicitados": dias_solicitados,
                            "fecha_fin": "No calculada",
                            "estado": estado_bot,
                            "observacion": observacion
                        }

                        guardar_vacacion_aprobada(nueva_vacacion)
                        actualizar_dias_disponibles(colaboradores, legajo_ingresado, dias_solicitados)

                        print("")
                        print("=== RESUMEN DE LA SOLICITUD ===")
                        print("Colaborador:", colaborador["nombre"])
                        print("Área:", colaborador["area"])
                        print("Proyecto/Obra:", colaborador["proyecto_obra"])
                        print("Fecha de inicio:", fecha_inicio)
                        print("Días solicitados:", dias_solicitados)
                        print("Estado final:", estado_bot)
                        print("Observación:", observacion)
                        print("Bot: La vacación aprobada fue registrada en la base de datos.")
                        print("Bot: También se actualizó el saldo de días disponibles del colaborador.")