"""
cnf_transform.py — Transformaciones a Forma Normal Conjuntiva (CNF).
El pipeline completo to_cnf() llama a todas las transformaciones en orden.
"""

from __future__ import annotations

from src.logic_core import And, Atom, Formula, Not, Or, Iff, Implies


# --- FUNCION GUÍA SUMINISTRADA COMPLETA ---


def eliminate_double_negation(formula: Formula) -> Formula:
    """
    Elimina dobles negaciones recursivamente.

    Transformacion:
        Not(Not(a)) -> a

    Se aplica recursivamente hasta que no queden dobles negaciones.

    Ejemplo:
        >>> eliminate_double_negation(Not(Not(Atom('p'))))
        Atom('p')
        >>> eliminate_double_negation(Not(Not(Not(Atom('p')))))
        Not(Atom('p'))
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        if isinstance(formula.operand, Not):
            return eliminate_double_negation(formula.operand.operand)
        return Not(eliminate_double_negation(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_double_negation(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_double_negation(d) for d in formula.disjuncts))
    return formula


# =====================================================================
# VERSION INICIAL (escrita de forma autónoma, antes de usar la IA)
# =====================================================================
# Esta fue mi primera aproximación. Funciona para la mayoría de casos
# simples pero tenía varios problemas:
#   - eliminate_iff y eliminate_implication no manejaban el caso Not
#     (en general olvidé que Not también tiene hijos que hay que recorrer).
#   - push_negation_inward lo escribí pensando solo en Not(And(a,b)) de
#     dos argumentos, no para n-arios (el AST del taller usa And/Or n-arios).
#   - distribute_or_over_and asumí que siempre hay exactamente 2 hijos en
#     un Or, así que Or(And(a,b), c, And(d,e)) rompía el caso test
#     test_or_with_multiple_and_children.
#   - flatten no manejaba el caso en que después de aplanar quede un único
#     elemento (And/Or requieren mínimo 2 operandos).
#
# La dejo comentada como registro histórico.
#
# def eliminate_iff(formula):
#     if isinstance(formula, Iff):
#         a = eliminate_iff(formula.left)
#         b = eliminate_iff(formula.right)
#         return And(Implies(a, b), Implies(b, a))
#     if isinstance(formula, And):
#         return And(*(eliminate_iff(c) for c in formula.conjuncts))
#     if isinstance(formula, Or):
#         return Or(*(eliminate_iff(d) for d in formula.disjuncts))
#     if isinstance(formula, Implies):
#         return Implies(eliminate_iff(formula.antecedent),
#                        eliminate_iff(formula.consequent))
#     # <-  me olvidé de Not aquí: un Iff adentro de un Not se quedaba sin eliminar
#     return formula
#
# def eliminate_implication(formula):
#     if isinstance(formula, Implies):
#         a = eliminate_implication(formula.antecedent)
#         b = eliminate_implication(formula.consequent)
#         return Or(Not(a), b)
#     if isinstance(formula, And):
#         return And(*(eliminate_implication(c) for c in formula.conjuncts))
#     if isinstance(formula, Or):
#         return Or(*(eliminate_implication(d) for d in formula.disjuncts))
#     # <- también me olvidé de Not y de Iff aquí
#     return formula
#
# def push_negation_inward(formula):
#     if isinstance(formula, Not):
#         inner = formula.operand
#         if isinstance(inner, And):
#             # asumí solo 2 conjunciones — rompe con And n-arios
#             a, b = inner.conjuncts[0], inner.conjuncts[1]
#             return Or(push_negation_inward(Not(a)),
#                       push_negation_inward(Not(b)))
#         if isinstance(inner, Or):
#             a, b = inner.disjuncts[0], inner.disjuncts[1]
#             return And(push_negation_inward(Not(a)),
#                        push_negation_inward(Not(b)))
#         return formula
#     if isinstance(formula, And):
#         return And(*(push_negation_inward(c) for c in formula.conjuncts))
#     if isinstance(formula, Or):
#         return Or(*(push_negation_inward(d) for d in formula.disjuncts))
#     return formula
#
# def distribute_or_over_and(formula):
#     if isinstance(formula, Or):
#         # solo pensaba en Or binario
#         a = distribute_or_over_and(formula.disjuncts[0])
#         b = distribute_or_over_and(formula.disjuncts[1])
#         if isinstance(a, And):
#             return And(*(distribute_or_over_and(Or(x, b))
#                          for x in a.conjuncts))
#         if isinstance(b, And):
#             return And(*(distribute_or_over_and(Or(a, x))
#                          for x in b.conjuncts))
#         return Or(a, b)
#     if isinstance(formula, And):
#         return And(*(distribute_or_over_and(c) for c in formula.conjuncts))
#     return formula
#
# def flatten(formula):
#     if isinstance(formula, And):
#         nuevos = []
#         for c in formula.conjuncts:
#             c2 = flatten(c)
#             if isinstance(c2, And):
#                 nuevos.extend(c2.conjuncts)
#             else:
#                 nuevos.append(c2)
#         return And(*nuevos)   # ← si nuevos tiene 1 elemento, And falla con ValueError
#     if isinstance(formula, Or):
#         nuevos = []
#         for d in formula.disjuncts:
#             d2 = flatten(d)
#             if isinstance(d2, Or):
#                 nuevos.extend(d2.disjuncts)
#             else:
#                 nuevos.append(d2)
#         return Or(*nuevos)
#     return formula
#
# =====================================================================
# PROMPTS USADOS PARA REFINAR LA VERSION INICIAL
# =====================================================================
#
# Prompt 1:
#   "Tengo estas implementaciones de eliminate_iff y eliminate_implication
#   en Python. El AST tiene And/Or n-arios y también Not, Implies e Iff.
#   ¿Qué casos del AST se me están saltando que harían que una
#   transformación anidada no llegue a un nodo interno?"
#
#
# Prompt 2:
#   "Mi push_negation_inward asume que And/Or son binarios pero el AST
#   los define como n-arios. ¿Cómo lo generalizo manteniendo De Morgan?"
#
#
# Prompt 3:
#   "distribute_or_over_and falla con Or de 3 o más hijos cuando hay
#   varios And (caso Or(And(a,b), c, And(d,e))). ¿Cómo lo hago robusto?"
#
#
# Prompt 4:
#   "En flatten, cuando aplano And(And(a,b)) me queda una lista con solo
#   1 elemento y And(*lista) lanza ValueError porque And requiere ≥2.
#   ¿Cómo lo manejo?"
#
#
# =====================================================================
# VERSION FINAL (activa) — incorpora los arreglos de los 4 prompts
# =====================================================================


# --- FUNCIONES QUE DEBEN IMPLEMENTAR ---


def eliminate_iff(formula: Formula) -> Formula:
    """
    Elimina bicondicionales recursivamente.

    Transformacion:
        Iff(a, b) -> And(Implies(a, b), Implies(b, a))

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_iff(Iff(Atom('p'), Atom('q')))
        And(Implies(Atom('p'), Atom('q')), Implies(Atom('q'), Atom('p')))

    Hint: Usa pattern matching sobre el tipo de la formula.
          Para cada tipo, aplica eliminate_iff recursivamente a los operandos,
          y solo transforma cuando encuentras un Iff.
    """
    # === YOUR CODE HERE ===
    
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_iff(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_iff(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_iff(d) for d in formula.disjuncts))
    if isinstance(formula, Implies):
        return Implies(
            eliminate_iff(formula.antecedent),
            eliminate_iff(formula.consequent),
        )
    if isinstance(formula, Iff):
        left = eliminate_iff(formula.left)
        right = eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))
    return formula
    # === END YOUR CODE ===


def eliminate_implication(formula: Formula) -> Formula:
    """
    Elimina implicaciones recursivamente.

    Transformacion:
        Implies(a, b) -> Or(Not(a), b)

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_implication(Implies(Atom('p'), Atom('q')))
        Or(Not(Atom('p')), Atom('q'))

    Hint: Similar a eliminate_iff. Recorre recursivamente y transforma
          solo los nodos Implies.
    """
    # === YOUR CODE HERE ===
    
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_implication(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_implication(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_implication(d) for d in formula.disjuncts))
    if isinstance(formula, Implies):
        antecedent = eliminate_implication(formula.antecedent)
        consequent = eliminate_implication(formula.consequent)
        return Or(Not(antecedent), consequent)
    if isinstance(formula, Iff):
        return Iff(
            eliminate_implication(formula.left),
            eliminate_implication(formula.right),
        )
    return formula
    # === END YOUR CODE ===


def push_negation_inward(formula: Formula) -> Formula:
    """
    Aplica las leyes de De Morgan y mueve negaciones hacia los atomos.

    Transformaciones:
        Not(And(a, b, ...)) -> Or(Not(a), Not(b), ...)   (De Morgan)
        Not(Or(a, b, ...))  -> And(Not(a), Not(b), ...)   (De Morgan)

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> push_negation_inward(Not(And(Atom('p'), Atom('q'))))
        Or(Not(Atom('p')), Not(Atom('q')))
        >>> push_negation_inward(Not(Or(Atom('p'), Atom('q'))))
        And(Not(Atom('p')), Not(Atom('q')))

    Hint: Cuando encuentres un Not, revisa que hay adentro:
          - Si es Not(And(...)): aplica De Morgan para convertir en Or de negaciones.
          - Si es Not(Or(...)): aplica De Morgan para convertir en And de negaciones.
          - Si es Not(Atom): dejar como esta.
          Para And y Or sin negacion encima, simplemente recursa sobre los hijos.

    Nota: Esta funcion se llama DESPUES de eliminar Iff e Implies,
          asi que no necesitas manejar esos tipos.
    """
    # === YOUR CODE HERE ===
    if isinstance(formula, Atom):
        return formula

    if isinstance(formula, Not):
        inner = formula.operand
        if isinstance(inner, And):
            return push_negation_inward(
                Or(*(Not(c) for c in inner.conjuncts))
            )
        
        if isinstance(inner, Or):
            return push_negation_inward(
                And(*(Not(d) for d in inner.disjuncts))
            )
    
        if isinstance(inner, Not):
            return push_negation_inward(inner.operand)
       
        return formula

    if isinstance(formula, And):
        return And(*(push_negation_inward(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(push_negation_inward(d) for d in formula.disjuncts))

    return formula
    # === END YOUR CODE ===


def distribute_or_over_and(formula: Formula) -> Formula:
    """
    Distribuye Or sobre And para obtener CNF.

    Transformacion:
        Or(A, And(B, C)) -> And(Or(A, B), Or(A, C))

    Debe aplicarse recursivamente hasta que no queden Or que contengan And.

    Ejemplo:
        >>> distribute_or_over_and(Or(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Atom('p'), Atom('q')), Or(Atom('p'), Atom('r')))

    Hint: Para un nodo Or, primero distribuye recursivamente en los hijos.
          Luego busca si algun hijo es un And. Si lo encuentras, aplica la
          distribucion y recursa sobre el resultado (podria haber mas).
          Para And, simplemente recursa sobre cada conjuncion.
          Atomos y Not se retornan sin cambio.

    Nota: Esta funcion se llama DESPUES de mover negaciones hacia adentro,
          asi que solo veras Atom, Not(Atom), And y Or.
    """
    # === YOUR CODE HERE ===
    if isinstance(formula, (Atom, Not)):
        return formula

    if isinstance(formula, And):
        return And(*(distribute_or_over_and(c) for c in formula.conjuncts))

    if isinstance(formula, Or):
        children = [distribute_or_over_and(d) for d in formula.disjuncts]

        and_index = None
        for i, child in enumerate(children):
            if isinstance(child, And):
                and_index = i
                break

        if and_index is None:
            return Or(*children)

        and_child = children[and_index]
        others = children[:and_index] + children[and_index + 1:]

        new_conjuncts = []
        for c in and_child.conjuncts:
            if len(others) == 0:
                new_or: Formula = c
            elif len(others) == 1:
                new_or = Or(c, others[0])
            else:
                new_or = Or(c, *others)
            new_conjuncts.append(distribute_or_over_and(new_or))

        return And(*new_conjuncts)

    return formula
    # === END YOUR CODE ===


def flatten(formula: Formula) -> Formula:
    """
    Aplana conjunciones y disyunciones anidadas.

    Transformaciones:
        And(And(a, b), c) -> And(a, b, c)
        Or(Or(a, b), c)   -> Or(a, b, c)

    Debe aplicarse recursivamente.

    Ejemplo:
        >>> flatten(And(And(Atom('a'), Atom('b')), Atom('c')))
        And(Atom('a'), Atom('b'), Atom('c'))
        >>> flatten(Or(Or(Atom('a'), Atom('b')), Atom('c')))
        Or(Atom('a'), Atom('b'), Atom('c'))

    Hint: Para un And, recorre cada hijo. Si un hijo tambien es And,
          agrega sus conjuncts directamente en vez de agregar el And.
          Igual para Or con sus disjuncts.
          Si al final solo queda 1 elemento, retornalo directamente.
    """
    # === YOUR CODE HERE ===
    if isinstance(formula, Atom):
        return formula

    if isinstance(formula, Not):
        return Not(flatten(formula.operand))

    if isinstance(formula, And):
        flat: list[Formula] = []
        for c in formula.conjuncts:
            c_flat = flatten(c)
            if isinstance(c_flat, And):
                flat.extend(c_flat.conjuncts)
            else:
                flat.append(c_flat)
        if len(flat) == 1:
            return flat[0]
        return And(*flat)

    if isinstance(formula, Or):
        flat_or: list[Formula] = []
        for d in formula.disjuncts:
            d_flat = flatten(d)
            if isinstance(d_flat, Or):
                flat_or.extend(d_flat.disjuncts)
            else:
                flat_or.append(d_flat)
        if len(flat_or) == 1:
            return flat_or[0]
        return Or(*flat_or)

    return formula
    # === END YOUR CODE ===


# --- PIPELINE COMPLETO ---


def to_cnf(formula: Formula) -> Formula:
    """
    [DADO] Pipeline completo de conversion a CNF.

    Aplica todas las transformaciones en el orden correcto:
    1. Eliminar bicondicionales (Iff)
    2. Eliminar implicaciones (Implies)
    3. Mover negaciones hacia adentro (Not)
    4. Eliminar dobles negaciones (Not Not)
    5. Distribuir Or sobre And
    6. Aplanar conjunciones/disyunciones

    Ejemplo:
        >>> to_cnf(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Not(Atom('p')), Atom('q')), Or(Not(Atom('p')), Atom('r')))
    """
    formula = eliminate_iff(formula)
    formula = eliminate_implication(formula)
    formula = push_negation_inward(formula)
    formula = eliminate_double_negation(formula)
    formula = distribute_or_over_and(formula)
    formula = flatten(formula)
    return formula


