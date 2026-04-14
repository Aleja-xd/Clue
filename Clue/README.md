# Taller de Logica — Investigacion Criminalistica

Resuelve casos criminales usando logica proposicional y de predicados.

## Estructura del Proyecto

```
Clue/
├── src/                              # Motor de logica
│   ├── logic_core.py                 # AST de formulas proposicionales (dado)
│   ├── model_checking.py             # [IMPLEMENTAR] Model checking
│   ├── cnf_transform.py              # [IMPLEMENTAR] Transformacion a CNF
│   ├── resolution.py                 # Resolucion proposicional (dado)
│   ├── predicate_logic.py            # Logica de predicados (dado)
│   ├── forward_chaining.py           # Forward chaining (dado)
│   ├── backward_chaining.py          # Backward chaining (dado)
│   ├── utils.py                      # Utilidades de visualizacion
│   ├── crime_case.py                 # Estructura de datos de casos
│   └── tui.py                        # Interfaz grafica de terminal
├── crimes/                           # [IMPLEMENTAR] Casos criminales
│   ├── veneno_villa_espinas.py       # Asesinato con arsenico
│   ├── robo_expreso_sur.py           # Robo de joyas en tren
│   ├── sabotaje_pharmax.py           # Sabotaje a laboratorio
│   ├── herencia_hacienda_rosal.py    # Envenenamiento por herencia
│   └── red_puerto_sombras.py         # Red de contrabando
├── tests/                            # Pruebas unitarias (calificacion)
│   ├── test_model_checking.py        # Tests para Punto 1
│   ├── test_cnf.py                   # Tests para Punto 2
│   └── test_predicates.py            # Tests para Punto 3
├── notebooks/                        # Guias de aprendizaje (NO evaluadas)
│   ├── guia_objetos_python.ipynb     # Guia de POO en Python
│   ├── parte1_model_checking.ipynb   # Guia: model checking
│   ├── parte2_cnf.ipynb              # Guia: transformacion a CNF
│   └── parte3_predicados.ipynb       # Guia: logica de predicados
├── main.py                           # Interfaz grafica (opcional)
└── pyproject.toml                    # Configuracion del proyecto
```

## Inicio Rapido

Se recomienda instalar el proyecto usando [uv](https://docs.astral.sh/uv/), que se encargará de crear un entorno virtual y gestionar las dependencias. 

```bash
uv sync                  # Instalar dependencias
uv run main.py --test    # Ejecutar pruebas unitarias
uv run main.py           # Interfaz grafica (opcional)
```

## Notebooks de Apoyo

Los notebooks en `notebooks/` son **guias para entender el motor de logica**.
NO son evaluados — la calificacion se basa exclusivamente en las pruebas unitarias.

Si no tienes experiencia con programacion orientada a objetos, empieza por
`notebooks/guia_objetos_python.ipynb`.
