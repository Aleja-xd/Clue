"""
crime_case.py

Interfaz de datos para un caso criminal de lógica de predicados.
Cada archivo en crimes/ debe exponer una instancia de CrimeCase como variable CASE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from src.predicate_logic import ExistsGoal, ForallGoal, KnowledgeBase, Predicate


@dataclass
class QuerySpec:
    """Una consulta de investigación: descripción en lenguaje natural y objetivo lógico."""

    description: str
    goal: Predicate | ExistsGoal | ForallGoal


@dataclass
class CrimeCase:
    """
    Un caso criminal completo, autocontenido.

    Campos:
        id          Identificador único del caso (ej: "veneno_villa_espinas").
        title       Título del caso.
        description Descripción narrativa del caso (resumen breve).
        create_kb   Función que construye y retorna la KnowledgeBase.
        queries     Consultas que los investigadores deben resolver.
        suspects    Tupla de claves de sospechosos (constantes del KB).
        narrative   Narrativa completa del caso (docstring del módulo).
        scene       (Obsoleto) Descripción del lugar — mantener por compatibilidad.
        characters  (Obsoleto) Diccionario de personajes — mantener por compatibilidad.

    Cada crimes/*.py expone su caso como variable de módulo CASE:
        from crimes.veneno_villa_espinas import CASE
    """

    id: str
    title: str
    description: str
    create_kb: Callable[[], KnowledgeBase]
    queries: tuple[QuerySpec, ...]
    suspects: tuple[str, ...] = field(default_factory=tuple)
    narrative: str = ""
    scene: dict = field(default_factory=dict)
    characters: dict = field(default_factory=dict)
