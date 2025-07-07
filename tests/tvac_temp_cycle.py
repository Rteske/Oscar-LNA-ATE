import pyvisa
from tests.temp_cycle_test import PmTest
from instruments.daq import RS422_DAQ
from instruments.power_meter import E4418BPowerMeter
from instruments.power_supply import PowerSupply
from instruments.signal_generator import SynthesizedCWGenerator
from instruments.temp_probe import DracalTempProbe, Agilent34401A
from instruments.temp_controller import TempController
from configs.calibration import Calibration
import time

class TempCycle:
    def __init__(self, cal, temp_profile={}, sim=True) -> None:
        self.instruments_connection = {"rfpm1": True, "rfpm2": True, "rfpm3": True, "rfsg": True, "temp_probe": True, "daq": True, "temp_controller": True}
        if not sim:
            self.rm = pyvisa.ResourceManager()
            self.instruments = self.rm.list_resources()
            print(self.instruments)
            self.running_state = False
            self.state = False
            rfpm1_cal_factor_table = {
                3e+9: 99.3,
                1.25e+10: 97.25,
                2.8e+10: 94.83
            }

            rfpm2_cal_factor_table = {
                3e+9: 99.4,
                1.25e+10: 97.4,
                2.8e+10: 97
            }

            rfpm3_cal_factor_table = {
                3e+9: 99.4,
                1.25e+10: 97.25,
                2.8e+10: 94.13
            }
            
            try:
                self.rfpm1 = E4418BPowerMeter("GPIB0::15::INSTR", name="rfpm1")
                self.rfpm1.freqs_to_factors = rfpm1_cal_factor_table
            except:
                self.instruments_connection["rfpm1"] = False

            try:
                self.rfpm2 = E4418BPowerMeter("GPIB0::14::INSTR", name="rfpm2")
                self.rfpm2.freqs_to_factors = rfpm2_cal_factor_table
            except: 
                self.instruments_connection["rfpm2"] = False

            try:
                self.rfpm3 = E4418BPowerMeter("GPIB0::13::INSTR", name="rfpm3")
                self.rfpm3.freqs_to_factors = rfpm3_cal_factor_table
            except:
                self.instruments_connection["rfpm3"] = False

            try:
                self.rfsg = SynthesizedCWGenerator("GPIB0::19::INSTR")
            except:
                self.instruments_connection["rfsg"] = False

            try:
                # self.temp_probe = DracalTempProbe("E25098")
                self.temp_probe = Agilent34401A("GPIB0::22::INSTR")
            except:
                print("Failed to connect to temp probe")
                self.instruments_connection["temp_probe"] = False

            try:
                self.temp_probe2 = Agilent34401A("GPIB0::2::INSTR")
            except:
                print("Failed to connect to temp probe 2")
                self.instruments_connection["temp_probe2"] = False

            try:
                self.power_supply = PowerSupply(visa_address="GPIB0::5::INSTR")
                self.power_supply.set_voltage(28)
                self.power_supply.set_current(2)
                self.power_supply.set_output_state(True)
                self.power_supply.set_overcurrent_protection(True)
                time.sleep(2.5)
            except:
                self.instruments_connection["power_supply"] = False

            try:
                self.daq = RS422_DAQ()
            except:
                print("Failed to connect to daq")
                self.instruments_connection["daq"] = False

            try:
                self.temp_controller = TempController()
            except:
                print("Failed to connect to temp controller")
                self.instruments_connection["temp_controller"] = False



            self.test = PmTest(rfpm1=self.rfpm1, rfpm2=self.rfpm2, rfpm3=self.rfpm3, rfsg=self.rfsg, temp_probe=self.temp_probe, temp_probe2=self.temp_probe2, daq=self.daq, psu=self.power_supply, temp_controller=self.temp_controller, cal=cal)

            self.frequencies = {"L": 3e+9, "M": 1.25e+10,"H": 2.8e+10}

            self.gain_setting = 41

            self.cal = cal

    def set_temp_profile(self, temp_profile):
        self.temp_profile = temp_profile
    
    def determine_frequency(self, jack):
        jack = jack.lower()
        if jack == 'j3_j4' or jack == 'j9_j10':
            return self.frequencies["L"]
        elif jack == 'j5_j6'or jack == 'j11_j12':
            return self.frequencies["M"]
        elif jack == 'j7_j8' or jack == 'j13_j14':
            return self.frequencies["H"]
        else:
            raise ValueError()

    def run_tests(self):
        print("Running tests")
        for step in self.temp_profile:
            self.t_end_current_profile = time.time() + (step["dwell_time"] * 60)
            set_temp_already = False
            while time.time() < self.t_end_current_profile:
                self.test.running_temp = step["temperature"] + step["temp_controller_offset"]

                for band, frequency in self.frequencies.items():
                    print(f"STARTING TEST for band: {band} at frequency: {frequency} with temperature: {step['temperature']}")
                    self.test.set_up_measurement(frequency=frequency, temperature=step["temperature"], bandpath=band, gain_setting=self.gain_setting, voltage=step["voltage"])
                    self.test.measure_and_record(step["time_per_band"], temp_target=step["temperature"], temp_delta=3, frequency=frequency, voltage=step["voltage"])        

    def get_input_loss(self, jack):
        frequency = self.determine_frequency(jack)
        # Calibration Stage Making sure -10 is going into the unit
        input_power = self.test.input_power_validation(frequency=frequency, target_power=0, start_power=-25) 

        self.rfpm1.set_frequency(frequency)
        self.rfpm2.set_frequency(frequency)

        horizontal = self.rfpm1.get_power_measurement()
        vertical = self.rfpm2.get_power_measurement()

        return input_power - horizontal, input_power - vertical
    
    def get_output_loss(self, jack):
        frequency = self.determine_frequency(jack)
        # Calibration Stage Making sure -10 is going into the unit

        output_power = self.test.input_power_validation(frequency=frequency, target_power=0, start_power=-25)

        self.rfpm1.set_frequency(frequency)
        self.rfpm2.set_frequency(frequency)

        input_loss_horizontal, input_loss_vertical = self.cal.get_input_loss_at_frequency(frequency)

        horizontal = self.rfpm1.get_power_measurement()
        vertical = self.rfpm2.get_power_measurement()

        return horizontal - float(input_loss_horizontal), vertical - float(input_loss_vertical)
    


