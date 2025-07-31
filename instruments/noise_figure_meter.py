import pyvisa
import time
import csv
from datetime import datetime

import pyvisa.constants


class NoiseFigure8970B:
    def __init__(self, visa_address):
        self.rm = pyvisa.ResourceManager()
        self._res = self.rm.open_resource(visa_address)
        self._lib = self.rm.visalib
        self._res.timeout = 3000

    # def clear_status(self):
    #     print("SHIT")

    # def enable_status(self):
    #     # 48.0 enabling the noise figure meter to be controller
    #     self._res.write("SC")

    #     # PASS THROUGH OFF [DP]
    #     self._res.write("DP")

    #     self._res.write("CT")
    #     # ACTIVE CONTROL NEEDS ON [CT]
        

    #     # 42.3 MIN FREQUENCY 42.4 MAX FREQUENCY in detected 
    #     # Actual instrument measurement range set thru FA FB

    def set_up(self, start, stop, step, output_power):
        # ENABLE 1.1 MODE FOR HIGHER FREQS
        self._res.write("E1 EN")
        time.sleep(.2)

        # SET START [MN] AND STOP [MX]
        self._res.write(f"MN {start} EN")
        self._res.write(f"MX {stop} EN")
        time.sleep(.2)

        # SET 
        self._res.write(f"FA {start} EN")
        self._res.write(f"FB {stop} EN")
        time.sleep(.2)

        # SET STEPSIZE 
        self._res.write(f"SS {step} EN")
        time.sleep(.2)

        # SET INC [FN]
        self._res.write(f"FN {step} EN")
        time.sleep(.2)

        # SELECT ENR TABLE
        self._res.write("RC NR 1 EN NR")
        time.sleep(.2)

        self._res.write(f"PL {output_power} EN")

        # CAL
        # self._res.write(f"CA EN")
        # time.sleep(30)
        # CORRETED VALUE [M2]

        # self._res.write(f"M2 EN")
        # time.sleep(.2)

    def get_noise_power_on_and_off_at_frequencies(self, freqs):
        # H2 is the noise temperature and insertion gain

        bucket = []
        for freq in freqs:
            self._res.write(f"FR {freq} EN")
            self._res.write(f"T2 EN")
            time.sleep(2)

            source_off = self._res.query("N5 EN")
            source_off = source_off.strip().split(",")[2]
            time.sleep(.5)
            source_on = self._res.query("N6 EN")
            source_on = source_on.strip().split(",")[2]

            bucket.append({"freq": float(freq), "source_on_noise_power": float(source_on), "source_off_noise_power": float(source_off)})

        filename = f"noise_temp_insertion_gain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['datetime', 'frequency',  "source_on_noise_power", "source_off_noise_power"])
            writer.writeheader()
            for entry in bucket:
                writer.writerow({
                    'datetime': datetime.now().isoformat(),
                    'frequency': entry['freq'],
                    'source_on_noise_power': entry['source_on_noise_power'],
                    'source_off_noise_power': entry['source_off_noise_power']
                })
        print(f"Noise temperature and insertion gain saved to {filename}")
    
    def get_noise_temp_on_and_off_at_frequencies(self, freqs):
        # H2 is the noise temperature and insertion gain

        bucket = []
        for freq in freqs:
            self._res.write(f"FR {freq} EN")
            self._res.write(f"T2 EN")
            time.sleep(2)

            self._res.write("N5 EN")
            source_off = self._res.query("N4 EN")
            source_off = source_off.strip().split(",")[2]
            time.sleep(.5)
            self._res.write("N6 EN")
            source_on = self._res.query("N4 EN")
            source_on = source_on.strip().split(",")[2]

            bucket.append({"freq": float(freq), "source_on_noise_temp": float(source_on), "source_off_noise_temp": float(source_off)})

        filename = f"noise_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['datetime', 'frequency',"source_on_noise_temp", "source_off_noise_temp"])
            writer.writeheader()
            for entry in bucket:
                writer.writerow({
                    'datetime': datetime.now().isoformat(),
                    'frequency': entry['freq'],
                    'source_on_noise_temp': entry['source_on_noise_temp'],
                    'source_off_noise_temp': entry['source_off_noise_temp']
                })
        print(f"Noise temperature and insertion gain saved to {filename}")


    def deassert_ren(self):
        print(self._res.lock_state)

        self._lib.gpib_control_ren(self._res.session, pyvisa.constants.RENLineOperation.deassert)

    def set_and_measure(self, freqs):
        bucket = []
        for freq in freqs:
            self._res.write(f"FR {freq} EN")
            self._res.write(f"T2 EN")
            time.sleep(2)
            noise_figure = self._res.query("MEASUREMENT")
            time.sleep(2)
            bucket.append([freq, float(noise_figure)])
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.flush_transmit_buffer)
        

            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_read_buffer)
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_write_buffer)
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_transmit_buffer)
            
        
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_receive_buffer)
        return bucket
    
    # def get_noise_figure(self, freq):
    #     freq = int(freq / 1e6)
    #     self._res.write(f"FREQUENCY {freq} MHz")
    #     time.sleep(5)
    #     noise_figure = self._res.query("MEASUREMENT")
    #     noise_figure = float(noise_figure.strip())

    #     return noise_figure

    # def set_start_and_stop_freq_mghz(self, start_freq, stop_freq):
    #     start_freq = start_freq / 1e6
    #     stop_freq = stop_freq / 1e6

    #     self._res.write(f"START FREQ {start_freq} MHz")
    #     self._res.write(f"STOP FREQ {stop_freq} MHz")

if __name__ == "__main__":
    noise_figrue = NoiseFigure8970B(visa_address="GPIB0::8::INSTR")

    start = 2000
    stop = 4000
    ss = 200
    output_power = 15

    freqs = list(range(start, stop + ss, ss))
    freqs = [1900] + freqs

    # start = 18000
    # stop = 31000
    # ss = 1000
    # output_power = 6

    # freqs = list(range(start, stop + ss, ss))

    noise_figrue.set_up(1900, stop + ss, ss, output_power)

    # noise_figrue.get_noise_power_on_and_off_at_frequencies(freqs)

    noise_figrue.get_noise_temp_on_and_off_at_frequencies(freqs)

    # save to a csv the noise figures

    # noise_figures = noise_figrue.set_and_measure(freqs)
    # print(noise_figures)

    # filename = f"noise_figures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    # with open(filename, mode='w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(['datetime', 'frequency', 'noise_figure'])
    #     for freq, nf in noise_figures:
    #         writer.writerow([datetime.now().isoformat(), freq, nf])
    # print(f"Noise figures saved to {filename}")

    # for k, i in enumerate(noise_figures):
    #     print("FREQ:", i[0], " NOISE FIG:", i[1]) 
    
    # rm = pyvisa.ResourceManager()
    # resources = rm.list_resources()
    # print(resources)