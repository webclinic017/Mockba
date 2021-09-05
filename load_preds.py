import pandas as pd
import postgrescon as pg


def load_pred_eth(pcon, psymbol):
    df = pd.read_csv('predict_' + psymbol + '.csv')
    df.columns = ['close_time', 'close_pred']
    # print(df)
    df.to_sql('predict_' + psymbol, if_exists="replace", con=pcon, index=True)
