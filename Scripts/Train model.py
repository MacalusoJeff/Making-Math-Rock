import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

# Importing the training data
# cwd = os.getcwd()
cwd = "C:/Users/jemacalu/OneDrive - Microsoft/Projects/Misc/Music/Making Math Rock"
training_data_path = os.path.join(cwd, "Data/training_data.npy")
training_label_path = training_data_path.replace("_data.npy", "_labels.npy")
sequences = np.load(training_data_path, allow_pickle=True)
next_notes = np.load(training_label_path, allow_pickle=True)

# Input shape for the model
sequence_length = sequences.shape[1]
num_pitches = sequences.shape[2]

# # Simple LSTM
# simple_model = tf.keras.Sequential()
# simple_model.add(tf.keras.Input(shape=(sequence_length, num_pitches)))
# simple_model.add(layers.LSTM(56))
# simple_model.add(layers.Dense(num_pitches, activation="softmax"))
# simple_model.summary()

# simple_model.compile(
#     loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
# )

# epochs = 10
# batch_size = 128

early_stopping_callback = tf.keras.callbacks.EarlyStopping(
    monitor="loss",
    min_delta=0,
    patience=2,
    verbose=0,
    mode="auto",
    baseline=None,
    restore_best_weights=True,
    # start_from_epoch=0,
)

# # Training the model w/ early stopping
# history = simple_model.fit(
#     sequences,
#     next_notes,
#     batch_size=batch_size,
#     epochs=epochs,
#     callbacks=[early_stopping_callback],
# )

# # Saving the model
# model_path = os.path.join(cwd, "Data/Outputs/simple_LSTM.h5")
# simple_model.save(model_path)


# More complex LSTM with dropout
model = tf.keras.Sequential()
model.add(tf.keras.Input(shape=(sequence_length, num_pitches)))
model.add(layers.LSTM(128, return_sequences=True))
model.add(layers.Dropout(0.3))
model.add(layers.LSTM(56))
model.add(layers.Dropout(0.3))
model.add(layers.Dense(num_pitches, activation="softmax"))
model.summary()

model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

epochs = 10
batch_size = 128

# Training the model w/ early stopping
history = model.fit(
    sequences,
    next_notes,
    batch_size=batch_size,
    epochs=epochs,
    callbacks=[early_stopping_callback],
)

# Saving the model
model_path = os.path.join(cwd, "Data/Outputs/LSTM.h5")
model.save(model_path)
