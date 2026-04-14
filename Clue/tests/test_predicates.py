"""
Tests automaticos para los 5 casos criminales resueltos con logica de predicados.

Verifica que backward_chain y forward_chain resuelven correctamente cada caso.
Ejecutar con: pytest tests/test_predicates.py -v
"""

from crimes.herencia_hacienda_rosal import CASE as herencia
from crimes.red_puerto_sombras import CASE as red_puerto
from crimes.robo_expreso_sur import CASE as robo
from crimes.sabotaje_pharmax import CASE as sabotaje
from crimes.veneno_villa_espinas import CASE as veneno
from src.backward_chaining import backward_chain
from src.forward_chaining import forward_chain
from src.predicate_logic import Predicate, Term


# ---------------------------------------------------------------------------
# 1. TestVenenoVillaEspinas
# ---------------------------------------------------------------------------


class TestVenenoVillaEspinas:
    """Backward chaining: 5 queries del caso El Veneno de Villa Espinas."""

    def setup_method(self) -> None:
        self.case = veneno
        self.kb = self.case.create_kb()

    def test_pablo_descartado(self) -> None:
        r = backward_chain(self.kb, self.case.queries[0].goal)
        assert r.success, self.case.queries[0].description

    def test_testimonio_pablo_confiable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[1].goal)
        assert r.success, self.case.queries[1].description

    def test_reynaldo_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[2].goal)
        assert r.success, self.case.queries[2].description

    def test_margot_encubridora(self) -> None:
        r = backward_chain(self.kb, self.case.queries[3].goal)
        assert r.success, self.case.queries[3].description

    def test_coartada_cruzada_existe(self) -> None:
        r = backward_chain(self.kb, self.case.queries[4].goal)
        assert r.success, self.case.queries[4].description


# ---------------------------------------------------------------------------
# 2. TestRoboExpresoSur
# ---------------------------------------------------------------------------


class TestRoboExpresoSur:
    """Backward chaining: 5 queries del caso El Robo en el Expreso del Sur."""

    def setup_method(self) -> None:
        self.case = robo
        self.kb = self.case.create_kb()

    def test_don_rodrigo_descartado(self) -> None:
        r = backward_chain(self.kb, self.case.queries[0].goal)
        assert r.success, self.case.queries[0].description

    def test_acusacion_marquesa_creible(self) -> None:
        r = backward_chain(self.kb, self.case.queries[1].goal)
        assert r.success, self.case.queries[1].description

    def test_elena_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[2].goal)
        assert r.success, self.case.queries[2].description

    def test_victor_defiende_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[3].goal)
        assert r.success, self.case.queries[3].description

    def test_alianza_coartadas_existe(self) -> None:
        r = backward_chain(self.kb, self.case.queries[4].goal)
        assert r.success, self.case.queries[4].description


# ---------------------------------------------------------------------------
# 3. TestSabotajePharmax
# ---------------------------------------------------------------------------


class TestSabotajePharmax:
    """Backward chaining: 5 queries del caso El Sabotaje en Laboratorio Pharmax."""

    def setup_method(self) -> None:
        self.case = sabotaje
        self.kb = self.case.create_kb()

    def test_dra_santos_descartada(self) -> None:
        r = backward_chain(self.kb, self.case.queries[0].goal)
        assert r.success, self.case.queries[0].description

    def test_conflicto_intereses_tec_rios(self) -> None:
        r = backward_chain(self.kb, self.case.queries[1].goal)
        assert r.success, self.case.queries[1].description

    def test_tec_rios_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[2].goal)
        assert r.success, self.case.queries[2].description

    def test_denuncia_informada_mora(self) -> None:
        r = backward_chain(self.kb, self.case.queries[3].goal)
        assert r.success, self.case.queries[3].description

    def test_todo_culpable_tuvo_acceso(self) -> None:
        # Primero verificar que hay al menos un culpable (evita verdad vacua)
        r_culpable = backward_chain(self.kb, Predicate("culpable", (Term("tec_rios"),)))
        assert r_culpable.success, "Debe haber al menos un culpable para que el forall sea significativo"
        r = backward_chain(self.kb, self.case.queries[4].goal)
        assert r.success, self.case.queries[4].description


