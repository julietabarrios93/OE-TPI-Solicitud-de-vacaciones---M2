"""
Simulador de chatbot para solicitud y validacion de vacaciones en M2.

Trabajo Practico Integrador - Organizacion Empresarial
Proceso: Solicitud y validacion de vacaciones del personal mediante chatbot.

Ejecutar:
    python main.py
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
COLABORADORES_CSV = DATA_DIR / "colaboradores.csv"
SOLICITUDES_CSV = DATA_DIR / "solicitudes.csv"


@dataclass
class Colaborador:
    legajo: str
    nombre: str
    area: str
    proyecto_obra: str
    estado: str
    dias_disponibles: int
    responsable: str


@dataclass
class Solicitud:
    id_solicitud: str
    legajo: str
    fecha_inicio: datetime
    dias_solicitados: int
    fecha_fin: datetime
    estado: str
    observacion: str


class EstadoBot:
    INICIO = "INICIO"
    ESPERANDO_LEGAJO = "ESPERANDO_LEGAJO"
    VALIDANDO_COLABORADOR = "VALIDANDO_COLABORADOR"
    ESPERANDO_FECHA = "ESPERANDO_FECHA"
    ESPERANDO_DIAS = "ESPERANDO_DIAS"
    VALIDANDO_SALDO = "VALIDANDO_SALDO"
    VALIDANDO_COBERTURA = "VALIDANDO_COBERTURA"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    OBSERVADA = "OBSERVADA"
    DERIVADA_RRHH = "DERIVADA_RRHH"
    FINALIZADA = "FINALIZADA"


def cargar_colaboradores() -> dict[str, Colaborador]:
    colaboradores = {}
    with open(COLABORADORES_CSV, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            colaboradores[fila["legajo"]] = Colaborador(
                legajo=fila["legajo"],
                nombre=fila["nombre"],
                area=fila["area"],
                proyecto_obra=fila["proyecto_obra"],
                estado=fila["estado"],
                dias_disponibles=int(fila["dias_disponibles"]),
                responsable=fila["responsable"],
            )
    return colaboradores


def parsear_fecha(valor: str) -> datetime:
    return datetime.strptime(valor.strip(), "%d/%m/%Y")


def formatear_fecha(fecha: datetime) -> str:
    return fecha.strftime("%d/%m/%Y")


def cargar_solicitudes() -> list[Solicitud]:
    solicitudes = []
    if not SOLICITUDES_CSV.exists():
        return solicitudes

    with open(SOLICITUDES_CSV, newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            solicitudes.append(
                Solicitud(
                    id_solicitud=fila["id_solicitud"],
                    legajo=fila["legajo"],
                    fecha_inicio=parsear_fecha(fila["fecha_inicio"]),
                    dias_solicitados=int(fila["dias_solicitados"]),
                    fecha_fin=parsear_fecha(fila["fecha_fin"]),
                    estado=fila["estado"],
                    observacion=fila["observacion"],
                )
            )
    return solicitudes


def pedir_fecha(mensaje: str, max_intentos: int = 2) -> datetime | None:
    for _ in range(max_intentos):
        valor = input(mensaje).strip()
        try:
            fecha = parsear_fecha(valor)
            if fecha.date() <= datetime.today().date():
                print("Bot: La fecha debe ser posterior a la fecha actual.")
                continue
            return fecha
        except ValueError:
            print("Bot: La fecha ingresada no es valida. Usa el formato DD/MM/AAAA.")
    return None


def pedir_entero(mensaje: str, max_intentos: int = 2) -> int | None:
    for _ in range(max_intentos):
        valor = input(mensaje).strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        print("Bot: Debes ingresar un numero entero mayor a cero.")
    return None


def calcular_fecha_fin(fecha_inicio: datetime, dias: int) -> datetime:
    return fecha_inicio + timedelta(days=dias - 1)


def intervalos_se_superponen(inicio_a: datetime, fin_a: datetime, inicio_b: datetime, fin_b: datetime) -> bool:
    return inicio_a <= fin_b and inicio_b <= fin_a


def existe_conflicto_cobertura(colaborador: Colaborador, fecha_inicio: datetime, fecha_fin: datetime, colaboradores: dict[str, Colaborador], solicitudes: list[Solicitud]) -> bool:
    estados_a_considerar = {"Aprobada", "Pendiente"}
    for solicitud in solicitudes:
        if solicitud.estado not in estados_a_considerar:
            continue
        colaborador_solicitud = colaboradores.get(solicitud.legajo)
        if not colaborador_solicitud:
            continue
        misma_area = colaborador_solicitud.area == colaborador.area
        mismo_proyecto = colaborador_solicitud.proyecto_obra == colaborador.proyecto_obra
        if (misma_area or mismo_proyecto) and intervalos_se_superponen(fecha_inicio, fecha_fin, solicitud.fecha_inicio, solicitud.fecha_fin):
            return True
    return False


def generar_id_solicitud(solicitudes: list[Solicitud]) -> str:
    numeros = []
    for solicitud in solicitudes:
        codigo = solicitud.id_solicitud.replace("SOL", "")
        if codigo.isdigit():
            numeros.append(int(codigo))
    return f"SOL{max(numeros, default=0) + 1:03d}"


def guardar_solicitud(id_solicitud: str, legajo: str, fecha_inicio: datetime, dias_solicitados: int, fecha_fin: datetime, estado: str, observacion: str) -> None:
    archivo_existe = SOLICITUDES_CSV.exists()
    with open(SOLICITUDES_CSV, "a", newline="", encoding="utf-8") as archivo:
        campos = ["id_solicitud", "legajo", "fecha_inicio", "dias_solicitados", "fecha_fin", "estado", "observacion"]
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        if not archivo_existe:
            escritor.writeheader()
        escritor.writerow({
            "id_solicitud": id_solicitud,
            "legajo": legajo,
            "fecha_inicio": formatear_fecha(fecha_inicio),
            "dias_solicitados": dias_solicitados,
            "fecha_fin": formatear_fecha(fecha_fin),
            "estado": estado,
            "observacion": observacion,
        })


def simular_chatbot() -> None:
    print("\n=== Chatbot M2 - Solicitud de vacaciones ===")
    print("Bot: Hola. Voy a ayudarte a registrar una solicitud de vacaciones.")

    colaboradores = cargar_colaboradores()
    solicitudes = cargar_solicitudes()

    legajo = input("Bot: Ingresa tu numero de legajo: ").strip()
    colaborador = colaboradores.get(legajo)

    if not colaborador:
        estado = EstadoBot.RECHAZADA
        print("Bot: No encontre ese legajo en la base. La solicitud queda rechazada.")
        print(f"Estado final: {estado}")
        return

    if colaborador.estado != "Activo":
        estado = EstadoBot.RECHAZADA
        print("Bot: El colaborador no se encuentra activo. No puede iniciar una solicitud.")
        print(f"Estado final: {estado}")
        return

    print(f"Bot: Hola {colaborador.nombre}. Area: {colaborador.area}. Dias disponibles: {colaborador.dias_disponibles}.")

    fecha_inicio = pedir_fecha("Bot: Ingresa la fecha de inicio (DD/MM/AAAA): ")
    if fecha_inicio is None:
        estado = EstadoBot.DERIVADA_RRHH
        print("Bot: No pude validar la fecha. Derivo la consulta a Recursos Humanos.")
        print(f"Estado final: {estado}")
        return

    dias_solicitados = pedir_entero("Bot: Ingresa la cantidad de dias solicitados: ")
    if dias_solicitados is None:
        estado = EstadoBot.DERIVADA_RRHH
        print("Bot: No pude validar la cantidad de dias. Derivo la consulta a Recursos Humanos.")
        print(f"Estado final: {estado}")
        return

    if dias_solicitados > colaborador.dias_disponibles:
        estado = EstadoBot.RECHAZADA
        observacion = "Saldo insuficiente"
        id_solicitud = generar_id_solicitud(solicitudes)
        fecha_fin = calcular_fecha_fin(fecha_inicio, dias_solicitados)
        guardar_solicitud(id_solicitud, legajo, fecha_inicio, dias_solicitados, fecha_fin, estado, observacion)
        print(f"Bot: Solicitaste {dias_solicitados} dias y tenes {colaborador.dias_disponibles} disponibles.")
        print(f"Bot: Solicitud {id_solicitud} registrada como {estado}.")
        print(f"Estado final: {estado}")
        return

    fecha_fin = calcular_fecha_fin(fecha_inicio, dias_solicitados)
    hay_conflicto = existe_conflicto_cobertura(colaborador, fecha_inicio, fecha_fin, colaboradores, solicitudes)
    id_solicitud = generar_id_solicitud(solicitudes)

    if hay_conflicto:
        print("Bot: Detecte una posible superposicion de ausencias en el area/proyecto.")
        print("Bot: La solicitud requiere aprobacion del responsable.")
        decision = input("Simulacion - El responsable aprueba la solicitud? (si/no): ").strip().lower()
        if decision in {"si", "s"}:
            estado = EstadoBot.APROBADA
            observacion = "Aprobada por responsable ante conflicto de cobertura"
        else:
            estado = EstadoBot.RECHAZADA
            observacion = "Rechazada por responsable por conflicto de cobertura"
    else:
        estado = EstadoBot.APROBADA
        observacion = "Sin conflicto de cobertura"

    guardar_solicitud(id_solicitud, legajo, fecha_inicio, dias_solicitados, fecha_fin, estado, observacion)

    print("\nBot: Resultado de la solicitud")
    print(f"- ID: {id_solicitud}")
    print(f"- Colaborador: {colaborador.nombre}")
    print(f"- Fecha inicio: {formatear_fecha(fecha_inicio)}")
    print(f"- Fecha fin: {formatear_fecha(fecha_fin)}")
    print(f"- Dias solicitados: {dias_solicitados}")
    print(f"- Estado final: {estado}")
    print(f"- Observacion: {observacion}")


if __name__ == "__main__":
    simular_chatbot()
