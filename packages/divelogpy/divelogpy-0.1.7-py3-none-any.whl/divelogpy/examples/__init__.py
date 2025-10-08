
from .. import client
from ..plotting import plot_timeseries
dive_client = client.DiveLogClient('path_to_your_shearwater_cloud_exported_db.db')
all_dives = dive_client.get_dives() # get all dives
first_dive = all_dives[0] # get the first dive
only_primary_computer_dives = dive_client.get_primary_computer_dives() # get dives with multiple computers
single_dive = dive_client.get_dive(dive_id='dive_id') # get a specific dive by its ID
get_tank_names = single_dive.timeseries.available_tanks
get_tank_data = single_dive.timeseries.get_tank_data(tank_name='O2')
get_total_ccr_hours = sum([i.duration_seconds for i in only_primary_computer_dives if i.mode == 'ccr']) / 3600.0
get_po2_sensor_data = single_dive.sensors.despiked().to_df()
get_po2_data = single_dive.timeseries.average_ppo2()
get_ppo2_and_setpoint_against_depth = single_dive.timeseries.to_df()['depth_ft','average_ppo2','ppo2_setpoint']


# plots
# generate a plot that is properly scaled to show depth along with ppo2 data.
plot_timeseries(single_dive.timeseries,scale_groups=
                [
        ["average_ppo2", "ppo2_setpoint"],     # axis with shared scale       # axis for temp (auto label/color)
    ],)

