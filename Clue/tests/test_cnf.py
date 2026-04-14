"""
Tests automaticos para cnf_transform.py

Ejecutar con: pytest tests/test_cnf.py -v
"""

from src.logic_core import And, Atom, Iff, Implies, Not, Or, evaluate, get_atoms
from src.cnf_transform import (
    distribute_or_over_and,
    eliminate_double_negation,
    eliminate_iff,
    eliminate_implication,
    flatten,
    push_negation_inward,
    to_cnf,
)


def _is_equivalent(f1, f2):
    """Verifica si dos formulas son logicamente equivalentes."""
    atoms = get_atoms(f1) | get_atoms(f2)
    sorted_atoms = sorted(atoms)
    n = len(sorted_atoms)
    for i in range(2 ** n):
        model = {
            atom: bool((i >> (n - 1 - j)) & 1)
            for j, atom in enumerate(sorted_atoms)
        }
        if evaluate(f1, model) != evaluate(f2, model):
            return False
    return True


class TestEliminateIff:
    def test_simple_iff(self):
        formula = Iff(Atom("p"), Atom("q"))
        result = eliminate_iff(formula)
        assert not _contains_type(result, Iff)
        assert _is_equivalent(formula, result)

    def test_nested_iff(self):
        formula = Iff(Atom("p"), Iff(Atom("q"), Atom("r")))
        result = eliminate_iff(formula)
        assert not _contains_type(result, Iff)
        assert _is_equivalent(formula, result)

    def test_no_iff(self):
        formula = And(Atom("p"), Atom("q"))
        result = eliminate_iff(formula)
        assert result == formula

    def test_iff_inside_not(self):
        formula = Not(Iff(Atom("p"), Atom("q")))
        result = eliminate_iff(formula)
        assert not _contains_type(result, Iff)
        assert _is_equivalent(formula, result)

    def test_iff_inside_and(self):
        formula = And(Iff(Atom("p"), Atom("q")), Atom("r"))
        result = eliminate_iff(formula)
        assert not _contains_type(result, Iff)
        assert _is_equivalent(formula, result)


class TestEliminateImplication:
    def test_simple_implication(self):
        formula = Implies(Atom("p"), Atom("q"))
        result = eliminate_implication(formula)
        assert not _contains_type(result, Implies)
        assert _is_equivalent(formula, result)

    def test_nested_implication(self):
        formula = Implies(Atom("p"), Implies(Atom("q"), Atom("r")))
        result = eliminate_implication(formula)
        assert not _contains_type(result, Implies)
        assert _is_equivalent(formula, result)

    def test_no_implication(self):
        formula = Or(Atom("p"), Not(Atom("q")))
        result = eliminate_implication(formula)
        assert result == formula

    def test_implication_in_and(self):
        formula = And(Implies(Atom("p"), Atom("q")), Atom("r"))
        result = eliminate_implication(formula)
        assert not _contains_type(result, Implies)
        assert _is_equivalent(formula, result)


class TestPushNegationInward:
    def test_de_morgan_and(self):
        """Not(And(p, q)) -> Or(Not(p), Not(q))"""
        formula = Not(And(Atom("p"), Atom("q")))
        result = push_negation_inward(formula)
        assert not _has_negation_over_compound(result)
        assert _is_equivalent(formula, result)

    def test_de_morgan_or(self):
        """Not(Or(p, q)) -> And(Not(p), Not(q))"""
        formula = Not(Or(Atom("p"), Atom("q")))
        result = push_negation_inward(formula)
        assert not _has_negation_over_compound(result)
        assert _is_equivalent(formula, result)

    def test_no_negation(self):
        """And(p, q) sin negacion encima no cambia."""
        formula = And(Atom("p"), Atom("q"))
        result = push_negation_inward(formula)
        assert result == formula

    def test_nested_de_morgan(self):
        """Not(And(p, Not(q))) -> Or(Not(p), q)"""
        formula = Not(And(Atom("p"), Not(Atom("q"))))
        result = push_negation_inward(formula)
        assert not _has_negation_over_compound(result)
        assert _is_equivalent(formula, result)

    def test_deeply_nested(self):
        """Not(Or(And(p, q), r)) -> And(Or(Not(p), Not(q)), Not(r))"""
        formula = Not(Or(And(Atom("p"), Atom("q")), Atom("r")))
        result = push_negation_inward(formula)
        assert not _has_negation_over_compound(result)
        assert _is_equivalent(formula, result)

    def test_nary_de_morgan(self):
        """Not(And(p, q, r)) -> Or(Not(p), Not(q), Not(r))"""
        formula = Not(And(Atom("p"), Atom("q"), Atom("r")))
        result = push_negation_inward(formula)
        assert not _has_negation_over_compound(result)
        assert _is_equivalent(formula, result)


