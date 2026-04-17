"""
veneno_villa_espinas.py — El Veneno de Villa Espinas

La víctima fue encontrada muerta en la biblioteca con arsénico en su copa de vino.
-El frasco de arsénico hallado en la bodega es el arma del crimen.
-Las huellas dactilares de Reynaldo están en ese frasco.
-Pablo estaba podando en el jardín exterior durante toda la noche; no pudo haber accedido a la bodega.
-Bernardo estaba en el garaje durante toda la noche; tampoco pudo haber accedido a la bodega.
-Pablo acusa directamente a Reynaldo.
-Margot declara que Reynaldo estuvo con ella en la cocina toda la noche.
-Reynaldo declara que Margot estuvo con él en la cocina toda la noche.
-Reynaldo no tiene coartada verificada por ningún testigo independiente.

Como detective, he llegado a las siguientes conclusiones:
-Quien tiene huellas en el arma del crimen tiene evidencia directa en su contra.
-Quien estuvo lejos de la escena durante el crimen está descartado como culpable.
-El testimonio de alguien descartado como culpable es confiable.
-Quien tiene evidencia directa en su contra y no tiene coartada verificada es culpable.
-Quien da coartada a un culpable lo está encubriendo.
Si dos personas se dan coartada mutuamente, existe una coartada cruzada entre ellas.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    kb = KnowledgeBase()

    # Constantes del caso
    reynaldo       = Term("reynaldo")
    margot         = Term("margot")
    pablo          = Term("pablo")
    bernardo       = Term("bernardo")
    frasco_arsenico = Term("frasco_arsenico")

    # === YOUR CODE HERE ===
    kb.add_fact(Predicate("arma_crimen", (frasco_arsenico,)))
    kb.add_fact(Predicate("huellas_en", (reynaldo, frasco_arsenico)))
    kb.add_fact(Predicate("estuvo_lejos", (pablo,)))
    kb.add_fact(Predicate("estuvo_lejos", (bernardo,)))
    kb.add_fact(Predicate("acusa", (pablo, reynaldo)))
    kb.add_fact(Predicate("da_coartada", (margot, reynaldo)))   
    kb.add_fact(Predicate("da_coartada", (reynaldo, margot)))
    kb.add_fact(Predicate("coartada_no_verificada", (reynaldo,  )))                                        

    kb.add_rule(Rule(
        head=Predicate("evidencia_directa", (Term("$X"),)),
        body=(
            Predicate("huellas_en", (Term("$X"), Term("$Y"))),
            Predicate("arma_crimen", (Term("$Y"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("descartado", (Term("$X"),)),
        body=(
            Predicate("estuvo_lejos", (Term("$X"),)),
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
        head=Predicate("culpable", (Term("$X"),)),
        body=(
            Predicate("evidencia_directa", (Term("$X"),)),
            Predicate("coartada_no_verificada", (Term("$X"),)),
        )
    ))

    kb.add_rule(Rule(
        head=Predicate("encubridor", (Term("$X"),)),
        body=(
            Predicate("da_coartada", (Term("$X"), Term("$Y"))),
            Predicate("culpable", (Term("$Y"),)),
        )
    ))

    kb.add_rule(Rule(
        head=Predicate("coartada_cruzada", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("da_coartada", (Term("$X"), Term("$Y"))),
            Predicate("da_coartada", (Term("$Y"), Term("$X"))),
        )
    ))
    # === END YOUR CODE ===

    return kb


CASE = CrimeCase(
    id="veneno_villa_espinas",
    title="El Veneno de Villa Espinas",
    suspects=("reynaldo", "margot", "pablo", "bernardo"),
    narrative=__doc__,
    description=(
        "La víctima fue envenenada con arsénico. "
        "El mayordomo tiene las huellas en el frasco y solo cuenta con la coartada de la cocinera, "
        "quien a su vez solo cuenta con la de él. Razona sobre evidencia física, testimonios "
        "confiables y encubrimiento."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Pablo está descartado como culpable?",
            goal=Predicate("descartado", (Term("pablo"),)),
        ),
        QuerySpec(
            description="¿El testimonio de Pablo contra Reynaldo es confiable?",
            goal=Predicate("testimonio_confiable", (Term("pablo"), Term("reynaldo"))),
        ),
        QuerySpec(
            description="¿Reynaldo es culpable?",
            goal=Predicate("culpable", (Term("reynaldo"),)),
        ),
        QuerySpec(
            description="¿Margot está encubriendo al culpable?",
            goal=Predicate("encubridor", (Term("margot"),)),
        ),
        QuerySpec(
            description="¿Existe coartada cruzada entre Margot y Reynaldo?",
            goal=ExistsGoal("$X", Predicate("coartada_cruzada", (Term("$X"), Term("reynaldo")))),
        ),
    ),
)
