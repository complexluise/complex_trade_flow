# -*- coding: utf-8 -*-
"""
Modulo: red_comercial
=====================
Implementa la propuesta metodológica de *Cajas (2025)* para medir:

* **Influencia Comercial** – Ecuaciones (16‒19).
* **Retroalimentación Comercial Relativa** – Ecuaciones (22‒27).
* **Balance de Poder Comercial** – Ecuaciones (28‒30).
* **Identificación de Estructuras Centro–Periferia** – Tabla 5.1.

En esta versión se eliminaron todas las siglas técnicas (TI, RTF, BTP) dentro
 del código fuente —clases, variables, comentarios y claves de diccionarios—
 para mantener nombres completamente semánticos y auto‑explicativos.
"""

from __future__ import annotations

import numpy as np
import networkx as nx
import pandas as pd

###############################################################################
# 1.  Estructura de la red comercial                                           #
###############################################################################

class RedComercial:
    """Representa una red comercial dirigida y ponderada (importaciones)."""

    def __init__(self, grafo: nx.DiGraph):
        self.grafo = grafo
        self.mapa_nombres = self._mapear_nombres_nodos()
        self.matriz_propension = self._construir_matriz_nodal("propension")
        self.matriz_ingreso = self._construir_matriz_nodal("ingreso")

    # ------------------------------------------------------------------
    # Métodos privados                                                   #
    # ------------------------------------------------------------------

    def _construir_matriz_nodal(self, atributo: str) -> np.ndarray:
        valores = list(nx.get_node_attributes(self.grafo, atributo).values())
        return np.diag(valores)

    def _mapear_nombres_nodos(self) -> dict[int, str]:
        return dict(enumerate(self.grafo.nodes()))

    # ------------------------------------------------------------------
    # API pública                                                        #
    # ------------------------------------------------------------------

    def normalizar(self) -> None:
        """Convierte los flujos brutos de importación a coeficientes (%)."""
        self.grafo = self._normalizar_digrafo()

    def _normalizar_digrafo(self) -> nx.DiGraph:
        matriz = nx.to_numpy_array(self.grafo)
        matriz_norm = np.nan_to_num((matriz.T / matriz.sum(axis=1)).T)
        grafo_norm = nx.from_numpy_array(matriz_norm, create_using=nx.DiGraph())
        grafo_norm = nx.relabel_nodes(grafo_norm, self.mapa_nombres)
        return grafo_norm

    def asignar_atributos_nodo(self, valores: dict[str, float], nombre: str) -> None:
        nx.set_node_attributes(self.grafo, valores, nombre)

###############################################################################
# 2.  Cálculo de la matriz de elasticidades                                   #
###############################################################################

class CalculadoraElasticidades:
    """Computa la matriz de elasticidades ingreso‑ingreso y la red asociada.

    Matrices (notación explicada):
    * **M_coef_importaciones** – coeficientes de importación.
    * **D_propensiones** – diagonal de propensiones medias a importar.
    * **D_ingresos** – diagonal de niveles de ingreso.
    * **M_elasticidades** – elasticidades ingreso‑ingreso.
    * **red_influencia_comercial** – grafo dirigido con M_elasticidades como pesos.
    """

    def __init__(self, grafo: nx.DiGraph):
        self.grafo = grafo

    # .................................................................
    def calcular_matriz_y_red_influencia(self) -> tuple[np.ndarray, nx.DiGraph]:
        """Devuelve la tupla (M_elasticidades, red_influencia_comercial)."""
        # Matriz de coeficientes de importación
        M_coef_importaciones = nx.to_numpy_array(self.grafo)

        # Diagonal de propensiones a importar
        D_propensiones = np.diag(list(nx.get_node_attributes(self.grafo, "propension").values()))

        # Diagonal de ingresos absolutos
        D_ingresos = np.diag(list(nx.get_node_attributes(self.grafo, "ingreso").values()))

        # Fórmula de elasticidades (Ecuación 12)
        M_elasticidades = (
            D_ingresos
            @ D_propensiones
            @ M_coef_importaciones
            @ np.linalg.inv(np.eye(len(M_coef_importaciones)) - D_propensiones @ M_coef_importaciones)
            @ np.linalg.inv(D_ingresos)
        )

        # --- Construir red de influencia comercial --------------------
        red_influencia_comercial = nx.from_numpy_array(M_elasticidades, create_using=nx.DiGraph())
        red_influencia_comercial = nx.relabel_nodes(red_influencia_comercial, dict(enumerate(self.grafo.nodes())))
        nx.set_node_attributes(red_influencia_comercial, nx.get_node_attributes(self.grafo, "propension"), "propension")
        nx.set_node_attributes(red_influencia_comercial, nx.get_node_attributes(self.grafo, "ingreso"), "ingreso")

        return M_elasticidades, red_influencia_comercial

