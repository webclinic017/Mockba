import pandas as pd

# Params price from exchange, estimated percentage
def predict_proximity(precioc, percentage):
    print('Leer resultados')
    data = pd.read_csv("predict_ETHUSDT.csv")
    close_list = data['close'].values
    print(close_list)
    print('Trading analize')  
    print('Purchase price: ' + str(precioc))
    # Compare list values % accurate for signal
    preditec_list = list(filter(lambda x: (x <= precioc),  close_list))
    predicted_percentaje = round((len(preditec_list) / len(close_list))*100)
    print('Analisis percentage ' + str(predicted_percentaje) + '%')
    if predicted_percentaje > percentage:
       print("Mount order")
       return True
    else:
       print("Prediction does not macth percentaje")
       return False