import time

from configs.calibration import Calibration
import os

class Config:
    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        print("Converting to dict")
        return self.__dict__
    
class LynxOQPSKConfig(Config):
    def __init__(self):
        super().__init__("OQPSK_CALIBRATION")
        print("Initializing OQPSK")
        self.frequencies = {
            "L": [1.95E+9, 3E+9, 4E+9],
            "M": [10E+9, 12.5E+9, 15E+9],
            "H": [25E+9, 28E+9, 31E+9]
        }

        self.gain_settings = [41]
        self.static_bandwidths = [10E+6, 200E+6]
        self.harmonic_measurement_bandwidths = {
            "L": [1E+9, 8E+9],
            "M": [5E+9, 20E+9],
            "H": [18E+9, 40E+9]
        }

        self.waveforms = ["CW", "OQPSK"]
        self.sa_save_register = "1"

        # CHANGE BACK TO 4 FOR THOSE PATHS THAT HAVE 2 @ INDX 0, 4
        self.paths = {
            "Band1_SN1": [2,1,1,2,1,1],
            "Band2_SN1": [2,2,2,2,1,1],
            "Band3_SN1": [2,3,3,2,1,1],
            "Band1_SN2": [2,4,4,2,1,1],
            "Band2_SN2": [2,5,5,2,1,1],
            "Band3_SN3": [2,6,6,2,1,1]
        }

        self.input_losses = {
            "Band1_SN1": {1.95E+9: 8.76, 3E+9: 7.76, 4E+9: 7.78},
            "Band2_SN1": {10E+9: 6.83, 12.5E+9: 5.69, 15E+9: 5.65},
            "Band3_SN1": {25E+9: 4.05, 28E+9: 4.15, 31E+9: 3.45},
            "Band1_SN2": {1.95E+9: 8.76, 3E+9: 7.76, 4E+9: 7.78},
            "Band2_SN2": {10E+9: 6.83, 12.5E+9: 5.69, 15E+9: 5.65},
            "Band3_SN3": {25E+9: 4.05, 28E+9: 4.15, 31E+9: 3.45}
        }

        self.output_losses = {
            "Band1_SN1": {1.95E+9: 21.75, 3E+9: 22.21, 4E+9: 22.52},
            "Band2_SN1": {10E+9: 23.8, 12.5E+9: 24.33, 15E+9: 24.93},
            "Band3_SN1": {25E+9: 26.52, 28E+9: 26.92, 31E+9: 27.18},
            "Band1_SN2": {1.95E+9: 21.75, 3E+9: 22.21, 4E+9: 22.52},
            "Band2_SN2": {10E+9: 23.8, 12.5E+9: 24.33, 15E+9: 24.93},
            "Band3_SN3": {25E+9: 26.52, 28E+9: 26.92, 31E+9: 27.18}
        }

    def get_input_loss_by_switchpath_and_freq(self, switchpath, freq):
        input_loss = 0
        for path, losses in self.input_losses.items():
            if switchpath == path:
                print(losses)
                input_loss = losses[freq]
                break

        return input_loss
    
    def get_output_loss_by_switchpath_and_freq(self, switchpath, freq):
        output_loss = 0
        for path, losses in self.output_losses.items():
            if switchpath == path:
                output_loss = losses[freq]
                break

        return output_loss
    
    def get_bandpath_by_frequency(self,frequency):
        for bandpath, freqs in self.frequencies.items():
            if frequency in freqs:
                return bandpath

