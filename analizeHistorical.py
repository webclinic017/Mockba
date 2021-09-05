# Library Imports
import postgrescon as pg
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
plt.style.use("ggplot")

from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

from sqlalchemy import create_engine

import getHistorical as gh
# import getHistory as gh
# import postgrescon as pg
import load_preds as lp

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

def analize(psymbol):

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ['CUDA_VISIBLE_DEVICES'] = '5'

    if tf.test.gpu_device_name():
      print('--------------GPU found--------------')
    else:
      print("--------------No GPU found--------------")
    #tf_device='/gpu:1

    # Conexión a base de datos
    postgre_con = pg.Postgres().postgre_con

    # Tomando histórico
    # gh.getHistoricalData('ETHUSDT')
    gh.get_all_binance(psymbol, "5m", save=True)
    # Loading/Reading in the Data
    df = pd.read_csv(
        str(psymbol) + "-5m-data.csv").sort_values(by="timestamp", ascending=True)
    #df = pd.read_sql(
    #    "select to_char(TO_TIMESTAMP(close_time/1000),'dd/mm/yyyy hh24:mi:ss') close_time, close, close_time  b from temp_historial_ethusdt order by b asc", con=postgre_con)

 
    # Setting the datetime index as the date, only selecting the 'Close' column.
    df = df.set_index("timestamp")[['close']]
    df = df.set_index(pd.to_datetime(df.index))

    # Normalizing/Scaling the Data
    scaler = MinMaxScaler()
    df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

    # print(df.head())
    # Plotting the Closing Prices
    '''
    df.plot(figsize=(14,8))
    plt.title("BTC Closing Prices")
    plt.ylabel("Price (Normalized)")
    plt.show()
        '''

    def split_sequence(seq, n_steps_in, n_steps_out):
        """
        Splits the univariate time sequence
        """
        X, y = [], []
            
        for i in range(len(seq)):
            end = i + n_steps_in
            out_end = end + n_steps_out
            
            if out_end > len(seq):
                break
                
            seq_x, seq_y = seq[i:end], seq[end:out_end]
                
            X.append(seq_x)
            y.append(seq_y)
        
        return np.array(X), np.array(y)


    def visualize_training_results(results):
        """
        Plots the loss and accuracy for the training and testing data
            
        history = results.history
        plt.figure(figsize=(12,4))
        plt.plot(history['val_loss'])
        plt.plot(history['loss'])
        plt.legend(['val_loss', 'loss'])
        plt.title('Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.show()
            
        plt.figure(figsize=(12,4))
        plt.plot(history['val_accuracy'])
        plt.plot(history['accuracy'])
        plt.legend(['val_accuracy', 'accuracy'])
        plt.title('Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.show()
        """

    def layer_maker(n_layers, n_nodes, activation, drop=None, d_rate=.5):
        """
        Creates a specified number of hidden layers for an RNN
        Optional: Adds regularization option - the dropout layer to prevent potential overfitting (if necessary)
        """
            
        # Creating the specified number of hidden layers with the specified number of nodes
        for x in range(1,n_layers+1):
            model.add(LSTM(n_nodes, activation=activation, return_sequences=True))
            # model.add(Dense(units=32))
            # Adds a Dropout layer after every Nth hidden layer (the 'drop' variable)
            try:
                if x % drop == 0:
                    model.add(Dropout(d_rate))
            except:
                pass

    # How many periods looking back to learn
    n_per_in  = 30

    # How many periods to predict
    n_per_out = 20

    # Features (in this case it's 1 because there is only one feature: price)
    n_features = 1

    # Splitting the data into appropriate sequences
    X, y = split_sequence(list(df.close), n_per_in, n_per_out)

    # Reshaping the X variable from 2D to 3D
    X = X.reshape((X.shape[0], X.shape[1], n_features))

    # Instatiating the model
    model = Sequential()

    # Activation
    activ =  "relu"

    # Input layer
    model.add(LSTM(30, activation=activ, return_sequences=True, input_shape=(n_per_in, n_features)))

    # Hidden layers
    layer_maker(n_layers=8, n_nodes=24, activation=activ)

    # Final Hidden layer
    model.add(LSTM(10, activation=activ))

    # Output layer
    model.add(Dense(n_per_out))

    # Model summary
    model.summary()

    # Compiling the data with selected specifications
    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    res = model.fit(X, y, epochs=5, batch_size=3550, validation_split=0.1)

    visualize_training_results(res)
    plt.figure(figsize=(12,5))

    # Getting predictions by predicting from the last available X variable
    yhat = model.predict(X[-1].reshape(1, n_per_in, n_features)).tolist()[0]

    # Transforming values back to their normal prices
    yhat = scaler.inverse_transform(np.array(yhat).reshape(-1,1)).tolist()

    # Getting the actual values from the last available y variable which correspond to its respective X variable
    actual = scaler.inverse_transform(y[-1].reshape(-1,1))

    # Printing and plotting those predictions
    # print("Predicted Prices:\n", yhat)
    plt.plot(yhat, label='Predicted')

    # Printing and plotting the actual values
    # print("\nActual Prices:\n", actual.tolist())
    plt.plot(actual.tolist(), label='Actual')

        
    plt.title(f"Predicted vs Actual Closing Prices")
    plt.ylabel("Price")
    plt.legend()
    plt.savefig(psymbol + "_validation.png")
    """
    plt.show()
    """


    # Predicting off of y because it contains the most recent dates
    yhat = model.predict(np.array(df.tail(n_per_in)).reshape(1, n_per_in, n_features)).tolist()[0]

    # Transforming the predicted values back to their original prices
    yhat = scaler.inverse_transform(np.array(yhat).reshape(-1,1)).tolist()

    # Creating a DF of the predicted prices
    preds = pd.DataFrame(yhat, index=pd.date_range(start=df.index[-1], periods=len(yhat), freq="5T"), columns=df.columns)

    # Printing the predicted prices
    print(preds)

    # Generate csv
    header = ["timestamp", "close"]
    preds.to_csv('predict_' + psymbol + '.csv', header=header)

    # Load in database
    # lp.load_pred(postgre_con, "ETHUSDT")

    # Number of periods back to visualize the actual values
    pers = 10

    # Transforming the actual values to their original price
    actual = pd.DataFrame(scaler.inverse_transform(df[["close"]].tail(pers)), index=df.close.tail(pers).index, columns=df.columns).append(preds.head(1))

    # Plotting

    plt.figure(figsize=(16,6))
    plt.plot(actual, label="Actual Prices")
    plt.plot(preds, label="Predicted Prices")
    plt.ylabel("Price")
    plt.xlabel("Dates")
    plt.title(f"Forecasting the next {len(yhat)} períodos")
    plt.legend()
    plt.savefig(psymbol + "_predictions.png")
    """
    plt.show()
    """
