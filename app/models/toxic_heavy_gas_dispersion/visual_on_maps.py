import folium
from itertools import  count
import pandas
from folium.plugins import HeatMap
import pandas
import matplotlib.pyplot as plt

def draw_circles(leakageLat, leakageLong, rad, col, pop, fill,opc, map_name):
    folium.CircleMarker([leakageLat, leakageLong],
                    radius=rad,
                    color=col,
                    popup=pop,
                    fill_color=fill,
                    fill_opacity=opc).add_to(map_name)


def drawForLightPlume(gas_df, zoom):
    leakageLat = gas_df['gasLeakLat'].mode().tolist()
    leakageLong = gas_df['gasLeakLong'].mode().tolist()
    # print(leakageLong, type(leakageLong[0]))
    map_osm = folium.Map(location=[leakageLat[0], leakageLong[0]], zoom_start=zoom)
    # self.draw_circles(leakageLat[0], leakageLong[0],5,'#FF0000','Leakage Site','#FF0000',map_osm)
    folium.Marker([leakageLat[0], leakageLong[0]]).add_to(map_osm)
    # folium.CircleMarker([leakageLat[0], leakageLong[0]],
    #                 radius=5,
    #                 color='#FF0000',
    #                 popup='Leakage Site',
    #                 fill_color='#FF0000',
    #                ).add_to(map_osm).head(n=50)
    pointsForHeatMap = []
    downwind_latitude = gas_df['x_lat'].tolist()
    downwind_longitude = gas_df['x_long'].tolist()
    concentration = gas_df['C'].tolist()
    posCrosswindLatitutde = gas_df['y_loc_lat1'].tolist()
    posCrosswindLatitutde.reverse()
    # print(type(posCrosswindLatitutde), len(posCrosswindLatitutde))
    posCrosswindLongitude = gas_df['y_loc_long1'].tolist()
    posCrosswindLongitude.reverse()
    negCrosswindLatitude = gas_df['y_loc_lat2'].tolist()
    negCrosswindLongitude = gas_df['y_loc_long2'].tolist()
    coordinate = []
    x_axis = []
    x_axis.append([leakageLat[0], leakageLong[0], concentration[0] / 10000000])
    for i, xLat, xLong, yLat, yLong, c in zip(count(), downwind_latitude, downwind_longitude, negCrosswindLatitude,
                                              negCrosswindLongitude, concentration):
        # self.draw_circles(yLat, yLong,1,'#ee6531','Leakage Site','#ee6531',map_osm)
        coordinate.append([yLat, yLong])
        x_axis.append(([xLat, xLong, c / 10000000]))
    # folium.features.PolygonMarker(coordinate, color='blue', fill_color='blue', weight=1).add_to(map_osm)
    for i, yLat, yLong,c in zip(count(), posCrosswindLatitutde, posCrosswindLongitude,concentration):
        draw_circles(yLat, yLong, 1, '#ee6531', 'Leakage Site', '#ee6531',c/1000000, map_osm)
        coordinate.append([yLat, yLong])
    folium.features.PolygonMarker(coordinate, color='#ee6531', fill_color='#ee6531', weight=1).add_to(map_osm)
    # folium.PolyLine(x_axis, color="#0e0d0c", weight=1, opacity=1).add_to(map_osm)
    HeatMap(x_axis, 1).add_to(map_osm)
    map_osm.save('lightplume.html')
    return map_osm



def drawForHeavyPuff(gas_df,iC,zoom,map=None):

    leakageLat, leakageLong, downwind_latitude, downwind_longitude, map_osm=process_common_data(gas_df,zoom,map)
    downwind_latitude=gas_df['x_lat'].tolist()
    radius=gas_df['b'].tolist()
    time = gas_df['t'].tolist()
    concentration = gas_df['cmax'].tolist()
    x_axis=[]
    x_axis.append([leakageLat, leakageLong,iC])

    #draw_circles(leakageLat, leakageLong, f, '#ee6531', 'time ' + str(0) + ' s', '#ee6531', 1, map_osm)
    for i,xLat,xLong, radius_val,t,c in zip(count(), downwind_latitude,downwind_longitude, radius,time,concentration):
        opacity=2/(i+1)
        opacity = c/10
        # print "Drawing"
        # print yLat, yLong, radius_val
        if (map == None):

            draw_circles(xLat,xLong,radius_val,'#ee6531','concentration ' + str(c) + ' at time ' + str(t) + ' s','#ee6531',opacity,map_osm)
        else:
            draw_circles(xLat, xLong, radius_val, '#3186cc', 'concentration ' + str(c) + ' at time ' + str(t) + ' s',
                         '#3186cc', c, map_osm)
        x_axis.append([xLat, xLong,c])
    #folium.PolyLine(x_axis, color="#0e0d0c", weight=8, opacity=1).add_to(map_osm)
    HeatMap(x_axis,10).add_to(map_osm)
    map_osm.save('heavy_puff.html')
    #print type(map_osm)
    return map_osm


