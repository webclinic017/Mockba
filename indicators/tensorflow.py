import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras

# load data
df = pd.read_csv('crypto_data.csv')

# preprocess data
df = df.dropna() # remove null values
df = df[["open", "high", "low", "close", "volume", "market_cap"]] # select relevant features
df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0) # create target variable

# split data into train and test sets
split_idx = int(0.8 * len(df))
train_data = df[:split_idx]
test_data = df[split_idx:]

# normalize data
train_mean = train_data.mean()
train_std = train_data.std()
train_data = (train_data - train_mean) / train_std
test_data = (test_data - train_mean) / train_std

# create input pipeline
train_ds = tf.data.Dataset.from_tensor_slices((train_data.values[:, :-1], train_data.values[:, -1]))
train_ds = train_ds.shuffle(len(train_data)).batch(32)

test_ds = tf.data.Dataset.from_tensor_slices((test_data.values[:, :-1], test_data.values[:, -1]))
test_ds = test_ds.batch(32)

# define model
model = keras.Sequential([
    keras.layers.Dense(32, activation='relu', input_shape=(train_data.shape[-1]-1,)),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

# compile model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# train model
model.fit(train_ds, epochs=50)

# evaluate model on test data
loss, accuracy = model.evaluate(test_ds)
print(f"Test accuracy: {accuracy:.2f}")

# predict on new data
new_data = pd.DataFrame({'open': [8000], 'high': [9000], 'low': [7000], 'close': [8500], 'volume': [2000], 'market_cap': [150000000]})
new_data = (new_data - train_mean[:-1]) / train_std[:-1]
prediction = model.predict(new_data.values)
print(f"Prediction: {prediction}")
