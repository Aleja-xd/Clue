"""
utils.py

Utilidades: pretty print de fórmulas, visualización de tablas de verdad,
y funciones auxiliares para el taller.
"""

from __future__ import annotations

from src.logic_core import (
    And,
    Atom,
    Formula,
    Iff,
    Implies,
    Not,
    Or,
    evaluate,
    get_atoms,
)


def formula_to_string(formula: Formula) -> str:
    """
    Convierte una fórmula a notación infija legible.

    Ejemplo:
        >>> formula_to_string(Implies(Atom('p'), Not(Atom('q'))))
        '(p → ¬q)'
    """
    if isinstance(formula, Atom):
        return formula.name

    if isinstance(formula, Not):
        inner = formula_to_string(formula.operand)
        return f"¬{inner}"

    if isinstance(formula, And):
        parts = " ∧ ".join(formula_to_string(c) for c in formula.conjuncts)
        return f"({parts})"

    if isinstance(formula, Or):
        parts = " ∨ ".join(formula_to_string(d) for d in formula.disjuncts)
        return f"({parts})"

    if isinstance(formula, Implies):
        ant = formula_to_string(formula.antecedent)
        con = formula_to_string(formula.consequent)
        return f"({ant} → {con})"

    if isinstance(formula, Iff):
        left = formula_to_string(formula.left)
        right = formula_to_string(formula.right)
        return f"({left} ↔ {right})"

    return repr(formula)


def print_truth_table(formula: Formula) -> None:
    """
    Imprime la tabla de verdad completa de una fórmula.

    Ejemplo:
        >>> print_truth_table(Implies(Atom('p'), Atom('q')))
        | p     | q     | (p → q) |
        |-------|-------|---------|
        | True  | True  | True    |
        | True  | False | False   |
        | False | True  | True    |
        | False | False | True    |
    """
    atoms = sorted(get_atoms(formula))
    formula_str = formula_to_string(formula)

    # Calcular anchos de columna
    col_widths = {a: max(len(a), 5) for a in atoms}
    formula_width = max(len(formula_str), 5)

    # Header
    header_parts = [f" {a:<{col_widths[a]}} " for a in atoms]
    header_parts.append(f" {formula_str:<{formula_width}} ")
    header = "|" + "|".join(header_parts) + "|"

    separator_parts = ["-" * (col_widths[a] + 2) for a in atoms]
    separator_parts.append("-" * (formula_width + 2))
    separator = "|" + "|".join(separator_parts) + "|"

    print(header)
    print(separator)

    # Generar todas las combinaciones
    n = len(atoms)
    for i in range(2**n):
        model: dict[str, bool] = {}
        for j, atom in enumerate(atoms):
            model[atom] = bool((i >> (n - 1 - j)) & 1)

        result = evaluate(formula, model)

        row_parts = [f" {str(model[a]):<{col_widths[a]}} " for a in atoms]
        row_parts.append(f" {str(result):<{formula_width}} ")
        print("|" + "|".join(row_parts) + "|")


def format_model(model: dict[str, bool]) -> str:
    """
    Formatea un modelo de forma legible.

    Ejemplo:
        >>> format_model({'p': True, 'q': False, 'r': True})
        '{p = V, q = F, r = V}'
    """
    parts = []
    for atom in sorted(model.keys()):
        val = "V" if model[atom] else "F"
        parts.append(f"{atom} = {val}")
    return "{" + ", ".join(parts) + "}"


def format_kb(formulas: list[Formula]) -> str:
    """
    Formatea una base de conocimiento como lista numerada.

    Ejemplo:
        >>> format_kb([Atom('p'), Implies(Atom('p'), Atom('q'))])
        '1. p\\n2. (p → q)'
    """
    lines = []
    for i, f in enumerate(formulas, 1):
        lines.append(f"{i}. {formula_to_string(f)}")
    return "\n".join(lines)
