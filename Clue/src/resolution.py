"""
resolution.py

Algoritmo de resolución para lógica proposicional.
Se ejecuta para verificar las transformaciones CNF.
"""

from __future__ import annotations

from src.logic_core import And, Atom, Formula, Not, Or
from src.cnf_transform import to_cnf


def formula_to_clauses(cnf_formula: Formula) -> list[frozenset[str]]:
    """
    Convierte una fórmula en CNF a una lista de cláusulas.

    Cada cláusula es un frozenset de literales (strings).
    Literales positivos: 'p', negativos: '~p'.

    Args:
        cnf_formula: Fórmula ya en CNF.

    Returns:
        Lista de cláusulas (frozensets de literales).

    Ejemplo:
        >>> formula_to_clauses(And(Or(Atom('p'), Not(Atom('q'))), Atom('r')))
        [frozenset({'p', '~q'}), frozenset({'r'})]
    """

    def _literal_str(formula: Formula) -> str:
        if isinstance(formula, Atom):
            return formula.name
        if isinstance(formula, Not) and isinstance(formula.operand, Atom):
            return f"~{formula.operand.name}"
        raise ValueError(f"No es un literal válido: {formula!r}")

    def _clause_to_set(formula: Formula) -> frozenset[str]:
        if isinstance(formula, Or):
            return frozenset(_literal_str(d) for d in formula.disjuncts)
        return frozenset({_literal_str(formula)})

    if isinstance(cnf_formula, And):
        return [_clause_to_set(c) for c in cnf_formula.conjuncts]
    return [_clause_to_set(cnf_formula)]


def resolve(clause1: frozenset[str], clause2: frozenset[str]) -> frozenset[str] | None:
    """
    Aplica resolución entre dos cláusulas.

    Busca un par de literales complementarios (p y ~p).
    Si encuentra exactamente uno, retorna la resolvente.
    Si no encuentra o hay más de uno, retorna None.

    Args:
        clause1: Primera cláusula.
        clause2: Segunda cláusula.

    Returns:
        La cláusula resolvente, o None si no se puede resolver.

    Ejemplo:
        >>> resolve(frozenset({'p', 'q'}), frozenset({'~p', 'r'}))
        frozenset({'q', 'r'})
    """
    complementary_pairs = []

    for literal in clause1:
        complement = f"~{literal}" if not literal.startswith("~") else literal[1:]
        if complement in clause2:
            complementary_pairs.append((literal, complement))

    if len(complementary_pairs) != 1:
        return None

    lit, comp = complementary_pairs[0]
    resolvent = (clause1 - {lit}) | (clause2 - {comp})
    return resolvent


def resolution_prove(
    kb_formulas: list[Formula],
    query: Formula,
) -> tuple[bool, list[str]]:
    """
    Prueba por resolución si las fórmulas de la KB implican la query.

    Estrategia: Agrega ¬query a las cláusulas de la KB e intenta
    derivar la cláusula vacía (contradicción).

    Args:
        kb_formulas: Lista de fórmulas de la base de conocimiento.
        query: Fórmula a probar.

    Returns:
        (True, pasos) si la prueba es exitosa (la KB implica la query).
        (False, pasos) si no se puede probar.

    Ejemplo:
        >>> kb = [Implies(Atom('p'), Atom('q')), Atom('p')]
        >>> proved, steps = resolution_prove(kb, Atom('q'))
        >>> proved
        True
    """
    steps: list[str] = []

    # Convertir KB a CNF y extraer cláusulas
    all_clauses: list[frozenset[str]] = []
    for f in kb_formulas:
        cnf = to_cnf(f)
        clauses = formula_to_clauses(cnf)
        for c in clauses:
            all_clauses.append(c)
            steps.append(f"  KB: {_format_clause(c)}")

    # Agregar negación de la query
    negated_query = to_cnf(Not(query))
    neg_clauses = formula_to_clauses(negated_query)
    for c in neg_clauses:
        all_clauses.append(c)
        steps.append(f"  ¬Query: {_format_clause(c)}")

    steps.append("--- Inicio de resolución ---")

    # Algoritmo de resolución
    clause_set = set(all_clauses)
    new_clauses: set[frozenset[str]] = set()

    iteration = 0
    max_iterations = 1000

    while iteration < max_iterations:
        iteration += 1
        clause_list = list(clause_set)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvent = resolve(clause_list[i], clause_list[j])

                if resolvent is None:
                    continue

                step_str = (
                    f"  Resolviendo {_format_clause(clause_list[i])} "
                    f"con {_format_clause(clause_list[j])} "
                    f"→ {_format_clause(resolvent)}"
                )
                steps.append(step_str)

                # Cláusula vacía = contradicción = prueba exitosa
                if len(resolvent) == 0:
                    steps.append("  ¡Cláusula vacía derivada! QED.")
                    return (True, steps)

                new_clauses.add(resolvent)

        # Si no hay cláusulas nuevas, no podemos probar más
        if new_clauses.issubset(clause_set):
            steps.append("  No se pueden derivar nuevas cláusulas.")
            return (False, steps)

        clause_set = clause_set | new_clauses
        new_clauses = set()

    steps.append(f"  Límite de iteraciones alcanzado ({max_iterations}).")
    return (False, steps)


def _format_clause(clause: frozenset[str]) -> str:
    """Formatea una cláusula para impresión."""
    if len(clause) == 0:
        return "□ (vacía)"
    return "{" + ", ".join(sorted(clause)) + "}"
