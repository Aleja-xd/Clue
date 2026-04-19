"""
crimen_bono.py — Muerte de MissPeackock

Miss Peacock fue encontrada apuñalada en la cocina de su mansión el domingo por la noche. 
-El mayordomo Salas trabajó en la casa durante todo el fin de semana y no tiene coartada fuera de la mansión. 
-La empleada Lucía también permaneció en la mansión durante el fin de semana y tampoco tiene coartada verificable. 
-Tomás Peacock, hijo de la víctima, afirmó haber estado de viaje en otra ciudad y tiene documentación verificable. 
-Elena Peacock, hija de la víctima, asistió a una gala benéfica en Cartagena y existe un registro oficial de su participación y hospedaje. 
-Esos mismos registros muestran que la empleada Lucía también entró a la cocina esa misma noche, pocos minutos después.
-Una cámara del pasillo captó al mayordomo Salas conversando con Lucía cerca de la cocina poco antes del asesinato. 
-La empleada Lucía había sido informada de un inminente despido por robo de joyas, tenia un conflicto laboral. 
-El mayordomo Salas sabía que Miss Peacock planeaba reemplazarlo por un administrador más joven, tenia un conflicto laboral. 


Como detective, he llegado a las siguientes conclusiones: 
-Un registro oficial de viaje o de asistencia a un evento constituye coartada verificada. 
-Quien tiene coartada verificada queda descartado como autor del asesinato. 
-Quien fue captado cerca de la cocina poco antes del crimen estuvo en el lugar de los hechos. 
-Tenía un conflicto laboral directo con la víctima tenía motivo personal.
-Quien sin coartada tiene motivo y estuvo en la escena del crimen es culpable. 
-Si dos personas fueron captadas juntas mutuamente cerca de la escena del crimen, existe una alianza entre ellas. 
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import KnowledgeBase, Predicate, Rule, Term, ExistsGoal


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    
    kb = KnowledgeBase()

    # Constantes del caso
    miss_peacock = Term("miss_peacock")
    mayordomo_salas = Term("mayordomo_salas")
    empleada_lucia = Term("empleada_lucia")
    tomas_peacock = Term("tomas_peacock")
    elena_peacock = Term("elena_peacock")
    cocina = Term("cocina")
    
    kb.add_fact(Predicate("victima", (miss_peacock,)))
    kb.add_fact(Predicate("lugar_crimen", (cocina,)))
    kb.add_fact(Predicate("en_mansion", (mayordomo_salas,)))
    kb.add_fact(Predicate("en_mansion", (empleada_lucia,)))
    kb.add_fact(Predicate("coartada_no_verificada", (mayordomo_salas,)))
    kb.add_fact(Predicate("coartada_no_verificada", (empleada_lucia,)))
    kb.add_fact(Predicate("documentacion_oficial", (tomas_peacock,)))
    kb.add_fact(Predicate("documentacion_oficial", (elena_peacock,)))
    kb.add_fact(Predicate("accedio", (mayordomo_salas, cocina)))
    kb.add_fact(Predicate("accedio", (empleada_lucia, cocina)))
    kb.add_fact(Predicate("captados_juntos", (mayordomo_salas, empleada_lucia, cocina)))
    kb.add_fact(Predicate("captados_juntos", (empleada_lucia, mayordomo_salas, cocina)))
    kb.add_fact(Predicate("conflicto_laboral", (mayordomo_salas,miss_peacock)))
    kb.add_fact(Predicate("conflicto_laboral", (empleada_lucia,miss_peacock)))
   
    kb.add_rule(Rule(
        head=Predicate("coartada_verificada", (Term("$X"),)),
        body=(
            Predicate("documentacion_oficial", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("descartado", (Term("$X"),)),
        body=(
            Predicate("coartada_verificada", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("en_escena", (Term("$X"),)),
        body=(
            Predicate("accedio", (Term("$X"), Term("$Lugar"))),
            Predicate("lugar_crimen", (Term("$Lugar"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("motivo_personal", (Term("$X"),)),
        body=(
            Predicate("conflicto_laboral", (Term("$X"), Term("$Victima"))),
            Predicate("victima", (Term("$Victima"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("culpable", (Term("$X"),)),
        body=(
            Predicate("coartada_no_verificada", (Term("$X"),)),
            Predicate("motivo_personal", (Term("$X"),)),
            Predicate("en_escena", (Term("$X"),)),
        )
    ))
    
    kb.add_rule(Rule(
        head=Predicate("alianza", (Term("$Primero"), Term("$Segundo"))),
        body=(
            Predicate("captados_juntos", (Term("$Primero"), Term("$Segundo"), Term("$LugarAlianza"))),
            Predicate("captados_juntos", (Term("$Segundo"), Term("$Primero"), Term("$LugarAlianza"))),
            Predicate("lugar_crimen", (Term("$LugarAlianza"),)),
        )
    ))

    return kb


CASE = CrimeCase(
    id="asesinato_miss_peacock",
    title="El asesinato de Miss Peacock",
    suspects=("mayordomo_salas", "empleada_lucia", "tomas_peacock", "elena_peacock"),
    narrative=__doc__,
    description=(
        "Miss Peacock fue asesinada en la cocina de su mansión. "
        "El caso gira alrededor de coartadas verificadas, presencia en la escena, "
        "motivos laborales y posible coordinación entre dos culpables."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Tomás está descartado como culpable?",
            goal=Predicate("descartado", (Term("tomas_peacock"),)),
        ),
        QuerySpec(
            description="¿Elena está descartada como culpable?",
            goal=Predicate("descartado", (Term("elena_peacock"),)),
        ),
        QuerySpec(
            description="¿Lucía estuvo en la escena del crimen?",
            goal=Predicate("en_escena", (Term("empleada_lucia"),)),
        ),
        QuerySpec(
            description="¿Salas es culpable?",
            goal=Predicate("culpable", (Term("mayordomo_salas"),)),
        ),
        QuerySpec(
            description="¿Lucía es culpable?",
            goal=Predicate("culpable", (Term("empleada_lucia"),)),
        ),
        QuerySpec(
            description="¿Existe una alianza entre Lucía y alguien más?",
            goal=ExistsGoal(
                "$Socio", Predicate("alianza", (Term("empleada_lucia"), Term("$Socio"))),
            ),
        ),
    ),
)