class TestDistributeOrOverAnd:
    def test_simple_distribution(self):
        """Or(p, And(q, r)) -> And(Or(p, q), Or(p, r))"""
        formula = Or(Atom("p"), And(Atom("q"), Atom("r")))
        result = distribute_or_over_and(formula)
        assert _is_equivalent(formula, result)
        assert _is_cnf(result)

    def test_no_distribution_needed(self):
        """Or(p, q) ya es una clausula."""
        formula = Or(Atom("p"), Atom("q"))
        result = distribute_or_over_and(formula)
        assert _is_equivalent(formula, result)

    def test_and_stays(self):
        """And(p, q) ya esta en CNF."""
        formula = And(Atom("p"), Atom("q"))
        result = distribute_or_over_and(formula)
        assert result == formula

    def test_nested_distribution(self):
        """Or(p, And(q, And(r, s))) requiere multiples distribuciones."""
        formula = Or(Atom("p"), And(Atom("q"), And(Atom("r"), Atom("s"))))
        result = distribute_or_over_and(formula)
        assert _is_equivalent(formula, result)

    def test_both_sides_and(self):
        """Or(And(a, b), And(c, d)) -> And(Or(a,c), Or(a,d), Or(b,c), Or(b,d))"""
        formula = Or(And(Atom("a"), Atom("b")), And(Atom("c"), Atom("d")))
        result = distribute_or_over_and(formula)
        assert _is_equivalent(formula, result)
        assert _is_cnf(flatten(result))

    def test_or_with_multiple_and_children(self):
        """Or(And(a,b), c, And(d,e)) tiene DOS hijos And.

        El algoritmo solo detecta el PRIMER And (and_index=0) en cada llamada,
        pero la recursión al final maneja el And restante en 'others'.

        Verificación manual (tabla de verdad parcial) para (a∧b) ∨ c ∨ (d∧e):
        CNF esperado (tras flatten): (a∨c∨d) ∧ (a∨c∨e) ∧ (b∨c∨d) ∧ (b∨c∨e)

          a  b  c  d  e | Original | CNF
          T  T  F  F  F |    T     |  T∧T∧T∧T = T  ✓
          F  F  T  F  F |    T     |  T∧T∧T∧T = T  ✓
          F  F  F  T  T |    T     |  T∧T∧T∧T = T  ✓
          T  F  F  F  F |    F     |  T∧T∧F∧F = F  ✓
          F  T  F  T  F |    F     |  T∧F∧T∧T = F  ✓
        """
        formula = Or(And(Atom("a"), Atom("b")), Atom("c"), And(Atom("d"), Atom("e")))
        result = distribute_or_over_and(formula)
        assert _is_equivalent(formula, result)
        assert _is_cnf(flatten(result))


