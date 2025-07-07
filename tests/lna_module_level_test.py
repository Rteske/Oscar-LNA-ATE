
import time
from instruments.power_meter import E4418BPowerMeter, GigatronixPowerMeter
from instruments.signal_generator import SynthesizedCWGenerator, E4438CSignalGenerator
from instruments.power_supply import PowerSupply
from instruments.daq import RS422_DAQ
from instruments.temp_probe import DracalTempProbe, Agilent34401A
from configs.calibration import Calibration
from instruments.temp_controller import TempController
from instruments.ztm import ZtmModular
from instruments.signal_analyzer import MXASignalAnalyzer
from instruments.network_analyzer import PNAXNetworkAnalyzer
from instruments.AIOUSB.aiousb import Aiousb
from configs.configs import PNAXOscarLNAConfig
from configs.scribe import Scribe
from instruments.noise_figure_meter import NoiseFigure8970B
import datetime
import csv
import logging
import os

class RfTest:
    def __init__(self, rfpm1_input="SIM", rfpm2_output="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM", switch_bank2="SIM", na="SIM"):
        self.logger = logging.getLogger("Test")
        self.logger.setLevel(logging.DEBUG)
        
        self.sno = sno
        self.name = ""

class NetworkAnalyzerTest(RfTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", switch_bank2="SIM", config="SIM"):
        if isinstance(na, PNAXNetworkAnalyzer):
            self.na = na
        else:
            raise TypeError()
        
        if isinstance(psu, PowerSupply):
            self.psu = psu
        else:
            raise TypeError()
        
        if isinstance(daq, RS422_DAQ):
            self.daq = daq
        elif isinstance(daq, Aiousb):
            self.daq = daq
        else:
            raise TypeError
        
        if isinstance(temp_probe, Agilent34401A):
            self.temp_probe = temp_probe
        else:
            raise TypeError
        
        if isinstance(temp_probe2, Agilent34401A):
            self.temp_probe2 = temp_probe2
        else:
            raise TypeError
        
        if isinstance(switch_bank, ZtmModular):
            self.switch_bank = switch_bank
        else:
            raise TypeError
        
        if isinstance(switch_bank2, ZtmModular):
            self.switch_bank2 = switch_bank2
        else:
            raise TypeError
        
        if isinstance(config, PNAXOscarLNAConfig):
            self.config = config
        else:
            raise TypeError
        

        self.sno = sno
        self.name = ""

    def unplug_for_noise_meter(self):
        self.temp_probe.instrument.clear()
        self.temp_probe2.instrument.clear()
        self.temp_probe.instrument.close()
        self.temp_probe2.instrument.close()

    def replug_temp_probes(self):
        self.temp_probe = Agilent34401A("GPIB0::29::INSTR")
        self.temp_probe2 = Agilent34401A("GPIB0::22::INSTR")

class NetworkAnalyzerModuleTest(NetworkAnalyzerTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", switch_bank2="SIM", config="SIM"):
        super().__init__(na, psu, daq, temp_probe, temp_probe2, sno, switch_bank, switch_bank2, config)
        self.name = "Network Analyzer Standard Test"

    def set_up_measurement(self, switchpath, gain_setting, statefilepath):
        self.switch_bank.set_all_switches(switchpath[0])
        self.switch_bank2.set_all_switches(switchpath[1])

        print("Setting up measurement")

        self.na.load_saved_cal_and_state(statefilepath)

        self.daq.enable_rf()
        self.daq.set_attenuation(gain_setting)
        print("Completed setting up measurement")
        time.sleep(2)

    def clean_up_measurement(self):
        self.switch_bank.reset_all_switches()
        self.switch_bank2.reset_all_switches()
        self.daq.disable_rf()

    def get_gain_measurement(self, path, gain_setting, measurement_type):
        switchpath, statefile = self.config.get_switchpath_and_statefile_by_path_and_measurement_type(path, measurement_type)
        self.set_up_measurement(switchpath, gain_setting, statefile)
        time.sleep(5)
        voltage, current = self.get_voltage_and_current()
        probe_temp_value, probe_temp_value2 = self.get_temp_data()
        date_string = datetime.datetime.now()

        data, freqs = self.na.calc_and_stream_trace(1, 1, "MLOG")

        return {
        "gain_setting":f"{gain_setting}",
        "freqs":freqs,
        "gain_data": data,
        "datetime_string":date_string,
        "temp_probe1_value": probe_temp_value,
        "temp_probe2_value": probe_temp_value2,
        "voltage": voltage,
        "current": current
        }
    
    def get_gain_and_phase_measurement(self, path, gain_setting):
        measurement_type = "Gain_Phase"
        switchpath, statefile = self.config.get_switchpath_and_statefile_by_path_and_measurement_type(path, measurement_type)
        self.set_up_measurement(switchpath, gain_setting, statefile)
        time.sleep(5)
        voltage, current = self.get_voltage_and_current()
        probe_temp_value, probe_temp_value2 = self.get_temp_data()

        data, freqs = self.na.calc_and_stream_trace(1, 1, "MLOG")
        data2, freqs = self.na.calc_and_stream_trace(1, 1, "PHAS")
        datetime_string = datetime.datetime.now()

        return {
        "gain_setting":f"{gain_setting}",
        "datetime_string": datetime_string,
        "freqs":freqs,
        "gain_data": data,
        "phase_data": data2,
        "temp_probe1_value": probe_temp_value,
        "temp_probe2_value": probe_temp_value2,
        "voltage": voltage,
        "current": current
        }
    

    def psat_p1_measurement(self, path, gain_setting, linear_start_stop, saturation_start_stop):
        measurement_type = "PSAT"
        switchpath, linear_statefile = self.config.get_psat_switchpath_and_statefile_by_path_and_psat_stage(path, "linear")

        self.set_up_measurement(switchpath, gain_setting, linear_statefile)
        # Start and Stop source power 
        # Need to add the ability to change the source power calibration depending on the network analyzer attenuator click
        linear_source_start = linear_start_stop[0]
        linear_source_end = linear_start_stop[1]

        saturation_start_source_start = saturation_start_stop[0]
        saturation_start_source_end = saturation_start_stop[1]

        # Psat bucket to for data visualization at psat (MEaning all values are -1 below this point)
        psat = {}

        _, freqs = self.na.calc_and_stream_trace(1, 1, "MLOG")
        headers = ["source_db"] + freqs
 
        linear_gain_bucket = {}
        saturation_gain_bucket = {}
        # Start of comparison for linear range for comparison
        for index, source_db in enumerate(range(linear_source_start, linear_source_end, 1)):
            self.na.set_amplitude(1, source_db)
            time.sleep(1)
            gain, freqs = self.na.calc_and_stream_trace(1, 1, "MLOG")
            datetime_string = datetime.datetime.now()
            temp_probe1, temp_probe2 = self.get_temp_data()
            voltage, current = self.get_voltage_and_current()
            linear_gain_bucket[source_db] = {"gain": gain, "temp_probe1_value": temp_probe1, "temp_probe2_value": temp_probe2, "voltage": voltage, "current": current, "datetime_string": datetime_string}
            print(f"DONE WITH {source_db}")

        running_db = saturation_start_source_start
        while running_db != saturation_start_source_end:
            self.na.set_amplitude(1, running_db)
            time.sleep(1)
            gain, freqs = self.na.calc_and_stream_trace(1, 1, "MLOG")
            temp_probe1, temp_probe2 = self.get_temp_data()
            voltage, current = self.get_voltage_and_current()
            datetime_string = datetime.datetime.now()
            saturation_gain_bucket[running_db] = {"gain": gain, "temp_probe1_value": temp_probe1, "temp_probe2_value": temp_probe2, "voltage": voltage, "current": current, "datetime_string": datetime_string}
            running_db += .1
            running_db = round(running_db, 2)
            print(f"DONE WITH {running_db}")

        return linear_gain_bucket, saturation_gain_bucket, freqs

    def recover_test_state(self, switchpath, gain_setting, measurement_type):
        self.set_up_measurement(switchpath=switchpath, gain_setting=gain_setting, ratioed_power=measurement_type)
    
    def get_voltage_and_current(self):
        current = self.psu.get_current()
        voltage = self.psu.get_voltage()

        return voltage, current 
    
    def get_temp_data(self):
        probe_temp_value = self.temp_probe.measure_temp()
        print(f"Probe Temp Value: {probe_temp_value}")

        probe_temp_value2 = self.temp_probe2.measure_temp()
        print(f"Probe Temp Value 2: {probe_temp_value2}")

        return probe_temp_value, probe_temp_value2
    
    def set_up_noise_figure(self, switchpath, freqs):
        self.switch_bank.set_all_switches(switchpath[0])
        self.switch_bank2.set_all_switches(switchpath[1])

        self.noise_figure_meter = NoiseFigure8970B("GPIB0::8::INSTR")

        # self.unplug_for_noise_meter()

        bucket = self.noise_figure_meter.set_and_measure(freqs)

        self.noise_figure_meter.deassert_ren()

        # self.replug_temp_probes()
        del(self.noise_figure_meter)
        temp_probe1, temp_probe2 = self.get_temp_data()

        return bucket 