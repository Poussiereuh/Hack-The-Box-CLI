import time
import requests
from bs4 import BeautifulSoup
from sty import fg, bg, ef, rs
from art import text2art
import threading
import sys
import json

header_test = {
    "Host": "www.hackthebox.eu",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.hackthebox.eu/home/shoutbox",
    "X-Requested-With": "XMLHttpRequest"
    }

url = "https://hackthebox.eu/api/shouts/get/initial/html/18"

TOKEN = ""

show_only_reset = True

reset_list = []

# Get the (current) number of lines in the terminal
import shutil
height = shutil.get_terminal_size().lines - 1
print(height)

stdout_write_bytes = sys.stdout.buffer.write

# Some ANSI/VT100 Terminal Control Escape Sequences
CSI = b'\x1b['
CLEAR = CSI + b'2J'
CLEAR_LINE = CSI + b'2K'
SAVE_CURSOR = CSI + b's'
UNSAVE_CURSOR = CSI + b'u'
BOTTOW = CSI + b'0B'
HOME = CSI + b'0;20f'

GOTO_INPUT = CSI + b'%d;0H' % (height + 1)

def emit(*args):
    stdout_write_bytes(b''.join(args))

def set_scroll(n):
    return CSI + b'0;%dr' % n



def shootbox_input():
    while 1:
        emit(SAVE_CURSOR, GOTO_INPUT, CLEAR_LINE)
        shootbox_input = input("\n$ ")
        emit(UNSAVE_CURSOR)
        if shootbox_input == "":
            pass
        else:
            print("command sent")

def colorize_message(last_comment): 
    last_comment_split = last_comment.split()

    last_comment_split[0] = fg.cyan + last_comment_split[0] + fg.rs
    last_comment_split[1] = fg.cyan + last_comment_split[1] + fg.rs
    last_comment_split[2] = fg.cyan + last_comment_split[2] + fg.rs
    last_comment_split[3] = fg(255, 102, 204) + last_comment_split[3] + fg.rs

    for pos, word in enumerate(last_comment_split):
        if word == "on":
            last_comment_split[pos+1] = fg(255, 153, 0) + ef.bold+ last_comment_split[pos+1] + rs.bold_dim+fg.rs
            last_comment_split[pos+2] = fg.blue + last_comment_split[pos+2] + fg.rs
        if word == "reset":
            reset_list.append(last_comment)
            last_comment_split[pos] = fg.red + ef.bold+ last_comment_split[pos].upper() +fg.rs + rs.bold_dim
        
        if word == "/cancel":
            #last_comment_split[pos-1] = fg.magenta + ef.bold+ last_comment_split[pos-1] + rs.bold_dim+fg.rs
            last_comment_split[pos] = fg.magenta + ef.bold + last_comment_split[pos] + rs.bold_dim + fg.rs
            last_comment_split[pos+1] = fg.magenta + ef.bold+ last_comment_split[pos+1] + rs.bold_dim + fg.rs

        if word == "canceled":
            last_comment_split[pos+2] = fg(255, 102, 204) +last_comment_split[pos+2]+ fg.rs
            last_comment_split[pos-2] = fg(255, 153, 0) + ef.bold +last_comment_split[pos-2]+ rs.bold_dim+fg.rs





    last_comment = " ".join(last_comment_split)
    
    
    # last_comment = last_comment.replace(" reset ", fg.red + ef.bold + " RESET " + rs.bold_dim+ fg.rs)


    return last_comment


def retrieve_messages():
    token = TOKEN
    print(fg(138,197,62)+ ef.bold+">> "+rs.bold_dim+ fg.rs+ "Type "+ fg.cyan+"/cancel xxxx "+fg.rs+ "or just "+fg.cyan+ "xxxx "+fg.rs+ fg(255, 153, 0)+"to cancel a reset."+fg.rs)
    print("")
    arguments = {"api_token":token}
    r = requests.Session()
    last_comment = ""
    can_display = False
    
    while 1:
        # print("check")
        can_display = False
        commentaires = r.post(url, headers=header_test, params=arguments).json()["html"]

        if last_comment == "":
            for commentaire in commentaires:
                soup = BeautifulSoup(commentaire, "lxml")
                last_comment = soup.text

                last_comment_format = colorize_message(last_comment)

                if show_only_reset and "reset" in last_comment:
                    emit(UNSAVE_CURSOR)
                    print(last_comment_format)
                    emit(SAVE_CURSOR, GOTO_INPUT, CLEAR_LINE)

                    
                elif not show_only_reset:

                    print(last_comment_format)

        else:
            for commentaire in commentaires:
                soup = BeautifulSoup(commentaire, "lxml")
                if soup.text == last_comment:
                    can_display = True
                elif can_display:
                    last_comment = soup.text

                    last_comment_format = colorize_message(last_comment)

                    #print(last_comment_format)

                    if show_only_reset and "reset" in last_comment:
                        emit(UNSAVE_CURSOR)
                        print(last_comment_format)
                        emit(SAVE_CURSOR, GOTO_INPUT, CLEAR_LINE)
                    elif not show_only_reset:
                        emit(SAVE_CURSOR, GOTO_INPUT, CLEAR_LINE)
                        emit(UNSAVE_CURSOR)
                        print(last_comment_format)
            
            


        
        time.sleep(5)


if __name__ == "__main__":
    emit(CLEAR, set_scroll(height))
    Art = text2art("HTB CLI", font="small")
    print(fg(138,197,62) +Art+ "by PeterPwn (https://www.hackthebox.eu/profile/194774).\n"+fg.rs)
    threading.Thread(target=retrieve_messages).start()
    try:
        shootbox_input()
    except KeyboardInterrupt:
        #Disable scrolling, but leave cursor below the input row
        emit(set_scroll(0), GOTO_INPUT, b'\n')
    #threading.Thread(target=shootbox_input).start()