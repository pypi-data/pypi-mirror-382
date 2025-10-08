"""
LayerNet - Biblioteca modular de Machine Learning em um único arquivo.
Inclui suporte simbólico, visual e integração com TensorFlow.
Version 0.0.3
"""

import numpy as np
import pandas as pd
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import networkx as nx

# -------------------- UTILS --------------------
class Utils:
    class Logger:
        @staticmethod
        def info(msg): print(f"[INFO] {msg}")
        @staticmethod
        def success(msg): print(f"[OK] {msg}")
        @staticmethod
        def warn(msg): print(f"[WARN] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")

# -------------------- CORE --------------------
class Core:
    class Perceptron:
        def __init__(self, id, layer, type="dense", filters=32, kernel=(3,3), pool=(2,2)):
            self.id = id
            self.layer = layer
            self.type = type
            self.filters = filters
            self.kernel = kernel
            self.pool = pool

    class Layer:
        def __init__(self, index):
            self.index = index
            self.perceptrons = []

    class Network:
        def __init__(self, name):
            self.name = name
            self.layers_dict = {}  # {layer_number: [Perceptron,...]}
            self.model = None

        def add_perceptron(self, id, layer, type="dense", filters=32, kernel=(3,3), pool=(2,2)):
            p = Core.Perceptron(id, layer, type, filters, kernel, pool)
            self.layers_dict.setdefault(layer, []).append(p)

        def build_keras_model(self, input_shape, num_classes):
            inputs = Input(shape=input_shape)
            x = inputs

            for layer_num in sorted(self.layers_dict.keys()):
                for p in self.layers_dict[layer_num]:
                    if p.type == "dense":
                        if len(x.shape) > 2:  # CNN -> Flatten antes
                            x = Flatten()(x)
                        x = Dense(64, activation="relu")(x)
                    elif p.type == "conv":
                        x = Conv2D(p.filters, p.kernel, activation="relu", padding="same")(x)
                        x = MaxPooling2D(p.pool)(x)

            if num_classes == 1:
                outputs = Dense(1, activation="sigmoid")(x)
            else:
                outputs = Dense(num_classes, activation="softmax")(x)

            self.model = Model(inputs, outputs)
            self.model.compile(
                optimizer=Adam(),
                loss="binary_crossentropy" if num_classes == 1 else "sparse_categorical_crossentropy",
                metrics=["accuracy"]
            )
            return self.model

    class Trainer:
        def __init__(self, network):
            self.network = network

        def train_keras(self, X, y, epochs=10, batch_size=8):
            input_shape = X.shape[1:]
            num_classes = 1 if len(np.unique(y)) == 2 else len(np.unique(y))
            model = self.network.build_keras_model(input_shape, num_classes)
            Utils.Logger.info("🚀 Iniciando treinamento...")
            model.fit(X, y, epochs=epochs, batch_size=batch_size)
            Utils.Logger.success("✅ Treinamento concluído!")
            return model

        def predict(self, X):
            return self.network.model.predict(X)
        
        def evaluate(self, X, y):
         """Avalia o modelo treinado e retorna a acurácia e perda."""
         if self.network.model is None:
             print("[ERRO] ⚠ Nenhum modelo treinado encontrado.")
             return None
         loss, acc = self.network.model.evaluate(X, y, verbose=0)
         print(f"[INFO] 🎯 Avaliação -> Loss: {loss:.4f} | Accuracy: {acc:.4f}")
         return acc


# -------------------- IO --------------------
class IO:
    class DataLoader:
        @staticmethod
        def load_csv(url, columns=None, target_column=None):
            df = pd.read_csv(url, header=None, names=columns)
            X = df.drop(columns=[target_column]).values
            y = df[target_column].values
            return X, y

    @staticmethod
    def save_network(network, path):
        Utils.Logger.info(f"Saving network {network.name} to {path}")

    @staticmethod
    def export_network(network, path):
        Utils.Logger.info(f"Exporting network {network.name} to {path}")

# -------------------- GUI --------------------
class GUI:
    @staticmethod
    def show_network(network):
        try:
            G = nx.DiGraph()
            for layer_idx in sorted(network.layers_dict.keys()):
                for p in network.layers_dict[layer_idx]:
                    G.add_node(p.id, layer=layer_idx)

            for i in range(len(network.layers_dict)-1):
                layer_a = network.layers_dict[i]
                layer_b = network.layers_dict[i+1]
                for a in layer_a:
                    for b in layer_b:
                        G.add_edge(a.id, b.id)

            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=8)
            plt.title(f"Arquitetura: {network.name}")
            plt.show()
        except ImportError:
            Utils.Logger.error("Matplotlib ou NetworkX não estão instalados para exibir a GUI.")
