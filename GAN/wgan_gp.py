import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, Input, Concatenate, LeakyReLU, BatchNormalization
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
import joblib

# Constants
LATENT_DIM = 64
NUM_FEATURES = 15
NUM_CLASSES = 10
BATCH_SIZE = 128
EPOCHS = 20
D_STEPS = 5
GP_WEIGHT = 10.0

class CWGANGP(tf.keras.Model):
    def __init__(self, generator, critic, latent_dim, d_steps=5, gp_weight=10.0):
        super(CWGANGP, self).__init__()
        self.generator = generator
        self.critic = critic
        self.latent_dim = latent_dim
        self.d_steps = d_steps
        self.gp_weight = gp_weight

    def compile(self, d_optimizer, g_optimizer):
        super(CWGANGP, self).compile()
        self.d_optimizer = d_optimizer
        self.g_optimizer = g_optimizer
        self.d_loss_metric = tf.keras.metrics.Mean(name="d_loss")
        self.g_loss_metric = tf.keras.metrics.Mean(name="g_loss")

    @property
    def metrics(self):
        return [self.d_loss_metric, self.g_loss_metric]

    def gradient_penalty(self, batch_size, real_samples, fake_samples, labels):
        alpha = tf.random.normal([batch_size, 1], 0.0, 1.0)
        diff = fake_samples - real_samples
        interpolated = real_samples + alpha * diff

        with tf.GradientTape() as gp_tape:
            gp_tape.watch(interpolated)
            pred = self.critic([interpolated, labels], training=True)

        grads = gp_tape.gradient(pred, [interpolated])[0]
        norm = tf.sqrt(tf.reduce_sum(tf.square(grads), axis=[1]))
        gp = tf.reduce_mean((norm - 1.0) ** 2)
        return gp

    @tf.function
    def train_step(self, data):
        real_samples, labels = data
        batch_size = tf.shape(real_samples)[0]

        # Train critic
        for i in range(self.d_steps):
            random_latent_vectors = tf.random.normal(shape=(batch_size, self.latent_dim))
            
            with tf.GradientTape() as tape:
                fake_samples = self.generator([random_latent_vectors, labels], training=True)
                fake_logits = self.critic([fake_samples, labels], training=True)
                real_logits = self.critic([real_samples, labels], training=True)

                d_cost = tf.reduce_mean(fake_logits) - tf.reduce_mean(real_logits)
                gp = self.gradient_penalty(batch_size, real_samples, fake_samples, labels)
                d_loss = d_cost + gp * self.gp_weight

            d_gradient = tape.gradient(d_loss, self.critic.trainable_variables)
            self.d_optimizer.apply_gradients(zip(d_gradient, self.critic.trainable_variables))

        # Train generator
        random_latent_vectors = tf.random.normal(shape=(batch_size, self.latent_dim))
        with tf.GradientTape() as tape:
            generated_samples = self.generator([random_latent_vectors, labels], training=True)
            gen_logits = self.critic([generated_samples, labels], training=True)
            g_loss = -tf.reduce_mean(gen_logits)

        gen_gradient = tape.gradient(g_loss, self.generator.trainable_variables)
        self.g_optimizer.apply_gradients(zip(gen_gradient, self.generator.trainable_variables))

        self.d_loss_metric.update_state(d_loss)
        self.g_loss_metric.update_state(g_loss)

        return {"d_loss": self.d_loss_metric.result(), "g_loss": self.g_loss_metric.result()}

def build_generator():
    noise = Input(shape=(LATENT_DIM,))
    label = Input(shape=(NUM_CLASSES,))
    x = Concatenate()([noise, label])
    x = Dense(128)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = BatchNormalization()(x)
    x = Dense(256)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = BatchNormalization()(x)
    x = Dense(128)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = BatchNormalization()(x)
    out = Dense(NUM_FEATURES, activation='linear')(x)
    return Model([noise, label], out, name="generator")

def build_critic():
    features = Input(shape=(NUM_FEATURES,))
    label = Input(shape=(NUM_CLASSES,))
    x = Concatenate()([features, label])
    x = Dense(256)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = Dropout(0.3)(x)
    x = Dense(128)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = Dropout(0.3)(x)
    x = Dense(64)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = Dropout(0.3)(x)
    out = Dense(1)(x)
    return Model([features, label], out, name="critic")

def run():
    print("Loading original dataset...")
    df = pd.read_csv('ml_training/dataset/unsw_nb_cleaned.csv')
    
    features = ['proto', 'state', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sload', 'dload', 'sloss', 'dloss', 'ct_srv_src', 'ct_dst_ltm']
    X = df[features].copy()
    y = df['attack_cat'].copy()

    from sklearn.preprocessing import LabelEncoder
    
    le_dict = {}
    for c in ['proto', 'state']:
        le = LabelEncoder()
        X[c] = le.fit_transform(X[c].astype(str))
        le_dict[c] = le
        
    scaler = joblib.load('ml_training/artifacts_improved/scaler.pkl')
    X_scaled = scaler.transform(X).astype(np.float32)
    
    label_encoder = joblib.load('ml_training/artifacts_improved/label_encoder.pkl')
    y_encoded = label_encoder.transform(y)
    
    y_onehot = tf.keras.utils.to_categorical(y_encoded, num_classes=NUM_CLASSES)
    
    dataset = tf.data.Dataset.from_tensor_slices((X_scaled, y_onehot))
    dataset = dataset.shuffle(buffer_size=1024).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    generator = build_generator()
    critic = build_critic()
    
    wgan = CWGANGP(generator, critic, LATENT_DIM, D_STEPS, GP_WEIGHT)
    wgan.compile(
        d_optimizer=tf.keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5, beta_2=0.9),
        g_optimizer=tf.keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5, beta_2=0.9)
    )

    print("Training WGAN-GP...")
    wgan.fit(dataset, epochs=EPOCHS)
    
    print("Saving Generator Model...")
    generator.save('GAN/generator.h5')
    print("Generator saved to GAN/generator.h5")

if __name__ == '__main__':
    run()
