"""
red_puerto_sombras.py — La Red del Puerto de las Sombras

En el Puerto Industrial se encontró mercancía ilegal oculta en contenedores declarados como carga vacía.
El Capitán Herrera tiene registro digital de salida del puerto verificado durante el fin de semana del delito.
El Inspector Nova tiene documentación oficial de inspecciones realizadas fuera del puerto ese fin de semana.
El Oficial Duarte firma todos los manifiestos de carga del puerto; sus manifiestos son fraudulentos.
El Oficial Duarte no tiene coartada verificada.
El Marinero Pinto tiene acceso irrestricto a la bodega de contenedores; fue visto introduciendo mercancía ilegal.
El Marinero Pinto no tiene coartada verificada.
El Oficial Duarte y el Marinero Pinto pertenecen al mismo cartel portuario.
Un informante reportó al Oficial Duarte y al Marinero Pinto por nombre.
El Capitán Herrera acusa al Oficial Duarte.
El Oficial Duarte declara que el Marinero Pinto no estuvo en el puerto ese fin de semana.
El Marinero Pinto declara que el Oficial Duarte firmó los documentos por error administrativo.

Como detective, he llegado a las siguientes conclusiones:
Quien tiene registro oficial que lo ubica fuera del puerto durante el delito está descartado.
Quien firma manifiestos de carga fraudulentos comete fraude documental.
Quien tiene acceso a la bodega y fue visto introduciendo mercancía ilegal introduce contrabando.
Quien comete fraude documental sin coartada es culpable.
Quien introduce contrabando sin coartada es culpable.
Dos personas comparten red si pertenecen al mismo cartel.
Si dos culpables comparten red, su actividad constituye una operación conjunta.
El testimonio de una persona descartada contra alguien es confiable.
Una red está activa si al menos uno de sus miembros es culpable.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, ForallGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    kb = KnowledgeBase()

    # Constantes del caso
    capitan_herrera   = Term("capitan_herrera")
    oficial_duarte    = Term("oficial_duarte")
    marinero_pinto    = Term("marinero_pinto")
    inspector_nova    = Term("inspector_nova")
    cartel_portuario  = Term("cartel_portuario")

    # === YOUR CODE HERE ===

    # === END YOUR CODE ===

    return kb


CASE = CrimeCase(
    id="red_puerto_sombras",
    title="La Red del Puerto de las Sombras",
    suspects=("capitan_herrera", "oficial_duarte", "marinero_pinto", "inspector_nova"),
    narrative=__doc__,
    description=(
        "Contrabando en el Puerto Industrial: manifiestos fraudulentos y mercancía ilegal. "
        "Dos culpables con roles distintos operan como red. Identifica a ambos, verifica "
        "si su operación es conjunta y si hay redes activas."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Oficial Duarte cometió fraude documental?",
            goal=Predicate("fraude_documental", (Term("oficial_duarte"),)),
        ),
        QuerySpec(
            description="¿Marinero Pinto es culpable?",
            goal=Predicate("culpable", (Term("marinero_pinto"),)),
        ),
        QuerySpec(
            description="¿Hay operación conjunta entre Duarte y Pinto?",
            goal=Predicate("operacion_conjunta", (Term("oficial_duarte"), Term("marinero_pinto"))),
        ),
        QuerySpec(
            description="¿El testimonio del Capitán Herrera contra Duarte es confiable?",
            goal=Predicate("testimonio_confiable", (Term("capitan_herrera"), Term("oficial_duarte"))),
        ),
        QuerySpec(
            description="¿Existe alguna red activa?",
            goal=ExistsGoal("$R", Predicate("red_activa", (Term("$R"),))),
        ),
        QuerySpec(
            description="¿Todo reportado por informante es culpable?",
            goal=ForallGoal(
                "$X",
                Predicate("reportado_informante", (Term("$X"),)),
                Predicate("culpable", (Term("$X"),)),
            ),
        ),
    ),
)
