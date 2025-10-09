
'''
Copyright (c) 2025 Cameron S. Bodine
'''

import os
import ast
import numpy as np
import pandas as pd
import geopandas as gpd

#=======================================================================
def calcDetectIdx(smthTrkFile: str,
                  df: pd.DataFrame, 
                  stride: int, 
                  nchunk: int=0):
    '''
    Associate predicted crabpot with actual coordinates:

    1. Calculate trackline csv idx
    2. Get necessary attributes
    '''

    # Convert string xyxy into list
    if 'xyxy' in df.columns:
        df['xyxy'] = df['xyxy'].apply(ast.literal_eval)
        df[['box_x1', 'box_y1', 'box_x2', 'box_y2']] = pd.DataFrame(df['xyxy'].tolist(), index=df.index)

        # Calculate bbox center point
        df['mid_x'] = np.around((df['box_x2'] + df['box_x1'])/2, 0)
        df['mid_y'] = np.around((df['box_y2'] + df['box_y1'])/2, 0)

    else:
        df.rename(columns={'x': 'mid_x', 'y': 'mid_y'}, inplace=True)
    
    # Calculate box index
    if 'vid_frame_id' in df.columns:
        df['box_ping_idx'] = ((df['vid_frame_id'] * stride) + df['mid_x']).astype(int)

    else:
        df['box_ping_idx'] = ((df['chunk_id'] * nchunk) + df['chunk_offset'] + df['mid_x']).astype(int)

    df.set_index(keys='box_ping_idx', drop=False, inplace=True)

    # Get smooth trakcline file
    smthTrk = pd.read_csv(smthTrkFile)

    # Get the record number, trackline easting/northing, heading/cog, and pixM
    df['record_num'] = smthTrk['record_num']
    df['trk_utm_es'] = smthTrk['trk_utm_es']
    df['trk_utm_ns'] = smthTrk['trk_utm_ns']
    df['trk_lons'] = smthTrk['trk_lons']
    df['trk_lats'] = smthTrk['trk_lats']
    df['instr_heading'] = smthTrk['instr_heading']
    df['trk_cog'] = smthTrk['trk_cog']
    df['pixM'] = smthTrk['pixM']

    df.reset_index(inplace=True, drop=True)
    
    return df

#=======================================================================
def calcDetectLoc(beamName: str,
                  df: pd.DataFrame,
                  flip: bool=False,
                  wgs: bool=False,
                  cog: bool=True):

    '''
    Calculate target location with trackline location.
    '''

    lons = 'trk_lons'
    lats = 'trk_lats'
    ping_bearing = 'ping_bearing'

    ########################
    # Calculate ping bearing
    # Determine ping bearing.  Ping bearings are perpendicular to COG.
    if beamName == 'ss_port':
        rotate = -90  # Rotate COG by 90 degrees to the left
    else:
        rotate = 90 # Rotate COG by 90 degrees to the right
    if flip: # Flip rotation factor if True
        rotate *= -1

    # Calculate ping bearing and normalize to range 0-360
    # cog = False
    if cog:
        df[ping_bearing] = (df['trk_cog']+rotate) % 360
    else:
        df[ping_bearing] = (df['instr_heading']+rotate) % 360

    ##############################
    # Calculate Target Coordinates

    # Determine distance based on:
    ## y and
    ## pix_m
    df['target_range'] = d = df['mid_y'] * df['pixM']

    # Calculate the coordinates from:
    ## origin (track x/y), distance, and COG
    R = 6371.393*1000 #Radius of the Earth in meters
    brng = np.deg2rad(df[ping_bearing])

    # Get lat/lon for origin of each ping
    lat1 = np.deg2rad(df[lats])#.to_numpy()
    lon1 = np.deg2rad(df[lons])#.to_numpy()

    # Calculate latitude of range extent
    lat2 = np.arcsin( np.sin(lat1) * np.cos(d/R) +
        np.cos(lat1) * np.sin(d/R) * np.cos(brng))

    # Calculate longitude of range extent
    lon2 = lon1 + np.arctan2( np.sin(brng) * np.sin(d/R) * np.cos(lat1),
                            np.cos(d/R) - np.sin(lat1) * np.sin(lat2))

    # Convert range extent coordinates into degrees
    df['target_lat'] = np.degrees(lat2)
    df['target_lon'] = np.degrees(lon2)

    return df

#=======================================================================
def summarizeDetect(df: pd.DataFrame):
    
    '''
    Summarize by target_id
    '''

    summarized = []

    for name, group in df.groupby('tracker_id'):

        # Store summary in dictionary
        sum_dict = {}
        sum_dict['tracker_id'] = name

        # Most frequent class_id
        sum_dict['class_id'] = group['class_id'].mode()
        sum_dict['class_name'] = group['data'].mode()

        # Get count of predictions
        sum_dict['pred_cnt'] = len(group)

        # Get confidence stats
        sum_dict['conf_avg'] = group['confidence'].mean()
        sum_dict['conf_min'] = group['confidence'].min()
        sum_dict['conf_max'] = group['confidence'].max()
        sum_dict['conf_std'] = group['confidence'].std()

        # Get median record num
        sum_dict['record_num'] = group['record_num'].median()

        # Get avg box center point
        sum_dict['mid_x'] = int(group['mid_x'].mean())
        sum_dict['mid_y'] = int(group['mid_y'].mean())

        # Get avg location
        sum_dict['target_lat'] = np.around(group['target_lat'].mean(), 8)
        sum_dict['target_lon'] = np.around(group['target_lon'].mean(), 8)

        # Append
        summarized.append(sum_dict)

    finalDF = pd.DataFrame(summarized)

    return finalDF


#=======================================================================
def calcWpt(df: pd.DataFrame,
            outDir: str,
            projDir: str,
            threshold: float=0.2):
    
    '''
    '''

    # Filter by threshold
    if 'conf_avg' in df.columns:
        conf_col = 'conf_avg'
    else:
        conf_col = 'confidence'

    predDF = df.loc[df[conf_col] >= threshold]

    
    # # Calculate name
    # for i, row in predDF.iterrows():
    #     zero = self._addZero(i)
    #     # wptName = namePrefix+'{}{}'.format(zero, i)
    #     conf = int(row['confidence']*100)
    #     wptName = '{} {} {}%'.format(i, row['class_name'], conf)
    #     predDF.loc[i, 'wpt_name'] = wptName

    # Save to shp
    gdf = gpd.GeoDataFrame(predDF, geometry=gpd.points_from_xy(predDF['target_lon'], predDF['target_lat']), crs='EPSG:4326')

    # Save shapefile
    file_name = os.path.basename(projDir)+'.shp'
    file_name = os.path.join(outDir, file_name)
    gdf.to_file(file_name)

    # file_name = os.path.join(self.outDir, 'CrabPotLoc.gpx')
    file_name = file_name.replace('.shp', '.gpx')
    gdf = gdf.rename(columns={'tracker_id': 'name'})
    gdf = gdf[['name', 'geometry']]
    gdf.to_file(file_name, 'GPX')

    return