def drawForHeavyPlume(gas_df,initialConcentration,zoom):
    gas_dfLoc=gas_df[gas_df['above_loc']==True]
    leakageLat, leakageLong, downwind_latitude, downwind_longitude, map_osm=process_common_data(gas_df,zoom)
    posCrosswindLatitutde=gas_df['y1_lat'].tolist()
    posCrosswindLongitude=gas_df['y1_long'].tolist()
    negCrosswindLatitude=gas_df['y2_lat'].tolist()
    negCrosswindLongitude=gas_df['y2_long'].tolist()
    gasConcentration = gas_df['cmax'].tolist()

    curve_outline = []
    concentrationHeatMapPoints = []
    #first coordinate from gas leak point
    curve_outline.append([leakageLat[0], leakageLong[0]])
    concentrationHeatMapPoints.append([leakageLat[0], leakageLong[0],initialConcentration])
    for i, posy_Lat, posy_Long,concentration  in zip(count(), posCrosswindLatitutde, posCrosswindLongitude,gasConcentration):
        curve_outline.append([posy_Lat, posy_Long])
        concentrationHeatMapPoints.append([posy_Lat, posy_Long,concentration])
    negCrosswindLatitude.reverse()
    negCrosswindLongitude.reverse()
    gasConcentration.reverse()
    for i, negy_Lat, negy_Long,concentration1 in zip(count(), negCrosswindLatitude, negCrosswindLongitude,gasConcentration):
        curve_outline.append([negy_Lat, negy_Long])
        concentrationHeatMapPoints.append([negy_Lat, negy_Long, concentration1])
    curve_outline.append([leakageLat[0], leakageLong[0]])
    concentrationHeatMapPoints.append([leakageLat[0], leakageLong[0], initialConcentration])

    folium.features.PolygonMarker(curve_outline, color='#ee6531', fill_color='#ee6531', weight=2,fill_opacity=0.5).add_to(map_osm)
    #x_axis=[([leakageLat[0], leakageLong[0]]),([downwind_latitude, downwind_longitude])]
    #folium.PolyLine(x_axis, color="#0e0d0c", weight=1, opacity=1).add_to(map_osm)
    # We draw Loc
    posCrosswindLatitutdeLoc = gas_dfLoc['y1_lat'].tolist()
    posCrosswindLongitudeLoc = gas_dfLoc['y1_long'].tolist()
    negCrosswindLatitudeLoc = gas_dfLoc['y2_lat'].tolist()
    negCrosswindLongitudeLoc = gas_dfLoc['y2_long'].tolist()

    #Let us draw LOC
    curve_outlineLoc = []
    # first coordinate from gas leak point
    curve_outlineLoc.append([leakageLat[0], leakageLong[0]])
    for i, posy_Lat, posy_Long in zip(count(), posCrosswindLatitutdeLoc, posCrosswindLongitudeLoc):
        curve_outlineLoc.append([posy_Lat, posy_Long])

    negCrosswindLatitudeLoc.reverse()
    negCrosswindLongitudeLoc.reverse()

    for i, negy_Lat, negy_Long in zip(count(), negCrosswindLatitudeLoc, negCrosswindLongitudeLoc):
        curve_outlineLoc.append([negy_Lat, negy_Long])
    curve_outlineLoc.append([leakageLat[0], leakageLong[0]])


    folium.features.PolygonMarker(curve_outlineLoc, color='#FF0000', fill_color='#FF0000', weight=2,fill_opacity=0.5).add_to(map_osm)

    #We will draw the heatmap to show the intensity of gas intensity at these points.
    #Let get the array for heat map generation
    HeatMap(concentrationHeatMapPoints).add_to(map_osm)
    map_osm.save('heavy_plume.html')
    return map_osm


def drawForLightPuff(df,zoom):

    leakageLat, leakageLong, downwind_latitude, downwind_longitude, map_osm=process_common_data(df,zoom)
    posCrosswindLatitutde, posCrosswindLongitude, negCrosswindLatitude, negCrosswindLongitude = \
        extract_data(df, 'y_loc_peak_lat1', 'y_loc_peak_long1', 'y_loc_peak_lat2', 'y_loc_peak_long2', leakageLat,
                     leakageLong)
    map_osm = draw_boundary(downwind_latitude, downwind_longitude, posCrosswindLatitutde, posCrosswindLongitude, \
                           negCrosswindLatitude, negCrosswindLongitude, map_osm)
    radius = df['puffRadius']
    time = df['tpeak']
    concentration = df['Cpeak']
    x_axis=[]
    x_axis.append([leakageLat,leakageLong,concentration[0]/100000])
    for i,xLat,xLong,r,t,c, in zip(count(), downwind_latitude,downwind_longitude, radius,time,concentration):
        opacity=c/100000
        # print "Drawing"
        # print yLat, yLong, radius_val
        draw_circles(xLat,xLong,r,'#ee6531','Concentration ' + str(c) + 'Time Since Leakage ' + str(t) + ' s','#ee6531',opacity,map_osm)
        x_axis.append([xLat, xLong,c])
    #folium.PolyLine(x_axis, color="#0e0d0c", weight=1, opacity=1).add_to(map_osm)
    folium.PolyLine(x_axis, color="blue", weight=1, opacity=1).add_to(map_osm)
    #HeatMap(x_axis).add_to(map_osm)
    map_osm.save('light_puff.html')

    return map_osm
    
