"""
LayerNet - Biblioteca modular de Machine Learning em um único arquivo.
Inclui suporte simbólico, visual e integração com TensorFlow.
Version 0.0.5
"""

import json
import numpy as np
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
        def __init__(self, id, layer, type="dense", neurons=64, activation="relu", filters=32, kernel=(3,3), pool=(2,2)):
            """
            activation: str ou callable. Modos aceitos: 'relu', 'sigmoid', 'tanh', 'softmax', 'linear', etc. (Keras)
            Você pode passar uma função customizada também.
            """
            self.id = id
            self.layer = layer
            self.type = type
            self.neurons = neurons
            self.activation = activation
            self.filters = filters
            self.kernel = kernel
            self.pool = pool

    class Network:
        def __init__(self, name):
            self.name = name
            self.layers_dict = {}  # {layer_number: [Perceptron,...]}
            self.model = None

        def add_perceptron(self, id, layer, type="dense", neurons=64, activation="relu", filters=32, kernel=(3,3), pool=(2,2)):
            """
            Adiciona um perceptron à rede.

            Exemplo:
                net.add_perceptron("P1", layer=0, type="dense", neurons=32, activation="relu")
                net.add_perceptron("Conv1", layer=0, type="conv", filters=16, kernel=(3,3))
            """
            p = Core.Perceptron(id, layer, type, neurons, activation, filters, kernel, pool)
            self.layers_dict.setdefault(layer, []).append(p)
            Utils.Logger.info(f"Perceptron '{id}' adicionado na camada {layer} ({type}, ativação={activation})")

        def build_keras_model(self, input_shape, num_classes):
            inputs = Input(shape=input_shape)
            x = inputs

            for layer_num in sorted(self.layers_dict.keys()):
                for p in self.layers_dict[layer_num]:
                    if p.type == "dense":
                        if len(x.shape) > 2:  # CNN -> Flatten antes de densas
                            x = Flatten()(x)
                        x = Dense(p.neurons, activation=p.activation)(x)

                    elif p.type == "conv":
                        x = Conv2D(p.filters, p.kernel, activation=p.activation, padding="same")(x)
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