class OSCARPAOQPSKConfig(Config):
    def __init__(self):
        super().__init__("OQPSK_CALIBRATION")
        print("Initializing OQPSK")

        # self.gain_settings = [41]
        self.static_bandwidths = [10E+6, 200E+6]
        self.harmonic_measurement_bandwidths = {
            "L": [1E+9, 13E+9],
            "H": [17.5E+9, 40E+9]
        }

        self.waveforms = ["CW", "OQPSK"]
        self.attenuator_states = [0, 10]
        self.sa_save_register = "1"

        # CHANGE BACK TO 4 FOR THOSE PATHS THAT HAVE 2 @ INDX 0, 4
        # path1 = vertical = SN1
        # path2 = horizontal = SN2

        self.paths = {
            "HIGH_BAND_PATH1_20DB": [2,3,3,2,0,0],
            "HIGH_BAND_PATH2_20DB": [2,6,6,2,0,0],
            "LOW_BAND_PATH1_20DB": [2,1,1,2,0,0],
            "LOW_BAND_PATH2_20DB": [2,4,4,2,0,0],
        }

        self.frequencies = {
            "L": [1.9E+9, 3E+9, 4E+9],
            "H": [18e+9, 21e+9, 25E+9, 26e+9, 28E+9, 31E+9]
        }

        self.input_losses = {
            "HIGH_BAND_PATH1_20DB": {18e+9: 4.98 , 21e+9: 4.69, 25E+9: 3.67, 26e+9: 3.92, 28E+9: 3.99, 31E+9: 3.3},#
            "HIGH_BAND_PATH2_20DB": {18e+9: 5.04, 21e+9: 4.73, 25E+9: 3.9, 26e+9: 4.07, 28E+9: 3.97, 31E+9: 3.42},#
            "LOW_BAND_PATH1_20DB": {1.9E+9: 9, 3E+9: 7.84, 4E+9: 7.78},#
            "LOW_BAND_PATH2_20DB": {1.9E+9: 8.93, 3E+9: 7.8, 4E+9: 7.77},#
        }

        self.output_losses = {
            "HIGH_BAND_PATH1_20DB": {18e+9: 19.53 , 21e+9: 20.37, 25E+9: 21.32, 26e+9: 21.6, 28E+9: 22.02, 31E+9: 22.72},#
            "HIGH_BAND_PATH2_20DB": {18e+9: 19.57, 21e+9: 20.36, 25E+9: 21.29, 26e+9: 21.57, 28E+9: 22.03, 31E+9: 22.75},#
            "LOW_BAND_PATH1_20DB": {1.9E+9: 21.04, 3E+9: 21.54, 4E+9: 21.84},#
            "LOW_BAND_PATH2_20DB": {1.9E+9: 21.1, 3E+9: 21.6, 4E+9: 21.92},#
        }

    def get_input_loss_by_switchpath_and_freq(self, switchpath, freq):
        input_loss = 0
        for path, losses in self.input_losses.items():
            if switchpath == path:
                print(losses)
                input_loss = losses[freq]
                break

        return input_loss
    
    def get_output_loss_by_switchpath_and_freq(self, switchpath, freq):
        output_loss = 0
        for path, losses in self.output_losses.items():
            if switchpath == path:
                output_loss = losses[freq]
                break

        return output_loss
    
    def get_bandpath_by_frequency(self,frequency):
        for bandpath, freqs in self.frequencies.items():
            if frequency in freqs:
                return bandpath

