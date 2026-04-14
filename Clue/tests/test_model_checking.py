"""
Tests automaticos para model_checking.py

Se usan estos tests para validar la implementacion.
Ejecutar con: pytest tests/test_model_checking.py -v
"""

from src.logic_core import And, Atom, Iff, Implies, Not, Or
from src.model_checking import (
    check_entailment,
    check_satisfiable,
    check_valid,
    get_all_models,
    truth_table,
)


class TestGetAllModels:
    def test_single_atom(self):
        models = get_all_models({"p"})
        assert len(models) == 2
        values = {m["p"] for m in models}
        assert values == {True, False}

    def test_two_atoms(self):
        models = get_all_models({"p", "q"})
        assert len(models) == 4
        for m in models:
            assert set(m.keys()) == {"p", "q"}

    def test_three_atoms(self):
        models = get_all_models({"p", "q", "r"})
        assert len(models) == 8

    def test_empty_atoms(self):
        models = get_all_models(set())
        assert len(models) == 1
        assert models[0] == {}

    def test_all_combinations_present(self):
        models = get_all_models({"a", "b"})
        combos = {(m["a"], m["b"]) for m in models}
        assert combos == {
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        }


class TestCheckSatisfiable:
    def test_simple_satisfiable(self):
        sat, model = check_satisfiable(Atom("p"))
        assert sat is True
        assert model is not None
        assert model["p"] is True

    def test_contradiction_unsatisfiable(self):
        formula = And(Atom("p"), Not(Atom("p")))
        sat, model = check_satisfiable(formula)
        assert sat is False
        assert model is None

    def test_disjunction_satisfiable(self):
        formula = Or(Atom("p"), Atom("q"))
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model is not None

    def test_complex_satisfiable(self):
        formula = And(Implies(Atom("p"), Atom("q")), Atom("p"))
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model is not None
        assert model["p"] is True
        assert model["q"] is True


class TestCheckValid:
    def test_tautology(self):
        formula = Or(Atom("p"), Not(Atom("p")))
        assert check_valid(formula) is True

    def test_not_tautology(self):
        assert check_valid(Atom("p")) is False

    def test_implication_tautology(self):
        formula = Implies(Atom("p"), Atom("p"))
        assert check_valid(formula) is True

    def test_double_negation_tautology(self):
        formula = Iff(Atom("p"), Not(Not(Atom("p"))))
        assert check_valid(formula) is True

    def test_modus_ponens_tautology(self):
        formula = Implies(
            And(Implies(Atom("p"), Atom("q")), Atom("p")),
            Atom("q"),
        )
        assert check_valid(formula) is True


class TestCheckEntailment:
    def test_simple_entailment(self):
        kb = [Implies(Atom("p"), Atom("q")), Atom("p")]
        assert check_entailment(kb, Atom("q")) is True

    def test_no_entailment(self):
        kb = [Implies(Atom("p"), Atom("q"))]
        assert check_entailment(kb, Atom("q")) is False

    def test_contradiction_entails_everything(self):
        kb = [Atom("p"), Not(Atom("p"))]
        assert check_entailment(kb, Atom("q")) is True

    def test_chain_entailment(self):
        kb = [
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Atom("p"),
        ]
        assert check_entailment(kb, Atom("r")) is True

    def test_case_criminal(self):
        """Test basado en el caso criminal del taller."""
        kb = [
            Or(Atom("mayordomo_en_cocina"), Atom("mayordomo_en_biblioteca")),
            Implies(Atom("mayordomo_en_cocina"), Not(Atom("envenenó_copa"))),
            Implies(Not(Atom("llovía")), Not(Atom("jardín_mojado"))),
            Atom("jardín_mojado"),
        ]
        assert check_entailment(kb, Atom("llovía")) is True

    def test_empty_kb(self):
        """Una KB vacia solo implica tautologias."""
        assert check_entailment([], Or(Atom("p"), Not(Atom("p")))) is True
        assert check_entailment([], Atom("p")) is False


class TestTruthTable:
    def test_simple_atom(self):
        table = truth_table(Atom("p"))
        assert len(table) == 2

    def test_conjunction(self):
        table = truth_table(And(Atom("p"), Atom("q")))
        assert len(table) == 4
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 1
        model = true_rows[0][0]
        assert model["p"] is True and model["q"] is True

    def test_implication(self):
        table = truth_table(Implies(Atom("p"), Atom("q")))
        assert len(table) == 4
        false_rows = [(m, r) for m, r in table if not r]
        assert len(false_rows) == 1
        model = false_rows[0][0]
        assert model["p"] is True and model["q"] is False

    def test_three_atoms(self):
        table = truth_table(And(Atom("p"), Atom("q"), Atom("r")))
        assert len(table) == 8
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 1

    def test_biconditional(self):
        """Iff(p, q): verdadero en exactamente 2 de 4 filas."""
        table = truth_table(Iff(Atom("p"), Atom("q")))
        assert len(table) == 4
        true_rows = [(m, r) for m, r in table if r]
        assert len(true_rows) == 2