# -------------------- IO --------------------
class IO:
    class DataLoader:
        @staticmethod
        def load_csv(filepath, columns=None, target_column=None, delimiter=",", skip_header=False):
            """
            Carrega CSV simples usando apenas Python e numpy.
            columns: lista de nomes das colunas (opcional)
            target_column: nome ou índice da coluna alvo
            delimiter: separador (default ',')
            skip_header: se True, ignora a primeira linha
            """
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                if skip_header:
                    lines = lines[1:]
                data = [line.strip().split(delimiter) for line in lines if line.strip()]
                arr = np.array(data)
                if columns is not None:
                    col_names = columns
                else:
                    col_names = [str(i) for i in range(arr.shape[1])]
                if isinstance(target_column, str):
                    target_idx = col_names.index(target_column)
                elif isinstance(target_column, int):
                    target_idx = target_column
                else:
                    target_idx = -1  # última coluna por padrão
                X = np.delete(arr, target_idx, axis=1).astype(float)
                y = arr[:, target_idx]
                try:
                    y = y.astype(float)
                except:
                    pass
                return X, y
            except Exception as e:
                Utils.Logger.error(f"Erro ao carregar CSV: {e}")
                return None, None


    class Preprocess:
        @staticmethod
        def normalize(X, method="minmax"):
            """
            Normaliza os dados.
            method: 'minmax' (0-1), 'zscore' (média 0, desvio 1), 'none' (sem normalização)
            """
            X = np.array(X, dtype=float)
            if method == "minmax":
                return (X - np.min(X)) / (np.max(X) - np.min(X))
            elif method == "zscore":
                return (X - np.mean(X)) / (np.std(X) + 1e-8)
            elif method == "none":
                return X
            else:
                raise ValueError("Método de normalização não suportado: " + str(method))

        @staticmethod
        def split(X, y, test_size=0.2, shuffle=True, random_state=42):
            """
            Divide os dados em treino e teste sem sklearn.
            test_size: proporção (0-1) ou número absoluto de amostras de teste
            shuffle: embaralha antes de dividir
            """
            X = np.array(X)
            y = np.array(y)
            n = len(X)
            idx = np.arange(n)
            if shuffle:
                rng = np.random.RandomState(random_state)
                rng.shuffle(idx)
            X, y = X[idx], y[idx]
            if 0 < test_size < 1:
                n_test = int(n * test_size)
            else:
                n_test = int(test_size)
            X_train, X_test = X[:-n_test], X[-n_test:]
            y_train, y_test = y[:-n_test], y[-n_test:]
            return X_train, X_test, y_train, y_test

        @staticmethod
        def label_encode(y):
            """Codifica labels categóricos em inteiros."""
            classes, y_int = np.unique(y, return_inverse=True)
            return y_int, classes

        @staticmethod
        def one_hot_encode(y):
            """Codifica labels inteiros em one-hot."""
            y = np.array(y, dtype=int)
            n_classes = np.max(y) + 1
            return np.eye(n_classes)[y]

        @staticmethod
        def accuracy(y_true, y_pred):
            """Calcula acurácia simples."""
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)
            return np.mean(y_true == y_pred)

    @staticmethod
    def detect_overfit_underfit(history, threshold=0.05, plot=True):
        """
        Detecta e plota overfitting/underfitting baseado no histórico do treinamento (objeto History do Keras).
        threshold: diferença mínima entre acc/loss de treino e val para alertar.
        plot: se True, plota as curvas.
        """
        import matplotlib.pyplot as plt
        msg = []
        if hasattr(history, 'history'):
            hist = history.history
        else:
            hist = history
        if plot:
            plt.figure(figsize=(10,4))
            if 'loss' in hist:
                plt.subplot(1,2,1)
                plt.plot(hist['loss'], label='Treino')
                if 'val_loss' in hist:
                    plt.plot(hist['val_loss'], label='Validação')
                plt.title('Loss')
                plt.legend()
            if 'accuracy' in hist or 'acc' in hist:
                plt.subplot(1,2,2)
                acc_key = 'accuracy' if 'accuracy' in hist else 'acc'
                plt.plot(hist[acc_key], label='Treino')
                if 'val_' + acc_key in hist:
                    plt.plot(hist['val_' + acc_key], label='Validação')
                plt.title('Acurácia')
                plt.legend()
            plt.tight_layout()
            plt.show()
        # Detecta overfitting
        if 'val_loss' in hist and 'loss' in hist:
            final_train = hist['loss'][-1]
            final_val = hist['val_loss'][-1]
            if final_val > final_train + threshold:
                msg.append('Possível OVERFITTING detectado: loss de validação maior que o de treino.')
        if ('val_accuracy' in hist or 'val_acc' in hist) and ('accuracy' in hist or 'acc' in hist):
            acc_key = 'accuracy' if 'accuracy' in hist else 'acc'
            val_acc_key = 'val_' + acc_key
            if val_acc_key in hist:
                final_train_acc = hist[acc_key][-1]
                final_val_acc = hist[val_acc_key][-1]
                if final_train_acc - final_val_acc > threshold:
                    msg.append('Possível OVERFITTING: acurácia de treino muito maior que validação.')
        # Detecta underfitting
        if 'val_loss' in hist and 'loss' in hist:
            if hist['loss'][-1] > 1.0 and hist['val_loss'][-1] > 1.0:
                msg.append('Possível UNDERFITTING: loss alto em treino e validação.')
        if msg:
            for m in msg:
                Utils.Logger.warn(m)
        else:
            Utils.Logger.success('Nenhum sinal claro de overfitting ou underfitting.')
        return msg

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
        """Exibe graficamente a arquitetura da rede em estilo árvore (sem pygraphviz)."""
        try:
            G = nx.DiGraph()
            layers_sorted = sorted(network.layers_dict.keys())

            # Adiciona nós
            for layer_idx in layers_sorted:
                for p in network.layers_dict[layer_idx]:
                    for n in range(p.neurons):
                        node_id = f"{p.id}_{n+1}"
                        G.add_node(node_id, layer=layer_idx)

            # Conecta camadas vizinhas
            for i in range(len(layers_sorted) - 1):
                layer_a = network.layers_dict[layers_sorted[i]]
                layer_b = network.layers_dict[layers_sorted[i + 1]]
                for pa in layer_a:
                    for nb in range(pa.neurons):
                        id_a = f"{pa.id}_{nb+1}"
                        for pb in layer_b:
                            for nb2 in range(pb.neurons):
                                id_b = f"{pb.id}_{nb2+1}"
                                G.add_edge(id_a, id_b)

            # Calcula posição manual para árvore
            pos = {}
            y_offset = 0
            for layer_idx in layers_sorted:
                neurons = []
                for p in network.layers_dict[layer_idx]:
                    for n in range(p.neurons):
                        neurons.append(f"{p.id}_{n+1}")

                x_positions = np.linspace(-1, 1, len(neurons)) if len(neurons) > 1 else [0]
                for i, node in enumerate(neurons):
                    pos[node] = (x_positions[i], -layer_idx * 1.5)

            nx.draw(
                G, pos, with_labels=True, node_color='skyblue',
                node_size=1200, font_size=8, arrows=True
            )
            plt.title(f"Arquitetura: {network.name} (estilo árvore)")
            plt.show()

        except Exception as e:
            Utils.Logger.error(f"Erro ao exibir a rede: {e}")

