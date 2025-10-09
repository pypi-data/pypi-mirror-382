from tracker import track_ip
import time
import os
import sys

Wh = '\033[1;37m'
Gr = '\033[1;32m'
Re = '\033[1;31m'

def clear():
    """Limpia la pantalla del terminal"""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def show_banner():
    """Muestra el banner de la herramienta"""
    clear()
    time.sleep(1)
    print(f"""{Wh}
           ______ ____                     __            
          /  _/ / / /   ____  _________ _/ /_____  _____
          / // /_/ / /  / __ \\/ ___/ __ `/ __/ __ \\/ ___/
        _/ // __  / /___/ /_/ / /__/ /_/ / /_/ /_/ / /    
       /___/_/ /_/_____/\\____/\\___/\\__,_/\\__/\\____/_/     

          {Wh}[ + ]  {Gr}MODIFIED BY JMEIRACORBAL{Wh}  [ + ]
          {Wh}[ + ]  {Gr}ORIGINAL BY HUNXBYTS{Wh}      [ + ]
    """)
    time.sleep(0.5)

def main():
    while True:
        show_banner()
        
        try:
            track_ip()
            
            print(f'\n{Wh}[ {Gr}1 {Wh}] {Gr} Lookup another IP')
            print(f'{Wh}[ {Gr}0 {Wh}] {Gr} Exit')
            
            choice = input(f'\n{Wh}[ + ] {Gr} Select Option : {Wh}')
            
            if choice == '0':
                print(f'\n{Wh}[ {Re}! {Wh}] {Re}Exit')
                time.sleep(1)
                sys.exit(0)
            elif choice != '1':
                print(f'\n{Wh}[ {Re}! {Wh}] {Re}Invalid option, returning to lookup...')
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f'\n{Wh}[ {Re}! {Wh}] {Re}Exit')
            time.sleep(2)
            sys.exit(0)
        except Exception as e:
            print(f'\n{Wh}[ {Re}! {Wh}] {Re}Error: {e}')
            time.sleep(2)
            choice = input(f'\n{Wh}[ + ] {Gr} Try again? (y/N): {Wh}')
            if choice.lower() != 'y':
                sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n{Wh}[ {Re}! {Wh}] {Re}Exit')
        time.sleep(2)
        sys.exit(0)
