#!/usr/bin/python
import psycopg2
import pandas as pd
import datetime
import statsmodels 
from statsmodels import api as sm
import pickle
import warnings
warnings.filterwarnings('ignore')

class ParkingForecast:

    def getDBConnection(self,psqlhost, databaseName,userName , password):
        psqlConnection = psycopg2.connect(host=psqlhost, dbname=databaseName, user=userName , password=password)
        marker = psqlConnection.cursor();
        return marker

    def get_db(self, marker, tableName, location, sensorid):
        marker.execute("""select po.sid, po.occupancy_avg, po.city, po.ts, po.year, po.hour, po.week, po.weekday, po.month, ps.label, ps.levellabel from """ + tableName + """ as po JOIN parking_space as ps ON po.sid = ps.sid and po.city='"""+ location + """'""");
        #marker.execute("""SELECT sid,occupancy_avg, ts, year, hour, week, weekday, month From """ + tableName)
        result = marker.fetchall()
        dic = pd.DataFrame(result, columns=['sid','occupancy_avg', 'city','TimeStamp', 'year', 'hour', 'week', 'weekday', 'month', 'label', 'levellabel'])
        return dic

    def get_PDQ(self,series,p_vals=list(range(1,12)),d_vals=list(range(1,3)),q_vals=list(range(1,12)),criterian='aic'):
        """
        Automate generation of best suited PDQ varaible for series of data. 
        series : data sequence to be pass to get best PDQ value
        criterian :'aic/bic'parking_occupancy
        """

        aic_pdq =[]
        for p in p_vals:
            for d in q_vals:
                for q in d_vals:
                    #print(series)
                    try:
                        # arima model is used for analysis
                        arima_mod=statsmodels.tsa.arima_model.ARIMA(series,order=(p,d,q)).fit(transparams=True)
                        if criterian=='aic':
                            x=arima_mod.aic
                        elif criterian=='bic':
                            x=arima_mod.bic
                        else:
                            print("Use your Brain")
                        x1= p,d,q
                        #print (x1,x)

                        aic_pdq.append([x,x1])
                        #pdq.append(x1)

                    except:
                        pass
        df_1 = pd.DataFrame(aic_pdq,columns=['aic','pdq'])
        #print(df_1.shape)
        return df_1.loc[df_1['aic'].argmin()]

    def get_model_dict(self,data,label='occupancy_avg',grouping_col='sid'):
        """
        Currently only 2017 data is used 
        data : For which prediction has to be made

        Returns a dictionary of model
        """
        import statsmodels 
        from statsmodels import api as sm
        print("inside model_dict")
        models={}
        data_new=data[(data['year']==2017)]
        print(data_new)
        for idx,parking_space in enumerate(data_new[grouping_col].unique()):
            print(" modeling for " ,parking_space)
            data_id=data_new[data_new[grouping_col]==parking_space].sort_values('TimeStamp')
            series=data_id
            #series=data_id[data_id['month']==data_id['month'].max()]
            series.set_index('TimeStamp',inplace=True)
            res=self.get_PDQ(data_id[label])
            (p,d,q)=res['pdq']

            arima_mod=statsmodels.tsa.arima_model.ARIMA(series[label],order=(p,d,q),exog=series[['hour','week','weekday']]).fit(transparams=True)
            models[parking_space]=arima_mod

        return models

    def get_forecast(self,model,start_datetime,end_time):
        exog=[]
        step = datetime.timedelta(hours=1)
        start=start_datetime
        while start<= end_time:
            exog.append([start.hour,start.isocalendar()[1],start.weekday()])
            start += step
        exog=pd.DataFrame(exog)
        return model.forecast(exog.shape[0],exog)[0]

    def retrain_model(self,old_model,new_data,label):
        (p,d,q)=(old_model.k_ar,old_model.k_diff,old_model.k_ma)
        new_data.set_index('TimeStamp',inplace=True)
        arima_mod=statsmodels.tsa.arima_model.ARIMA(new_data[label],order=(p,d,q),exog=new_data[['hour','week','weekday']]).fit(transparams=True)
        return arima_mod


if __name__ == "__main__":
    pf = ParkingForecast()
    marker = pf.getDBConnection("52.55.107.13", "cdp", "sysadmin" ,"sysadmin")
    data_db = pf.get_db(marker,"parking_occupancy", "jaipur" ,"ParkingSpace__metro__Bldg8Flr1")
    #print(data_db.iloc[1:1000, :])
    #models=pf.get_model_dict(data_db)
    models = pf.get_model_dict(data_db[data_db['sid']=='ParkingSpace__metro__Bldg2Flr1'].sort_values('TimeStamp',ascending=False).iloc[1:10000,:])
    pickle.dump(models, open('parkingforcastModelCity.pickle', 'wb'))
    starttime = 1492234879
    endtime = 1492645279
    #models = pickle.load(open('parkingforcastModel.pickle', 'rb'))
    '''forecast_values=[]
    for parking_space in models.keys():
        #forecast_values.append(pf.get_forecast(models[parking_space],datetime.datetime(2017,4,13,0),datetime.datetime(2017,4,17,23)))
        forecast = pf.get_forecast(models[parking_space],datetime.datetime.fromtimestamp(float(starttime)),datetime.datetime.fromtimestamp(float(endtime)))
        print(forecast_values)'''
