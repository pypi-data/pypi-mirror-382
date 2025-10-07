from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import backend as K


class CustomAttentionLayer(tf.keras.layers.Layer):
    """
    Simple attention over the time dimension that emphasizes the top-10%
    time steps (by attention weight) via an emphasis factor.

    Output shape: (batch, 1, features)
    """

    def __init__(self, emphasis_factor: float = 1.5, **kwargs):
        super().__init__(**kwargs)
        self.emphasis_factor = float(emphasis_factor)

    def get_config(self):
        cfg = super().get_config()
        cfg.update({"emphasis_factor": self.emphasis_factor})
        return cfg

    def build(self, input_shape):
        self.W = self.add_weight(
            name="att_weight",
            shape=(input_shape[-1], 1),
            initializer="glorot_uniform",
            trainable=True,
        )
        self.b = self.add_weight(
            name="bias", shape=(1,), initializer="zeros", trainable=True
        )
        super().build(input_shape)

    def call(self, x):
        # x: (batch, T, features)
        e = K.tanh(K.dot(x, self.W) + self.b)   # (batch, T, 1)
        a = K.softmax(e, axis=1)                # (batch, T, 1)

        a_flat = tf.squeeze(a, axis=-1)         # (batch, T)
        T = tf.shape(a_flat)[1]
        k = tf.maximum(1, tf.cast(tf.cast(T, tf.float32) * 0.1, tf.int32))
        _, top_idx = tf.nn.top_k(a_flat, k)     # (batch, k)

        # Build boolean mask for top-k time steps
        top_idx_exp = tf.expand_dims(top_idx, 2)       # (batch, k, 1)
        range_row   = tf.reshape(tf.range(T), (1, 1, T))
        mask_flat   = tf.reduce_any(tf.equal(top_idx_exp, range_row), axis=1)  # (batch, T)
        mask        = tf.expand_dims(mask_flat, axis=-1)  # (batch, T, 1)

        a_emph = tf.where(mask, a * self.emphasis_factor, a)  # (batch, T, 1)
        return tf.reduce_sum(x * a_emph, axis=1, keepdims=True)  # (batch, 1, features)