class TestComplexSatisfiable:
    """Tests de satisfacibilidad con estructuras más complejas."""

    def test_criminal_kb_satisfiable(self):
        """KB del caso criminal debe ser consistente."""
        kb = And(
            Or(Atom("reynaldo_culpable"), Atom("margot_culpable")),
            Implies(Atom("margot_culpable"), Atom("margot_tiene_acceso")),
            Not(Atom("margot_tiene_acceso")),
        )
        sat, model = check_satisfiable(kb)
        assert sat is True
        assert model is not None
        assert model["margot_culpable"] is False
        assert model["reynaldo_culpable"] is True

    def test_four_atom_satisfiable(self):
        """Fórmula con 4 átomos: cadena de implicaciones + hecho base."""
        formula = And(
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Implies(Atom("r"), Atom("s")),
            Atom("p"),
        )
        sat, model = check_satisfiable(formula)
        assert sat is True
        assert model["p"] is True
        assert model["q"] is True
        assert model["r"] is True
        assert model["s"] is True

    def test_xor_satisfiable(self):
        """XOR(p, q) = (p ∨ q) ∧ ¬(p ∧ q) — exactamente uno verdadero."""
        xor = And(
            Or(Atom("p"), Atom("q")),
            Not(And(Atom("p"), Atom("q"))),
        )
        sat, model = check_satisfiable(xor)
        assert sat is True
        assert model is not None
        # Exactamente uno debe ser verdadero
        assert model["p"] != model["q"]

    def test_xor_has_two_models(self):
        """XOR tiene exactamente 2 modelos satisfacibles de los 4 posibles."""
        xor = And(
            Or(Atom("p"), Atom("q")),
            Not(And(Atom("p"), Atom("q"))),
        )
        table = truth_table(xor)
        true_rows = [m for m, r in table if r]
        assert len(true_rows) == 2


class TestComplexValid:
    """Tests de validez (tautologías) con fórmulas más complejas."""

    def test_de_morgan_tautology(self):
        """De Morgan: ¬(p ∧ q) ↔ (¬p ∨ ¬q)."""
        formula = Iff(
            Not(And(Atom("p"), Atom("q"))),
            Or(Not(Atom("p")), Not(Atom("q"))),
        )
        assert check_valid(formula) is True

    def test_hypothetical_syllogism(self):
        """Silogismo hipotético: (p→q) ∧ (q→r) → (p→r)."""
        formula = Implies(
            And(
                Implies(Atom("p"), Atom("q")),
                Implies(Atom("q"), Atom("r")),
            ),
            Implies(Atom("p"), Atom("r")),
        )
        assert check_valid(formula) is True

    def test_disjunctive_syllogism(self):
        """Silogismo disyuntivo: (p ∨ q) ∧ ¬p → q."""
        formula = Implies(
            And(Or(Atom("p"), Atom("q")), Not(Atom("p"))),
            Atom("q"),
        )
        assert check_valid(formula) is True

    def test_not_tautology_four_atoms(self):
        """(p ∧ q) → (r ∧ s) no es tautología."""
        formula = Implies(
            And(Atom("p"), Atom("q")),
            And(Atom("r"), Atom("s")),
        )
        assert check_valid(formula) is False


class TestComplexEntailment:
    """Tests de consecuencia lógica con cadenas de razonamiento."""

    def test_modus_tollens(self):
        """Modus tollens: p→q, ¬q ⊨ ¬p."""
        kb = [Implies(Atom("p"), Atom("q")), Not(Atom("q"))]
        assert check_entailment(kb, Not(Atom("p"))) is True

    def test_resolution_chain(self):
        """Cadena de resolución: p→q, q→r, r→s, p ⊨ s."""
        kb = [
            Implies(Atom("p"), Atom("q")),
            Implies(Atom("q"), Atom("r")),
            Implies(Atom("r"), Atom("s")),
            Atom("p"),
        ]
        assert check_entailment(kb, Atom("s")) is True

    def test_criminal_reasoning(self):
        """
        Razonamiento del caso criminal:
          - O Reynaldo o Margot son culpables
          - Para envenenar se necesita acceso al armario
          - Margot NO tiene acceso al armario
          ⊨ Reynaldo es culpable
        """
        kb = [
            Or(Atom("reynaldo_culpable"), Atom("margot_culpable")),
            Implies(Atom("margot_culpable"), Atom("margot_tiene_acceso")),
            Not(Atom("margot_tiene_acceso")),
        ]
        assert check_entailment(kb, Atom("reynaldo_culpable")) is True
        assert check_entailment(kb, Atom("margot_culpable")) is False

    def test_alibi_exclusion(self):
        """
        Exclusión por coartada verificada:
          - Si tiene_coartada entonces no_culpable
          - pablo tiene_coartada
          - bernardo tiene_coartada
          ⊨ pablo no es culpable, bernardo no es culpable
        """
        kb = [
            Implies(Atom("pablo_coartada"), Not(Atom("pablo_culpable"))),
            Implies(Atom("bernardo_coartada"), Not(Atom("bernardo_culpable"))),
            Atom("pablo_coartada"),
            Atom("bernardo_coartada"),
        ]
        assert check_entailment(kb, Not(Atom("pablo_culpable"))) is True
        assert check_entailment(kb, Not(Atom("bernardo_culpable"))) is True

    def test_no_entailment_insufficient_evidence(self):
        """Con evidencia insuficiente no se puede concluir culpabilidad."""
        kb = [
            Or(Atom("a_culpable"), Atom("b_culpable")),
        ]
        # No podemos concluir quién específicamente es culpable
        assert check_entailment(kb, Atom("a_culpable")) is False
        assert check_entailment(kb, Atom("b_culpable")) is False
