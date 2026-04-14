"""
backward_chaining.py

Motor de backward chaining (encadenamiento hacia atras) sobre clausulas de Horn.
Se usa para diagnostico: dado un objetivo, buscar la cadena de evidencia.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

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
class BackwardResult:
    """Resultado completo de backward chaining."""

    success: bool
    substitutions: tuple[dict[str, Term], ...]
    proof_steps: tuple[str, ...]
    query: object  # Predicate | ExistsGoal | ForallGoal



def backward_chain(
    kb: KnowledgeBase,
    query: Predicate | ExistsGoal | ForallGoal,
) -> BackwardResult:
    """
    Intenta probar la query encadenando hacia atras.

    Algoritmo:
    1. Buscar si la query unifica con algun hecho conocido.
    2. Si no, buscar reglas cuya cabeza unifique con la query.
    3. Para cada regla encontrada, intentar probar cada predicado del cuerpo.
    4. Si se prueban todos los predicados del cuerpo, la query es verdadera.

    Args:
        kb: Base de conocimiento con hechos y reglas.
        query: Predicado a probar.

    Returns:
        BackwardResult con exito/fracaso, sustituciones y pasos de prueba.

    Ejemplo:
        >>> kb = KnowledgeBase()
        >>> kb.add_fact(Predicate('tiene_motivo', (Term('mayordomo'),)))
        >>> kb.add_fact(Predicate('tiene_oportunidad', (Term('mayordomo'),)))
        >>> kb.add_rule(Rule(
        ...     head=Predicate('sospechoso', (Term('X'),)),
        ...     body=(
        ...         Predicate('tiene_motivo', (Term('X'),)),
        ...         Predicate('tiene_oportunidad', (Term('X'),)),
        ...     )
        ... ))
        >>> result = backward_chain(kb, Predicate('sospechoso', (Term('X'),)))
        >>> result.success
        True
    """
    steps: list[str] = []
    visited: set[str] = set()
    results = _prove(kb, query, {}, steps, visited, depth=0)

    return BackwardResult(
        success=len(results) > 0,
        substitutions=tuple(results),
        proof_steps=tuple(steps),
        query=query,
    )


def _prove(
    kb: KnowledgeBase,
    goal: Predicate | ExistsGoal | ForallGoal,
    current_subst: dict[str, Term],
    steps: list[str],
    visited: set[str],
    depth: int,
) -> list[dict[str, Term]]:
    """Recursivamente intenta probar un objetivo."""
    indent = "  " * depth

    # ─── Cuantificador existencial ────────────────────────────────
    if isinstance(goal, ExistsGoal):
        steps.append(f"{indent}? Existencial: {goal}")
        results = _prove(kb, goal.predicate, current_subst, steps, visited, depth)
        steps.append(f"{indent}>> Existe: {'Sí' if results else 'No'}")
        return results

    # ─── Cuantificador universal ──────────────────────────────────
    if isinstance(goal, ForallGoal):
        steps.append(f"{indent}? Universal: {goal}")
        domain_results = _prove(kb, goal.domain, current_subst, steps, visited, depth)
        if not domain_results:
            # Vacuamente verdadero: ningún elemento en el dominio
            steps.append(f"{indent}>> ∀ vacuamente verdadero (dominio vacío)")
            return [dict(current_subst)]
        for binding in domain_results:
            combined = dict(current_subst)
            combined.update(binding)
            prop_instance = apply_substitution(goal.prop, combined)
            prop_results = _prove(kb, prop_instance, combined, steps, visited, depth)
            if not prop_results:
                value = combined.get(goal.variable, "?")
                steps.append(f"{indent}>> ∀ falló para {goal.variable} = {value}")
                return []
        steps.append(f"{indent}>> ∀ verdadero para todos los elementos del dominio")
        return [dict(current_subst)]

    goal_str = repr(goal)

    # Prevenir ciclos infinitos
    if goal_str in visited:
        steps.append(f"{indent}>> Ciclo detectado: {goal}")
        return []
    visited = visited | {goal_str}

    steps.append(f"{indent}? Intentando probar: {goal}")

    results: list[dict[str, Term]] = []

    # Paso 1: Buscar hechos que unifiquen
    for fact in kb.facts:
        subst = unify(goal, fact.predicate)
        if subst is not None:
            combined = dict(current_subst)
            combined.update(subst)
            steps.append(f"{indent}>> Unifica con hecho: {fact.predicate}")
            results.append(combined)

    # Paso 2: Buscar reglas cuya cabeza unifique
    for rule in kb.rules:
        # Renombrar variables de la regla para evitar colisiones
        renamed_rule = _rename_variables(rule, depth)
        subst = unify(goal, renamed_rule.head)

        if subst is None:
            continue

        steps.append(f"{indent}-> Probando regla: {rule}")

        combined = dict(current_subst)
        combined.update(subst)

        # Intentar probar cada predicado del cuerpo
        body_results = _prove_body(
            kb, renamed_rule.body, 0, combined, steps, visited, depth + 1
        )

        results.extend(body_results)

    return results


def _prove_body(
    kb: KnowledgeBase,
    body: tuple,
    index: int,
    current_subst: dict[str, Term],
    steps: list[str],
    visited: set[str],
    depth: int,
) -> list[dict[str, Term]]:
    """Recursivamente prueba cada predicado del cuerpo de una regla."""
    if index >= len(body):
        return [dict(current_subst)]

    goal = body[index]
    results: list[dict[str, Term]] = []

    # Cuantificadores en el cuerpo de una regla
    if isinstance(goal, (ExistsGoal, ForallGoal)):
        sub_proofs = _prove(kb, goal, current_subst, steps, visited, depth)
        for sub_subst in sub_proofs:
            combined = dict(current_subst)
            combined.update(sub_subst)
            remaining = _prove_body(
                kb, body, index + 1, combined, steps, visited, depth
            )
            results.extend(remaining)
        return results

    target = apply_substitution(goal, current_subst)

    sub_proofs = _prove(kb, target, current_subst, steps, visited, depth)

    for sub_subst in sub_proofs:
        combined = dict(current_subst)
        combined.update(sub_subst)
        remaining = _prove_body(kb, body, index + 1, combined, steps, visited, depth)
        results.extend(remaining)

    return results


def _rename_variables(rule: Rule, depth: int) -> Rule:
    """Renombra variables de una regla añadiendo sufijo _d{depth} para evitar colisiones."""
    var_map: dict[str, str] = {}

    def rename_term(term: Term) -> Term:
        if term.is_variable:
            if term.name not in var_map:
                var_map[term.name] = f"{term.name}_d{depth}"
            return Term(var_map[term.name])
        return term

    def rename_pred(pred: Predicate) -> Predicate:
        new_args = tuple(rename_term(a) for a in pred.args)
        return Predicate(pred.name, new_args)

    new_head = rename_pred(rule.head)
    new_body = tuple(rename_pred(b) for b in rule.body)
    return Rule(head=new_head, body=new_body)


# ─── Interactive Wizard ────────────────────────────────────────────────────────

_uid_counter = itertools.count(1)


def _rename_rule_bw(rule: Rule, uid: int) -> Rule:
    """Renombra variables de una regla con sufijo único para evitar colisiones."""
    var_map: dict[str, str] = {}

    def rename_term(t: Term) -> Term:
        if t.is_variable:
            if t.name not in var_map:
                var_map[t.name] = f"{t.name}_r{uid}"
            return Term(var_map[t.name])
        return t

    def rename_pred(p: Predicate) -> Predicate:
        return Predicate(p.name, tuple(rename_term(a) for a in p.args))

    return Rule(
        head=rename_pred(rule.head),
        body=tuple(rename_pred(b) for b in rule.body),
    )


@dataclass
class GoalNode:
    """Nodo en el árbol de prueba de backward chaining interactivo."""

    goal: Predicate
    status: str = "pending"
    applied_rule: Rule | None = None
    sub_goals: list["GoalNode"] = field(default_factory=list)
    depth: int = 0

    def render_tree(self, indent: int = 0) -> str:
        status_icon = {"pending": "○", "active": "◉", "proven": "✓", "failed": "✗"}.get(self.status, "?")
        prefix = "  " * indent
        lines = [f"{prefix}{status_icon} {self.goal}"]
        if self.applied_rule:
            lines.append(f"{prefix}  └─ via [{self.applied_rule.head.name}(…)]")
        for i, sg in enumerate(self.sub_goals):
            connector = "├─" if i < len(self.sub_goals) - 1 else "└─"
            sub_lines = sg.render_tree(indent + 2).split("\n")
            if sub_lines:
                sub_lines[0] = f"{prefix}  {connector}{sub_lines[0].lstrip()}"
            lines.extend(sub_lines)
        return "\n".join(lines)

    def all_pending(self) -> list["GoalNode"]:
        result: list[GoalNode] = []
        if self.status == "pending":
            result.append(self)
        for sg in self.sub_goals:
            result.extend(sg.all_pending())
        return result

    def propagate_proven(self) -> None:
        if self.sub_goals and all(sg.status == "proven" for sg in self.sub_goals):
            self.status = "proven"


class BackwardWizard:
    """
    Backward chaining interactivo paso a paso para la TUI.

    Uso:
        wiz = BackwardWizard(kb, Predicate('culpable', (Term('X'),)))
        options = wiz.current_options()
        wiz.apply_rule(0)
        # Repetir hasta wiz.is_complete
    """

    def __init__(self, kb: KnowledgeBase, goal: Predicate) -> None:
        self.kb = kb
        self.root = GoalNode(goal=goal, status="active", depth=0)
        self.active_node: GoalNode | None = self.root
        self.log: list[str] = []
        # Pre-compute all derivable facts for variable resolution
        from src.forward_chaining import forward_chain
        result = forward_chain(kb)
        self._all_known: frozenset[Predicate] = frozenset(
            {f.predicate for f in kb.facts} | result.derived_facts
        )

    def is_direct_fact(self, pred: Predicate) -> bool:
        return any(unify(pred, known) is not None for known in self._all_known)

    def matching_rules(self, pred: Predicate) -> list[tuple[Rule, list[Predicate]]]:
        results: list[tuple[Rule, list[Predicate]]] = []
        for rule in self.kb.rules:
            uid = next(_uid_counter)
            renamed = _rename_rule_bw(rule, uid)
            subst = unify(pred, renamed.head)
            if subst is None:
                continue
            # Apply initial substitution to body
            sub_goals = [apply_substitution(b, subst) for b in renamed.body]
            # Iteratively resolve remaining variables via known facts
            changed = True
            while changed:
                changed = False
                for i, sg in enumerate(sub_goals):
                    if not any(arg.is_variable for arg in sg.args):
                        continue
                    for known in self._all_known:
                        fact_subst = unify(sg, known)
                        if fact_subst is not None:
                            sub_goals = [apply_substitution(g, fact_subst) for g in sub_goals]
                            changed = True
                            break
            # Only accept if all sub-goals are now ground
            if all(not any(arg.is_variable for arg in sg.args) for sg in sub_goals):
                results.append((rule, sub_goals))
        return results

    def try_prove_as_fact(self) -> bool:
        if self.active_node is None:
            return False
        if self.is_direct_fact(self.active_node.goal):
            self.active_node.status = "proven"
            self.log.append(f"✓ {self.active_node.goal}  [hecho base]")
            self._advance()
            return True
        return False

    def apply_rule(self, rule_idx: int) -> list[GoalNode]:
        if self.active_node is None:
            return []
        options = self.matching_rules(self.active_node.goal)
        if rule_idx >= len(options):
            return []
        rule, sub_goals = options[rule_idx]
        self.active_node.applied_rule = rule
        self.log.append(f"→ {self.active_node.goal}  via [{rule.head.name}]")
        pending_nodes: list[GoalNode] = []
        for sg in sub_goals:
            node = GoalNode(goal=sg, depth=self.active_node.depth + 1)
            if self.is_direct_fact(sg):
                node.status = "proven"
                self.log.append(f"  ✓ {sg}  [hecho base]")
            else:
                pending_nodes.append(node)
            self.active_node.sub_goals.append(node)
        self.active_node.propagate_proven()
        if self.active_node.status == "proven":
            self.log.append(f"✓ {self.active_node.goal}  [probado]")
            self._advance()
        elif pending_nodes:
            self.active_node = pending_nodes[0]
            self.active_node.status = "active"
        return pending_nodes

    def mark_failed(self) -> None:
        if self.active_node:
            self.active_node.status = "failed"
            self.log.append(f"✗ {self.active_node.goal}  [sin prueba]")
            self._advance()

    def _advance(self) -> None:
        pending = self.root.all_pending()
        if pending:
            self.active_node = pending[0]
            self.active_node.status = "active"
        else:
            self.active_node = None
            self.root.propagate_proven()

    @property
    def is_complete(self) -> bool:
        return self.active_node is None

    @property
    def verdict(self) -> bool:
        return self.root.status == "proven"

    def tree_text(self) -> str:
        return self.root.render_tree()

    def current_options(self) -> list[str]:
        if self.active_node is None:
            return []
        options: list[str] = []
        if self.is_direct_fact(self.active_node.goal):
            options.append("✓  Hecho base")
        for i, (rule, sub_goals) in enumerate(self.matching_rules(self.active_node.goal)):
            n = len(sub_goals)
            plural = "condiciones" if n != 1 else "condición"
            options.append(f"[{i + 1}]  {rule.head.name} ← {n} {plural}")
        if not options:
            options.append("✗  Sin opciones")
        return options

    def option_detail(self, idx: int) -> str:
        if self.active_node is None:
            return ""
        offset = 0
        if self.is_direct_fact(self.active_node.goal):
            if idx == 0:
                return f"Probar como hecho base:\n  {self.active_node.goal}"
            offset = 1
        rules = self.matching_rules(self.active_node.goal)
        rule_idx = idx - offset
        if rule_idx < 0 or rule_idx >= len(rules):
            return ""
        rule, sub_goals = rules[rule_idx]
        lines = [f"Regla: {rule.head.name}", "Sub-objetivos a probar:"]
        for sg in sub_goals:
            lines.append(f"  • {sg}")
        return "\n".join(lines)