def drawForSolidParticles(df,zoom):

    leakageLat, leakageLong, downwind_latitude, downwind_longitude, map_osm=process_common_data(df,zoom)
    posCrosswindLatitutde, posCrosswindLongitude, negCrosswindLatitude, negCrosswindLongitude = \
        extract_data(df, 'y_thresholdpeak_lat1', 'y_thresholdpeak_long1', 'y_thresholdpeak_lat2', 'y_thresholdpeak_long2', leakageLat,
                     leakageLong)
    map_osm = draw_boundary(downwind_latitude, downwind_longitude, posCrosswindLatitutde, posCrosswindLongitude, \
                           negCrosswindLatitude, negCrosswindLongitude, map_osm)
    radius = df['puffRadius']
    time = df['tpeak']
    concentration = df['Cpeak']
    x_axis=[]
    x_axis.append([leakageLat,leakageLong,concentration[0]/100000])
    for i,xLat,xLong,r,t,c, in zip(count(), downwind_latitude,downwind_longitude, radius,time,concentration):
        opacity=c/100000
        # print "Drawing"
        # print yLat, yLong, radius_val
        draw_circles(xLat,xLong,r,'#ee6531','Concentration ' + str(c) + 'Time Since Leakage ' + str(t) + ' s','#ee6531',opacity,map_osm)
        x_axis.append([xLat, xLong,c])
    #folium.PolyLine(x_axis, color="#0e0d0c", weight=1, opacity=1).add_to(map_osm)
    folium.PolyLine(x_axis, color="blue", weight=1, opacity=1).add_to(map_osm)
    #HeatMap(x_axis).add_to(map_osm)
    map_osm.save('solid_particle.html')

    return map_osm

def extract_data(gas_df, lat1, long1, lat2, long2, leakageLat, leakageLong):
    posCrosswindLatitutde=gas_df[lat1].tolist()
    posCrosswindLatitutde.reverse()
    posCrosswindLatitutde.append(leakageLat[0])
    posCrosswindLongitude=gas_df[long1].tolist()
    posCrosswindLongitude.reverse()
    posCrosswindLongitude.append(leakageLong[0])
    negCrosswindLatitude=gas_df[lat2].tolist()
    negCrosswindLongitude=gas_df[long2].tolist()  
    return posCrosswindLatitutde, posCrosswindLongitude, negCrosswindLatitude, negCrosswindLongitude   


def draw_boundary(downwind_latitude, downwind_longitude, posCrosswindLatitutde, posCrosswindLongitude, \
                  negCrosswindLatitude, negCrosswindLongitude, map_object):
    coordinate=[]
    x_axis=[]
    for i,xLat,xLong,yLat,yLong in zip(count(), downwind_latitude, downwind_longitude, negCrosswindLatitude, negCrosswindLongitude):
        #draw_circles(yLat, yLong,1,'#ee6531','Leakage Site','#ee6531',0.6,map_object)
        coordinate.append([yLat, yLong])
        x_axis.append(([xLat, xLong]))
    # folium.features.PolygonMarker(coordinate, color='blue', fill_color='blue', weight=1).add_to(map_osm)    
    for i,yLat,yLong in zip(count(), posCrosswindLatitutde, posCrosswindLongitude):
        #draw_circles(yLat, yLong,1,'#ee6531','Leakage Site','#ee6531',0.6,map_object)
        coordinate.append([yLat, yLong])
    #folium.features.PolygonMarker(coordinate, color='#ee6531', fill_color='#ee6531', weight=1).add_to(map_object)
    folium.features.PolygonMarker(coordinate, color='blue', fill_color='blue', weight=1).add_to(map_object)
    folium.PolyLine(x_axis, color="#0e0d0c", weight=1, opacity=1).add_to(map_object)
    #folium.PolyLine(x_axis, color="blue", weight=1, opacity=1).add_to(map_object)
    return map_object




        

