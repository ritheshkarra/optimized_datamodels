#!/usr/bin/python
import psycopg2
import pandas as pd
import numpy as np
import datetime
import statsmodels
from statsmodels import api as sm
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.utils import check_array
from functools import partial
from multiprocessing import Pool
import pickle
import json
from statsmodels.tsa.arima_model import ARIMA


class Forecast:
    def getdatabaseconnection(self, psqlhost, databaseName, userName, password):
        psqlConnection = psycopg2.connect(host=psqlhost, dbname=databaseName, user=userName, password=password)
        marker = psqlConnection.cursor();
        return marker

    def get_db(self, marker, tableName, location, sensorid):
        marker.execute(
            """select po.sid, po.occupancy_avg, po.city, po.ts, po.year, po.hour, po.week, po.weekday, po.month, ps.label, ps.levellabel from """ + tableName + """ as po JOIN parking_space as ps ON po.sid = ps.sid and po.city='""" + location + """'""");
        # marker.execute("""SELECT sid,occupancy_avg, ts, year, hour, week, weekday, month From """ + tableName)
        result = marker.fetchall()
        dic = pd.DataFrame(result,
                           columns=['sid', 'occupancy_avg', 'city', 'TimeStamp', 'year', 'hour', 'week', 'weekday',
                                    'month', 'label', 'levellabel'])
        return dic

    def mean_absolute_percentage_error(self, y_true, y_pred):
        y_pred = y_pred[(y_true > 0)]
        y_true = y_true[(y_true > 0)]

        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def get_PDQ(self, series, p_vals=list(range(1, 11)), d_vals=list(range(1, 3)), q_vals=list(range(1, 11)),
                criterian='aic'):
        """
        Automate generation of best suited PDQ varaible for series of data. 
        series : data sequence to be pass to get best PDQ value
        criterian :'aic/bic'
        """

        aic_pdq = []
        for p in p_vals:
            for d in q_vals:
                for q in d_vals:
                    # print(series)
                    try:
                        # arima model is used for analysis
                        arima_mod = statsmodels.tsa.arima_model.ARIMA(series, order=(p, d, q), method='css').fit(
                            transparams=True, method='css')
                        if criterian == 'aic':
                            x = arima_mod.aic
                        elif criterian == 'bic':
                            x = arima_mod.bic
                        else:
                            print("Use your Brain")
                        x1 = p, d, q
                        # print (x1,x)

                        aic_pdq.append([x, x1])
                        # pdq.append(x1)

                    except:
                        pass
        df_1 = pd.DataFrame(aic_pdq, columns=['aic', 'pdq'])
        # print(df_1.shape)
        return df_1.loc[df_1['aic'].argmin()]

    def get_model_dict(self, data, label='occupancy_avg', grouping_col='sid'):
        """
        Currently only 2017 data is used 
        data : For which prediction has to be made

        Returns a dictionary of model
        """
        models = {}
        accuracy = {}
        data_new = data[(data['year'] == 2017)]
        for idx, parking_space in enumerate(data_new[grouping_col].unique()):
            print(" modeling for ", parking_space)
            data_id = data_new[data_new[grouping_col] == parking_space]
            series = data_id.copy()
            # series=data_id[data_id['month']==data_id['month'].max()]
            series.sort_values('TimeStamp', inplace=True)
            series.set_index('TimeStamp', inplace=True, drop=False)
            # res=self.get_PDQ(data_id[label])
            res = self.get_PDQ_parallel(series[label])
            try:
                (p, d, q) = np.argmin(res['aic'])
            except:
                models[parking_space] = np.median(series[label].values)
                continue
            # arima_mod = statsmodels.tsa.arima_model.ARIMA(series[label], order=(p, d, q),exog=series[['hour', 'week', 'weekday']], freq='H').fit(transparams=True, method='css')
            arima_mod = statsmodels.tsa.arima_model.ARIMA(series[label], order=(p, d, q), freq='H').fit(
                transparams=True, method='css')
            models[parking_space] = arima_mod

            y_pred = self.get_forecast(model=arima_mod,
                                       start_datetime=series['TimeStamp'].max() - datetime.timedelta(hours=11),
                                       end_time=series['TimeStamp'].max())
            y_true = series.loc[[series['TimeStamp'].max() - datetime.timedelta(hours=11 - i) for i in range(12)]][
                label]
            try:
                mape = self.mean_absolute_percentage_error(y_pred=y_pred, y_true=y_true)
                r2_val = r2_score(y_true, y_pred)
            except:
                mape = np.nan
                r2_val = np.nan
            accuracy[parking_space] = [mape, r2_val]
        return models, accuracy

    def get_parkingforecast(self, model, start_datetime, end_time):
        """
        model: Provide a model to get forcast value 
        start_datetime: datetime in datetime format from which hourly prediction will start
        end_datetime: datetime in datetime format at which hourly prediction will ends

        """
        exog = []
        #   start = datetime.datetime(2017,4,1,0)
        #   end = datetime.datetime(2017,4,30,23)
        step = datetime.timedelta(hours=1)
        start = start_datetime
        TimeStamp = []
        while start <= end_time:
            exog.append([start.hour, start.isocalendar()[1], start.weekday()])
            # print(start.isoweekday())
            TimeStamp.append(start)
            start += step
            exog = pd.DataFrame(exog)

            # return pd.DataFrame({"TimeStamp":TimeStamp,"Forecastvalue":model.forecast(exog.shape[0],exog)[0]})
        if type(model) != np.float64:
            #df = pd.DataFrame({"TimeStamp": TimeStamp, "Forecastvalue": model.forecast(exog.shape[0])[0]})
            df = pd.DataFrame({"TimeStamp": TimeStamp, "Forecastvalue": model.forecast(len(TimeStamp))[0]})
        else:
            # print(TimeStamp,[model]*(exog.shape[0]+1))
            df = pd.DataFrame({"TimeStamp": TimeStamp, "Forecastvalue": [model] * (len(TimeStamp))})
        return df

    def get_forecast(self, model, start_datetime, end_time):
        """
        model: Provide a model to get forcast value 
        start_datetime: datetime in datetime format from which hourly prediction will start
        end_datetime: datetime in datetime format at which hourly prediction will ends

        """
        exog = []
        #   start = datetime.datetime(2017,4,1,0)
        #   end = datetime.datetime(2017,4,30,23)
        step = datetime.timedelta(hours=1)
        start = start_datetime
        TimeStamp = []
        while start <= end_time:
            exog.append([start.hour, start.isocalendar()[1], start.weekday()])
            # print(start.isoweekday())
            TimeStamp.append(start)
            start += step
        exog = pd.DataFrame(exog)

        return pd.DataFrame({"TimeStamp":TimeStamp,"Forecastvalue":model.forecast(exog.shape[0],exog)[0]})

    def get_aic_bic(self, order, series):
        aic = np.nan
        bic = np.nan
        # print(series.shape,order)
        try:
            arima_mod = statsmodels.tsa.arima_model.ARIMA(series, order=order, freq='H').fit(transparams=True,
                                                                                             method='css')
            aic = arima_mod.aic
            bic = arima_mod.bic
            print(order, aic, bic)
        except:
            pass
        return aic, bic

    def get_PDQ_parallel(self, data, n_jobs=7):
        p_val = 13
        q_val = 13
        d_vals = 2
        pdq_vals = [(p, d, q) for p in range(p_val) for d in range(d_vals) for q in range(q_val)]
        get_aic_bic_partial = partial(self.get_aic_bic, series=data)
        p = Pool(n_jobs)
        res = p.map(get_aic_bic_partial, pdq_vals)
        p.close()
        return pd.DataFrame(res, index=pdq_vals, columns=['aic', 'bic'])


