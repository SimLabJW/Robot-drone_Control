from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite
import argparse
# import asyncio

#file from
from RemoteControl.RemoteManager import RemoteManager
from LogControl.LogManager import LogManager

# device from
from Robomaster.Robomaster import Robomaster
            
def select_mode(mode, device, device_info):
    if mode == "log":
            print("Log Control Mode")
            # asyncio.run(LogManager().main(device))
            log = LogManager(device)
            
    elif mode == "remote":
        print("Remote Control Mode")   
        # asyncio.run(RemoteManager().main(device))
        remote = RemoteManager(device, device_info)
            

def device_confirm(mode, device):

    try:
    
        if device == "Robomaster":
            if mode == "remote":
                print(f"Select {device}")
                device_instance = Robomaster()
                return device_instance
            else:
                return None

        elif device == "TelloDrone":
            print(f"Select {device}") 

        elif device == "Mirobot":
            print(f"Select {device}")

    except:
        print(f"Don't have {device}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Control")
    parser.add_argument("mode", choices=["log", "remote"])    
    parser.add_argument("device", choices=['Robomaster', 'TelloDrone', 'Mirobot'])   
    
    args = parser.parse_args()
    
    print(f"{args.mode}")
    print(f"{args.device}")

    print("Select Simulation Code 'Log Simulation' or 'Remote Control' \n \
          'python filename log or remote'")
    
    mode = args.mode
    device = args.device

    device_info = device_confirm(mode, device)
    select_mode(mode, device, device_info)