"""
logic_core.py

Define el AST (Abstract Syntax Tree) de fórmulas lógicas.
Es la columna vertebral de todo el taller.

Clases principales:
    Formula, Atom, Not, And, Or, Implies, Iff

Funciones principales:
    get_atoms(formula) — extrae todas las proposiciones atómicas
    evaluate(formula, model) — evalúa una fórmula dado un modelo
"""

from __future__ import annotations

from typing import FrozenSet


class Formula:
    """Clase base abstracta para todas las fórmulas lógicas."""

    def evaluate(self, model: dict[str, bool]) -> bool:
        raise NotImplementedError

    def get_atoms(self) -> FrozenSet[str]:
        raise NotImplementedError


class Atom(Formula):
    """
    Proposición atómica.

    Ejemplo:
        >>> Atom('sospechoso_en_cocina')
        Atom('sospechoso_en_cocina')
    """

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, model: dict[str, bool]) -> bool:
        if self.name not in model:
            raise ValueError(
                f"El átomo '{self.name}' no tiene valor en el modelo. "
                f"Átomos disponibles: {sorted(model.keys())}"
            )
        return model[self.name]

    def get_atoms(self) -> FrozenSet[str]:
        return frozenset({self.name})

    def __repr__(self) -> str:
        return f"Atom('{self.name}')"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Atom", self.name))


class Not(Formula):
    """
    Negación.

    Ejemplo:
        >>> Not(Atom('llovía'))
        Not(Atom('llovía'))
    """

    def __init__(self, operand: Formula):
        self.operand = operand

    def evaluate(self, model: dict[str, bool]) -> bool:
        return not self.operand.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.operand.get_atoms()

    def __repr__(self) -> str:
        return f"Not({self.operand!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash(("Not", self.operand))


class And(Formula):
    """
    Conjunción (n-aria).

    Ejemplo:
        >>> And(Atom('p'), Atom('q'))
        And(Atom('p'), Atom('q'))
    """

    def __init__(self, *conjuncts: Formula):
        if len(conjuncts) < 2:
            raise ValueError("And requiere al menos 2 operandos")
        self.conjuncts = tuple(conjuncts)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return all(c.evaluate(model) for c in self.conjuncts)

    def get_atoms(self) -> FrozenSet[str]:
        result: FrozenSet[str] = frozenset()
        for c in self.conjuncts:
            result = result | c.get_atoms()
        return result

    def __repr__(self) -> str:
        args = ", ".join(repr(c) for c in self.conjuncts)
        return f"And({args})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self) -> int:
        return hash(("And", self.conjuncts))


class Or(Formula):
    """
    Disyunción (n-aria).

    Ejemplo:
        >>> Or(Atom('p'), Atom('q'))
        Or(Atom('p'), Atom('q'))
    """

    def __init__(self, *disjuncts: Formula):
        if len(disjuncts) < 2:
            raise ValueError("Or requiere al menos 2 operandos")
        self.disjuncts = tuple(disjuncts)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return any(d.evaluate(model) for d in self.disjuncts)

    def get_atoms(self) -> FrozenSet[str]:
        result: FrozenSet[str] = frozenset()
        for d in self.disjuncts:
            result = result | d.get_atoms()
        return result

    def __repr__(self) -> str:
        args = ", ".join(repr(d) for d in self.disjuncts)
        return f"Or({args})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self) -> int:
        return hash(("Or", self.disjuncts))


class Implies(Formula):
    """
    Implicación.

    Ejemplo:
        >>> Implies(Atom('p'), Atom('q'))
        Implies(Atom('p'), Atom('q'))
    """

    def __init__(self, antecedent: Formula, consequent: Formula):
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model: dict[str, bool]) -> bool:
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.antecedent.get_atoms() | self.consequent.get_atoms()

    def __repr__(self) -> str:
        return f"Implies({self.antecedent!r}, {self.consequent!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Implies)
            and self.antecedent == other.antecedent
            and self.consequent == other.consequent
        )

    def __hash__(self) -> int:
        return hash(("Implies", self.antecedent, self.consequent))


class Iff(Formula):
    """
    Bicondicional.

    Ejemplo:
        >>> Iff(Atom('p'), Atom('q'))
        Iff(Atom('p'), Atom('q'))
    """

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, model: dict[str, bool]) -> bool:
        return self.left.evaluate(model) == self.right.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.left.get_atoms() | self.right.get_atoms()

    def __repr__(self) -> str:
        return f"Iff({self.left!r}, {self.right!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Iff)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self) -> int:
        return hash(("Iff", self.left, self.right))


# ─── Funciones de utilidad ───────────────────────────────────────────


def get_atoms(formula: Formula) -> frozenset[str]:
    """
    Extrae todas las proposiciones atómicas de una fórmula.

    Ejemplo:
        >>> get_atoms(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        frozenset({'p', 'q', 'r'})
    """
    return formula.get_atoms()


def evaluate(formula: Formula, model: dict[str, bool]) -> bool:
    """
    Evalúa una fórmula dado un modelo (diccionario {str: bool}).

    Ejemplo:
        >>> evaluate(And(Atom('p'), Atom('q')), {'p': True, 'q': False})
        False
    """
    return formula.evaluate(model)
