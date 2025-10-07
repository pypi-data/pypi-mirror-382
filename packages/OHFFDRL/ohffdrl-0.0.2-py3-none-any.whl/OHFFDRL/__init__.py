from collections import Counter

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


class OHFFDRL:
    def __init__(self, input_dim, X_train, X_val, y_train, y_val):
        self.input_dim = input_dim
        self.X_train = X_train
        self.X_val = X_val
        self.y_train = y_train
        self.y_val = y_val

    def build_model(self, mu_init, sigma_init):
        fuzzy = FuzzyLayer(self.input_dim, num_memberships=3)
        fuzzy.mu.assign(tf.convert_to_tensor(mu_init, dtype=tf.float32))
        fuzzy.sigma.assign(tf.convert_to_tensor(sigma_init, dtype=tf.float32))

        inputs = tf.keras.Input(shape=(self.input_dim,))
        fuzzy_out = fuzzy(inputs)
        flat = tf.keras.layers.Flatten()(fuzzy_out)
        dense1 = tf.keras.layers.Dense(128, activation='relu')(flat)
        drop = tf.keras.layers.Dropout(0.2)(dense1)
        dense2 = tf.keras.layers.Dense(64, activation='relu')(drop)
        output = tf.keras.layers.Dense(2, activation='softmax')(dense2)

        model = tf.keras.Model(inputs=inputs, outputs=output)
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy'])
        return model

    def fitness_function(self, position):
        mu = position[:len(position) // 2].reshape(3, self.input_dim)
        sigma = np.abs(
            position[len(position) // 2:].reshape(3, self.input_dim)) + 1e-2
        model = self.build_model(mu, sigma)
        model.fit(
            self.X_train,
            self.y_train,
            epochs=10,
            batch_size=32,
            verbose=0)
        y_pred = np.argmax(model.predict(self.X_val), axis=1)
        return 1 - accuracy_score(self.y_val, y_pred)

    def whho_optimize(self, dim, n_agents=5, max_iter=5):
        pop = np.random.uniform(-1, 1, (n_agents, dim))
        fitness = np.array([self.fitness_function(ind) for ind in pop])
        best_idx = np.argmin(fitness)
        best = pop[best_idx]

        for _ in range(max_iter):
            for i in range(n_agents):
                r = np.random.rand()
                pop[i] = pop[i] + r * (best - pop[i])
                fitness[i] = self.fitness_function(pop[i])
            best_idx = np.argmin(fitness)
            best = pop[best_idx]
        return best


class FuzzyLayer(tf.keras.layers.Layer):
    def __init__(self, in_features, num_memberships):
        super(FuzzyLayer, self).__init__()
        self.in_features = in_features
        self.num_memberships = num_memberships
        self.mu = self.add_weight(
            name="mu", shape=[num_memberships, in_features],
            initializer="random_normal",
            trainable=True)
        self.sigma = self.add_weight(
            name="sigma", shape=[num_memberships, in_features],
            initializer="ones",
            trainable=True)

    def call(self, inputs):
        x = tf.expand_dims(inputs, axis=1)
        mu = tf.expand_dims(self.mu, axis=0)
        sigma = tf.expand_dims(self.sigma, axis=0)
        return tf.exp(-tf.square((x - mu) / sigma))
