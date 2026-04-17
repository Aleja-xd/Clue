"""
red_puerto_sombras.py — La Red del Puerto de las Sombras

En el Puerto Industrial se encontró mercancía ilegal oculta en contenedores declarados como carga vacía.
-El Capitán Herrera tiene registro digital de salida del puerto verificado durante el fin de semana del delito.
-El Inspector Nova tiene documentación oficial de inspecciones realizadas fuera del puerto ese fin de semana.
-El Oficial Duarte firma todos los manifiestos de carga del puerto; sus manifiestos son fraudulentos.
-El Oficial Duarte no tiene coartada verificada.
-El Marinero Pinto tiene acceso irrestricto a la bodega de contenedores; fue visto introduciendo mercancía ilegal.
-El Marinero Pinto no tiene coartada verificada.
-El Oficial Duarte y el Marinero Pinto pertenecen al mismo cartel portuario.
-Un informante reportó al Oficial Duarte y al Marinero Pinto por nombre.
-El Capitán Herrera acusa al Oficial Duarte.
-El Oficial Duarte declara que el Marinero Pinto no estuvo en el puerto ese fin de semana.
-El Marinero Pinto declara que el Oficial Duarte firmó los documentos por error administrativo.

Como detective, he llegado a las siguientes conclusiones:
- Quien tiene registro oficial que lo ubica fuera del puerto durante el delito está descartado.
- Quien firma manifiestos de carga fraudulentos comete fraude documental.
- Quien tiene acceso a la bodega y fue visto introduciendo mercancía ilegal introduce contrabando.
- Quien comete fraude documental sin coartada es culpable.
- Quien introduce contrabando sin coartada es culpable.
- Dos personas comparten red si pertenecen al mismo cartel.
- Si dos culpables comparten red, su actividad constituye una operación conjunta.
- El testimonio de una persona descartada contra alguien es confiable.
Una red está activa si al menos uno de sus miembros es culpable.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, ForallGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo.
    No se hizo uso de IA para construir esta KB, se realizo siguiendo la narrativa y las conclusiones del caso.
    """
    kb = KnowledgeBase()

    # Constantes del caso
    capitan_herrera   = Term("capitan_herrera")
    oficial_duarte    = Term("oficial_duarte")
    marinero_pinto    = Term("marinero_pinto")
    inspector_nova    = Term("inspector_nova")
    cartel_portuario  = Term("cartel_portuario")

    # === YOUR CODE HERE ===
    kb.add_fact(Predicate("fuera_puerto", (capitan_herrera,)))
    kb.add_fact(Predicate("fuera_puerto", (inspector_nova,)))
    kb.add_fact(Predicate("firma_manifiestos_fraudulentos", (oficial_duarte,)))
    kb.add_fact(Predicate("coartada_no_verificada", (oficial_duarte,)))
    kb.add_fact(Predicate("acceso_a_bodega", (marinero_pinto,)))
    kb.add_fact(Predicate("visto_introduciendo_ilegal", (marinero_pinto,)))
    kb.add_fact(Predicate("coartada_no_verificada", (marinero_pinto,)))
    kb.add_fact(Predicate("pertenece", (oficial_duarte, cartel_portuario)))
    kb.add_fact(Predicate("pertenece", (marinero_pinto, cartel_portuario)))
    kb.add_fact(Predicate("reportado_informante", (oficial_duarte,)))
    kb.add_fact(Predicate("reportado_informante", (marinero_pinto,)))
    kb.add_fact(Predicate("acusa", (capitan_herrera, oficial_duarte)))
    kb.add_fact(Predicate("da_coartada", (oficial_duarte, marinero_pinto))) 
    kb.add_fact(Predicate("da_excusa", (marinero_pinto, oficial_duarte))) 
    
    
    kb.add_rule(Rule(
        head=Predicate("descartado", (Term("$X"),)),
        body=(
            Predicate("fuera_puerto", (Term("$X"),)),
        )
    ))

    kb.add_rule(Rule(
        head=Predicate("fraude_documental", (Term("$X"),)),
        body=(
            Predicate("firma_manifiestos_fraudulentos", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("introduce_contrabando", (Term("$X"),)),
        body=(
            Predicate("acceso_a_bodega", (Term("$X"),)),
            Predicate("visto_introduciendo_ilegal", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("culpable", (Term("$X"),)),
        body=(
            Predicate("fraude_documental", (Term("$X"),)),
            Predicate("coartada_no_verificada", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(  
        head=Predicate("culpable", (Term("$X"),)),
        body=(
            Predicate("introduce_contrabando", (Term("$X"),)),
            Predicate("coartada_no_verificada", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head= Predicate("comparten_red", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("pertenece", (Term("$X"), Term("$R"))),
            Predicate("pertenece", (Term("$Y"), Term("$R"))),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("operacion_conjunta", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("culpable", (Term("$X"),)),
            Predicate("culpable", (Term("$Y"),)),
            Predicate("comparten_red", (Term("$X"), Term("$Y"))),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("testimonio_confiable", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("descartado", (Term("$X"),)),
            Predicate("acusa", (Term("$X"), Term("$Y"))),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("testimonio_confiable", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("descartado", (Term("$X"),)),
            Predicate("da_coartada", (Term("$X"), Term("$Y"))),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("testimonio_confiable", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("descartado", (Term("$X"),)),
            Predicate("da_excusa", (Term("$X"), Term("$Y"))),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("red_activa", (Term("$R"),)),
        body=(
            Predicate("pertenece", (Term("$X"), Term("$R"))),
            Predicate("culpable", (Term("$X"),)),
        )
    ))

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