###############################################################################
# 3.  Participación del ingreso (vector w)                                    #
###############################################################################

class CalculadoraParticipacion:
    """Genera el vector de participación de ingreso para un grupo."""

    def __init__(self, grafo: nx.DiGraph):
        self.grafo = grafo

    def calcular_participacion(self, grupo: list[str]) -> dict[str, float]:
        ingresos = nx.get_node_attributes(self.grafo, "ingreso")
        ingreso_total_grupo = sum(ingresos[p] for p in grupo)
        return {p: (ingresos[p] / ingreso_total_grupo if p in grupo else 0.0) for p in ingresos}

###############################################################################
# 4.  Influencia Comercial                                                    #
###############################################################################

class CalculadoraInfluenciaComercial:
    """Operaciones sobre la matriz de elasticidades (expresiones 16–19)."""

    def __init__(self, matriz_elasticidades: np.ndarray):
        self.matriz_elasticidades = matriz_elasticidades

    def influencia_nodo_a_grupo(self, vector_participacion_grupo: dict[str, float]) -> dict[str, float]:
        return dict(zip(vector_participacion_grupo.keys(), self.matriz_elasticidades @ np.array(list(vector_participacion_grupo.values()))))

    def influencia_grupo_a_nodo(self, vector_participacion_grupo: dict[str, float]) -> dict[str, float]:
        return dict(zip(vector_participacion_grupo.keys(), self.matriz_elasticidades.T @ np.array(list(vector_participacion_grupo.values()))))

    def influencia_grupo_a_grupo(self, vector_participacion_origen: dict[str, float], vector_participacion_destino: dict[str, float]) -> float:
        return np.array(list(vector_participacion_origen.values())).T @ self.matriz_elasticidades @ np.array(list(vector_participacion_destino.values()))

###############################################################################
# 5.  Retroalimentación Comercial Relativa                                    #
###############################################################################

class CalculadoraRetroalimentacionComercial:
    """Calcula la retroalimentación comercial relativa para un grupo (Eq. 27)."""

    def __init__(self, matriz_elasticidades: np.ndarray, propensiones: dict[str, float]):
        self.matriz_elasticidades = matriz_elasticidades
        self.propensiones = propensiones
        self.calculadora_influencia = CalculadoraInfluenciaComercial(matriz_elasticidades)

    # ..................................................................
    def retroalimentacion_relativa_grupo(self, vector_participacion_grupo: dict[str, float]) -> float:
        """Calcula la retroalimentación relativa del grupo."""
        cantidad_paises_grupo = sum(1 for w in vector_participacion_grupo.values() if w > 0)

        # Retroalimentación absoluta del grupo
        retroalimentacion_absoluta = self.calculadora_influencia.influencia_grupo_a_grupo(
            vector_participacion_grupo, vector_participacion_grupo
        )

        # Métricas auxiliares para el caso homogéneo
        vector_participacion = np.array(list(vector_participacion_grupo.values()))
        propension_media_global = np.mean(list(self.propensiones.values()))

        # Retroalimentación bajo una estructura homogénea
        retroalimentacion_homogenea = (
            cantidad_paises_grupo
            * vector_participacion.T
            @ np.diag(list(self.propensiones.values()))
            @ vector_participacion
        ) / (len(self.matriz_elasticidades) * (1 - propension_media_global))

        # Indicador relativo adimensional
        return retroalimentacion_absoluta / retroalimentacion_homogenea

