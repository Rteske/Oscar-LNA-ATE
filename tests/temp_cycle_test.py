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
from configs.calibration import Calibration
from configs.configs import OQPSKConfig, PNAXConfig, OSCARPAOQPSKConfig, PNAXOscarPAConfig
from configs.scribe import Scribe
import datetime
import csv
import logging
import os

class RfTest:
    def __init__(self, rfpm1_input="SIM", rfpm2_output="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM", na="SIM"):
        self.logger = logging.getLogger("Test")
        self.logger.setLevel(logging.DEBUG)
        
        self.sno = sno
        self.name = ""

# class PowerMeterTest(RfTest):
#     def __init__(self, rfpm1="SIM", rfpm2="SIM", rfpm3="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM"):
#         super.__init__(rfpm1, rfpm2, rfpm3, rfsg, psu, daq, temp_probe, temp_probe2, temp_controller, sno, switch_bank)

#         dt = datetime.datetime.now()
#         self.session_date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")
#         self.dir_name = os.getcwd()

#         self.scribe = Scribe("Test")

#         self.sno = sno
#         self.name = ""

#         self.line_count = 0

#         self.current_flie_count = 1

#     def set_sno(self, sno):
#         self.data_filepath = self.dir_name + "\\data" + f"\\{sno}" + f"\\{self.session_date_string}" + f"\\{self.current_flie_count}" + ".csv"
#         if not os.path.exists(self.dir_name + "\\data" + f"\\{sno}"):
#             os.mkdir(self.dir_name + "\\data" + f"\\{sno}")
        
#         os.mkdir(self.dir_name + "\\data" + f"\\{sno}" + f"\\{self.session_date_string}")

#     def write2file(self, array):
#         if self.line_count < 1e+6:
#             with open(self.data_filepath, 'a', encoding="utf-8", newline='') as ff:
#                 writer = csv.writer(ff)
#                 if self.line_count == 0:
#                     writer.writerow(["frequency", "rfpm1_dBm", "rfpm2_dBm", "psu_voltage", "psu_current", "rfpm3_dBm", "daq_rf_on_off", "daq_fault_status", "daq_bandpath", "daq_datetime", "daq_gain_value", "daq_temp_value", "temp_probe1_value", "temp_probe2_value", "temp_plate_value"])
#                 print(array)
#                 writer.writerow(array)
#                 ff.close()

#                 self.line_count += 1
#         else:
#             self.current_flie_count += 1
#             self.data_filepath = self.dir_name + "\\data" + f"\\{self.sno}" + f"\\{self.session_date_string}" + f"\\{self.current_flie_count}" + ".csv"
#             with open(self.data_filepath, 'a', encoding="utf-8", newline='') as ff:
#                 writer = csv.writer(ff)
#                 writer.writerow(["frequency", "rfpm1_dBm", "rfpm2_dBm", "psu_voltage", "psu_current", "rfpm3_dBm", "daq_rf_on_off", "daq_fault_status", "daq_bandpath", "daq_datetime", "daq_gain_value", "daq_temp_value", "temp_probe1_value", "temp_probe2_value", "temp_plate_value"])
#                 writer.writerow(array)
#                 ff.close()

#                 self.line_count = 0

#     def set_up_measurement(self, frequency, temperature, bandpath, gain_setting, voltage=28, current=5):
#         self.psu.set_voltage(voltage)
#         self.psu.set_current(current)
#         self.psu.set_output_state(True)
#         print("Setting up measurement")

#         self.rfpm1.set_frequency(frequency)
#         self.rfpm2.set_frequency(frequency)

#         horizontal, vertical = self.cal.get_input_loss_at_frequency(frequency)
#         input_loss = round((horizontal + vertical) / 2, 3)
#         rfsg_input_power = self.input_power_validation(frequency, target_power=-10, start_power=-30, input_loss=input_loss)

#         self.rfsg.set_amplitude(rfsg_input_power)
#         self.daq.enable_rf()
#         self.daq.set_band(bandpath)
#         self.daq.change_gain(gain_setting)
#         print("Completed setting up measurement")

#     def clean_up_measurement(self):
#         self.daq.disable_rf()
#         self.daq.set_band("NONE")
#         self.rfsg.stop_output()

#     def measure_and_record(self, time_total, temp_target, temp_delta=3, frequency=None, voltage=28):
#         t_end = time.time() + (time_total * 60)
#         while time.time() < t_end:
#             horizontal, vertical = self.cal.get_input_loss_at_frequency(frequency)
#             input_loss = round((horizontal + vertical) / 2, 3)
            
#             errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm, psu_current, psu_voltage = self.validate_power(frequency, max_gain=33, min_gain=29, max_current=2.1, min_current=.5, max_voltage=voltage + 1.5, min_voltage=voltage - 1.5, input_loss=input_loss, max_input=6)

#             rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()

#             _, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(temp_target, temp_delta)
#             os.system('cls')
#             print("\n")
#             if errors:
#                 print("ERRORS DETECTED")
#                 print(errors)
#                 self.write2file(errors)

#             frame = [frequency, rfpm1_dBm, rfpm2_dBm, psu_voltage, psu_current, rfpm3_dBm, rf_on_off, fault_status, bandpath, date_string, gain_value, dut_temp_value, probe_temp_value, probe_temp_value2, temp_plate_value]
#             if completed:
#                 self.write2file(frame)
#             else:
#                 self.write2file(["FAILED TEMP"])
#                 time_taken = self.wait_for_temp_change(temp_target, temp_delta)
#                 t_end += time_taken

#         self.clean_up_measurement()

#     def input_power_validation(self, frequency, target_power, start_power, input_loss):
#         # Calibration Stage Making sure -10 is going into the unit
#         rfsg_input_power = start_power
#         self.rfsg.set_frequency(frequency)
#         self.rfsg.set_amplitude(rfsg_input_power)
#         self.rfsg.start_output()

#         time.sleep(1)

#         power_increments = [1, .5, .25, .1, .75]
#         power_inc_index = 0

