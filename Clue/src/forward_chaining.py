"""
forward_chaining.py

Motor de forward chaining (encadenamiento hacia adelante) sobre clausulas de Horn.
Se usa para clasificacion de sospechosos: dado un conjunto de hechos, derivar nuevos hechos. 
"""

from __future__ import annotations

from dataclasses import dataclass

from src.predicate_logic import (
    ExistsGoal,
    ForallGoal,
    KnowledgeBase,
    Predicate,
    Rule,
    Term,
    apply_substitution,
    unify,
)


@dataclass(frozen=True)
class DerivationStep:
    """Un paso individual en una derivacion."""

    description: str
    rule_name: str
    fact_derived: Predicate
    iteration: int
    depth: int = 0


@dataclass(frozen=True)
class ForwardResult:
    """Resultado completo de forward chaining."""

    derived_facts: frozenset[Predicate]
    steps: tuple[DerivationStep, ...]
    iterations: int



def forward_chain(kb: KnowledgeBase) -> ForwardResult:
    """
    Deriva todos los hechos posibles a partir de la KB usando forward chaining.

    Algoritmo:
    1. Empezar con los hechos conocidos.
    2. Para cada regla, intentar satisfacer todos los predicados del cuerpo
       con hechos conocidos (usando unificacion).
    3. Si se satisface el cuerpo completo, agregar la cabeza como nuevo hecho.
    4. Repetir hasta que no se puedan derivar nuevos hechos (punto fijo).

    Args:
        kb: Base de conocimiento con hechos y reglas.

    Returns:
        ForwardResult con todos los predicados derivados y pasos de razonamiento.

    Ejemplo:
        >>> kb = KnowledgeBase()
        >>> kb.add_fact(Predicate('persona', (Term('mayordomo'),)))
        >>> kb.add_fact(Predicate('tiene_motivo', (Term('mayordomo'),)))
        >>> kb.add_fact(Predicate('tiene_oportunidad', (Term('mayordomo'),)))
        >>> kb.add_rule(Rule(
        ...     head=Predicate('sospechoso', (Term('X'),)),
        ...     body=(
        ...         Predicate('persona', (Term('X'),)),
        ...         Predicate('tiene_motivo', (Term('X'),)),
        ...         Predicate('tiene_oportunidad', (Term('X'),)),
        ...     )
        ... ))
        >>> result = forward_chain(kb)
        >>> Predicate('sospechoso', (Term('mayordomo'),)) in result.derived_facts
        True
    """
    # Conjunto de hechos conocidos
    known_facts: set[Predicate] = {f.predicate for f in kb.facts}
    steps: list[DerivationStep] = []

    changed = True
    iteration = 0
    max_iterations = 100

    while changed and iteration < max_iterations:
        changed = False
        iteration += 1

        for rule in kb.rules:
            # Intentar satisfacer el cuerpo de la regla
            new_predicates = _match_rule(rule, known_facts)

            for new_pred in new_predicates:
                if new_pred not in known_facts:
                    known_facts.add(new_pred)
                    steps.append(
                        DerivationStep(
                            description=(
                                f"Derivado {new_pred} usando regla {rule.head.name}"
                            ),
                            rule_name=rule.head.name,
                            fact_derived=new_pred,
                            iteration=iteration,
                        )
                    )
                    changed = True

    return ForwardResult(
        derived_facts=frozenset(known_facts),
        steps=tuple(steps),
        iterations=iteration,
    )


def _match_rule(
    rule: Rule,
    known_facts: set[Predicate],
) -> list[Predicate]:
    """
    Intenta satisfacer todos los predicados del cuerpo de una regla.

    Retorna una lista de instancias de la cabeza para cada forma de
    satisfacer el cuerpo completo.
    """
    # Recolectar todas las sustituciones que satisfacen el cuerpo
    substitutions = _satisfy_body(rule.body, 0, {}, known_facts)

    results = []
    for subst in substitutions:
        head_instance = apply_substitution(rule.head, subst)
        # Solo agregar si todos los argumentos son constantes (ground)
        if all(not arg.is_variable for arg in head_instance.args):
            results.append(head_instance)

    return results