###############################################################################
# 6.  Balance de Poder Comercial                                              #
###############################################################################

class CalculadoraBalancePoderComercial:
    """Implementa las ecuaciones 28 y 29 para dos grupos centro–periferia."""

    def __init__(self, matriz_elasticidades: np.ndarray, propensiones: dict[str, float]):
        self.matriz_elasticidades = matriz_elasticidades
        self.propensiones = propensiones
        self.calculadora_influencia = CalculadoraInfluenciaComercial(matriz_elasticidades)
        self.calculadora_retroalimentacion = CalculadoraRetroalimentacionComercial(matriz_elasticidades, propensiones)

    def balance_poder_entre_grupos(self, vector_participacion_centro: dict[str, float], vector_participacion_periferia: dict[str, float]) -> float:
        """Devuelve el balance de poder comercial del centro respecto a la periferia."""
        retro_centro = self.calculadora_retroalimentacion.retroalimentacion_relativa_grupo(vector_participacion_centro)
        retro_periferia = self.calculadora_retroalimentacion.retroalimentacion_relativa_grupo(vector_participacion_periferia)
        influencia_centro_sobre_periferia = self.calculadora_influencia.influencia_grupo_a_grupo(
            vector_participacion_centro, vector_participacion_periferia
        )
        influencia_periferia_sobre_centro = self.calculadora_influencia.influencia_grupo_a_grupo(
            vector_participacion_periferia, vector_participacion_centro
        )
        return retro_centro * influencia_centro_sobre_periferia - retro_periferia * influencia_periferia_sobre_centro

###############################################################################
# 7.  Identificación Centro–Periferia                                         #
###############################################################################

class IdentificadorCentroPeriferia:
    """Algoritmo recursivo descrito en la Tabla 5.1."""

    def __init__(self, red_influencia: nx.DiGraph):
        self.red_influencia_original = red_influencia
        self.matriz_elasticidades_original = nx.to_numpy_array(red_influencia)
        self.propensiones_original = nx.get_node_attributes(red_influencia, "propension")

    # ..................................................................
    def identificar(self) -> dict[int, dict[str, list[str] | float]]:
        niveles: dict[int, dict[str, list[str] | float]] = {}
        influencia_global = self._influencia_sobre_resto_del_mundo()
        red_trabajo = self.red_influencia_original.copy()
        nivel_actual = 0

        while len(influencia_global) > 2:
            niveles[nivel_actual] = {"balance_poder": 0.0, "nodos": []}
            centro_provisional: list[str] = []

            for pais in list(influencia_global.keys())[:-1]:
                centro_provisional.append(pais)
                periferia = [n for n in red_trabajo.nodes() if n not in centro_provisional]
                vector_centro = CalculadoraParticipacion(red_trabajo).calcular_participacion(centro_provisional)
                vector_periferia = CalculadoraParticipacion(red_trabajo).calcular_participacion(periferia)

                matriz_elasticidades_local = nx.to_numpy_array(red_trabajo)
                propensiones_locales = nx.get_node_attributes(red_trabajo, "propension")
                calculadora_balance = CalculadoraBalancePoderComercial(matriz_elasticidades_local, propensiones_locales)
                balance_actual = calculadora_balance.balance_poder_entre_grupos(vector_centro, vector_periferia)

                if balance_actual > niveles[nivel_actual]["balance_poder"]:
                    niveles[nivel_actual]["balance_poder"] = balance_actual
                    niveles[nivel_actual]["nodos"] = centro_provisional.copy()

            red_trabajo.remove_nodes_from(niveles[nivel_actual]["nodos"])
            for nodo_eliminado in niveles[nivel_actual]["nodos"]:
                influencia_global.pop(nodo_eliminado, None)
            nivel_actual += 1

        return niveles

    # ------------------------------------------------------------------