#         power_delta = 10000
#         power_delta_limit = .1

#         output_power = self.rfpm1.get_power_measurement() + input_loss

#         while power_delta > power_delta_limit:
#             if power_delta > power_increments[power_inc_index]:
#                 inc = power_increments[power_inc_index]
#             else:
#                 if power_inc_index != len(power_increments) - 1:
#                     power_inc_index += 1
#                     inc = power_increments[power_inc_index]
#                 else:
#                     inc = power_increments[power_inc_index]

#             if target_power - output_power < 0:
#                 print("Increasing power")
#                 rfsg_input_power -= inc
#             else:
#                 print("Decreasing power")
#                 rfsg_input_power += inc

#             self.rfsg.set_amplitude(rfsg_input_power)

#             output_power = self.rfpm2.get_power_measurement() + input_loss

#             power_delta = abs(target_power - output_power)  
#             print(f"INPUT POWER VALIDATION (output_power: {output_power}, power_delta: {power_delta})")
#             time.sleep(.2)

#         print(f"INPUT POWER VALIDATION COMPLETE (output_power: {output_power}, power_delta: {power_delta})")
#         return rfsg_input_power

#     def validate_tempature(self, target_temp, target_temp_delta):
#         probe_temp_value = self.temp_probe.measure_temp()
#         print(f"Probe Temp Value: {probe_temp_value}")

#         probe_temp_value2 = self.temp_probe2.measure_temp()
#         print(f"Probe Temp Value 2: {probe_temp_value2}")

#         _, _, _, _, _, dut_temp_value = self.daq.read_status_return()
#         print(f"DUT Temp Value: {dut_temp_value}")

#         temp_plate_value = self.temp_controller.query_actual(1)
#         print(f"Temp Plate Value: {temp_plate_value}")

#         temp_delta = abs(target_temp - float(probe_temp_value))
#         print(f"Temp Delta: {temp_delta}")

#         complete = float(probe_temp_value) < target_temp + target_temp_delta and float(probe_temp_value) > target_temp - target_temp_delta
#         print(f"Temp Complete: {complete}")

#         print(f"{target_temp} target temp, {target_temp_delta} target temp delta")

#         return temp_delta, complete, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value
    
#     def wait_for_temp_change(self, target_temp, target_temp_delta=3):
#         temp_delta, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(target_temp, target_temp_delta) 
#         t_start = time.time()

#         tries = 0

#         while not completed:
#             os.system('cls')
#             print("\n")
#             print("\n")
#             print(f"Waiting for temperature to stabilize at {target_temp} target temp")
#             if tries > 200:
#                 print("Temperature confirmation failed")
#                 self.temp_controller.set_chamber_state("OFF")

#                 if target_temp + target_temp_delta < float(probe_temp_value):
#                     self.running_temp = self.running_temp - 2
#                 elif target_temp - target_temp_delta > float(probe_temp_value):
#                     self.running_temp = self.running_temp + 2

#                 self.temp_controller.set_setpoint(1, self.running_temp) 
#                 self.temp_controller.set_chamber_state("ON")
#                 tries = 0

#             tries += 1
#             rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()
#             temp_delta, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(target_temp, target_temp_delta)

#             frame = ["", "", "", "", "", "", rf_on_off, fault_status, bandpath, date_string, gain_value, dut_temp_value, probe_temp_value, probe_temp_value2, temp_plate_value]
#             self.write2file(frame)
            
#             time.sleep(3)
#             if completed:
#                 break

#         print(f"Temperature confirmation completed with {temp_delta} delta @ {target_temp} target temp")
#         return time.time() - t_start
    
#     def set_temp(self, timer, target_temp, target_temp_delta=3, temp_controller_offset=0):
#         self.temp_controller.set_setpoint(1, target_temp + temp_controller_offset)
#         self.temp_controller.set_chamber_state(True)

#         elapsed_time = self.wait_for_temp_change(target_temp, target_temp_delta)
#         print(f"Temperature confirmation t0ok {elapsed_time} seconds ")
#         return elapsed_time

#     def validate_power(self, frequency, max_input, max_gain, min_gain, max_current, min_current, max_voltage, min_voltage, input_loss):
#         errors = []
#         output_horizontal, output_vertical = self.cal.get_output_loss_at_frequency(frequency)
#         rfpm1_dBm = self.rfpm1.get_power_measurement() - output_horizontal 
#         rfpm2_dBm = self.rfpm2.get_power_measurement() - output_vertical 
#         rfpm3_dBm = self.rfpm3.get_power_measurement() + input_loss

#         psu_current = self.psu.get_current()
#         psu_voltage = self.psu.get_voltage()

#         if rfpm1_dBm < min_gain or rfpm1_dBm > max_gain:
#             errors.append("rfpm1_dBm_output_range_error")

#         if rfpm2_dBm < min_gain or rfpm2_dBm > max_gain:
#             errors.append("rfpm2_dBm_output_range_error")

#         if rfpm3_dBm > max_input:
#             errors.append("rfpm3_dBm_output_range_error")

#         if psu_current < min_current or psu_current > max_current:
#             errors.append("psu_current_range_error")

#         if psu_voltage < min_voltage or psu_voltage > max_voltage:
#             errors.append("psu_voltage_range_error")

#         print(errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm, psu_current, psu_voltage)

#         return errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm
    
