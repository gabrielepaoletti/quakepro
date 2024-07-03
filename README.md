# QUAKEPRO: earthQUAKE Processing and Retrieval Operations

An user-friendly tool designed to automate the process of downloading seismic waveforms from CSV earthquake catalogs. This project aims to facilitate the retrieval of seismic data for researchers and enthusiasts in the field of seismology.

## 📋 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Output](#-output)
- [Contributing](#-contributing)
- [License](#-license)
- [Contacts](#-contacts)

## ✨ Features
- 📥 **Automated data retrieval**: Automatically download seismic waveforms using FDSN web services.
- 📅 **CSV catalog input**: Supports input from CSV files containing earthquake event data.
- 🌐 **Multiple clients**: Compatible with various seismic data service clients.
- ⚙️ **Configurable parameters**: Customizable parameters for precise waveform retrieval.
- 📊 **Data processing**: Options for detrending, resampling, and response removal.
- 💾 **HDF5 output**: Saves downloaded waveforms and metadata in HDF5 format.

## 🛠️ Installation

To install **QUAKEPRO**, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quakepro.git
   cd quakepro
   ```

2. (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the package:
    ```bash
    pip install .
    ```

## 🚀 Usage

After installation, you can use the `qpf` command to start downloading seismic waveforms. 

### Arguments

- `-p`, `--client` (required): Client code for the FDSN data service.
- `-n`, `--network` (required): Network code to identify the seismic network.
- `-s`, `--station` (required): Station code to retrieve data for.
- `-l`, `--location` (required): Location code within the station.
- `-c`, `--channel` (required): Channel code(s) indicating types of data.
- `-m`, `--model` (required): Earth model for travel time calculations.
- `--time_before_p` (required): Time in seconds before P-wave arrival to start the trace.
- `--time_after_p` (required): Time in seconds after P-wave arrival to end the trace.
- `--catalog_path` (required): Path to the earthquake catalog CSV file.
- `--detrend` (optional): Method used for detrending data (default: linear).
- `--resample` (optional): New sampling rate in Hz to resample the waveform data.
- `--remove_response` (optional): Remove the instrument response and convert to the specified output (Velocity, Acceleration, or Displacement).

### CSV Catalog Format

The CSV catalog must be structured as follows and contain the following columns (all lowercase):

- `id`: Unique identifier for the earthquake event.
- `time`: Origin time of the event (in a format recognizable by Pandas, e.g., `YYYY-MM-DD HH:MM:SS`).
- `lon`: Longitude of the earthquake event.
- `lat`: Latitude of the earthquake event.
- `depth`: Depth of the earthquake event in kilometers (positive value).
- `magnitude`: Magnitude of the earthquake event.

### Example

```bash
qpf-csv -p "INGV" -n "IV" -s "MMO1" -l "*" -c "EH*" -m "iasp91" --time_before_p 5 --time_after_p 15 --catalog_path "path_to_your_catalog.csv"
```

## 📂 Output

The script will generate the following output files:

1. **HDF5 file**: Contains all the downloaded waveforms.
2. **CSV attributes file**: Contains metadata for each waveform with the following columns:
    - `trace_name`: Name of the trace.
    - `trace_start_time`: Start time of the trace.
    - `rec_network`: Code of the seismic network.
    - `rec_name`: Name of the receiver (station).
    - `rec_type`: Type of the receiver.
    - `rec_elevation_m`: Elevation of the receiver in meters.
    - `rec_latitude_deg`: Latitude of the receiver.
    - `rec_longitude_deg`: Longitude of the receiver.
    - `rec_sampling_rate_hz`: Sampling rate of the receiver in Hz.
    - `src_id`: Unique identifier of the earthquake event.
    - `src_depth_km`: Depth of the earthquake event in kilometers.
    - `src_latitude_deg`: Latitude of the earthquake event.
    - `src_longitude_deg`: Longitude of the earthquake event.
    - `src_magnitude`: Magnitude of the earthquake event.
    - `src_origin_time`: Origin time of the earthquake event.
    - `p_travel_sec`: P-wave travel time in seconds.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contacts

Author: Gabriele Paoletti  
Email: gabriele.paoletti@uniroma1.it

Feel free to reach out if you have any questions or suggestions!