class LynxPNAXConfig(Config):
    def __init__(self):
        super().__init__("PNAX_CALIBRATION")
        print("Initializing PNAX")

        self.base_dir = "D:\\Lynx\\ATE\\"
        self.paths = {
            "Band1_SN1_10DB": [1,1,1,1,1,1],
            "Band2_SN1_10DB": [1,2,2,1,1,1],
            "Band3_SN1_10DB": [1,3,3,1,1,1],
            "Band1_SN2_10DB": [1,4,4,1,1,1],
            "Band2_SN2_10DB": [1,5,5,1,1,1],
            "Band3_SN3_10DB": [1,6,6,1,1,1],
            "Band1_SN1_20DB": [1,1,1,1,4,4],
            "Band2_SN1_20DB": [1,2,2,1,4,4],
            "Band3_SN1_20DB": [1,3,3,1,4,4],
            "Band1_SN2_20DB": [1,4,4,1,4,4],
            "Band2_SN2_20DB": [1,5,5,1,4,4],
            "Band3_SN3_20DB": [1,6,6,1,4,4]
        }

        self.ratioed_powers_w_statefilepath = {
            "S21": {
                "Band1_SN1": os.path.join(self.base_dir, "band1_1_gain_phase.csa"),
                "Band2_SN1": os.path.join(self.base_dir, "band2_1_gain_phase.csa"),
                "Band3_SN1": os.path.join(self.base_dir, "band3_1_gain_phase.csa"),
                "Band1_SN2": os.path.join(self.base_dir, "band1_2_gain_phase.csa"),
                "Band2_SN2": os.path.join(self.base_dir, "band2_2_gain_phase.csa"),
                "Band3_SN3": os.path.join(self.base_dir, "band3_3_gain_phase.csa")
            },
            "S11": {
                "Band1_SN1": os.path.join(self.base_dir, "band1_1_gain_phase.csa"),
                "Band2_SN1": os.path.join(self.base_dir, "band2_1_gain_phase.csa"),
                "Band3_SN1": os.path.join(self.base_dir, "band3_1_gain_phase.csa"),
                "Band1_SN2": os.path.join(self.base_dir, "band1_2_gain_phase.csa"),
                "Band2_SN2": os.path.join(self.base_dir, "band2_2_gain_phase.csa"),
                "Band3_SN3": os.path.join(self.base_dir, "band3_3_gain_phase.csa")
            },
            "S22": {
                "Band1_SN1": os.path.join(self.base_dir, "band1_1_gain_phase.csa"),
                "Band2_SN1": os.path.join(self.base_dir, "band2_1_gain_phase.csa"),
                "Band3_SN1": os.path.join(self.base_dir, "band3_1_gain_phase.csa"),
                "Band1_SN2": os.path.join(self.base_dir, "band1_2_gain_phase.csa"),
                "Band2_SN2": os.path.join(self.base_dir, "band2_2_gain_phase.csa"),
                "Band3_SN3": os.path.join(self.base_dir, "band3_3_gain_phase.csa")
            },
        }

    def get_bandpath_by_switchpath(self, switchpath):
        if "Band1" in switchpath:
            return "L"
        elif "Band2" in switchpath:
            return "M"
        elif "Band3" in switchpath:
            return "H"
        
class PNAXOscarPAConfig:
    def __init__(self):
        super().__init__()
        print("Initializing PNAX")

        self.base_dir = "D:\\Oscar\\ATE\\PA\\"


        self.paths = {
            "HIGH_BAND_PATH1_10DB": [1,0,3,1,4,4],
            "HIGH_BAND_PATH2_10DB": [1,0,6,1,4,4],
            "LOW_BAND_PATH1_10DB": [1,0,1,1,4,4],
            "LOW_BAND_PATH2_10DB": [1,0,4,1,4,4],
            "HIGH_BAND_PATH1_20DB": [1,3,3,1,1,1],
            "HIGH_BAND_PATH2_20DB": [1,6,6,1,1,1],
            "LOW_BAND_PATH1_20DB": [1,1,1,1,1,1],
            "LOW_BAND_PATH2_20DB": [1,4,4,1,1,1],
        }

        self.s21_statefile_paths = {
            "HIGH_BAND_PATH1_20DB": os.path.join(self.base_dir, "HighBand_1_gain_phase.csa"),
            "HIGH_BAND_PATH2_20DB": os.path.join(self.base_dir, "HighBand_2_gain_phase.csa"),
            "LOW_BAND_PATH1_20DB": os.path.join(self.base_dir, "LowBand_1_gain_phase.csa"),
            "LOW_BAND_PATH2_20DB": os.path.join(self.base_dir, "LowBand_2_gain_phase.csa"),
        }

        self.s11_statefile_paths = {
            "HIGH_BAND_PATH1_20DB": os.path.join(self.base_dir, "HighBand_1_S11.csa"),
            "HIGH_BAND_PATH2_20DB": os.path.join(self.base_dir, "HighBand_2_S11.csa"),
            "LOW_BAND_PATH1_20DB": os.path.join(self.base_dir, "LowBand_1_S11.csa"),
            "LOW_BAND_PATH2_20DB": os.path.join(self.base_dir, "LowBand_2_S11.csa"),
        }

        self.s22_statefile_paths = {
            "HIGH_BAND_PATH1_10DB": os.path.join(self.base_dir, "HighBand_1_S22.csa"),
            "HIGH_BAND_PATH2_10DB": os.path.join(self.base_dir, "HighBand_2_S22.csa"),
            "LOW_BAND_PATH1_10DB": os.path.join(self.base_dir, "LowBand_1_S22.csa"),
            "LOW_BAND_PATH2_10DB": os.path.join(self.base_dir, "LowBand_2_S22.csa"),
        }

        self.temp_profile = [
            {"temperature": 25, "target_temp_delta": 3, "temp_controller_offset": 0},
            {"temperature": 50, "target_temp_delta": 3, "temp_controller_offset": 0}
        ]
    
    def get_statefile_by_switchpath_and_ratioed_power(self, switchpath, ratioed_power):
        if "10DB" in switchpath:
            return self.s22_statefile_paths[switchpath]
        elif "20DB" in switchpath:
            if ratioed_power == "S21":
                return self.s21_statefile_paths[switchpath]
            if ratioed_power == "S11":
                return self.s11_statefile_paths[switchpath]
        else:
            raise TypeError



