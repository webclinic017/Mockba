import tensorflow as tf
import numpy as np

# Load historical data for the crypto asset
data = np.loadtxt("/home/andres/Descargas/crypto_data.csv", delimiter=",")

# Split the data into training and test sets
train_data = data[:8000]
test_data = data[8000:]

# Define the input and output layers of the neural network
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, input_shape=(3,), activation='relu'),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model on the training data
model.fit(train_data[:, :3], train_data[:, 3], epochs=10)

# Use the model to predict the price for the test data
predictions = model.predict(test_data[:, :3])

# Calculate the signal by comparing the predictions to the actual prices
signal = predictions - test_data[:, 3]