class TestFlatten:
    def test_flatten_and(self):
        """And(And(a, b), c) -> And(a, b, c)"""
        formula = And(And(Atom("a"), Atom("b")), Atom("c"))
        result = flatten(formula)
        assert isinstance(result, And)
        assert len(result.conjuncts) == 3

    def test_flatten_or(self):
        """Or(Or(a, b), c) -> Or(a, b, c)"""
        formula = Or(Or(Atom("a"), Atom("b")), Atom("c"))
        result = flatten(formula)
        assert isinstance(result, Or)
        assert len(result.disjuncts) == 3

    def test_no_flatten_needed(self):
        """And(a, b) ya esta plano."""
        formula = And(Atom("a"), Atom("b"))
        result = flatten(formula)
        assert result == formula

    def test_deep_nesting(self):
        """And(And(And(a, b), c), d) -> And(a, b, c, d)"""
        formula = And(And(And(Atom("a"), Atom("b")), Atom("c")), Atom("d"))
        result = flatten(formula)
        assert isinstance(result, And)
        assert len(result.conjuncts) == 4

    def test_mixed_nesting(self):
        """And(Or(a, b), And(c, d)) -> And(Or(a, b), c, d)"""
        formula = And(Or(Atom("a"), Atom("b")), And(Atom("c"), Atom("d")))
        result = flatten(formula)
        assert isinstance(result, And)
        assert len(result.conjuncts) == 3

    def test_single_element_after_flatten(self):
        """And(And(a, b)) cuando se aplana resulta en And(a, b)."""
        # Simula un caso donde aplanar reduce a menos nodos
        formula = And(And(Atom("a"), Atom("b")), And(Atom("a"), Atom("b")))
        result = flatten(formula)
        assert isinstance(result, And)
        assert _is_equivalent(formula, result)

    def test_flatten_not(self):
        """Not se recursa correctamente."""
        formula = Not(And(And(Atom("a"), Atom("b")), Atom("c")))
        result = flatten(formula)
        assert isinstance(result, Not)
        inner = result.operand
        assert isinstance(inner, And)
        assert len(inner.conjuncts) == 3


class TestEliminateDoubleNegation:
    def test_double_negation(self):
        formula = Not(Not(Atom("p")))
        result = eliminate_double_negation(formula)
        assert result == Atom("p")

    def test_triple_negation(self):
        formula = Not(Not(Not(Atom("p"))))
        result = eliminate_double_negation(formula)
        assert result == Not(Atom("p"))

    def test_no_double_negation(self):
        formula = Not(Atom("p"))
        result = eliminate_double_negation(formula)
        assert result == Not(Atom("p"))

    def test_nested_double_negation(self):
        formula = And(Not(Not(Atom("p"))), Atom("q"))
        result = eliminate_double_negation(formula)
        assert _is_equivalent(formula, result)
        assert not _has_double_negation(result)