def _satisfy_body(
    body: tuple,
    index: int,
    current_subst: dict[str, Term],
    known_facts: set[Predicate],
) -> list[dict[str, Term]]:
    """
    Recursivamente satisface cada predicado del cuerpo.

    Retorna todas las sustituciones posibles que satisfacen todos
    los predicados del cuerpo desde el indice dado.
    """
    if index >= len(body):
        return [dict(current_subst)]

    goal = body[index]

    # ─── Cuantificador existencial en cuerpo de regla ────────────
    if isinstance(goal, ExistsGoal):
        # Existe X tal que goal.predicate(X) — buscar al menos un hecho
        target = apply_substitution(goal.predicate, current_subst)
        results: list[dict[str, Term]] = []
        for fact in known_facts:
            subst = unify(target, fact)
            if subst is not None:
                combined = dict(current_subst)
                combined.update(subst)
                sub_results = _satisfy_body(body, index + 1, combined, known_facts)
                results.extend(sub_results)
        return results

    # ─── Cuantificador universal en cuerpo de regla ──────────────
    if isinstance(goal, ForallGoal):
        # Para todo X en dominio, propiedad(X) debe ser derivable
        domain_target = apply_substitution(goal.domain, current_subst)
        domain_bindings: list[dict[str, Term]] = []
        for fact in known_facts:
            subst = unify(domain_target, fact)
            if subst is not None:
                combined = dict(current_subst)
                combined.update(subst)
                domain_bindings.append(combined)
        if not domain_bindings:
            # Vacuamente verdadero
            return _satisfy_body(body, index + 1, current_subst, known_facts)
        for binding in domain_bindings:
            prop_target = apply_substitution(goal.prop, binding)
            if not any(unify(prop_target, fact) is not None for fact in known_facts):
                return []  # Hay un elemento del dominio que no satisface la propiedad
        return _satisfy_body(body, index + 1, current_subst, known_facts)

    target = apply_substitution(goal, current_subst)
    results: list[dict[str, Term]] = []

    for fact in known_facts:
        subst = unify(target, fact)
        if subst is not None:
            # Combinar sustituciones
            combined = dict(current_subst)
            combined.update(subst)
            # Recursivamente satisfacer el resto del cuerpo
            sub_results = _satisfy_body(body, index + 1, combined, known_facts)
            results.extend(sub_results)

    return results


# ─── Interactive Wizard ────────────────────────────────────────────────────────


class ForwardWizard:
    """
    Forward chaining interactivo paso a paso para la TUI.

    El usuario ve qué reglas pueden dispararse y elige cuál aplicar.
    """

    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb
        self.known: set[Predicate] = {f.predicate for f in kb.facts}
        self.derived: list[tuple[Rule, Predicate]] = []
        self.log: list[str] = []

    def applicable(self) -> list[tuple[Rule, Predicate]]:
        seen: set[str] = set()
        results: list[tuple[Rule, Predicate]] = []
        for rule in self.kb.rules:
            for pred in _match_rule(rule, self.known):
                key = repr(pred)
                if pred not in self.known and key not in seen:
                    results.append((rule, pred))
                    seen.add(key)
        return results

    def apply(self, rule: Rule, fact: Predicate) -> None:
        self.known.add(fact)
        self.derived.append((rule, fact))
        self.log.append(f"+ {fact}  [via {rule.head.name}]")

    def apply_all(self) -> int:
        items = self.applicable()
        for rule, fact in items:
            if fact not in self.known:
                self.apply(rule, fact)
        return len(items)

    def is_complete(self) -> bool:
        return not self.applicable()

    def known_by_source(self) -> tuple[list[Predicate], list[Predicate]]:
        base_set = {f.predicate for f in self.kb.facts}
        base = sorted(base_set, key=repr)
        derived = [fact for _, fact in self.derived]
        return base, derived

    def suspect_statuses(self, char_keys: list[str]) -> dict[str, str]:
        statuses: dict[str, str] = {}
        for key in char_keys:
            term = Term(key)
            culpable = Predicate("culpable", (term,)) in self.known
            descartado = Predicate("descartado", (term,)) in self.known
            sospechoso = (
                Predicate("sospechoso", (term,)) in self.known
                or Predicate("sospechoso_principal", (term,)) in self.known
                or Predicate("sospechoso_maximo", (term,)) in self.known
            )
            if culpable:
                statuses[key] = "culpable"
            elif descartado:
                statuses[key] = "descartado"
            elif sospechoso:
                statuses[key] = "sospechoso"
            else:
                statuses[key] = "?"
        return statuses

    def rule_label(self, rule: Rule, fact: Predicate) -> str:
        fact_str = repr(fact)
        if len(fact_str) > 30:
            fact_str = fact_str[:29] + "…"
        n = len(rule.body)
        plural = "cond." if n != 1 else "cond."
        return f"→ {fact_str}  [{n} {plural}]"

    def rule_detail(self, rule: Rule, fact: Predicate) -> str:
        lines = [f"Derivar: {fact}", f"Via regla: {rule.head.name}", "Condiciones:"]
        for b in rule.body:
            lines.append(f"  • {b}")
        return "\n".join(lines)
