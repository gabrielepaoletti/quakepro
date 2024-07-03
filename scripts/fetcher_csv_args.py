import argparse

parser = argparse.ArgumentParser(description="Download seismic waveforms using FDSN web services.")

# Mandatory arguments
parser.add_argument('-p', '--client', type=str, required=True, help='Client code for the FDSN data service.')
parser.add_argument('-n', '--network', type=str, required=True, help='Network code to identify the seismic network.')
parser.add_argument('-s', '--station', type=str, required=True, help='Station code to retrieve data for.')
parser.add_argument('-l', '--location', type=str, required=True, help='Location code within the station.')
parser.add_argument('-c', '--channel', type=str, required=True, help='Channel code(s) indicating types of data.')
parser.add_argument('-m', '--model', type=str, required=True, help='Earth model for travel time calculations.')
parser.add_argument('--time_before_p', type=float, required=True, help='Time in seconds before P-wave arrival to start the trace.')
parser.add_argument('--time_after_p', type=float, required=True, help='Time in seconds after P-wave arrival to end the trace.')
parser.add_argument('--catalog_path', type=str, required=True, help='Path to the earthquake catalog CSV file.')

# Optional arguments
parser.add_argument('--detrend', type=str, choices=['simple', 'linear', 'constant', 'polynomial', 'spline', 'None'], default='linear', help='Method used for detrending data (default: linear).')
parser.add_argument('--resample', type=float, help='New sampling rate in Hz to resample the waveform data.')
parser.add_argument('--remove_response', choices=['VEL', 'ACC', 'DISP', 'None'], help='Remove the instrument response and convert to the specified output (Velocity, Acceleration, or Displacement).')
