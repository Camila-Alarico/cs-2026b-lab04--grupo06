"""Máquina de estados del agente (E3). Cada estado del diagrama diseno/estados.puml existe aquí."""
from enum import Enum


class Estado(str, Enum):
    INICIO = "INICIO"
    DECIDIENDO = "DECIDIENDO"                  # el modelo propone la siguiente decisión
    VALIDANDO_CONTRATO = "VALIDANDO_CONTRATO"  # ¿cumple el protocolo JSON?
    CONTRATO_INVALIDO = "CONTRATO_INVALIDO"
    EVALUANDO_POLITICA = "EVALUANDO_POLITICA"  # ¿el rol puede hacer esto?
    ESPERANDO_APROBACION = "ESPERANDO_APROBACION"  # el humano aprueba o rechaza una edición
    BLOQUEADO = "BLOQUEADO"
    EJECUTANDO = "EJECUTANDO"
    OBSERVANDO = "OBSERVANDO"                  # el resultado (o el error) vuelve al modelo
    LIMITE_ALCANZADO = "LIMITE_ALCANZADO"      # terminal: se agotaron los pasos
    FINALIZADO = "FINALIZADO"                  # terminal: el modelo entregó su resultado


E = Estado
TRANSICIONES = {
    E.INICIO: {E.DECIDIENDO},
    E.DECIDIENDO: {E.VALIDANDO_CONTRATO},
    E.VALIDANDO_CONTRATO: {E.CONTRATO_INVALIDO, E.EVALUANDO_POLITICA, E.FINALIZADO},
    E.CONTRATO_INVALIDO: {E.DECIDIENDO, E.LIMITE_ALCANZADO},
    E.EVALUANDO_POLITICA: {E.EJECUTANDO, E.ESPERANDO_APROBACION, E.BLOQUEADO, E.LIMITE_ALCANZADO},
    E.ESPERANDO_APROBACION: {E.EJECUTANDO, E.BLOQUEADO},
    E.BLOQUEADO: {E.DECIDIENDO},
    E.EJECUTANDO: {E.OBSERVANDO},
    E.OBSERVANDO: {E.DECIDIENDO},
    E.LIMITE_ALCANZADO: set(),
    E.FINALIZADO: set(),
}
