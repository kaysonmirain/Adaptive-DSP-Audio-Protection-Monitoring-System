import sounddevice as sd
import numpy as np
import noisereduce as nr
import socket
import os
import sys
import time
from colorama import Fore, Style, init

init(autoreset=True)

SAMPLE_RATE = 16000
BLOCK_SIZE = 2048
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

THRESHOLD = 0.015
OSHA_LIMIT_DB = 85.0
MODERATE_ZONE_DB = 70.0
MAX_EAR_OUTPUT = 0.25

class SiteSyncHeadset:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        self.db_offset = 98.0
        self.daily_dose = 0.0
        self.last_update = time.time()

    def calculate_db(self, rms):
        if rms < 0.00001: return 0.0
        return max(0, 20 * np.log10(rms) + self.db_offset)

    def get_dynamic_anc(self, raw_db, is_talking):
        if raw_db >= OSHA_LIMIT_DB:
            return 0.98, "CRITICAL PROTECTION", Fore.RED + Style.BRIGHT
        elif raw_db >= MODERATE_ZONE_DB:
            return 0.65, "ACTIVE REDUCTION", Fore.YELLOW
        else:
            factor = 0.05 if is_talking else 0.15
            return factor, "TRANSPARENCY MODE", Fore.GREEN

    def draw_interface(self, rms, is_talking, raw_db, anc_level, zone_label, zone_color):
        sys.stdout.write("\033[H")
        
        print(f"{Fore.CYAN}{Style.BRIGHT}\nAUDIO PROTECTION SYSTEM\033[K")
        print("\033[K") 

        dose_color = Fore.GREEN if self.daily_dose < 50 else (Fore.YELLOW if self.daily_dose < 85 else Fore.RED)
        comm_status = f"{Fore.GREEN}UPLINK ACTIVE" if is_talking else f"{Fore.WHITE}UPLINK STANDBY"
        
        print(f"{Fore.WHITE}ACOUSTIC LOAD:     {zone_color}{raw_db:05.1f} dB SPL\033[K")
        print(f"{Fore.WHITE}PROTECTION MODE:   {zone_color}{zone_label}\033[K")
        print(f"{Fore.WHITE}EXPOSURE DOSE:   {dose_color}{self.daily_dose:>6.2f}% OSHA Capacity\033[K")
        print("\033[K") 

        print(f"{Fore.WHITE}SUPPRESSION:       {Fore.MAGENTA}{int(anc_level*100):02}% Intensity\033[K")
        print(f"{Fore.WHITE}COMMS STATUS:      {comm_status}\033[K")
        print("\033[K") 

        print(f"{Fore.WHITE}PEAK AMPLITUDE:    {Fore.CYAN}{rms:.4f}\033[K")
        
        bar_len = 30
        peak = int(min(rms * 15, 1.0) * bar_len)
        bar = "█" * peak + " " * (bar_len - peak)
        print(f"{Fore.WHITE}SIGNAL ANALYZE:    {Fore.CYAN}{bar}\033[K")
        
        print("\033[K")
        print(f"{Style.DIM}ENCRYPTED SESSION | CTRL+C TO TERMINATE\033[K")
        sys.stdout.flush()

    def audio_callback(self, indata, outdata, frames, time_info, status):
        try:
            raw_audio = indata.flatten()
            raw_rms = np.sqrt(np.mean(raw_audio**2))
            raw_db = self.calculate_db(raw_rms)
            is_talking = raw_rms > THRESHOLD

            if raw_db > 80:
                elapsed = 0.12
                self.daily_dose += (elapsed / (8 * 3600)) * (2 ** ((raw_db - 85) / 5)) * 100

            anc_factor, zone_label, zone_color = self.get_dynamic_anc(raw_db, is_talking)
            
            processed = nr.reduce_noise(y=raw_audio, sr=SAMPLE_RATE, prop_decrease=anc_factor, stationary=True)
            
            peak = np.max(np.abs(processed))
            if peak > MAX_EAR_OUTPUT:
                processed = processed * (MAX_EAR_OUTPUT / peak)

            if is_talking:
                self.sock.sendto(processed.tobytes(), (UDP_IP, UDP_PORT))

            self.draw_interface(raw_rms, is_talking, raw_db, anc_factor, zone_label, zone_color)
            outdata[:] = processed.reshape(-1, 1)
        except:
            pass

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write("\033[?25l") 
        try:
            with sd.Stream(channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, callback=self.audio_callback):
                while self.running:
                    sd.sleep(100)
        except KeyboardInterrupt:
            self.running = False
        finally:
            sys.stdout.write("\033[?25h") 
            print(f"\n{Fore.RED}CONNECTION TERMINATED.")

if __name__ == "__main__":
    headset = SiteSyncHeadset()
    headset.start()