class TestToCNF:
    def test_simple_implication(self):
        formula = Implies(Atom("p"), Atom("q"))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_distribute_or_over_and(self):
        formula = Or(Atom("p"), And(Atom("q"), Atom("r")))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_de_morgan(self):
        formula = Not(And(Atom("p"), Atom("q")))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_complex_formula(self):
        formula = And(
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
        )
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_biconditional(self):
        formula = Iff(Atom("p"), Atom("q"))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_complex_nested(self):
        formula = Not(Implies(Atom("p"), And(Atom("q"), Atom("r"))))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_nested_biconditional_chain(self):
        """Iff(p, Iff(q, r)) — bicondicional anidado con 3 variables."""
        formula = Iff(Atom("p"), Iff(Atom("q"), Atom("r")))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_four_variables_complex(self):
        """(p → q) ∧ (q → r) ∧ (r → s) — cadena de implicaciones."""
        formula = And(
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Implies(Atom("r"), Atom("s")),
        )
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_double_negation_inside_iff(self):
        """Iff(Not(Not(p)), q) — doble negación dentro de bicondicional."""
        formula = Iff(Not(Not(Atom("p"))), Atom("q"))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_criminal_case_knowledge(self):
        """
        KB del caso criminal: culpable si tiene_huellas y sin_coartada.

        Formalización:
          (tiene_huellas → evidencia_directa)
          ∧ (evidencia_directa ∧ sin_coartada → culpable)
          ∧ tiene_huellas ∧ sin_coartada

        CNF esperada: cada implicación se convierte en cláusula,
        todos los conjuntos deben ser cláusulas válidas.
        """
        formula = And(
            Implies(Atom("tiene_huellas"), Atom("evidencia_directa")),
            Implies(
                And(Atom("evidencia_directa"), Atom("sin_coartada")),
                Atom("culpable"),
            ),
            Atom("tiene_huellas"),
            Atom("sin_coartada"),
        )
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_mutual_alibi_structure(self):
        """
        Estructura de coartada cruzada (dos personas se cubren mutuamente):
          (da_coartada_a_margot ↔ da_coartada_a_reynaldo)
        """
        formula = Iff(Atom("da_coartada_margot"), Atom("da_coartada_reynaldo"))
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)

    def test_or_of_three_conjunctions(self):
        """Or(And(a,b), And(c,d), And(e,f)) — distribución con 3 conjunciones."""
        formula = Or(
            And(Atom("a"), Atom("b")),
            And(Atom("c"), Atom("d")),
            And(Atom("e"), Atom("f")),
        )
        cnf = to_cnf(formula)
        assert _is_equivalent(formula, cnf)
        assert _is_cnf(cnf)


# --- Funciones auxiliares para tests ---


def _contains_type(formula, target_type) -> bool:
    """Verifica si una formula contiene un nodo del tipo dado."""
    if isinstance(formula, target_type):
        return True
    if isinstance(formula, Not):
        return _contains_type(formula.operand, target_type)
    if isinstance(formula, And):
        return any(_contains_type(c, target_type) for c in formula.conjuncts)
    if isinstance(formula, Or):
        return any(_contains_type(d, target_type) for d in formula.disjuncts)
    if isinstance(formula, Implies):
        return (_contains_type(formula.antecedent, target_type)
                or _contains_type(formula.consequent, target_type))
    if isinstance(formula, Iff):
        return (_contains_type(formula.left, target_type)
                or _contains_type(formula.right, target_type))
    return False


def _has_double_negation(formula) -> bool:
    """Verifica si una formula tiene doble negacion."""
    if isinstance(formula, Not) and isinstance(formula.operand, Not):
        return True
    if isinstance(formula, Not):
        return _has_double_negation(formula.operand)
    if isinstance(formula, And):
        return any(_has_double_negation(c) for c in formula.conjuncts)
    if isinstance(formula, Or):
        return any(_has_double_negation(d) for d in formula.disjuncts)
    return False


def _has_negation_over_compound(formula) -> bool:
    """Verifica si hay un Not directamente sobre And u Or."""
    if isinstance(formula, Not):
        if isinstance(formula.operand, (And, Or)):
            return True
        return _has_negation_over_compound(formula.operand)
    if isinstance(formula, And):
        return any(_has_negation_over_compound(c) for c in formula.conjuncts)
    if isinstance(formula, Or):
        return any(_has_negation_over_compound(d) for d in formula.disjuncts)
    return False


def _is_literal(formula) -> bool:
    """Verifica si es un literal (atomo o negacion de atomo)."""
    if isinstance(formula, Atom):
        return True
    if isinstance(formula, Not) and isinstance(formula.operand, Atom):
        return True
    return False


def _is_clause(formula) -> bool:
    """Verifica si es una clausula (disyuncion de literales)."""
    if _is_literal(formula):
        return True
    if isinstance(formula, Or):
        return all(_is_literal(d) for d in formula.disjuncts)
    return False


def _is_cnf(formula) -> bool:
    """Verifica si una formula esta en CNF."""
    if _is_clause(formula):
        return True
    if isinstance(formula, And):
        return all(_is_clause(c) for c in formula.conjuncts)
    return False
