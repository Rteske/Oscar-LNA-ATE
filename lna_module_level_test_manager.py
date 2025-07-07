import pyvisa
from instruments.network_analyzer import PNAXNetworkAnalyzer
from instruments.power_supply import PowerSupply
from instruments.temp_probe import Agilent34401A
from instruments.ztm import ZtmModular  
from instruments.AIOUSB.aiousb import Aiousb
from configs.scribe import Scribe
from logging_utils import log_message, configure_logging, log_queue
import logging
import time

logger = logging.getLogger()

class LNAModuleTestManager:
    def __init__(self, sim) -> None:
        self.instruments_connection = {"na": True, "temp_probe": True, "daq": True}
        if not sim:
            self.rm = pyvisa.ResourceManager()
            self.instruments = self.rm.list_resources()
            log_message(self.instruments)
            self.running_state = False
            self.state = False

            try:
                self.na = PNAXNetworkAnalyzer("TCPIP0::K-Instr0000.local::hislip0::INSTR")
                log_message("NA CONNECTED")
            except:
                self.instruments_connection["na"] = False
                log_message("NA NOT connected")

            try:

                self.temp_probe = Agilent34401A("GPIB0::29::INSTR")
                log_message("TEMP PROBE 1 CONNECTED")
            except:
                log_message("Failed to connect to temp probe")
                self.instruments_connection["temp_probe"] = False

            try:
                self.temp_probe2 = Agilent34401A("GPIB0::22::INSTR")
                log_message("TEMP PROBE 2 CONNECTED")
            except:
                log_message("Failed to connect to temp probe 2")
                
                self.instruments_connection["temp_probe2"] = False

            try:
                self.power_supply = PowerSupply("GPIB0::15::INSTR")
            except:
                self.instruments_connection["power_supply"] = False

            try:
                self.daq = Aiousb()
            except:
                log_message("FAILED TO CONNECT TO AIOUSB")
                self.instruments_connection["daq"] = False

            try:
                sno = "02402230028"
                self.switch_bank = ZtmModular()
                self.switch_bank.init_resource(sno)
                self.switch_bank.reset_all_switches()
                sno = "01905230039"
                self.switch_bank2 = ZtmModular()
                self.switch_bank2.init_resource(sno)
                self.switch_bank2.reset_all_switches()
            except Exception as e:
                print(e)
                log_message(e)
                log_message("Failed to connect to switch bank")
                self.instruments_connection["switch_bank"] = False

            from configs.configs import PNAXOscarLNAConfig

            network_analyzer_config = PNAXOscarLNAConfig("OSCAR_LNA")
            from tests.lna_module_level_test import NetworkAnalyzerModuleTest

            self.na_test = NetworkAnalyzerModuleTest(na=self.na, temp_probe=self.temp_probe, temp_probe2=self.temp_probe2, daq=self.daq, psu=self.power_supply, config=network_analyzer_config, switch_bank=self.switch_bank, switch_bank2=self.switch_bank2)

            self.freqs_and_switchpaths_na_tests = {}

            self.paths = [
            "HIGH_BAND_PATH1",
            "HIGH_BAND_PATH2",
            "LOW_BAND_PATH1",
            "LOW_BAND_PATH2"
            ]

            self.scribe = Scribe("OSCAR_LNA")

    def clean_up(self):
        self.daq.disable_rf()
        # self.power_supply.get_output_state(False)
        self.switch_bank.reset_all_switches()
        self.switch_bank2.reset_all_switches()

    def disconnect_instruments(self):
        self.na_test.noise_figure_meter._res.close()
        self.na._res.close()
        self.temp_probe.instrument.close()
        self.temp_probe2.instrument.close()
        self.power_supply._res.close()

    def run_state_process(self, path, measurement_type):
        if measurement_type == "Noise_Figure":
            switchpath = self.na_test.config.paths[path][measurement_type]["switchpath"]

            self.switch_bank.set_all_switches(switchpath[0])
            self.switch_bank2.set_all_switches(switchpath[1])

        elif measurement_type == "S21":
            statefile = self.na_test.config.paths[path]["Gain_Phase"]["statefile"]
            switchpath = self.na_test.config.paths[path]["Gain_Phase"]["switchpath"]

            self.na.load_saved_cal_and_state(statefile)

            self.switch_bank.set_all_switches(switchpath[0])
            self.switch_bank2.set_all_switches(switchpath[1])    
        else:
            statefile = self.na_test.config.paths[path][measurement_type]["statefile"]
            switchpath = self.na_test.config.paths[path][measurement_type]["switchpath"]

            self.na.load_saved_cal_and_state(statefile)

            self.switch_bank.set_all_switches(switchpath[0])
            self.switch_bank2.set_all_switches(switchpath[1])


    def process_and_write_module_data(self, path, measurement_type, data):
        if measurement_type == "PSAT":
            linear = data["linear"]

            headers_for_psat = [
                "P1",
                "00",
                "00",
                "00",
                "00"
            ] + data["freqs"]


            headers_for_p1 = [
                "PSAT",
                "00",
                "00",
                "00",
                "00"
            ] + data["freqs"]

            headers = [
                "source_db",
                "datetime",
                "temp_probe",
                "temp_probe2",
                "voltage",
                "current"
            ] + data["freqs"]
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], headers)
            for source_db, psat in linear.items():
                gain = psat["gain"]
                datetime_string = psat["datetime_string"]
                temp_probe = psat["temp_probe1_value"]
                temp_probe2 = psat["temp_probe2_value"]
                voltage = psat["voltage"]
                current = psat["current"]
                frame = [
                    source_db,
                    datetime_string,
                    temp_probe,
                    temp_probe2,
                    voltage,
                    current
                ] + gain

                self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], frame)

            sat = data["saturation"]
            for source_db, sat in sat.items():
                gain = sat["gain"]
                datetime_string = sat["datetime_string"]
                temp_probe = sat["temp_probe1_value"]
                temp_probe2 = sat["temp_probe2_value"]
                voltage = sat["voltage"]
                current = sat["current"]
                frame = [
                    source_db,
                    datetime_string,
                    temp_probe,
                    temp_probe2,
                    voltage,
                    current
                ] + gain

                self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], frame)

            padding = [
                "00",
                "00",
                "00",
                "00",
                "00"
            ]

            psat = padding + list(data["psat"])
            p1 = padding + list(data["p1"])
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], headers_for_psat)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], psat)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], headers_for_p1)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], p1)
        elif measurement_type == "S22" or measurement_type == "S11" or measurement_type == "IP3":
            freqs = data["freqs"]
            gain = data["gain_data"]
            datetime_string = data["datetime_string"]
            temp_probe = data["temp_probe1_value"]
            temp_probe2 = data["temp_probe2_value"]
            voltage = data["voltage"]
            current = data["current"]

            headers = [
                "datetime_string",
                "temp_probe1_value",
                "temp_probe2_value",
                "voltage",
                "current"
            ] + freqs
            
            frame = [
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
                ] + gain
            
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], headers)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], frame)
        elif measurement_type == "Gain_Phase":
            freqs = data["freqs"]
            gain = data["gain_data"]
            datetime_string = data["datetime_string"]
            temp_probe = data["temp_probe1_value"]
            temp_probe2 = data["temp_probe2_value"]
            voltage = data["voltage"]
            current = data["current"]
            
            headers = [
                "datetime_string",
                "temp_probe1",
                "temp_probe2",
                "voltage",
                "current"
            ] + freqs

            gain_frame = [
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
                ] + gain
            
            freqs = data["freqs"]
            phase = data["phase_data"]
            datetime_string = data["datetime_string"]
            temp_probe = data["temp_probe1_value"]
            temp_probe2 = data["temp_probe2_value"]
            voltage = data["voltage"]
            current = data["current"]
            
            phase_frame = [
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
                ] + phase


            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"][0], headers)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"][1], headers)

            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"][0], gain_frame)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"][1], phase_frame)
        elif measurement_type == "Noise_Figure":
            freqs = [i[0] for i in data]
            noise_figure = [i[1] for i in data]
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], freqs)
            self.scribe.write_data_from_filepath(self.na_test.config.paths[path][measurement_type]["results_filepath"], noise_figure)


    def run_and_process_tests(self, path, sno, options={}):
        self.running_state = True

        for measurement_type, measurement_config in self.na_test.config.paths[path].items():
            if measurement_type == "PSAT" and options["PSAT"] == True:
                log_message(f"STARTING {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")
                linear_results, saturation_results, freqs = self.na_test.psat_p1_measurement(path, measurement_config["gain_setting"], measurement_config["linear_start_stop"], measurement_config["saturation_start_stop"])
                psat, p1 = self.scribe.get_p1_data_v2(freqs,linear_results, saturation_results)
                log_message(f"FINISHED {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")
                results = {"linear": linear_results, "saturation": saturation_results, "psat": psat.values(), "p1": p1.values(), "freqs":freqs}
                self.process_and_write_module_data(path, measurement_type, results)
                log_message(f"FINISHED {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")

                self.clean_up()

            if measurement_type == "Gain_Phase" and options["Gain_Phase"] == True:
                log_message(f"STARTING {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")
                gain_phase_results = self.na_test.get_gain_and_phase_measurement(path, measurement_config["gain_setting"])
                self.process_and_write_module_data(path, measurement_type, gain_phase_results)
                log_message(f"FINISHED {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")

                self.clean_up()

            if (measurement_type == "S22" and options["S22"] == True) or (measurement_type == "S11" and options["S11"] == True) or (measurement_type == "IP3" and options["IP3"] == True):
                log_message(f"STARTING {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")
                results_hash = self.na_test.get_gain_measurement(path, measurement_config["gain_setting"], measurement_type)
                self.process_and_write_module_data(path, measurement_type, results_hash)
                log_message(f"FINISHED {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")

                self.clean_up()

            if measurement_type == "Noise_Figure" and options["Noise_Figure"] == True:
                log_message(f"STARTING {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")
                results = self.na_test.set_up_noise_figure(measurement_config["switchpath"], measurement_config["freqs"])
                self.process_and_write_module_data(path, measurement_type, results)
                log_message(f"FINISHED {measurement_type} @ {measurement_config['gain_setting']} dB with path {path}")

                self.clean_up()

        


if __name__ == "__main__":

    manager = LNAModuleTestManager(sim=False)

    import os 

    def query_user_for_path():
            
        for i, path in enumerate(manager.paths):
            log_message(f"{i}  {path}")

        select = input("SELECT PATH")
        log_message(f"You have selected > {select}")
        answer = input("Are you sure? y/n")

        if answer.lower() == "y":
            return select
        else:
            os.system("cls")
            query_user_for_path()

    select = query_user_for_path()

    sno = input("ENTER SNO >  ")

    manager.run_and_process_tests(manager.paths[int(select)], sno=sno)
    configure_logging(sno)
