import numpy as np
import networkx as nx
import pandas as pd
import copy


class TradeNetwork:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.mapa_labels = self._get_node_names()
        self.matriz_propension = self._get_nodal_matrix("propension")
        self.matriz_ingreso = self._get_nodal_matrix("ingreso")
        self.matriz = TradeNetwork._get_np_matrix(self.graph)
        self.normalized_graph = self._normalize_DiGraph()
        self.normalized_matrix = TradeNetwork._get_np_matrix(self.normalized_graph)

    @staticmethod
    def _get_np_matrix(graph):
        return nx.to_numpy_array(graph)

    def _get_nodal_matrix(self, nodal_attribute):
        return np.diag(
            [
                float(x)
                for x in list(
                    nx.get_node_attributes(self.graph, nodal_attribute).values()
                )
            ]
        )

    def _get_node_names(self):
        return dict(
            zip(
                [i for i in range(len(list(self.graph.nodes())))],
                list(self.graph.nodes()),
            )
        )

    def normalize(self):
        self.graph = self._normalize_DiGraph()

    def _normalize_DiGraph(self):
        normalized_matrix = (self.matriz.T / self.matriz.sum(axis=1)).T
        normalized_graph = nx.from_numpy_array(
            normalized_matrix, create_using=nx.DiGraph()
        )
        normalized_graph = nx.relabel_nodes(normalized_graph, self.mapa_labels)
        return normalized_graph

    def set_node_attributes(self, values, name):
        nx.set_node_attributes(self.graph, values, name)


class ElasticityCalculator:
    def __init__(self, trade_network: TradeNetwork):
        self.trade_network = trade_network
        self.graph = (
            trade_network.normalized_graph
        )  # Aquí debe estar el grafo normalizado
        self.matriz = (
            trade_network.normalized_matrix
        )  # Aquí debe estar la matriz normalizada

    def compute_elasticities(self):
        matriz = self.matriz
        matriz_propension = self.trade_network.matriz_propension
        matriz_ingreso = self.trade_network.matriz_ingreso

        E = (
            matriz_ingreso
            @ matriz_propension
            @ matriz
            @ np.linalg.inv(np.identity(len(matriz)) - matriz_propension @ matriz)
            @ np.linalg.inv(matriz_ingreso)
        )

        mapa_labels = self.trade_network.mapa_labels
        TI = nx.from_numpy_array(E, create_using=nx.DiGraph())
        TI = nx.relabel_nodes(TI, mapa_labels)

        nx.set_node_attributes(
            TI, dict(self.graph.nodes(data="propension")), "propension"
        )
        nx.set_node_attributes(TI, dict(self.graph.nodes(data="ingreso")), "ingreso")

        return E, TI


class ParticipationCalculator:
    def __init__(self, trade_network: TradeNetwork):
        self.trade_network = trade_network

    def compute_participation(self, group):
        ingreso = self.trade_network.matriz_ingreso
        ingresos_grupo = 0.0
        participaciones = []

        for nodo in ingreso:
            if nodo in group:
                valor = ingreso[nodo]
                ingresos_grupo += valor
                participaciones.append(valor)
            else:
                participaciones.append(0.0)

        return dict(zip(ingreso.keys(), np.array(participaciones) / ingresos_grupo))


class TI_Calculator:
    def __init__(self, E):
        self.E = E

    def TI_ng(self, wg):
        return dict(zip(wg.keys(), self.E @ np.array(list(wg.values()))))

    def TI_gn(self, wg):
        return dict(zip(wg.keys(), self.E.T @ np.array(list(wg.values()))))

    def TI_gg(self, wg, wg_prima):
        return (
            np.array(list(wg.values())).T @ self.E @ np.array(list(wg_prima.values()))
        )


class RTF_Calculator:
    def __init__(self, E, propension):
        self.E = E
        self.propension = propension

    def RTF_g(self, wg):
        len_grupo = np.count_nonzero(np.array(list(wg.values())))
        TF_g = TI_Calculator(self.E).TI_gg(wg, wg)
        TF_g_H = (
            len_grupo
            * (
                np.array(list(wg.values())).T
                @ np.diag(list(self.propension.values()))
                @ np.array(list(wg.values()))
            )
            / (len(self.E) * (1 - np.mean(list(self.propension.values()))))
        )
        return TF_g / TF_g_H


class BTP_Calculator:
    def __init__(self, E, propension):
        self.E = E
        self.propension = propension

    def BTP_gg(self, wg, wg_prima):
        RTF_calc = RTF_Calculator(self.E, self.propension)
        return RTF_calc.RTF_g(wg) * TI_Calculator(self.E).TI_gg(
            wg, wg_prima
        ) - RTF_calc.RTF_g(wg_prima) * TI_Calculator(self.E).TI_gg(wg_prima, wg)


class CentralPeripheryStructureFinder:
    def __init__(self, TI, paises):
        self.TI = TI
        self.paises = paises

    def find_structures(self):
        TIc = copy.deepcopy(self.TI)
        E = nx.to_numpy_array(TIc)
        propension = nx.get_node_attributes(TIc, "propension")
        ingreso = nx.get_node_attributes(TIc, "ingreso")
        influencias = dict.fromkeys(self.paises)

        for pais in self.paises:
            paises_restantes = [x for x in self.paises if x != pais]
            wn = ParticipationCalculator(TIc).compute_participation([pais])
            wg = ParticipationCalculator(TIc).compute_participation(paises_restantes)
            influencias[pais] = TI_Calculator(E).TI_gg(wn, wg)

        influencias = dict(
            sorted(influencias.items(), key=lambda item: item[1], reverse=True)
        )
        particiones = {}
        q = 0

        while len(influencias) > 2:
            particiones[q] = {"BTP": 0.0, "nodos": None}
            centro = []

            for pais in list(influencias.keys())[:-1]:
                centro.append(pais)
                periferia = [x for x in self.paises if x not in centro]
                wc = ParticipationCalculator(TIc).compute_participation(centro)
                wp = ParticipationCalculator(TIc).compute_participation(periferia)
                BTP = BTP_Calculator(E, propension).BTP_gg(wc, wp)

                if particiones[q]["BTP"] < BTP:
                    particiones[q]["BTP"] = BTP
                    particiones[q]["nodos"] = centro.copy()

            for nodo in particiones[q]["nodos"]:
                influencias.pop(nodo)
            TIc.remove_nodes_from(particiones[q]["nodos"])

            E = nx.to_numpy_array(TIc)
            propension = nx.get_node_attributes(TIc, "propension")
            ingreso = nx.get_node_attributes(TIc, "ingreso")

            q = q + 1

        return particiones


if __name__ == "__main__":
    # Cargar datos
    path = (
        "Processed_Data/BACI_HS92_V202301/Y1995/Graph_BACI_HS92_Y1995_V202301.graphml"
    )

    G = nx.read_graphml(path)

    trade_network = TradeNetwork(G)

    # Calcular las elasticidades
    elasticity_calculator = ElasticityCalculator(trade_network)
    E, TI = elasticity_calculator.compute_elasticities()

    # TODO guardar grafo de las elasticidades

    # TODO calcular las estructuras de centralidad-periferia y guardarlas como
    # TODO guardar las estructuras de centralidad-periferia como

    # Encontrar las estructuras de centro-periferia
    paises = ["A", "B", "C"]
    central_periphery_finder = CentralPeripheryStructureFinder(TI, paises)
    particiones = central_periphery_finder.find_structures()

    # TODO hacer dataframe con los resultados de influencias y poder

    print(particiones)