if __name__ == "__main__":
    def __getnewargs__(self):
        return ((self.endog), (self.k_lags, self.k_diff, self.k_ma))


    ARIMA.__getnewargs__ = __getnewargs__

    pf = Forecast()
    marker = pf.getdatabaseconnection("52.55.107.13", "cdp", "sysadmin", "sysadmin")
    marker.execute("""select sid, occupancy_avg, city, ts, year, hour, week, weekday, month from parking_occupancy """)
    data = marker.fetchall()
    data_db = pd.DataFrame(data,
                           columns=['sid', 'occupancy_avg', 'city', 'TimeStamp', 'year', 'hour', 'week', 'weekday',
                                    'month'])
    data_db.dropna(subset=['occupancy_avg'], inplace=True, axis=0)
    models, accuracy = pf.get_model_dict(data_db, label='occupancy_avg')
    pickle.dump(models, open('parkingforcast.pickle', 'wb'))
    # starttime = 1492234879
    # endtime = 1492645279
    # models = pickle.load(open('parkingforcastModelAll.pickle', 'rb'))
    # forecast_values = {}
    # forecast_dict = {}
    # for parking_space in models.keys():
    # forecast_values[parking_space] = pf.get_forecast(models[parking_space], datetime.datetime(2017, 4, 13, 0),datetime.datetime(2017, 4, 17, 23)).to_json()
    # print(pf.get_forecast(models[parking_space], datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime))))
    # print(json.loads(forecast_values))
    # print(forecast_values)