class DataLoader:
    @staticmethod
    def load_csv(filepath, columns=None, target_column=None, delimiter=",", skip_header=False):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if skip_header:
                lines = lines[1:]
            data = [line.strip().split(delimiter) for line in lines if line.strip()]
            arr = np.array(data)
            if columns is not None:
                col_names = columns
            else:
                col_names = [str(i) for i in range(arr.shape[1])]
            if isinstance(target_column, str):
                target_idx = col_names.index(target_column)
            elif isinstance(target_column, int):
                target_idx = target_column
            else:
                target_idx = -1
            X = np.delete(arr, target_idx, axis=1).astype(float)
            y = arr[:, target_idx]
            try:
                y = y.astype(float)
            except:
                pass
            return X, y
        except Exception as e:
            Utils.Logger.error(f"Erro ao carregar CSV: {e}")
            return None, None

class Preprocess:
    @staticmethod
    def normalize(X, method="minmax"):
        X = np.array(X, dtype=float)
        if method == "minmax":
            return (X - np.min(X)) / (np.max(X) - np.min(X))
        elif method == "zscore":
            return (X - np.mean(X)) / (np.std(X) + 1e-8)
        elif method == "none":
            return X
        else:
            raise ValueError("Método de normalização não suportado: " + str(method))

    @staticmethod
    def split(X, y, test_size=0.2, shuffle=True, random_state=42):
        X = np.array(X)
        y = np.array(y)
        n = len(X)
        idx = np.arange(n)
        if shuffle:
            rng = np.random.RandomState(random_state)
            rng.shuffle(idx)
        X, y = X[idx], y[idx]
        if 0 < test_size < 1:
            n_test = int(n * test_size)
        else:
            n_test = int(test_size)
        X_train, X_test = X[:-n_test], X[-n_test:]
        y_train, y_test = y[:-n_test], y[-n_test:]
        return X_train, X_test, y_train, y_test

    @staticmethod
    def label_encode(y):
        classes, y_int = np.unique(y, return_inverse=True)
        return y_int, classes

    @staticmethod
    def one_hot_encode(y):
        y = np.array(y, dtype=int)
        n_classes = np.max(y) + 1
        return np.eye(n_classes)[y]
class Metrics:
    @staticmethod
    def accuracy(y_true, y_pred):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        return np.mean(y_true == y_pred)

    @staticmethod
    def confusion_matrix(y_true, y_pred):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        classes = np.unique(np.concatenate([y_true, y_pred]))
        matrix = np.zeros((len(classes), len(classes)), dtype=int)
        for t, p in zip(y_true, y_pred):
            i = np.where(classes == t)[0][0]
            j = np.where(classes == p)[0][0]
            matrix[i, j] += 1
        return matrix, classes

    @staticmethod
    def precision(y_true, y_pred, average='macro'):
        cm, classes = Metrics.confusion_matrix(y_true, y_pred)
        precisions = np.diag(cm) / (np.sum(cm, axis=0) + 1e-8)
        if average == 'macro':
            return np.mean(precisions)
        return precisions

    @staticmethod
    def recall(y_true, y_pred, average='macro'):
        cm, classes = Metrics.confusion_matrix(y_true, y_pred)
        recalls = np.diag(cm) / (np.sum(cm, axis=1) + 1e-8)
        if average == 'macro':
            return np.mean(recalls)
        return recalls

    @staticmethod
    def f1_score(y_true, y_pred, average='macro'):
        p = Metrics.precision(y_true, y_pred, average=None)
        r = Metrics.recall(y_true, y_pred, average=None)
        f1 = 2 * p * r / (p + r + 1e-8)
        if average == 'macro':
            return np.mean(f1)
        return f1
