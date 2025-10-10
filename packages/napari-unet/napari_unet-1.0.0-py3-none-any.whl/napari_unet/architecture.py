import tensorflow as tf
from keras.models import Model
from keras.callbacks import Callback
from keras.callbacks import ReduceLROnPlateau, LearningRateScheduler
from keras.layers import (Input, Conv2D, MaxPooling2D, 
                                     Dropout, BatchNormalization,
                                     UpSampling2D, concatenate, Add,
                                     Conv2DTranspose, Activation, Multiply)

import tifffile
import shutil
import math

class EpochTickCallback(Callback):
    def __init__(self, callback_fx):
        super().__init__()
        self.callback_fx = callback_fx

    def on_epoch_end(self, epoch, logs=None):
        self.callback_fx(epoch+1)

class SavePredictionsCallback(Callback):
    def __init__(self, model_path, working_directory, dataset_generator, num_examples=5):
        """
        Custom callback to save predictions to images at the end of each epoch.

        Args:
            validation_data (tf.data.Dataset): The validation dataset to predict on.
            output_dir (str): The directory where images will be saved.
            num_examples (int): The number of examples to save at each epoch.
        """
        super().__init__()
        self.qc_dataset = dataset_generator() # make_dataset("validation", False)
        self.output_dir = working_directory / "predictions"
        self.num_examples = num_examples
        self.model_path = model_path

        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)

    def on_epoch_end(self, epoch, logs=None):
        if self.model is None:
            return

        ds_one = self.qc_dataset.take(self.num_examples).batch(self.num_examples)
        val_images, val_masks = tf.data.Dataset.get_single_element(ds_one)
        predictions = self.model.predict(val_images, verbose=0)

        epoch_dir = self.output_dir / f'epoch_{epoch + 1:03d}'
        epoch_dir.mkdir(parents=True, exist_ok=True)
        num_samples = int(val_images.shape[0])

        for i in range(num_samples):
            idx = i + 1
            tifffile.imwrite(epoch_dir / f'input_{idx:05d}.tif',  val_images[i].numpy())
            tifffile.imwrite(epoch_dir / f'mask_{idx:05d}.tif',   val_masks[i].numpy())
            tifffile.imwrite(epoch_dir / f'prediction_{idx:05d}.tif', predictions[i])

    def on_train_end(self, logs=None):
        # Move the last predictions into the model folder.
        all_epochs = sorted([f for f in self.output_dir.iterdir() if f.name.startswith('epoch')])
        if len(all_epochs) == 0:
            return
        last_epoch = all_epochs[-1]
        last_epoch_path = self.output_dir / last_epoch
        last_epoch_dest = self.model_path / "predictions"
        last_epoch_dest.mkdir(parents=True, exist_ok=True)
        shutil.move(last_epoch_path, last_epoch_dest)

def get_cosine_annealing_scheduler(learning_rate, n_epochs):
    def cosine_annealing(epoch, _):
        period = 50
        alpha = epoch * (1.0 / n_epochs)
        cosine_decay = 0.5 * (1 + math.cos(math.pi * (epoch % period) / period))
        decayed = (1.0 - alpha) * cosine_decay
        return float(learning_rate * decayed)
    return LearningRateScheduler(cosine_annealing)

def get_reduce_lr_on_plateau(learning_rate, n_epochs):
    return ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.75,
        patience=10,
        verbose=1,
        mode="auto",
        min_delta=1e-4,
        cooldown=0,
        min_lr=1e-6
    )

def attention_block(x, g, intermediate_channels):
    """
    Attention Block pour UNet.
    
    Args:
        x: TensorFlow tensor des caractéristiques de l'encodeur (skip connection).
        g: TensorFlow tensor des caractéristiques du décodeur.
        intermediate_channels: Nombre de canaux intermédiaires.

    Returns:
        Tensor avec attention appliquée sur `x`.
    """
    # Transformation de la caractéristique du décodeur
    g1 = Conv2D(intermediate_channels, kernel_size=1, strides=1, padding="same")(g)
    g1 = BatchNormalization()(g1)
    
    # Transformation de la caractéristique de l'encodeur
    x1 = Conv2D(intermediate_channels, kernel_size=1, strides=1, padding="same")(x)
    x1 = BatchNormalization()(x1)
    
    # Calcul de l'attention (g1 + x1 -> ReLU -> Sigmoid)
    psi = Add()([g1, x1])
    psi = Activation('relu')(psi)
    psi = Conv2D(1, kernel_size=1, strides=1, padding="same")(psi)
    psi = BatchNormalization()(psi)
    psi = Activation('sigmoid')(psi)
    
    # Application de l'attention sur x
    out = Multiply()([x, psi])
    return out

def create_unet2d_model(input_shape, unet_depth, num_filters_start, dropout_rate, use_attention=True):
    """
    Generates a UNet2D model with ReLU activations after each Conv2D layer.
    """
    inputs = Input(shape=input_shape)
    x = inputs

    # --- Encoder ---
    skip_connections = []
    for i in range(unet_depth):
        num_filters = num_filters_start * 2**i
        coef = (unet_depth - i - 1) / unet_depth
        x = Conv2D(num_filters, 3, activation='relu', padding='same', kernel_initializer='he_normal')(x)
        x = BatchNormalization()(x)
        x = Conv2D(num_filters, 3, activation='relu', padding='same', kernel_initializer='he_normal')(x)
        x = BatchNormalization()(x)
        skip_connections.append(x)
        x = Dropout(coef * dropout_rate)(x)
        x = MaxPooling2D(2)(x)
    
    # --- Bottleneck ---
    num_filters = num_filters_start * 2**unet_depth
    x = Conv2D(num_filters, 3, activation='relu', padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)
    x = Conv2D(num_filters, 3, activation='relu', padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)

    # --- Decoder ---
    for i in reversed(range(unet_depth)):
        num_filters = num_filters_start * 2**i
        x = UpSampling2D(2)(x)
        x = Conv2DTranspose(num_filters, (3, 3), strides=(1, 1), padding='same')(x)
        if use_attention:
            x = attention_block(skip_connections[i], x, intermediate_channels=8)
        x = concatenate([x, skip_connections[i]])
        x = Conv2D(num_filters, 3, activation='sigmoid', padding='same', kernel_initializer='he_normal')(x)
        x = Conv2D(num_filters, 3, activation='sigmoid', padding='same', kernel_initializer='he_normal')(x)
        if i > 0:
            x = BatchNormalization()(x)

    outputs = Conv2D(1, 1, activation='sigmoid')(x)
    model = Model(inputs=inputs, outputs=outputs)
    return model
