import os
import re
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf

SEQ_LENGTH    = 100
EMBEDDING_DIM = 16
GRU_UNITS     = 128
BATCH_SIZE    = 32
EPOCHS        = 10

_BASE             = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.path.join(_BASE, 'models')
DEFAULT_CSV       = os.path.join(_BASE, 'dataset', 'poems.csv')


def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zñáéíóúüç\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _to_dataset(sequence, length: int, shuffle: bool = False,
                seed: int | None = None, batch_size: int = BATCH_SIZE):
    
    ds = tf.data.Dataset.from_tensor_slices(sequence)
    ds = ds.window(length + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(length + 1))
    if shuffle:
        ds = ds.shuffle(100_000, seed=seed)
    ds = ds.batch(batch_size)
    return ds.map(lambda w: (w[:, :-1], w[:, 1:])).prefetch(1)


class PoetryGenerator:
    def __init__(self):
        self.text_vec_layer: tf.keras.layers.TextVectorization | None = None
        self._inner_model: tf.keras.Model | None = None 
        self._poem_model:  tf.keras.Model | None = None  
        self.n_tokens:     int = 0
        self.authors_text: dict[str, str] = {}

    def _build_inner_model(self) -> tf.keras.Model:
        tf.random.set_seed(42)
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(input_dim=self.n_tokens, output_dim=EMBEDDING_DIM),
            tf.keras.layers.GRU(GRU_UNITS, return_sequences=True),
            tf.keras.layers.Dense(self.n_tokens, activation="softmax"),
        ])
        model.compile(
            loss="sparse_categorical_crossentropy",
            optimizer="nadam",
            metrics=["accuracy"],
        )
        return model

    def _build_poem_model(self) -> tf.keras.Model:
        return tf.keras.Sequential([
            self.text_vec_layer,
            tf.keras.layers.Lambda(lambda X: X - 2), 
            self._inner_model,
        ])

    def train(self, csv_path: str = DEFAULT_CSV, epochs: int = EPOCHS) -> None:
        df = pd.read_csv(csv_path)

        for author, group in df.groupby('author'):
            self.authors_text[author] = _clean(
                ' '.join(group['content'].fillna('').astype(str).tolist())
            )

        full_text = _clean(' '.join(df['content'].fillna('').astype(str).tolist()))

        self.text_vec_layer = tf.keras.layers.TextVectorization(
            split="character", standardize="lower"
        )
        self.text_vec_layer.adapt([full_text])

        encoded = self.text_vec_layer([full_text])[0]
        encoded -= 2                                         
        self.n_tokens = self.text_vec_layer.vocabulary_size() - 2

        print(f"Vocabulary size: {self.n_tokens} characters")
        print(f"Dataset size   : {len(encoded)} encoded chars")

        split = int(len(encoded) * 0.9)
        train_set = _to_dataset(encoded[:split], SEQ_LENGTH, shuffle=True, seed=42)
        valid_set = _to_dataset(encoded[split:],  SEQ_LENGTH)

        self._inner_model = self._build_inner_model()

        os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)
        ckpt = tf.keras.callbacks.ModelCheckpoint(
            os.path.join(DEFAULT_MODEL_DIR, 'best_model.keras'),
            monitor="val_accuracy",
            save_best_only=True,
        )
        self._inner_model.fit(
            train_set, validation_data=valid_set,
            epochs=epochs, callbacks=[ckpt],
        )

        self._poem_model = self._build_poem_model()

    def save(self, model_dir: str = DEFAULT_MODEL_DIR) -> None:
        os.makedirs(model_dir, exist_ok=True)
        self._inner_model.save(os.path.join(model_dir, 'inner_model.keras'))
        with open(os.path.join(model_dir, 'meta.pkl'), 'wb') as f:
            pickle.dump({
                'vocab':        self.text_vec_layer.get_vocabulary(),
                'n_tokens':     self.n_tokens,
                'authors_text': self.authors_text,
            }, f)

    def load(self, model_dir: str = DEFAULT_MODEL_DIR) -> None:
        import zipfile, io, h5py

        
        with open(os.path.join(model_dir, 'meta.pkl'), 'rb') as f:
            data = pickle.load(f)

        self.n_tokens     = data['n_tokens']
        self.authors_text = data['authors_text']

        
        self._inner_model = self._build_inner_model()
       
        self._inner_model(tf.zeros((1, SEQ_LENGTH), dtype=tf.int32))

        keras_path = os.path.join(model_dir, 'inner_model.keras')
        with zipfile.ZipFile(keras_path, 'r') as z:
            raw = z.read('model.weights.h5')

        with h5py.File(io.BytesIO(raw), 'r') as f:
            embedding_w  = f['layers/embedding/vars/0'][:]
            gru_kernel   = f['layers/gru/cell/vars/0'][:]
            gru_rec      = f['layers/gru/cell/vars/1'][:]
            gru_bias     = f['layers/gru/cell/vars/2'][:]
            dense_kernel = f['layers/dense/vars/0'][:]
            dense_bias   = f['layers/dense/vars/1'][:]

        self._inner_model.set_weights(
            [embedding_w, gru_kernel, gru_rec, gru_bias, dense_kernel, dense_bias]
        )

        self.text_vec_layer = tf.keras.layers.TextVectorization(
            split="character", standardize="lower"
        )
        self.text_vec_layer.set_vocabulary(data['vocab'])

        self._poem_model = self._build_poem_model()


    @property
    def is_ready(self) -> bool:
        return self._poem_model is not None and self.n_tokens > 0

    def list_authors(self) -> list[str]:
        return sorted(self.authors_text.keys())

    def find_author(self, query: str) -> str | None:
        """Return the best-matching author name found inside a free-text query."""
        q = query.lower()
        best: str | None = None
        best_len = 0
        for author in self.authors_text:
            for part in re.split(r'\s+', author.lower()):
                if len(part) > 3 and part in q and len(part) > best_len:
                    best = author
                    best_len = len(part)
        return best

    def generate_poem(
        self,
        author: str | None = None,
        num_chars: int = 300,
        temperature: float = 1.0,
    ) -> str:
        if not self.is_ready:
            raise RuntimeError("Modelo no cargado. Llama a train() o load() primero.")

        corpus = self.authors_text.get(author or '', '') or \
                 ' '.join(self.authors_text.values())
        corpus = _clean(corpus)

        if len(corpus) >= SEQ_LENGTH:
            start = np.random.randint(0, len(corpus) - SEQ_LENGTH)
            seed  = corpus[start:start + SEQ_LENGTH]
        else:
            seed = (corpus * (SEQ_LENGTH // max(len(corpus), 1) + 1))[:SEQ_LENGTH]

        window = list((self.text_vec_layer([seed]) - 2).numpy()[0])
        vocab  = self.text_vec_layer.get_vocabulary()

        generated: list[str] = []
        for _ in range(num_chars):
            x       = tf.constant([window[-SEQ_LENGTH:]])              
            y_proba = self._inner_model(x, training=False)[0, -1:]      
            logits  = tf.math.log(y_proba) / temperature
            idx     = int(tf.random.categorical(logits, num_samples=1)[0, 0])
            window.append(idx)
            generated.append(vocab[idx + 2])

        return ''.join(generated)
