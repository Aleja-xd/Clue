"""
predicate_logic.py

Motor de lógica de predicados con unificación.
Define términos, predicados, cláusulas de Horn y bases de conocimiento.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    """
    Un término: variable o constante.

    Las variables empiezan con $ ($X, $Y, $Persona).
    Las constantes NO empiezan con $ (mayordomo, cocina, veneno).

    Ejemplo:
        >>> Term('$X')         # Variable
        >>> Term('mayordomo')  # Constante
    """

    name: str

    @property
    def is_variable(self) -> bool:
        return self.name.startswith("$")

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Predicate:
    """
    Un predicado con argumentos.

    Ejemplo:
        >>> Predicate('tiene_motivo', (Term('mayordomo'),))
        tiene_motivo(mayordomo)
    """

    name: str
    args: tuple[Term, ...]

    def __repr__(self) -> str:
        args_str = ", ".join(repr(a) for a in self.args)
        return f"{self.name}({args_str})"


@dataclass(frozen=True)
class Fact:
    """
    Un hecho: predicado sin cuerpo (siempre verdadero).

    Ejemplo:
        >>> Fact(Predicate('persona', (Term('mayordomo'),)))
        persona(mayordomo).
    """

    predicate: Predicate

    def __repr__(self) -> str:
        return f"{self.predicate}."


@dataclass(frozen=True)
class Rule:
    """
    Una regla: head :- body1, body2, ...

    Cláusula de Horn: la cabeza se cumple si todos los predicados del cuerpo se cumplen.

    Ejemplo:
        >>> Rule(
        ...     head=Predicate('sospechoso_principal', (Term('$X'),)),
        ...     body=(
        ...         Predicate('tiene_motivo', (Term('$X'),)),
        ...         Predicate('tiene_oportunidad', (Term('$X'),)),
        ...     )
        ... )
        sospechoso_principal($X) :- tiene_motivo($X), tiene_oportunidad($X).
    """

    head: Predicate
    body: tuple[Predicate, ...]

    def __repr__(self) -> str:
        body_str = ", ".join(repr(b) for b in self.body)
        return f"{self.head} :- {body_str}."


class KnowledgeBase:
    """
    Base de conocimiento: colección de hechos y reglas.

    Ejemplo:
        >>> kb = KnowledgeBase()
        >>> kb.add_fact(Predicate('persona', (Term('mayordomo'),)))
        >>> kb.add_rule(Rule(
        ...     head=Predicate('sospechoso', (Term('$X'),)),
        ...     body=(Predicate('persona', (Term('$X'),)), Predicate('tiene_motivo', (Term('$X'),)))
        ... ))
    """

    def __init__(self) -> None:
        self._facts: list[Fact] = []
        self._rules: list[Rule] = []

    @property
    def facts(self) -> tuple[Fact, ...]:
        return tuple(self._facts)

    @property
    def rules(self) -> tuple[Rule, ...]:
        return tuple(self._rules)

    def add_fact(self, predicate: Predicate) -> None:
        """Agrega un hecho a la base de conocimiento."""
        fact = Fact(predicate) if not isinstance(predicate, Fact) else predicate
        if fact not in self._facts:
            self._facts.append(fact)

    def add_rule(self, rule: Rule) -> None:
        """Agrega una regla a la base de conocimiento."""
        if rule not in self._rules:
            self._rules.append(rule)

    def query_facts(self, name: str) -> list[Fact]:
        """Retorna todos los hechos con el predicado dado."""
        return [f for f in self._facts if f.predicate.name == name]

    def query_rules(self, head_name: str) -> list[Rule]:
        """Retorna todas las reglas cuya cabeza tiene el predicado dado."""
        return [r for r in self._rules if r.head.name == head_name]

    def __repr__(self) -> str:
        lines = ["=== Base de Conocimiento ==="]
        if self._facts:
            lines.append("Hechos:")
            for f in self._facts:
                lines.append(f"  {f}")
        if self._rules:
            lines.append("Reglas:")
            for r in self._rules:
                lines.append(f"  {r}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ExistsGoal:
    """
    Cuantificador existencial: ∃variable. predicate(variable, ...)

    Se cumple si existe al menos un valor del variable que hace
    el predicado verdadero en la base de conocimiento.

    Ejemplo:
        >>> ExistsGoal('$X', Predicate('culpable', (Term('$X'),)))
        ∃$X. culpable($X)
    """

    variable: str
    predicate: Predicate

    def __repr__(self) -> str:
        return f"∃{self.variable}. {self.predicate}"


@dataclass(frozen=True)
class ForallGoal:
    """
    Cuantificador universal: ∀variable. dominio(variable) → propiedad(variable)

    Se cumple si para todo valor del variable que satisface el dominio,
    la propiedad también se cumple.

    Ejemplo:
        >>> ForallGoal(
        ...     '$X',
        ...     Predicate('persona', (Term('$X'),)),
        ...     Predicate('tiene_motivo', (Term('$X'),)),
        ... )
        ∀$X. persona($X) → tiene_motivo($X)
    """

    variable: str
    domain: Predicate
    prop: Predicate

    def __repr__(self) -> str:
        return f"∀{self.variable}. {self.domain} → {self.prop}"


# ─── Unificación ─────────────────────────────────────────────────────

Substitution = dict[str, Term]


def unify(
    pred1: Predicate,
    pred2: Predicate,
) -> Substitution | None:
    """
    Intenta unificar dos predicados.

    Retorna una sustitución (dict de variable → término) si es posible,
    o None si los predicados no son unificables.

    Ejemplo:
        >>> unify(
        ...     Predicate('tiene_motivo', (Term('$X'),)),
        ...     Predicate('tiene_motivo', (Term('mayordomo'),))
        ... )
        {'$X': mayordomo}
    """
    if pred1.name != pred2.name:
        return None
    if len(pred1.args) != len(pred2.args):
        return None

    subst: Substitution = {}

    for arg1, arg2 in zip(pred1.args, pred2.args):
        t1 = _apply_subst_term(arg1, subst)
        t2 = _apply_subst_term(arg2, subst)

        if t1 == t2:
            continue

        if t1.is_variable:
            subst[t1.name] = t2
        elif t2.is_variable:
            subst[t2.name] = t1
        else:
            return None  # Dos constantes distintas

    return subst


def apply_substitution(predicate: Predicate, subst: Substitution) -> Predicate:
    """
    Aplica una sustitución a un predicado.

    Ejemplo:
        >>> apply_substitution(
        ...     Predicate('tiene_motivo', (Term('$X'),)),
        ...     {'$X': Term('mayordomo')}
        ... )
        tiene_motivo(mayordomo)
    """
    new_args = tuple(_apply_subst_term(arg, subst) for arg in predicate.args)
    return Predicate(predicate.name, new_args)


def _apply_subst_term(term: Term, subst: Substitution) -> Term:
    """Aplica una sustitución a un término individual."""
    if term.is_variable and term.name in subst:
        result = subst[term.name]
        # Seguir la cadena de sustitución
        while result.is_variable and result.name in subst:
            result = subst[result.name]
        return result
    return term
