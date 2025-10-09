from flask import Flask, jsonify, render_template, request

import polars as pl

from hkjc.live import live_odds, _fetch_live_races
from hkjc.harville_model import fit_harville_to_odds
from hkjc.historical import get_horse_data
from hkjc.speedpro import speedmap, speedpro_energy

app = Flask(__name__)


@app.route("/")
def disp_race_info():    
    race_info = _fetch_live_races('', '')

    df_speedpro = speedpro_energy(race_info['Date'])
    for race_num, race in race_info['Races'].items():
        for i, runner in enumerate(race['Runners']):
            df = (df_speedpro
                     .filter(pl.col('RaceNo')==race_num)
                     .filter(pl.col('RunnerNumber')==int(runner['No']))
                     )
            race_info['Races'][race_num]['Runners'][i]['SPEnergy'] = df['SpeedPRO_Energy_Difference'].item(0)
            race_info['Races'][race_num]['Runners'][i]['Fitness'] = df['FitnessRatings'].item(0)

# TODO: add horse running style favorite from horse info
    return render_template('index.html',
                           race_info=race_info)


turf_going_dict = {'FIRM': 'F',
                   'GOOD TO FIRM': 'GF',
                   'GOOD': 'G',
                   'GOOD TO YIELDING': 'GY',
                   'YIELDING': 'Y',
                   'YIELDING TO SOFT': 'YS',
                   'SOFT': 'S',
                   'HEAVY': 'H'}
aw_going_dict = {'WET FAST': 'WF',
                 'FAST': 'FT',
                 'GOOD': 'GD',
                 'SLOW': 'SL',
                 'WET SLOW': 'WS',
                 'RAIN AFFECTED': 'RA',
                 'NORMAL WATERING': 'NW'}
going_dict = {'TURF': turf_going_dict, 'ALL WEATHER TRACK': aw_going_dict}

@app.route("/horse_info/<horse_no>", methods=['GET'])
def disp_horse_info(horse_no):
    # read optional filters
    dist = request.args.get('dist', type=int)
    track = request.args.get('track')
    going = request.args.get('going')

    if track not in going_dict.keys():
        track = None
    if (going is not None) and (track is not None) and (going in going_dict[track].keys()):
        going = going_dict[track][going] # translate going to code
    else:
        going = None

    df = get_horse_data(horse_no)
    if dist is not None:
        df = df.filter(pl.col('Dist')==dist)
    if track and track.upper() == 'TURF':
        df = df.filter(pl.col('Track')=='Turf')
    elif track and track.upper() == 'ALL WEATHER TRACK':
        df = df.filter(pl.col('Track')=='AWT')
    if going is not None:
        df = df.filter(pl.col('G')==going)
    
    return render_template('horse-info.html', df=df)

@app.route('/live_odds/<race_no>')
def disp_live_odds(race_no=1):
    odds_dict = live_odds('','',int(race_no))
    fitted_odds = fit_harville_to_odds(odds_dict)

# TODO: repackage odds into json 
    return fitted_odds.__repr__()

@app.route('/speedmap/<race_no>')
def disp_speedmap(race_no=1):
    return speedmap(int(race_no))

# TODO: trades 