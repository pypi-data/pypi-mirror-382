"""
LayerNet - Biblioteca modular de Machine Learning em um único arquivo.
Inclui suporte simbólico, visual e integração com TensorFlow.
Version 0.0.4
"""

import json
import numpy as np
import pandas as pd
from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.model_selection import train_test_split

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

            outputs = Dense(
                1 if num_classes == 1 else num_classes,
                activation="sigmoid" if num_classes == 1 else "softmax"
            )(x)

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
            self.history = None

        def train_keras(self, X, y, epochs=10, batch_size=8):
            input_shape = X.shape[1:]
            num_classes = 1 if len(np.unique(y)) == 2 else len(np.unique(y))
            model = self.network.build_keras_model(input_shape, num_classes)
            Utils.Logger.info("🚀 Iniciando treinamento...")
            self.history = model.fit(X, y, epochs=epochs, batch_size=batch_size)
            Utils.Logger.success("✅ Treinamento concluído!")
            return model

        def predict(self, X):
            return self.network.model.predict(X)

        def evaluate(self, X, y):
            """Avalia o modelo treinado e retorna a acurácia e perda."""
            if self.network.model is None:
                Utils.Logger.error("⚠ Nenhum modelo treinado encontrado.")
                return None
            loss, acc = self.network.model.evaluate(X, y, verbose=0)
            Utils.Logger.info(f"🎯 Avaliação -> Loss: {loss:.4f} | Accuracy: {acc:.4f}")
            return acc

        def summary(self):
            """Exibe o resumo do modelo Keras."""
            if self.network.model:
                self.network.model.summary()
            else:
                Utils.Logger.warn("Modelo ainda não foi criado.")

        def plot_history(self):
            """Plota o gráfico de acurácia e perda do treinamento."""
            if not self.history:
                Utils.Logger.warn("Histórico de treinamento não encontrado.")
                return
            plt.figure(figsize=(8, 4))
            plt.subplot(1, 2, 1)
            plt.plot(self.history.history['accuracy'])
            plt.title('Acurácia')
            plt.subplot(1, 2, 2)
            plt.plot(self.history.history['loss'])
            plt.title('Perda')
            plt.tight_layout()
            plt.show()

# -------------------- IO --------------------
class IO:
    class DataLoader:
        @staticmethod
        def load_csv(url, columns=None, target_column=None):
            """Carrega CSV com tratamento de erros básicos."""
            try:
                df = pd.read_csv(url, header=None if columns else "infer", names=columns)
            except Exception as e:
                Utils.Logger.error(f"Erro ao carregar CSV: {e}")
                return None, None

            if target_column not in df.columns:
                Utils.Logger.error(f"Coluna alvo '{target_column}' não encontrada.")
                return None, None

            X = df.drop(columns=[target_column]).values
            y = df[target_column].values
            return X, y

    class Preprocess:
        @staticmethod
        def normalize(X):
            """Normaliza os dados entre 0 e 1."""
            return (X - np.min(X)) / (np.max(X) - np.min(X))

        @staticmethod
        def split(X, y, test_size=0.2):
            """Divide os dados em treino e teste."""
            return train_test_split(X, y, test_size=test_size, random_state=42)

    @staticmethod
    def save_network(network, path):
        """Salva a estrutura da rede em JSON."""
        try:
            data = {
                "name": network.name,
                "layers": {
                    str(k): [vars(p) for p in v] for k, v in network.layers_dict.items()
                }
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            Utils.Logger.success(f"Rede '{network.name}' salva em {path}")
        except Exception as e:
            Utils.Logger.error(f"Erro ao salvar rede: {e}")

    @staticmethod
    def export_network(network, path):
        """Exporta o modelo Keras treinado (HDF5)."""
        if network.model:
            network.model.save(path)
            Utils.Logger.success(f"Modelo exportado para {path}")
        else:
            Utils.Logger.warn("Nenhum modelo Keras encontrado para exportar.")

# -------------------- GUI --------------------
class GUI:
    @staticmethod
    def show_network(network):
        """Exibe graficamente a arquitetura da rede."""
        try:
            G = nx.DiGraph()
            layers_sorted = sorted(network.layers_dict.keys())

            for layer_idx in layers_sorted:
                for p in network.layers_dict[layer_idx]:
                    G.add_node(p.id, layer=layer_idx)

            # conecta camadas vizinhas (corrigido para camadas não sequenciais)
            for i in range(len(layers_sorted) - 1):
                layer_a = network.layers_dict[layers_sorted[i]]
                layer_b = network.layers_dict[layers_sorted[i + 1]]
                for a in layer_a:
                    for b in layer_b:
                        G.add_edge(a.id, b.id)

            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, font_size=8)
            plt.title(f"Arquitetura: {network.name}")
            plt.show()
        except ImportError:
            Utils.Logger.error("Matplotlib ou NetworkX não estão instalados para exibir a GUI.")
        except Exception as e:
            Utils.Logger.error(f"Erro ao exibir a rede: {e}")