def process_common_data(data_frame,zoom,map=None):
    leakageLat=data_frame['gasLeakLat'].mode().tolist()
    leakageLong=data_frame['gasLeakLong'].mode().tolist()
    if (map == None):
        map_osm = folium.Map(location=[leakageLat[0], leakageLong[0]],zoom_start=zoom)
    else:
        print("utilizing the existing map")
        map_osm = map
    draw_circles(leakageLat[0], leakageLong[0],5,'#FF0000','Leakage Site','#FF0000',0.6,map_osm)
    folium.Marker([leakageLat[0], leakageLong[0]]).add_to(map_osm)
    downwind_latitude=data_frame['x_lat'].tolist()
    downwind_longitude=data_frame['x_long'].tolist()
    return leakageLat, leakageLong,downwind_latitude, downwind_longitude, map_osm


### This function is only for plume
def distance_conc(x_axis_header, y_axis_header, heavy_light,puff_plume, results_df, time_distance, unit, loc):
    distance=results_df[x_axis_header].tolist()
    conc=results_df[y_axis_header].tolist()
    if unit=="microgram":
        conc=[a / 1000000 for a in conc]
    y_label_string="Concentration (kg/m3)"
    x_label_string=time_distance
    plot=plotter(heavy_light, distance, conc, x_label_string, y_label_string, puff_plume, time_distance, loc)

def plotter(heavy_light, x, y, x_label_string, y_label_string, puff_plume, time_distance, loc):
    fig = plt.figure()
    text ="Concentration vs "+time_distance+" for "+heavy_light+ " gas " +puff_plume
    fig.suptitle(text, fontsize=14, fontweight='bold')
    plt.plot(x, y, 'r--')
    plt.axhline(y=loc)
    plt.xlabel(x_label_string)
    plt.ylabel(y_label_string)
    plt.grid(True)
    plt.savefig(heavy_light+"_"+puff_plume+"_"+x_label_string+".png")
    plt.show()
    plt.close()

def plot2charts(x_head1, y_head1, x_head2, y_head2, heavy_light,puff_plume, results_df,unit, loc):
    x1=results_df[x_head1].tolist()
    y1=results_df[y_head1].tolist()
    x2=results_df[x_head2].tolist()
    y2=results_df[y_head2].tolist()
    if unit=="microgram":
        y1=[a / 1000000 for a in y1]
        y2=[a / 1000000 for a in y2]        
    fig = plt.figure()
    text1 ="Concentration vs distance for "+heavy_light+ " gas " +puff_plume
    fig.suptitle(text1, fontsize=14, fontweight='bold')
    plt.subplot(2, 1, 1)
    plt.plot(x1, y1, 'r--')
    plt.axhline(loc)
    plt.xlabel("Distance (m)")
    plt.ylabel("Concentration (kg/m3)")
    plt.grid(True)
    text2 ="Concentration vs time for "+heavy_light+ " gas " +puff_plume
    fig.suptitle(text2, fontsize=14, fontweight='bold')
    plt.subplot(2, 1, 2)
    plt.plot(x2, y2, 'r--')
    plt.axhline(loc)    
    plt.xlabel("Time (s)")
    plt.ylabel("Concentration (kg/m3)")
    plt.grid(True)
    plt.savefig(heavy_light+"_"+puff_plume+".png")
    plt.show()
    plt.close()




def testPlotter():
    results_df = pandas.read_csv("testOutComeLightGasPlume.csv")
    distance_conc('x', 'C', "light", "plume", results_df, "distance", "microgram", 3)
    results_df = pandas.read_csv("concentrationDataPuffModel.csv")
    plot2charts('x', 'cmax', 't', 'cmax', 'heavy','puff', results_df, "kg", 3)    
    results_df = pandas.read_csv("plumeconcentrationheaveyGas1.csv")
    distance_conc('x', 'cmax', "heavy", "plume", results_df,"distance", "kg", 3)  ###########################HEAVY LIGHT CAN BE TAKEN FROM THE SPLIT STRING OF COMMANDER FUNTION
    results_df = pandas.read_csv("testOutComePuffmodelLightGases.csv")
    plot2charts('x', 'Cpeak', 'tpeak', 'Cpeak', 'light','puff', results_df, "microgram", 3)    

def main():
    # results_df=pandas.read_csv("testOutComeLightGasPlume.csv")
    # map_osm=drawForLightPlume(results_df)
    # results_df=pandas.read_csv("concentrationDataPuffModel.csv")
    # map_osm=drawForHeavyPuff(results_df)
    # results_df=pandas.read_csv("plumeconcentrationheaveyGas1.csv")
    # map_osm=drawForHeavyPlume(results_df)
    results_df=pandas.read_csv("testOutComePuffmodelLightGases.csv")
    map_osm=drawForLightPuff(results_df)

if __name__ == "__main__":
    # main()
    testPlotter()