# ---------------------------------------------------------------------------
# 4. TestHerenciaHaciendaRosal
# ---------------------------------------------------------------------------


class TestHerenciaHaciendaRosal:
    """Backward chaining: 5 queries del caso La Herencia Maldita de Hacienda El Rosal."""

    def setup_method(self) -> None:
        self.case = herencia
        self.kb = self.case.create_kb()

    def test_enfermera_campos_descartada(self) -> None:
        r = backward_chain(self.kb, self.case.queries[0].goal)
        assert r.success, self.case.queries[0].description

    def test_sobrino_esteban_motivo_doble(self) -> None:
        r = backward_chain(self.kb, self.case.queries[1].goal)
        assert r.success, self.case.queries[1].description

    def test_sobrino_esteban_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[2].goal)
        assert r.success, self.case.queries[2].description

    def test_desvio_sospechoso_esteban(self) -> None:
        r = backward_chain(self.kb, self.case.queries[3].goal)
        assert r.success, self.case.queries[3].description

    def test_acusacion_corroborada_restrepo(self) -> None:
        r = backward_chain(self.kb, self.case.queries[4].goal)
        assert r.success, self.case.queries[4].description


# ---------------------------------------------------------------------------
# 5. TestRedPuertoSombras
# ---------------------------------------------------------------------------


class TestRedPuertoSombras:
    """Backward chaining: 6 queries del caso La Red del Puerto de las Sombras."""

    def setup_method(self) -> None:
        self.case = red_puerto
        self.kb = self.case.create_kb()

    def test_fraude_documental_duarte(self) -> None:
        r = backward_chain(self.kb, self.case.queries[0].goal)
        assert r.success, self.case.queries[0].description

    def test_marinero_pinto_culpable(self) -> None:
        r = backward_chain(self.kb, self.case.queries[1].goal)
        assert r.success, self.case.queries[1].description

    def test_operacion_conjunta_duarte_pinto(self) -> None:
        r = backward_chain(self.kb, self.case.queries[2].goal)
        assert r.success, self.case.queries[2].description

    def test_testimonio_confiable_herrera(self) -> None:
        r = backward_chain(self.kb, self.case.queries[3].goal)
        assert r.success, self.case.queries[3].description

    def test_red_activa_existe(self) -> None:
        r = backward_chain(self.kb, self.case.queries[4].goal)
        assert r.success, self.case.queries[4].description

    def test_todo_reportado_es_culpable(self) -> None:
        # Primero verificar que hay reportados (evita verdad vacua)
        r_reportado = backward_chain(self.kb, Predicate("reportado_informante", (Term("oficial_duarte"),)))
        assert r_reportado.success, "Debe haber al menos un reportado para que el forall sea significativo"
        r = backward_chain(self.kb, self.case.queries[5].goal)
        assert r.success, self.case.queries[5].description


# ---------------------------------------------------------------------------
# 6. TestForwardChaining
# ---------------------------------------------------------------------------


