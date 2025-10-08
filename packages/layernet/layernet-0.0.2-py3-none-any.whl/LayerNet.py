"""LayerNet Single-File Edition
Biblioteca modular de Machine Learning em um único arquivo.
Inclui core, io, gui e utils.
"""
import tensorflow as tf
from tensorflow.keras import layers, models
# -------------------- UTILS --------------------
class Utils:
    @staticmethod
    def log(msg):
        print(f"[LayerNet] {msg}")

# -------------------- CORE --------------------
class Core:
    class Perceptron:
        def __init__(self, pid):
            self.id = pid

    class Layer:
        def __init__(self, index):
            self.index = index
            self.perceptrons = []

    class Network:
        def __init__(self, name):
            self.name = name
            self.layers = {}

        def add_perceptron(self, perceptron_id, layer_index):
            if layer_index not in self.layers:
                self.layers[layer_index] = Core.Layer(layer_index)
            self.layers[layer_index].perceptrons.append(perceptron_id)

    class Trainer:
        def __init__(self, network):
            self.network = network
            self.model = None
    
        def train_keras(self, X, y, epochs=1):
            
            
            # Criar modelo baseado nas camadas do Core.Network
            self.model = models.Sequential()
            first_layer = True
            for idx in sorted(self.network.layers.keys()):
                size = len(self.network.layers[idx].perceptrons)
                if first_layer:
                    self.model.add(layers.Dense(size, activation='relu', input_shape=(X.shape[1],)))
                    first_layer = False
                else:
                    self.model.add(layers.Dense(size, activation='relu'))
            self.model.add(layers.Dense(1, activation='sigmoid'))  # Saída binária
            
            self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            self.model.fit(X, y, epochs=epochs)
            print("Treinamento concluído")

# -------------------- IO --------------------
class IO:
    @staticmethod
    def save_network(network, path):
        Utils.log(f"Saving network {network.name} to {path}")

    @staticmethod
    def export_network(network, path):
        Utils.log(f"Exporting network {network.name} to {path}")

# -------------------- GUI --------------------
class GUI:
    @staticmethod
    def show_network(network):
        try:
            import matplotlib.pyplot as plt
            import networkx as nx

            G = nx.DiGraph()
            for layer_idx in sorted(network.layers.keys()):
                for p in network.layers[layer_idx].perceptrons:
                    G.add_node(p, layer=layer_idx)
            for i in range(len(network.layers)-1):
                layer_a = network.layers[i].perceptrons
                layer_b = network.layers[i+1].perceptrons
                for a in layer_a:
                    for b in layer_b:
                        G.add_edge(a, b)

            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=10)
            plt.show()
        except ImportError:
            Utils.log("Matplotlib ou NetworkX não estão instalados para exibir a GUI.")