class SignalAnalyzerTest(RfTest):
    def __init__(self, rfpm2_input="SIM", rfpm1_output="SIM" , rfsa="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        if isinstance(rfpm2_input, E4418BPowerMeter):
            self.rfpm2_input = rfpm2_input
            # self.logger.debug("Succesfully connected to rfpm1 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(rfpm1_output, E4418BPowerMeter):
            self.rfpm1_output = rfpm1_output
            # self.logger.debug("Succesfully connected to rfpm2 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(psu, PowerSupply):
            self.psu = psu
        else:
            raise TypeError()
        
        if isinstance(rfsa, MXASignalAnalyzer):
            self.rfsa = rfsa
        else:
            raise TypeError()

        if isinstance(rfsg, E4438CSignalGenerator):
            self.rfsg = rfsg
            # self.logger.debug("Successfully connected to rfsg (SynthesizedCWGenerator)")
        else:
            raise TypeError()
        
        if isinstance(daq, RS422_DAQ):
            self.daq = daq
            # self.logger.debug("Succesfully connected to daq and DUT (ARDUINO)")
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
        
        if isinstance(config, OSCARPAOQPSKConfig):
            self.config = config
        else:
            raise TypeError
        
        self.sno = sno
        self.name = ""

class NetworkAnalyzerTest(RfTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
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
        
        if isinstance(config, PNAXOscarPAConfig):
            self.config = config
        else:
            raise TypeError
        
        self.sno = sno
        self.name = ""

# class NetworkAnalyzerStandardTest(NetworkAnalyzerTest):
#     def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
#         super().__init__(na, psu, daq, temp_probe, temp_probe2, temp_controller, sno, switch_bank, config)
#         self.name = "Network Analyzer Standard Test"
        

#     def set_up_measurement(self, switchpath, bandpath, gain_setting, voltage=28, current=5):
#         print(switchpath)
#         self.switch_bank.set_all_switches(self.config.paths[switchpath])

#         self.psu.set_voltage(voltage)
#         self.psu.set_current(current)
#         self.psu.set_output_state(True)
#         print("Setting up measurement")

#         hash = self.config.ratioed_powers_w_statefilepath["S21"]
#         self.na.load_saved_cal_and_state(hash[switchpath])

#         self.daq.enable_rf()
#         self.daq.set_band(bandpath)
#         self.daq.change_gain(gain_setting)
#         print("Completed setting up measurement")
#         time.sleep(5)

#     def clean_up_measurement(self):
#         self.switch_bank.reset_all_switches()
#         self.daq.disable_rf()

#     def get_31_steps_at_switchpath(self, switchpath):
#         print(switchpath)
#         bandpath = self.config.get_bandpath_by_switchpath(switchpath)

#         phase_bucket = []
#         gain_bucket = []
#         freqs = ''
#         gain_setting = 10
#         self.set_up_measurement(switchpath, bandpath, gain_setting)
#         for gain_setting in range(10, 42):
#             self.daq.change_gain(gain_setting)
#             time.sleep(3)
#             voltage, current = self.get_voltage_and_current()
#             probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.get_temp_data()
#             rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()

#             gain, freqs = self.na.calc_and_stream_trace(1, 1)
#             phase, freqs = self.na.calc_and_stream_trace(1, 2)

#             gain_bucket.append({
#                 "gain_setting":f"{gain_setting}",
#                 "freqs":freqs,
#                 "gain":gain,
#                 "rf_on_off":rf_on_off,
#                 "fault_status": fault_status,
#                 "bandpath":bandpath,
#                 "gain_value":gain_value,
#                 "datetime_string":date_string,
#                 "temp_probe1_value": probe_temp_value,
#                 "temp_probe2_value": probe_temp_value2,
#                 "dut_temp_value": dut_temp_value,
#                 "temp_plate_value": temp_plate_value,
#                 "voltage": voltage,
#                 "current": current
#             }
#             )
#             phase_bucket.append({
#                 "gain_setting":f"{gain_setting}",
#                 "freqs":freqs,
#                 "phase":phase,
#                 "rf_on_off":rf_on_off,
#                 "fault_status": fault_status,
#                 "bandpath":bandpath,
#                 "gain_value":gain_value,
#                 "datetime_string":date_string,
#                 "temp_probe1_value": probe_temp_value,
#                 "temp_probe2_value": probe_temp_value2,
#                 "dut_temp_value": dut_temp_value,
#                 "temp_plate_value": temp_plate_value,
#                 "voltage": voltage,
#                 "current": current
#             }
#             )            

#         self.clean_up_measurement()


#         return gain_bucket, phase_bucket
    
#     def get_voltage_and_current(self):
#         current = self.psu.get_current()
#         voltage = self.psu.get_voltage()

#         return voltage, current 
    
#     def get_temp_data(self):
#         probe_temp_value = self.temp_probe.measure_temp()
#         print(f"Probe Temp Value: {probe_temp_value}")

#         probe_temp_value2 = self.temp_probe2.measure_temp()
#         print(f"Probe Temp Value 2: {probe_temp_value2}")

#         _, _, _, _, _, dut_temp_value = self.daq.read_status_return()
#         print(f"DUT Temp Value: {dut_temp_value}")

#         temp_plate_value = self.temp_controller.query_actual(1)
#         print(f"Temp Plate Value: {temp_plate_value}")

#         return probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value

# class BandwithPowerTest(SignalAnalyzerTest):
#     def __init__(self, rfpm1="SIM", rfpm2="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM" , sno="SIM", switch_bank="SIM", config="SIM", rfsa="SIM"): 
#         super().__init__(rfpm2_input=rfpm2, rfpm1_output=rfpm1, rfsg=rfsg, rfsa=rfsa, psu=psu, daq=daq, temp_probe=temp_probe, temp_probe2=temp_probe2, temp_controller=temp_controller, sno=sno, switch_bank=switch_bank, config=config) 

#     def set_up_measurement(self, frequency, switchpath, bandpath, gain_setting, waveform, voltage=28, current=5):
#         print(gain_setting)
#         self.switch_bank.set_all_switches(self.config.paths[switchpath])

#         self.psu.set_voltage(voltage)
#         self.psu.set_current(current)
#         self.psu.set_output_state(True)
#         print("Setting up measurement")

#         self.rfpm2_input.set_frequency(frequency)
#         self.rfpm1_output.set_frequency(frequency)

#         self.rfsa.load_saved_cal_and_state_from_register(1)
#         self.rfsa.set_center_frequency(frequency)
#         self.rfsa.set_attenuation_level(10)

#         input_loss = self.config.get_input_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
#         rfsg_input_power = self.input_power_validation(frequency, target_power=-10, start_power=-30, input_loss=input_loss)

#         # self.rfsg.select_waveform()
#         self.rfsg.set_frequency(frequency=frequency)
#         self.rfsg.set_amplitude(rfsg_input_power)
#         if waveform == "CW":
#             self.rfsg.enable_modulation("OFF")
#         elif waveform == "OQPSK":
#             self.rfsg.select_demod_filter(waveform)
#             self.rfsg.enable_modulation("ON")

#         self.daq.enable_rf()
#         self.daq.set_band(bandpath)
#         self.daq.change_gain(gain_setting)

#         self.rfsa.auto_set_reference_level()

#         print("Completed setting up measurement")

#     def input_power_validation(self, frequency, target_power, start_power, input_loss):
#         # Calibration Stage Making sure -10 is going into the unit
#         rfsg_input_power = start_power
#         self.rfsg.set_frequency(frequency)
#         self.rfsg.set_amplitude(rfsg_input_power)
#         self.rfsg.start_output()

#         time.sleep(1)

#         power_increments = [1, .5, .25, .1, .75]
#         power_inc_index = 0

#         power_delta = 10000
#         power_delta_limit = .1

#         output_power = self.rfpm2_input.get_power_measurement() + input_loss

#         while power_delta > power_delta_limit:
#             if power_delta > power_increments[power_inc_index]:
#                 inc = power_increments[power_inc_index]
#             else:
#                 if power_inc_index != len(power_increments) - 1:
#                     power_inc_index += 1
#                     inc = power_increments[power_inc_index]
#                 else:
#                     inc = power_increments[power_inc_index]

#             if target_power - output_power < 0:
#                 print("Increasing power")
#                 rfsg_input_power -= inc
#             else:
#                 print("Decreasing power")
#                 rfsg_input_power += inc

#             self.rfsg.set_amplitude(rfsg_input_power)

#             output_power = self.rfpm2_input.get_power_measurement() + input_loss

#             power_delta = abs(target_power - output_power)  
#             print(f"INPUT POWER VALIDATION (output_power: {output_power}, power_delta: {power_delta})")
#             time.sleep(.2)

#         print(f"INPUT POWER VALIDATION COMPLETE (output_power: {output_power}, power_delta: {power_delta})")
#         return rfsg_input_power
    
#     def clean_up_measurement(self):
#         self.rfsg.stop()
#         self.daq.disable_rf()
#         self.switch_bank.reset_all_switches()

#     def get_bandwidth_by_frequency_and_switchpath(self, switchpath, frequency):
#         standard_bucket = []
#         harmonic_bucket = []
#         rfpm1_bucket = []
#         print("IN THIS BITCH", frequency)
#         bandpath = self.config.get_bandpath_by_frequency(frequency)
#         high_gain_setting = 41
#         low_gain_setting = 10

#         for waveform in self.config.waveforms:
#             self.set_up_measurement(frequency=frequency, waveform=waveform, bandpath=bandpath, switchpath=switchpath, gain_setting=low_gain_setting)
#             if waveform == "OQPSK":
#                 for bandwidth in self.config.static_bandwidths:
#                     self.rfsa.set_center_span(bandwidth)
#                     time.sleep(2)
#                     frequencies, powers = self.rfsa.get_frequency_span_data()
#                     voltage, current = self.get_voltage_and_current()
#                     probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.get_temp_data()
#                     rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()
                    
#                     standard_bucket.append(
#                     {
#                         "freqs":frequencies,
#                         "powers":powers,
#                         "bandwidth":bandwidth,
#                         "waveform": waveform,
#                         "gain_setting":low_gain_setting,
#                         "rf_on_off":rf_on_off,
#                         "fault_status": fault_status,
#                         "bandpath":bandpath,
#                         "gain_value":gain_value,
#                         "datetime_string":date_string,
#                         "temp_probe1_value": probe_temp_value,
#                         "temp_probe2_value": probe_temp_value2,
#                         "dut_temp_value": dut_temp_value,
#                         "temp_plate_value": temp_plate_value,
#                         "voltage": voltage,
#                         "current": current
#                     }
#                     )

#                     rfpm1_output_power = self.rfpm1_output.get_power_measurement()

#                     output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
#                     rfpm1_bucket.append(
#                     {
#                         "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
#                         "rfpm1_output_power_uncalibrated": rfpm1_output_power,
#                         "rfpm1_output_loss_@_freq": output_loss, "waveform":waveform,
#                         "rf_on_off":rf_on_off,
#                         "fault_status": fault_status,
#                         "bandpath":bandpath,
#                         "gain_value":gain_value,
#                         "datetime_string":date_string,
#                         "temp_probe1_value": probe_temp_value,
#                         "temp_probe2_value": probe_temp_value2,
#                         "dut_temp_value": dut_temp_value,
#                         "temp_plate_value": temp_plate_value,
#                         "voltage": voltage,
#                         "current": current
#                     }
#                     )

                
#                 self.daq.change_gain(high_gain_setting)

#                 # For the swap between gain settings
#                 time.sleep(3)

#                 for bandwidth in self.config.static_bandwidths:
#                     self.rfsa.set_center_span(bandwidth)
#                     time.sleep(2)
#                     frequencies, powers = self.rfsa.get_frequency_span_data()
#                     voltage, current = self.get_voltage_and_current()
#                     probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.get_temp_data()
#                     rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()
                    
#                     standard_bucket.append(
#                     {
#                         "freqs":frequencies,
#                         "powers":powers,
#                         "bandwidth":bandwidth,
#                         "waveform": waveform,
#                         "gain_setting":low_gain_setting,
#                         "rf_on_off":rf_on_off,
#                         "fault_status": fault_status,
#                         "bandpath":bandpath,
#                         "gain_value":gain_value,
#                         "datetime_string":date_string,
#                         "temp_probe1_value": probe_temp_value,
#                         "temp_probe2_value": probe_temp_value2,
#                         "dut_temp_value": dut_temp_value,
#                         "temp_plate_value": temp_plate_value,
#                         "voltage": voltage,
#                         "current": current
#                     }
#                     )
#                     rfpm1_output_power = self.rfpm1_output.get_power_measurement()

#                     output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
#                     rfpm1_bucket.append(
#                     {
#                         "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
#                         "rfpm1_output_power_uncalibrated": rfpm1_output_power,
#                         "rfpm1_output_loss_@_freq": output_loss, "waveform":waveform,
#                         "rf_on_off":rf_on_off,
#                         "fault_status": fault_status,
#                         "bandpath":bandpath,
#                         "gain_value":gain_value,
#                         "datetime_string":date_string,
#                         "temp_probe1_value": probe_temp_value,
#                         "temp_probe2_value": probe_temp_value2,
#                         "dut_temp_value": dut_temp_value,
#                         "temp_plate_value": temp_plate_value,
#                         "voltage": voltage,
#                         "current": current
#                     }
#                     )


#             self.daq.change_gain(high_gain_setting)
#             start_stop = self.config.harmonic_measurement_bandwidths[bandpath]
            
#             span = int(start_stop[1]) - int(start_stop[0])
#             bandwidth = span
#             center = int(start_stop[0]) + (span / 2)
#             self.rfsa.set_center_frequency(center)
#             self.rfsa.set_center_span(span)
#             time.sleep(2)
#             frequencies, powers = self.rfsa.get_frequency_span_data()
#             voltage, current = self.get_voltage_and_current()
#             probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.get_temp_data()
#             rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()
#             harmonic_bucket.append(
#             {
#                 "freqs":frequencies,
#                 "powers":powers,
#                 "bandwidth":bandwidth,
#                 "waveform": waveform,
#                 "gain_setting":gain_value,
#                 "rf_on_off":rf_on_off,
#                 "fault_status": fault_status,
#                 "bandpath":bandpath,
#                 "gain_value":gain_value,
#                 "datetime_string":date_string,
#                 "temp_probe1_value": probe_temp_value,
#                 "temp_probe2_value": probe_temp_value2,
#                 "dut_temp_value": dut_temp_value,
#                 "temp_plate_value": temp_plate_value,
#                 "voltage": voltage,
#                 "current": current
#             }
#             )
#             rfpm1_output_power = self.rfpm1_output.get_power_measurement()

#             output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
#             rfpm1_bucket.append(
#             {
#                 "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
#                 "rfpm1_output_power_uncalibrated": rfpm1_output_power,
#                 "rfpm1_output_loss_@_freq": output_loss, "waveform":waveform,
#                 "rf_on_off":rf_on_off,
#                 "fault_status": fault_status,
#                 "bandpath":bandpath,
#                 "gain_value":gain_value,
#                 "datetime_string":date_string,
#                 "temp_probe1_value": probe_temp_value,
#                 "temp_probe2_value": probe_temp_value2,
#                 "dut_temp_value": dut_temp_value,
#                 "temp_plate_value": temp_plate_value,
#                 "voltage": voltage,
#                 "current": current
#             }
#             )
#             self.clean_up_measurement()


#         return standard_bucket, harmonic_bucket, rfpm1_bucket

#     def get_voltage_and_current(self):
#         current = self.psu.get_current()
#         voltage = self.psu.get_voltage()

#         return voltage, current 
    
#     def get_temp_data(self):
#         probe_temp_value = self.temp_probe.measure_temp()
#         print(f"Probe Temp Value: {probe_temp_value}")

#         probe_temp_value2 = self.temp_probe2.measure_temp()
#         print(f"Probe Temp Value 2: {probe_temp_value2}")

#         _, _, _, _, _, dut_temp_value = self.daq.read_status_return()
#         print(f"DUT Temp Value: {dut_temp_value}")

#         temp_plate_value = self.temp_controller.query_actual(1)
#         print(f"Temp Plate Value: {temp_plate_value}")

#         return probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value
    
class BandwithPowerModuleTest(SignalAnalyzerTest):
    def __init__(self, rfpm1="SIM", rfpm2="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM", rfsa="SIM"): 
        super().__init__(rfpm2_input=rfpm2, rfpm1_output=rfpm1, rfsg=rfsg, rfsa=rfsa, psu=psu, daq=daq, temp_probe=temp_probe, temp_probe2=temp_probe2, sno=sno, switch_bank=switch_bank, config=config) 

    def set_up_measurement(self, frequency, switchpath, gain_setting, waveform, voltage=8.5, current=1.7):
        print(gain_setting)
        self.switch_bank.set_all_switches(self.config.paths[switchpath])

        self.psu.set_voltage(voltage)
        self.psu.set_current(current)
        self.psu.set_output_state(True)
        print(f"Setting up measurement @ FREQ:{frequency} SWITCHPATH:{switchpath} GAIN SETTING:{gain_setting} WAVEFORM: {waveform}")

        self.rfpm2_input.set_frequency(frequency)
        self.rfpm1_output.set_frequency(frequency)

        self.rfsa.load_saved_cal_and_state_from_register(1)
        self.rfsa.set_center_frequency(frequency)
        self.rfsa.set_attenuation_level(10)

        input_loss = self.config.get_input_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
        rfsg_input_power = self.input_power_validation(frequency, target_power=-10, start_power=-30, input_loss=input_loss)

        # self.rfsg.select_waveform()
        self.rfsg.set_frequency(frequency=frequency)
        self.rfsg.set_amplitude(rfsg_input_power)
        if waveform == "CW":
            self.rfsg.enable_modulation("OFF")
        elif waveform == "OQPSK":
            self.rfsg.select_demod_filter(waveform)
            self.rfsg.enable_modulation("ON")

        self.daq.enable_rf()
        self.daq.set_attenuation(gain_setting)

        self.rfsa.auto_set_reference_level()

        print("Completed setting up measurement")

    def input_power_validation(self, frequency, target_power, start_power, input_loss):
        # Calibration Stage Making sure -10 is going into the unit
        rfsg_input_power = start_power
        self.rfsg.set_frequency(frequency)
        self.rfsg.set_amplitude(rfsg_input_power)
        self.rfsg.start_output()

        time.sleep(1)

        power_increments = [1, .5, .25, .1, .75]
        power_inc_index = 0

        power_delta = 10000
        power_delta_limit = .1

        output_power = self.rfpm2_input.get_power_measurement() + input_loss

        while power_delta > power_delta_limit:
            if power_delta > power_increments[power_inc_index]:
                inc = power_increments[power_inc_index]
            else:
                if power_inc_index != len(power_increments) - 1:
                    power_inc_index += 1
                    inc = power_increments[power_inc_index]
                else:
                    inc = power_increments[power_inc_index]

            if target_power - output_power < 0:
                print("Increasing power")
                rfsg_input_power -= inc
            else:
                print("Decreasing power")
                rfsg_input_power += inc

            self.rfsg.set_amplitude(rfsg_input_power)

            output_power = self.rfpm2_input.get_power_measurement() + input_loss

            power_delta = abs(target_power - output_power)  
            print(f"INPUT POWER VALIDATION (output_power: {output_power}, power_delta: {power_delta})")
            time.sleep(.2)

        print(f"INPUT POWER VALIDATION COMPLETE (output_power: {output_power}, power_delta: {power_delta})")
        return rfsg_input_power
    
    def clean_up_measurement(self):
        self.rfsg.stop()
        self.daq.disable_rf()
        self.switch_bank.reset_all_switches()

    def get_bandwidth_by_frequency_and_switchpath(self, switchpath, frequency):
        standard_bucket = []
        harmonic_bucket = []
        rfpm1_bucket = []
        print("FREQ ", frequency)
        bandpath = self.config.get_bandpath_by_frequency(frequency)
        high_gain_setting = 41 - 10
        low_gain_setting = 10 - 10

        for waveform in self.config.waveforms:
            self.set_up_measurement(frequency=frequency, waveform=waveform, switchpath=switchpath, gain_setting=low_gain_setting)
            for bandwidth in self.config.static_bandwidths:
                self.rfsa.set_center_span(bandwidth)
                time.sleep(2)
                frequencies, powers = self.rfsa.get_frequency_span_data()
                voltage, current = self.get_voltage_and_current()
                probe_temp_value, probe_temp_value2 = self.get_temp_data()
                date_string = datetime.datetime.now()
                
                standard_bucket.append(
                {
                    "freqs":frequencies,
                    "powers":powers,
                    "bandwidth":bandwidth,
                    "waveform": waveform,
                    "gain_setting":low_gain_setting,
                    "datetime_string":date_string,
                    "temp_probe1_value": probe_temp_value,
                    "temp_probe2_value": probe_temp_value2,
                    "voltage": voltage,
                    "current": current
                }
                )

                rfpm1_output_power = self.rfpm1_output.get_power_measurement()

                output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
                rfpm1_bucket.append(
                {
                    "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
                    "rfpm1_output_power_uncalibrated": rfpm1_output_power,
                    "rfpm1_output_loss_@_freq": output_loss,
                    "waveform":waveform,
                    "gain_setting":low_gain_setting,
                    "datetime_string":date_string,
                    "temp_probe1_value": probe_temp_value,
                    "temp_probe2_value": probe_temp_value2,
                    "voltage": voltage,
                    "current": current
                }
                )

            
            self.daq.set_attenuation(high_gain_setting)

            # For the swap between gain settings
            time.sleep(3)

            for bandwidth in self.config.static_bandwidths:
                self.rfsa.set_center_span(bandwidth)
                time.sleep(2)
                frequencies, powers = self.rfsa.get_frequency_span_data()
                voltage, current = self.get_voltage_and_current()
                probe_temp_value, probe_temp_value2 = self.get_temp_data()
                
                standard_bucket.append(
                {
                    "freqs":frequencies,
                    "powers":powers,
                    "bandwidth":bandwidth,
                    "waveform": waveform,
                    "gain_setting":high_gain_setting,
                    "datetime_string":date_string,
                    "temp_probe1_value": probe_temp_value,
                    "temp_probe2_value": probe_temp_value2,
                    "voltage": voltage,
                    "current": current
                }
                )
                rfpm1_output_power = self.rfpm1_output.get_power_measurement()

                output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
                rfpm1_bucket.append(
                {
                    "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
                    "rfpm1_output_power_uncalibrated": rfpm1_output_power,
                    "rfpm1_output_loss_@_freq": output_loss,
                    "waveform":waveform,
                    "gain_setting":high_gain_setting,
                    "datetime_string":date_string,
                    "temp_probe1_value": probe_temp_value,
                    "temp_probe2_value": probe_temp_value2,
                    "voltage": voltage,
                    "current": current
                }
                )


            self.daq.set_attenuation(high_gain_setting)
            start_stop = self.config.harmonic_measurement_bandwidths[bandpath]
            
            span = int(start_stop[1]) - int(start_stop[0])
            bandwidth = span
            center = int(start_stop[0]) + (span / 2)
            self.rfsa.set_center_frequency(center)
            self.rfsa.set_center_span(span)
            time.sleep(2)
            frequencies, powers = self.rfsa.get_frequency_span_data()
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2 = self.get_temp_data()
            date_string = datetime.datetime.now()
            harmonic_bucket.append(
            {
                "freqs":frequencies,
                "powers":powers,
                "bandwidth":bandwidth,
                "waveform": waveform,
                "gain_setting": high_gain_setting,
                "datetime_string":date_string,
                "temp_probe1_value": probe_temp_value,
                "temp_probe2_value": probe_temp_value2,
                "voltage": voltage,
                "current": current
            }
            )
            rfpm1_output_power = self.rfpm1_output.get_power_measurement()

            output_loss = self.config.get_output_loss_by_switchpath_and_freq(switchpath=switchpath, freq=frequency)
            rfpm1_bucket.append(
                {
                    "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
                    "rfpm1_output_power_uncalibrated": rfpm1_output_power,
                    "rfpm1_output_loss_@_freq": output_loss,
                    "waveform":waveform,
                    "gain_setting":high_gain_setting,
                    "datetime_string":date_string,
                    "temp_probe1_value": probe_temp_value,
                    "temp_probe2_value": probe_temp_value2,
                    "voltage": voltage,
                    "current": current
                }
            )
            self.clean_up_measurement()


        return standard_bucket, harmonic_bucket, rfpm1_bucket

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

class NetworkAnalyzerModuleTest(NetworkAnalyzerTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        super().__init__(na, psu, daq, temp_probe, temp_probe2, sno, switch_bank, config)
        self.name = "Network Analyzer Standard Test"

    def set_up_measurement(self, switchpath, gain_setting, voltage=8.5, current=1.7, ratioed_power="S21"):
        print(switchpath)
        self.switch_bank.set_all_switches(self.config.paths[switchpath])

        self.psu.set_voltage(voltage)
        self.psu.set_current(current)
        self.psu.set_output_state(True)
        print("Setting up measurement")

        statefilepath = self.config.get_statefile_by_switchpath_and_ratioed_power(switchpath, ratioed_power)
        self.na.load_saved_cal_and_state(statefilepath)

        self.daq.enable_rf()
        self.daq.set_attenuation(gain_setting)
        print("Completed setting up measurement")
        time.sleep(5)

    def clean_up_measurement(self):
        self.switch_bank.reset_all_switches()
        self.daq.disable_rf()

    def get_31_steps_at_switchpath_and_ratioed_powers(self, switchpath, ratioed_power):
        print(switchpath)

        phase_bucket = []
        gain_bucket = []
        freqs = ''
        gain_setting = 0
        self.set_up_measurement(switchpath, gain_setting)
        for gain_setting in range(0, 32, 1):
            self.daq.set_attenuation(gain_setting)
            time.sleep(3)
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2 = self.get_temp_data()

            date_string = datetime.datetime.now()

            if ratioed_power == "S21":
                gain, freqs = self.na.calc_and_stream_trace(1, 1)
                phase, freqs = self.na.calc_and_stream_trace(1, 2)
            elif ratioed_power == "S22":
                gain, freqs = self.na.calc_and_stream_trace(1, 1)
                phase, freqs = self.na.calc_and_stream_trace(1, 2)
                print("S22 MEAUSR")
            elif ratioed_power == "S11":
                gain, freqs = self.na.calc_and_stream_trace(1, 1)
                phase, freqs = self.na.calc_and_stream_trace(1, 2)
                print("S11 MEAUSR")

            gain_bucket.append({
            "gain_setting":f"{gain_setting}",
            "freqs":freqs,
            "gain":gain,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
            }
            )
            phase_bucket.append({
            "gain_setting":f"{gain_setting}",
            "freqs":freqs,
            "phase":phase,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
            }
            )      

        self.clean_up_measurement()


        return gain_bucket, phase_bucket


    def get_31_steps_at_switchpath(self, switchpath):
        print(switchpath)

        phase_bucket = []
        gain_bucket = []
        freqs = ''
        gain_setting = 0
        self.set_up_measurement(switchpath, gain_setting)
        for gain_setting in range(0, 32, 1):
            self.daq.set_attenuation(gain_setting)
            time.sleep(3)
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2, temp_plate_value = self.get_temp_data()

            date_string = datetime.datetime.now()
            gain, freqs = self.na.calc_and_stream_trace(1, 1)
            phase, freqs = self.na.calc_and_stream_trace(1, 2)

            gain_bucket.append({
                "gain_setting":f"{gain_setting}",
                "freqs":freqs,
                "gain":gain,
                "datetime_string":date_string,
                "temp_probe1_value": probe_temp_value,
                "temp_probe2_value": probe_temp_value2,
                "voltage": voltage,
                "current": current
            }
            )
            phase_bucket.append({
                "gain_setting":f"{gain_setting}",
                "freqs":freqs,
                "phase":phase,
                "datetime_string":date_string,
                "temp_probe1_value": probe_temp_value,
                "temp_probe2_value": probe_temp_value2,
                "voltage": voltage,
                "current": current
            }
            )            

        self.clean_up_measurement()


        return gain_bucket, phase_bucket
    
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

class OSCARPNAXTest:
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        if isinstance(na, PNAXNetworkAnalyzer):
            self.na = na
        else:
            raise TypeError()
        
        # if isinstance(psu, PowerSupply):
        #     self.psu = psu
        # else:
        #     raise TypeError()
        
        # if isinstance(temp_probe, Agilent34401A):
        #     self.temp_probe = temp_probe
        # else:
        #     raise TypeError
        
        # if isinstance(temp_probe2, Agilent34401A):
        #     self.temp_probe2 = temp_probe2
        # else:
        #     raise TypeError
        
        # if isinstance(temp_controller, TempController):
        #     self.temp_controller = temp_controller
        # else:
        #     raise TypeError
        
        # if isinstance(switch_bank, ZtmModular):
        #     self.switch_bank = switch_bank
        # else:
        #     raise TypeError
        
        # if isinstance(config, ):
        #     self.config = config
        # else:
        #     raise TypeError
        
        self.sno = sno
        self.name = ""

    def run_psat_and_p1_tests_v1(self):
        # Start and Stop source power 
        # Need to add the ability to change the source power calibration depending on the network analyzer attenuator click
        source_max = -20 
        source_start = -45

        # Integer associated with the source power at which the psat is detected
        source_psat_start = 0

        # Linear bucket to for data visualization
        linear_gain_bucket = []

        # Psat bucket to for data visualization on the way to psat
        psat_gain_bucket = []

        # Psat bucket to for data visualization at psat (MEaning all values are -1 below this point)
        psat = {}

        # Start of comparison for linear range for first comparison
        self.na.set_amplitude(1, source_start)
        time.sleep(3)
        gain, freqs = self.na.calc_and_stream_trace(1, 1)
        linear_gain_bucket.append(gain)

        # Start of comparison for linear range for comparison
        for index, source_db in enumerate(range(source_start, source_max, 1)):
            self.na.set_amplitude(1, source_db)
            time.sleep(3)
            gain, freqs = self.na.calc_and_stream_trace(1, 1)
            linear_gain_bucket.append(gain)

            diff = self.compare_traces_diff_avg(linear_gain_bucket[index - 1], gain) 

            # If the difference is less than .75 then we have reached the psat start because we are increasing by 1 
            # and if the difference is less that one then the dut is compressing
            # meaning however much we increase the source power the dut will not increase in power
            if diff < .75:
            # Assign the source_psat_start to the source_db value for the smaller step size starting at the last value of the linear range
                source_psat_start = source_db
                break

        # Start of comparison for psat range for comparison
        gain_bucket_before_p1 = linear_gain_bucket[-1]
        # Running number for the source power incrementing by .1 dBm
        source_db = source_psat_start

        # While loop to find the psat +.1 dBm increment value
        while source_psat_start <= source_max:
            source_db += .1
            self.na.set_amplitude(1, source_db)
            time.sleep(3)
            gain, freqs = self.na.calc_and_stream_trace(1, 1)
            psat_gain_bucket.append(gain)

            diff = self.compare_traces_diff_avg(gain_bucket_before_p1, gain) 

            if diff <= -1: 
                # Assign Psat gain values to range of values before the psat
                psat[source_db] = gain
                break 

        return linear_gain_bucket, psat_gain_bucket, psat

    def get_values_diff_index_by_target(self, trace1, trace2, target):
        diff_bucket = {}
        for index, trace1_gain in enumerate(trace1):
            trace2_gain = trace2[index]
            diff = trace1_gain - trace2_gain
            if diff >= target:
                diff_bucket[index] = trace2

        return diff_bucket
    
    def compare_traces_diff_avg(self, trace1, trace2):
        diff_bucket = []
        for index, trace1_gain in enumerate(trace1):
            trace2_gain = trace2[index]
            diff = trace1_gain - trace2_gain
            diff_bucket.append(diff)

        avg_diff = sum(diff_bucket) / len(diff_bucket) 

        return avg_diff
    
    def run_psat_and_p1_tests_v2(self):
        # Start and Stop source power 
        # Need to add the ability to change the source power calibration depending on the network analyzer attenuator click
        linear_source_start = -45
        linear_source_end = -40

        saturation_source_start = -40
        saturation_source_end = -19

        # Linear bucket to for data visualization
        
        saturation_gain_bucket = []

        # Psat bucket to for data visualization at psat (MEaning all values are -1 below this point)
        psat = {}

        _, freqs = self.na.calc_and_stream_trace(1, 1)
        headers = ["source_db"] + freqs
 
        linear_gain_bucket = []
        linear_gain_bucket.append(headers)

        # Start of comparison for linear range for comparison
        for index, source_db in enumerate(range(linear_source_start, linear_source_end, 1)):
            self.na.set_amplitude(1, source_db)
            time.sleep(1)
            gain, freqs = self.na.calc_and_stream_trace(1, 1)
            linear_gain_bucket.append([source_db] + gain)
            print(f"DONE WITH {source_db}")

        running_db = saturation_source_start
        while running_db < saturation_source_end:
            self.na.set_amplitude(1, running_db)
            time.sleep(1)
            gain, freqs = self.na.calc_and_stream_trace(1, 1)
            saturation_gain_bucket.append([running_db] + gain)
            running_db += .1
            print(f"DONE WITH {running_db}")

        # # Start of comparison for psat range for comparison
        # gain_bucket_before_p1 = linear_gain_bucket[-1]
        # # Running number for the source power incrementing by .1 dBm
        # source_db = source_psat_start

        # # While loop to find the psat +.1 dBm increment value
        # while source_psat_start <= source_max:
        #     source_db += .1
        #     self.na.set_amplitude(1, source_db)
        #     time.sleep(3)
        #     gain, freqs = self.na.calc_and_stream_trace(1, 1)
        #     psat_gain_bucket.append(gain)

        #     diff = self.compare_traces_diff_avg(gain_bucket_before_p1, gain) 

        #     if diff <= -1: 
        #         # Assign Psat gain values to range of values before the psat
        #         psat[source_db] = gain
        #         break 

        return linear_gain_bucket, saturation_gain_bucket

    
if __name__ == "__main__":
    na = PNAXNetworkAnalyzer("TCPIP0::K-Instr0000.local::hislip0::INSTR")
    import csv

    switch_bank = ZtmModular()
    switch_bank.init_resource()
    test = OSCARPNAXTest(na=na)
    linear_gain_bucket, sat_gain_bucket = test.run_psat_and_p1_tests_v2()

    base = os.getcwd()
    filepath = os.path.join(base, "psat_3_data.csv")

    num_of_points = len(linear_gain_bucket[0]) - 1
    freqs = linear_gain_bucket[0].pop(0)
    sum_buck = []
    for i in range(0, num_of_points):
        sum_buck.append(0)

    for index, linear_gain in enumerate(linear_gain_bucket):
        if index == 0:
            continue 
        else:
            for index, gain_value in enumerate(linear_gain):
                sum_buck[index] += gain_value

    avg_linear_line = []
    for index, sum in enumerate(sum_buck):
        avg = sum / num_of_points
        avg_linear_line.append(avg)

    print("AVERAGE LIN LINE")
    p1_data = {}

    for freq in linear_gain_bucket[0]:
        p1_data[freq] = 0

    for gain_saturated in sat_gain_bucket:
        for index, gain_value in enumerate(gain_saturated):
            if index == 0:
                continue
            else:
                if gain_value - avg_linear_line[index] < -1:
                    p1_data[freqs[index]] = gain_saturated[0]


    with open(filepath, mode="a", newline="") as f:
        writer = csv.writer(f)
        for frequency, source_db in p1_data.items():
            writer.writerow([frequency, source_db])

        f.close()