class TestForwardChaining:
    """Forward chaining: verifica culpables y descartados derivados en cada caso."""

    def test_veneno_culpables(self) -> None:
        kb = veneno.create_kb()
        result = forward_chain(kb)
        culpables = {f for f in result.derived_facts if f.name == "culpable"}
        assert Predicate("culpable", (Term("reynaldo"),)) in culpables

    def test_veneno_descartados(self) -> None:
        kb = veneno.create_kb()
        result = forward_chain(kb)
        descartados = {f for f in result.derived_facts if f.name == "descartado"}
        assert Predicate("descartado", (Term("bernardo"),)) in descartados
        assert Predicate("descartado", (Term("pablo"),)) in descartados

    def test_robo_culpables(self) -> None:
        kb = robo.create_kb()
        result = forward_chain(kb)
        culpables = {f for f in result.derived_facts if f.name == "culpable"}
        assert Predicate("culpable", (Term("elena"),)) in culpables

    def test_robo_descartados(self) -> None:
        kb = robo.create_kb()
        result = forward_chain(kb)
        descartados = {f for f in result.derived_facts if f.name == "descartado"}
        assert Predicate("descartado", (Term("don_rodrigo"),)) in descartados

    def test_sabotaje_culpables(self) -> None:
        kb = sabotaje.create_kb()
        result = forward_chain(kb)
        culpables = {f for f in result.derived_facts if f.name == "culpable"}
        assert Predicate("culpable", (Term("tec_rios"),)) in culpables

    def test_sabotaje_descartados(self) -> None:
        kb = sabotaje.create_kb()
        result = forward_chain(kb)
        descartados = {f for f in result.derived_facts if f.name == "descartado"}
        assert Predicate("descartado", (Term("director_vega"),)) in descartados
        assert Predicate("descartado", (Term("dra_santos"),)) in descartados

    def test_herencia_culpables(self) -> None:
        kb = herencia.create_kb()
        result = forward_chain(kb)
        culpables = {f for f in result.derived_facts if f.name == "culpable"}
        assert Predicate("culpable", (Term("sobrino_esteban"),)) in culpables

    def test_herencia_descartados(self) -> None:
        kb = herencia.create_kb()
        result = forward_chain(kb)
        descartados = {f for f in result.derived_facts if f.name == "descartado"}
        assert Predicate("descartado", (Term("enfermera_campos"),)) in descartados

    def test_red_puerto_culpables(self) -> None:
        kb = red_puerto.create_kb()
        result = forward_chain(kb)
        culpables = {f for f in result.derived_facts if f.name == "culpable"}
        assert Predicate("culpable", (Term("marinero_pinto"),)) in culpables
        assert Predicate("culpable", (Term("oficial_duarte"),)) in culpables

    def test_red_puerto_descartados(self) -> None:
        kb = red_puerto.create_kb()
        result = forward_chain(kb)
        descartados = {f for f in result.derived_facts if f.name == "descartado"}
        assert Predicate("descartado", (Term("inspector_nova"),)) in descartados
        assert Predicate("descartado", (Term("capitan_herrera"),)) in descartados


# ---------------------------------------------------------------------------
# 7. TestNegativeCases
# ---------------------------------------------------------------------------


class TestNegativeCases:
    """Verifica que proposiciones que NO deben ser probables retornan False."""

    def test_margot_not_culpable_veneno(self) -> None:
        kb = veneno.create_kb()
        # Verificar que la KB tiene datos (reynaldo debe ser culpable)
        r_check = backward_chain(kb, Predicate("culpable", (Term("reynaldo"),)))
        assert r_check.success, "KB debe tener datos para que el test negativo sea significativo"
        r = backward_chain(kb, Predicate("culpable", (Term("margot"),)))
        assert not r.success, "Margot no debe ser culpable en el caso veneno"

    def test_victor_not_descartado_robo(self) -> None:
        kb = robo.create_kb()
        # Verificar que la KB tiene datos (don_rodrigo debe estar descartado)
        r_check = backward_chain(kb, Predicate("descartado", (Term("don_rodrigo"),)))
        assert r_check.success, "KB debe tener datos para que el test negativo sea significativo"
        r = backward_chain(kb, Predicate("descartado", (Term("victor"),)))
        assert not r.success, "Victor no debe estar descartado en el caso robo"

    def test_nonexistent_predicate_returns_false(self) -> None:
        kb = veneno.create_kb()
        # Verificar que la KB tiene datos
        r_check = backward_chain(kb, Predicate("culpable", (Term("reynaldo"),)))
        assert r_check.success, "KB debe tener datos para que el test sea significativo"
        r = backward_chain(kb, Predicate("inexistente", (Term("nadie"),)))
        assert not r.success, "Un predicado inexistente no debe ser provable"
