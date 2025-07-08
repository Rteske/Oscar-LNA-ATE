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

    # start = 1900
    # stop = 4000
    # ss = 200
    # output_power = 15

    # freqs = list(range(2000, 4200, 200))
    # freqs = [1900] + freqs

    start = 18000
    stop = 31000
    ss = 1000
    output_power = 6

    freqs = list(range(start, stop + ss, ss))

    noise_figrue.set_up(start, stop, ss, output_power)

    noise_figrue._res.write("M2 EN")

        
    noise_figures = noise_figrue.set_and_measure(freqs)
    print(noise_figures)

    filename = f"noise_figures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['datetime', 'frequency', 'noise_figure'])
        for freq, nf in noise_figures:
            writer.writerow([datetime.now().isoformat(), freq, nf])
    print(f"Noise figures saved to {filename}")

    for k, i in enumerate(noise_figures):
        print("FREQ:", i[0], " NOISE FIG:", i[1]) 
    
    # rm = pyvisa.ResourceManager()
    # resources = rm.list_resources()
    # print(resources)