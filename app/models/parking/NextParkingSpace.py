#!/usr/bin/python
import pandas as pd
import numpy as np
import os,sys,ast,requests
import json
from math import radians, cos, sin, asin, sqrt
import itertools
import requests
import psycopg2
import ast
#from IPython.display import display,HTML
os.environ['TZ'] = 'Asia/Kolkata'

class NextParkingSpace:

    def getDBConnection(self, psqlhost, databaseName, userName, password):
        psqlConnection = psycopg2.connect(host=psqlhost, dbname=databaseName, user=userName, password=password)
        marker = psqlConnection.cursor();
        return marker


    def get_geo_parking(self):
        data_1=json.dumps({
        "Query":{
        "Find":{
        "ParkingSpace":{
        "sid":{
        "ne":""
        }
        }
        }
        }
        })
        # Real time api for parking
        link='https://cdp-jaipur.cisco.com/deveng/fid-CIMQueryInterface?SensorCustomerKey=500001&AppKey=CDP-App&UserKey=500060'
        headers = {'Content-type': 'application/json', 'body': 'raw'}
        parking_real_time=requests.post(link,data=data_1)
        #print(parking_real_time.status_code)
        data=parking_real_time.json()
        li=[]
        colms=['sid','levelLabel','operatedBy','label','occupied','total','sensorCustomerId','hierId','siblingIndex'\
               ,'provider','providerId','geo_pts','maxDurationMinutes','parkingRate_durationMinutes'\
               ,'parkingRate_farePerMinute','zoneType']
        li.append(colms)
        for item in data['Find']['Result']:
            elem=item['ParkingSpace']
            sid=elem['sid']
        try:
            levelLabel=elem['levelLabel']
        except:
            levelLabel=np.nan
        try:
            operatedBy=elem['operatedBy']
        except:
            operatedBy=np.nan
        label=elem['label']
        occupied=elem['state']['occupied']
        total=elem['state']['total']    
        sensorCustomerId=elem['sensorCustomerId']
        hierId=elem['hierId']
        try:
            siblingIndex=elem['siblingIndex']
        except:
            siblingIndex=np.nan   
        provider=elem['providerDetails']['provider']
        providerId=elem['providerDetails']['providerId']
        geo_pt=elem['boundary']
        try:
            maxDurationMinutes=elem['opParams']['maxDurationMinutes']
            parkingRate_durationMinutes=elem['opParams']['parkingRate']['durationMinutes']
            parkingRate_farePerMinute=elem['opParams']['parkingRate']['farePerMinute']
            zoneType=elem['opParams']['zoneType']
        except:
            maxDurationMinutes=np.nan
            parkingRate_durationMinutes=np.nan
            parkingRate_farePerMinute=np.nan
            zoneType=np.nan        
        geo_pts=[] 
        for elem_1 in geo_pt['geoPoint']:
            geo_pts.append([elem_1['latitude'],elem_1['longitude']])
        li.append([sid,levelLabel,operatedBy,label,occupied,total,sensorCustomerId,hierId,siblingIndex,provider,providerId\
                   ,geo_pts,maxDurationMinutes,parkingRate_durationMinutes,parkingRate_farePerMinute,zoneType])   

        data_df=pd.DataFrame(li[1:],columns=li[0])
        return data_df
    
    def create_data_1(self,dictionary,path_to_save=None):
        RWS=dictionary['RWS']
        l=[]
        for rw in RWS:
            EBU_COUNTRY_CODE=rw['EBU_COUNTRY_CODE']
            EXTENDED_COUNTRY_CODE=rw['EXTENDED_COUNTRY_CODE']
            UNITS=rw['UNITS']
            for elem in rw['RW']:
                DE=elem['DE']
                LI=elem['LI']
                PBT=elem['PBT']
                mid=elem['mid']
                FIS=elem['FIS']
                for FI in FIS:
                    elem_1=FI['FI']
                    for elem_2 in elem_1:
                        LE=elem_2['TMC']['LE']
                        PC=elem_2['TMC']['PC']
                        QD=elem_2['TMC']['QD']
                        SHP=elem_2['SHP'][0]['value'][0]
                        SHP=SHP.split(" ")[0]
                        CF=elem_2['CF']
                        for elem_3 in CF:
                            FF=elem_3['FF']
                            CN=elem_3['CN']
                            JF=elem_3['JF']
                            SP=elem_3['SP']
                            SU=elem_3['SU']
                            TY=elem_3['TY']
                            l.append([EBU_COUNTRY_CODE,EXTENDED_COUNTRY_CODE,UNITS,DE,LI,PBT,mid,LE,PC,QD,SHP,FF,CN,JF,SP,SU,TY])
        clms=['EBU_COUNTRY_CODE','EXTENDED_COUNTRY_CODE','UNITS','DE','LI','PBT','mid','LE','PC','QD','SHP','FF','CN','JF','SP','SU','TY']
        df=pd.DataFrame(l,columns=clms)
        df['PBT']=datetime.datetime.now()
        #print(json.dumps(rws_list, indent=2))
        if path_to_save:
            if os.path.isfile(path_to_save):
                df.to_csv(path_to_save,mode='a',header=False,index=False)
            else:
                df.to_csv(path_to_save,mode='w',index=False)
        else:
            return df   
 
    def get_road_info(self,point,radius=50):
        link='https://traffic.cit.api.here.com/traffic/6.1/flow.json?prox='+str(point[0])+'%2C'+str(point[1])+'%2C'+str(radius)+'&responseattributes=sh,fc&app_id=ONe0616Q1jK0RLmeN7fc&app_code=bWQ6Eir1V2KRjaS-5oMOcw'
        r=requests.get(link)
        road=self.create_data_1(r.json())[['DE','SHP']]
        return road.drop_duplicates(subset='DE')
 

    def get_route_info(self, point_1,point_2,mode=['fastest','car'],app_id='QacvSHflGqkVBJGvs9OS',app_code='9dbgDyDrC1ChasubHX7Xfw',traffic_mode='enabled'):
        #mode='list of modes['fastest','car']
        link='https://route.cit.api.here.com/routing/7.2/calculateroute.json?waypoint0='+str(point_1[0][0])+'%2C'+str(point_1[0][1])+'&waypoint1='+str(point_2[0][0])+'%2C'+str(point_2[0][1])+'&mode='+'%3B'.join(str(e) for e in mode)+'%3Btraffic%3A'+traffic_mode+'&app_id='+app_id+'&app_code='+app_code+'&departure=now'
        r=requests.get(link)
        jsn=r.json()
        summary=jsn['response']['route'][0]['summary']
        return summary['trafficTime'],summary['travelTime'],summary['distance']

    def get_traffic_info(self,data,grouping_cols='sid'):
        dist_stat={}
        #get traffic info travel time and distance
        sen_pos=data.groupby(grouping_cols).agg({'geo_pts':'first'})
        dist_df=pd.DataFrame(index=sen_pos.index,columns=sen_pos.index)
        travel_time_df=pd.DataFrame(index=sen_pos.index,columns=sen_pos.index)
        traffic_time_df=pd.DataFrame(index=sen_pos.index,columns=sen_pos.index)
        pt1_pt2=[]
        for subset in itertools.combinations(sen_pos.index, 2):
            pt1_pt2.append(subset)
        for i in pt1_pt2:
            temp=self.get_route_info(sen_pos.loc[i[0]]['geo_pts'],sen_pos.loc[i[1]]['geo_pts'])
            temp1=self.get_route_info(sen_pos.loc[i[1]]['geo_pts'],sen_pos.loc[i[0]]['geo_pts'])
            # travelling from a to b
            dist_df.loc[i[0],i[1]]=temp[0]
            travel_time_df.loc[i[0],i[1]]=temp[1]
            traffic_time_df.loc[i[0],i[1]]=temp[2]
            # travelling from b to a
            dist_df.loc[i[1],i[0]]=temp1[0]
            travel_time_df.loc[i[1],i[0]]=temp1[1]
            traffic_time_df.loc[i[1],i[0]]=temp1[2]
        dist_stat['dist']=dist_df
        dist_stat['travel_time']=travel_time_df
        dist_stat['traffic_time']=traffic_time_df
        return dist_stat

    def conv_2_list(self,row):
        geo_pts = []
        for elem_1 in row['geoPoint']:
            geo_pts.append([elem_1['latitude'], elem_1['longitude']])
        return geo_pts

    def next_parkingspace_main(self,spaceId,radius):
        #nps = NextParkingSpace()
        marker = self.getDBConnection("52.55.107.13", "cdp", "sysadmin" ,"sysadmin")
        query="select sid, state, providerdetails, boundary, label, levellabel, ts from parking_space where sid = '" + spaceId + "'"
        marker.execute(query)
        #marker.execute("""select sid, state, providerdetails, boundary, label, levellabel, ts from parking_space""")
        data_db = marker.fetchall()
        data = pd.DataFrame(data_db,columns=['sid', 'state', 'providerdetails', 'geo_pts', 'label', 'levellabel', 'ts'])
        data['geo_pts'] = data['geo_pts'].apply(lambda x: ast.literal_eval(x))
        data['geo_pts'] = data['geo_pts'].apply(lambda x: self.conv_2_list(x))
        #data=nps.get_geo_parking()
        data['mean_position']=data['geo_pts'].apply(lambda x: [np.mean([i[0] for i in x]),np.mean([i[1] for i in x])])
        #dist_stat=self.get_traffic_info(data)
        #road_inf=data['mean_position'].apply(lambda x:  self.get_road_info(x,radius))
        return self.get_road_info(data['mean_position'][0],radius)
        '''
        ## minimum distance`
        dist_stat['dist'][dist_stat['dist']==0]=np.nan
        x = dist_stat['dist'].apply(lambda x: np.argmin(x))

        ### minimum travel time
        dist_stat['travel_time'][dist_stat['travel_time']==0]=np.nan
        travel = dist_stat['travel_time'].apply(lambda x: np.argmin(x))

        ### minimum traffic distance
        dist_stat['traffic_time'][dist_stat['traffic_time']==0]=np.nan
        traffic = dist_stat['traffic_time'].apply(lambda x: np.argmin(x))
        '''

        
if __name__ == "__main__":
    nps = NextParkingSpace()
    nps.next_parkingspace_main('ParkingSpace__metro__Bldg1Flr7',50)