class PNAXOscarLNAConfig:
    def __init__(self, project):
        super().__init__()
        print("Initializing PNAX")

        self.highband_base_dir = "D:\\OSCAR\\ATE\\LNA\\High Band"
        self.lowband_base_dir = "D:\\OSCAR\\ATE\\LNA\\Low Band"

        self.test_dir = os.getcwd()
        self.data_dir_base = os.path.join(self.test_dir, f"{project}_data")
        self.data_dir_results = self.data_dir_base

        self.init_paths()


    def create_session_dir(self):
        start_timestamp = datetime.datetime.now()
        session = start_timestamp.strftime("%Y%m%d%H%M%S")
        self.data_dir_results = os.path.join(self.data_dir_results, session)

        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def change_sno_dir(self, sno):
        self.data_dir_results = os.path.join(self.data_dir_results, sno)
        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def change_results_dir(self, results_dir_name):
        self.data_dir_results = os.path.join(self.data_dir_results, results_dir_name)
        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def new_sno(self, sno, results_dir_name):
        self.data_dir_results = self.data_dir_base
        self.change_sno_dir(sno)
        self.change_results_dir(results_dir_name)
        self.create_session_dir()
        self.init_paths()

    def init_paths(self):
        self.paths = {
            "HIGH_BAND_PATH1": {
                "Noise_Figure": {
                    "gain_setting": 31,
                    "switchpath": [[4,1,0,0,0,0], [0,0,0,4,4]],
                    "freqs": [17500, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000, 31000, 317500],
                    "results_filepath": os.path.join(self.data_dir_results, "High Band Noise_Figure_1.csv")
                },
                "Gain_Phase": {
                    "gain_setting": 31,
                    "switchpath": [[1,1,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band Gain_1.csa"),
                    "results_filepath": [os.path.join(self.data_dir_results, "High Band Gain_1.csv"), os.path.join(self.data_dir_results, "High Band Phase_1.csv")],
                },
                "S11": {
                    "gain_setting": 31,
                    "switchpath": [[1,1,0,0,0,2], [0,0,0,0,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band S11_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band S11_1.csv"),
                },
                "S22": {
                    "gain_setting": 31,
                    "switchpath": [[1,0,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band S22_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band S22_1.csv"),
                },
                "IP3": {
                    "gain_setting": 31,
                    "switchpath": [[1,1,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band IIP3_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band IIP3_1.csv"),
                },
                "PSAT": {
                    "linear": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -45_-36dB Linear region_1.csa"),
                        "source_range": [-46,-36],
                    },
                    "-19": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -19 dB_1.csa"),
                        "source_range": [-25,-19],
                    },
                    "-35_-26": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -35_-26dB_1.csa"),
                        "source_range": [-35,-26],
                    },
                    "gain_setting": 31,
                    "linear_start_stop": [-45, -40],
                    "saturation_start_stop": [-32, -19],
                    "switchpath": [[1,1,0,0,0,2], [0,0,0,4,2]],
                    "results_filepath": os.path.join(self.data_dir_results, "High Band Psat_1.csv"),
                },
            },
            "HIGH_BAND_PATH2": {
                "Noise_Figure": {
                    "gain_setting": 31,
                    "switchpath": [[4,2,0,0,0,0], [0,0,0,3,4]],
                    "freqs": [17500, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000, 31000, 317500],
                    "results_filepath": os.path.join(self.data_dir_results, "High Band Noise_Figure_2.csv")
                },
                "Gain_Phase": {
                    "gain_setting": 31,
                    "switchpath": [[1,2,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band Gain_2.csa"),
                    "results_filepath": [os.path.join(self.data_dir_results, "High Band Gain_2.csv"), os.path.join(self.data_dir_results, "High Band Phase_2.csv")],
                },
                "S11": {
                    "gain_setting": 31,
                    "switchpath": [[1,2,0,0,0,2], [0,0,0,0,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band S11_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band S11_2.csv"),
                },
                "S22": {
                    "gain_setting": 31,
                    "switchpath": [[1,0,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band S22_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band S22_2.csv"),
                },
                "IP3": {
                    "gain_setting": 31,
                    "switchpath": [[1,2,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.highband_base_dir, "High Band IIP3_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "High Band IIP3_2.csv"),
                },
                "PSAT": {
                    "linear": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -45_-36dB Linear region_2.csa"),
                        "source_range": [-46,-36],
                    },
                    "-19": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -19 dB_2.csa"),
                        "source_range": [-25,-19],
                    },
                    "-35_-26": {
                        "statefile": os.path.join(self.highband_base_dir, "High Band Psat -35_-26dB_2.csa"),
                        "source_range": [-35,-26],
                    },
                    "gain_setting": 31,
                    "switchpath": [[1,2,0,0,0,2], [0,0,0,3,2]],
                    "linear_start_stop":[-45, -40],
                    "saturation_start_stop":[-32, -19],
                    "results_filepath": os.path.join(self.data_dir_results, "High Band Psat_2.csv"),
                },
            },  
            "LOW_BAND_PATH1": {
                "Noise_Figure": {
                    "gain_setting": 31,
                    "switchpath": [[4,3,0,0,0,0], [0,0,0,4,4]],
                    "freqs":  [1400, 1900, 2000, 2200, 2400, 2600, 2800, 2900, 3000,3200,3400,3600, 3800, 4000, 4500],
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band Noise_Figure_1.csv")
                },
                "Gain_Phase": {
                    "gain_setting": 31,
                    "switchpath": [[1,3,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band Gain_1.csa"),
                    "results_filepath": [os.path.join(self.data_dir_results, "Low Band Gain_1.csv"), os.path.join(self.data_dir_results, "Low Band Phase_1.csv")],
                },
                "S11": {
                    "gain_setting": 31,
                    "switchpath": [[1,3,0,0,0,2], [0,0,0,0,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band S11_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band S11_1.csv"),
                },
                "S22": {
                    "gain_setting": 31,
                    "switchpath": [[1,0,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band S22_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band S22_1.csv"),
                },
                "IP3": {
                    "gain_setting": 31,
                    "switchpath": [[1,3,0,0,0,2], [0,0,0,4,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band IIP3_1.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band IIP3_1.csv"),
                },
                "PSAT": {
                    "linear": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -45_-36dB Linear region_1.csa"),
                        "source_range": [-46,-36],
                    },
                    "-19": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -19 dB_1.csa"),
                        "source_range": [-25,-19],
                    },
                    "-35_-26": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -35_-26dB_1.csa"),
                        "source_range": [-35,-26],
                    },
                    "gain_setting": 31,
                    "switchpath": [[1,3,0,0,0,2], [0,0,0,4,2]],
                    "linear_start_stop":[-45, -40],
                    "saturation_start_stop":[-25, -13],
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band Psat_1.csv"),
                },
            },  
            "LOW_BAND_PATH2": {
                "Noise_Figure": {
                    "gain_setting": 31,
                    "switchpath": [[4,4,0,0,0,0], [0,0,0,3,4]],
                    "freqs": [1400, 1900, 2000, 2200, 2400, 2600, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000, 4500],
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band Noise_Figure_2.csv")
                },
                "Gain_Phase": {
                    "gain_setting": 31,
                    "switchpath": [[1,4,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band Gain_2.csa"),
                    "results_filepath": [os.path.join(self.data_dir_results, "Low Band Gain_2.csv"), os.path.join(self.data_dir_results, "Low Band Phase_2.csv")],
                },
                "S11": {
                    "gain_setting": 31,
                    "switchpath": [[1,4,0,0,0,2], [0,0,0,0,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band S11_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band S11_2.csv"),
                },
                "S22": {
                    "gain_setting": 31,
                    "switchpath": [[1,0,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band S22_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band S22_2.csv"),
                },
                "IP3": {
                    "gain_setting": 31,
                    "switchpath": [[1,4,0,0,0,2], [0,0,0,3,2]],
                    "statefile": os.path.join(self.lowband_base_dir, "Low Band IIP3_2.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band IIP3_2.csv"),
                },
                "PSAT": {
                    "linear": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -45_-36dB Linear region_2.csa"),
                        "source_range": [-46,-36],
                    },
                    "-19": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -19 dB_2.csa"),
                        "source_range": [-25,-19],
                    },
                    "-35_-26": {
                        "statefile": os.path.join(self.lowband_base_dir, "Low Band Psat -35_-26dB_2.csa"),
                        "source_range": [-35,-26],
                    },
                    "gain_setting": 31,
                    "switchpath": [[1,4,0,0,0,2], [0,0,0,3,2]],
                    "linear_start_stop":[-45, -40],
                    "saturation_start_stop":[-25, -13],
                    "results_filepath": os.path.join(self.data_dir_results, "Low Band Psat_2.csv"),
                },
            },  
        }


        self.gain_statefile_paths = {
            "HIGH_BAND_S21_PATH1": os.path.join(self.highband_base_dir, "High Band Gain_1.csa"),
            "HIGH_BAND_S21_PATH2": os.path.join(self.highband_base_dir, "High Band Gain_2.csa"),
            "LOW_BAND_S21_PATH1": os.path.join(self.data_dir_results, "Low Band Gain_1.csa"),
            "LOW_BAND_S21_PATH2": os.path.join(self.lowband_base_dir, "Low Band Gain_2.csa"),
        }

        self.ip3_statefile_paths = {
            "HIGH_BAND_IP3_PATH1": os.path.join(self.highband_base_dir, "High Band IP3_1.csa"),
            "HIGH_BAND_IP3_PATH2": os.path.join(self.highband_base_dir, "High Band IP3_2.csa"),
            "LOW_BAND_IP3_PATH1": os.path.join(self.lowband_base_dir, "Low Band IP3_1.csa"),
            "LOW_BAND_IP3_PATH2": os.path.join(self.lowband_base_dir, "Low Band IP3_2.csa"),
        }

        self.s11_statefile_paths = {
            "HIGH_BAND_S11_PATH1": os.path.join(self.highband_base_dir, "High Band S11_1.csa"),
            "HIGH_BAND_S11_PATH2": os.path.join(self.highband_base_dir, "High Band S11_2.csa"),
            "LOW_BAND_S11_PATH1": os.path.join(self.lowband_base_dir, "Low Band S11_1.csa"),
            "LOW_BAND_S11_PATH2": os.path.join(self.lowband_base_dir, "Low Band S11_2.csa"),
        }

        self.s22_statefile_paths = {
            "HIGH_BAND_S22_PATH1": os.path.join(self.highband_base_dir, "High Band S22_1.csa"),
            "HIGH_BAND_S22_PATH2": os.path.join(self.highband_base_dir, "High Band S22_2.csa"),
            "LOW_BAND_S22_PATH1": os.path.join(self.lowband_base_dir, "Low Band S22_1.csa"),
            "LOW_BAND_S22_PATH2": os.path.join(self.lowband_base_dir, "Low Band S22_2.csa"),
        }

        self.psat_statefile_paths = {
            "HIGH_BAND_PSAT_-46_-36_PATH1": os.path.join(self.highband_base_dir, "High Band Psat -46_-36dB Linear region_1.csa"),
            "HIGH_BAND_PSAT_-46_-36_PATH2": os.path.join(self.highband_base_dir, "High Band Psat -46_-36dB Linear region_2.csa"),
            "LOW_BAND_PSAT_-46_-36_PATH1": os.path.join(self.lowband_base_dir, "Low Band Psat -46_-36dB Linear region_1.csa"),
            "LOW_BAND_PSAT_-46_-36_PATH2": os.path.join(self.lowband_base_dir, "Low Band Psat -46_-36dB Linear region_2.csa"),
            "HIGH_BAND_PSAT_-35_-26_PATH1": os.path.join(self.highband_base_dir, "High Band Psat -35_-26dB_1.csa"),
            "HIGH_BAND_PSAT_-35_-26_PATH2": os.path.join(self.highband_base_dir, "High Band Psat -35_-26dB_2.csa"),
            "LOW_BAND_PSAT_-35_-26_PATH1": os.path.join(self.lowband_base_dir, "Low Band Psat -35_-26dB_1.csa"),
            "LOW_BAND_PSAT_-35_-26_PATH2": os.path.join(self.lowband_base_dir, "Low Band Psat -35_-26dB_2.csa"),
            "HIGH_BAND_PSAT_-19_PATH1": os.path.join(self.highband_base_dir, "High Band Psat -19dB_1.csa"),
            "HIGH_BAND_PSAT_-19_PATH2": os.path.join(self.highband_base_dir, "High Band Psat -19dB_2.csa"),
            "LOW_BAND_PSAT_-19_PATH1": os.path.join(self.lowband_base_dir, "Low Band Psat -19 dB_1.csa"),
            "LOW_BAND_PSAT_-19_PATH2": os.path.join(self.lowband_base_dir, "Low Band Psat -19 dB_2.csa"),
        }

    def get_psat_switchpath_and_statefile_by_path_and_psat_stage(self, path, psat_stage):
        if psat_stage == "linear":
            return self.paths[path]["PSAT"]["switchpath"], self.paths[path]["PSAT"]["linear"]["statefile"]
        elif psat_stage == "-19":
            return self.paths[path]["PSAT"]["switchpath"], self.paths[path]["PSAT"]["-19"]["statefile"]
        elif psat_stage == "-35_-26":
            return self.paths[path]["PSAT"]["switchpath"], self.paths[path]["PSAT"]["-35_-26"]["statefile"]
        elif psat_stage == "-45_-26":
            return self.paths[path]["PSAT"]["switchpath"], self.paths[path]["PSAT"]["-45_-36"]["statefile"]
        else:
            raise TypeError

    def get_switchpath_and_statefile_by_path_and_measurement_type(self, path, measurement_type):
        switchpath = self.paths[path][measurement_type]["switchpath"]
        statefile = self.paths[path][measurement_type]["statefile"]
        return switchpath, statefile
    
    def get_results_filepath_by_path_and_measurement_type(self, path, measurement_type):
        return self.paths[path][measurement_type]["results_filepath"]


class Results:
    def __init__(self, name):
        self.name = None
        self.frequencies = []

    def to_dict(self):
        return self.__dict__
    
class PNAXResults(Results):
    def __init__(self):
        super().__init__("PNAX_Result")
        self.paths = {}

class OQPSKResults(Results):
    def __init__(self):
        super().__init__("OQPSK_Result")
        self.paths = {}