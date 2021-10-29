# cr0m

import board
import touchio
import time
import busio
import displayio

from adafruit_display_text.label import Label
from adafruit_display_text import label
import terminalio

# For wifi
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import adafruit_sht31d

import board
from rainbowio import colorwheel

# SHT-30 Mesh-protected Weather-proof Temperature/Humidity Sensor
# https://www.adafruit.com/product/4099
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

## Important Things

# Influx location and database
POST_URL = "http://192.168.9.15:8086/write?db=TempHumid"

# Humidity Colors
humidColor1 = 0x3d5aff
humidColor2 = 0x82B673
humidColor3 = 0xF5ED73


# Slider bar indicator thingie
def sliderBar(percentage):
    if percentage == 100:
        print("100")
        text_area_line2.text="--------"
        text_area_line2.color = 0xffffff
    elif percentage == 75:
        print("75")
        text_area_line2.text="------"
        text_area_line2.color = 0xffffff
    elif percentage == 50:
        print("50")
        text_area_line2.text="----"
        text_area_line2.color = 0xffffff        
    elif percentage == 25:
        print("25")
        text_area_line2.text="--"
        text_area_line2.color = 0xffffff        
    elif percentage > 0:
        print("0")
    return 

# GUI
def humidColor(humidity):
    if humidity >= 60:
        colorhumidity = humidColor1
    elif humidity >= 20:
        colorhumidity = humidColor2
    else:
        colorhumidity = humidColor3
    return colorhumidity
    
def tempColor(temp): 
    if temp >= 101: # lol
        # colortemp = 0xE33C1B
        colortemp = 0xE23C1B
    elif temp >= 100:
        # colortemp = 0xF2C23B
        colortemp = 0xEC882B
    elif temp >= 80:
        # colortemp = 0xFDFB4C
        colortemp = 0xE9882C
    elif temp >= 70:
        # colortemp = 0x58AB5A
        colortemp = 0xFEFD4C
    elif temp >= 65:
        # colortemp = 0x5CAEDF
        colortemp = 0xBBE767
    elif temp >= 50:
        # colortemp = 0x3870BC
        colortemp = 0x82D1AD
    elif temp >= 0:
        # colortemp = 0x673A9C
        colortemp = 0x62BAF9
    else:
        colortemp = 333
    return colortemp
    
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240

TEMPTEXT=0
HUMIDTEXT=0

text_area_title = label.Label(terminalio.FONT, text="Outside")
text_area_title.scale  = 5
# text_area_title.color = 0x7CFC00
text_area_title.anchor_point = (0.0, 0.0)
text_area_title.anchored_position = (20, -5)

text_area_line = label.Label(terminalio.FONT, text="--------")
text_area_line.scale  = 5
text_area_line.color = 0x585858
text_area_line.anchor_point = (0.0, 0.0)
text_area_line.anchored_position = (0, 30)

# "Status bar"
text_area_line2 = label.Label(terminalio.FONT, text="--------")
text_area_line2.scale  = 5
text_area_line2.color = 0x585858
text_area_line2.anchor_point = (0.0, 0.0)
text_area_line2.anchored_position = (0, 30)

text_area_status = label.Label(terminalio.FONT, text="DEBUG TEXT")
text_area_status.scale  = 2
text_area_status.color = 0x32CD32
text_area_status.anchor_point = (1.0, 0.0)
text_area_status.anchored_position = (DISPLAY_WIDTH, 70)

# Temp TEXT
text_area_temptext = label.Label(terminalio.FONT, text=str(TEMPTEXT))
text_area_temptext.scale = 6
text_area_temptext.anchor_point = (1.0, 0.5)
text_area_temptext.anchored_position = (DISPLAY_WIDTH-45, DISPLAY_HEIGHT / 2)

text_area_degree = label.Label(terminalio.FONT, text="o")
text_area_degree.scale=3
text_area_degree.anchor_point = (0.0, 1.0)
text_area_degree.anchored_position = (DISPLAY_WIDTH-43, DISPLAY_HEIGHT / 2 + 10)

text_area_f = label.Label(terminalio.FONT, text="F")
text_area_f.scale=4
text_area_f.anchor_point = (0.0, 1.0)
text_area_f.anchored_position = (DISPLAY_WIDTH-25, DISPLAY_HEIGHT / 2 + 35)

# Humidity TEXT
text_area_humidtext = label.Label(terminalio.FONT, text=str(HUMIDTEXT))
text_area_humidtext.scale = 6
text_area_humidtext.anchor_point = (1.0, 1.0)
text_area_humidtext.anchored_position = (DISPLAY_WIDTH-1, DISPLAY_HEIGHT)

text_area_hperc = label.Label(terminalio.FONT, text="%")
text_area_hperc.scale=4
text_area_hperc.anchor_point = (0.0, 1.0)
text_area_hperc.anchored_position = (DISPLAY_WIDTH-30, 225)

text_group = displayio.Group()
text_group.append(text_area_title)
text_group.append(text_area_line)
text_group.append(text_area_line2)
text_group.append(text_area_status)
text_group.append(text_area_temptext)
text_group.append(text_area_degree)
text_group.append(text_area_f)
text_group.append(text_area_humidtext)
text_group.append(text_area_hperc)
board.DISPLAY.show(text_group)
# END GUI

button_down = board.BUTTON_DOWN
button_up = board.BUTTON_UP
button_select = board.BUTTON_SELECT

# ?pir = board.PIR_SENSE
touch_crowleft6 = board.CAP6
touch_crow_top_left7 = board.CAP7
touch_crow_top_right8 = board.CAP8

touch_pad9 = board.CAP9
touch_pad10 = board.CAP10
touch_pad11 = board.CAP11
touch_pad12 = board.CAP12
touch_pad13 = board.CAP13

LED_BRIGHTNESS=0

# Wifi Connection
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("y u no secrets.py?!")
    raise
print("ESP32-S2 WebClient Test")
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print(
        "\t%s\t\tRSSI: %d\tChannel: %d"
        % (str(network.ssid, "utf-8"), network.rssi, network.channel)
    )
wifi.radio.stop_scanning_networks()

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)
ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4) * 1000))

# Side buttons
button_down_touched = touchio.TouchIn(button_down)
button_up_touched = touchio.TouchIn(button_up)
button_select_touched = touchio.TouchIn(button_select)

# Left and Top Touch Pads
touch6 = touchio.TouchIn(touch_crowleft6)
touch7 = touchio.TouchIn(touch_crow_top_left7)
touch8 = touchio.TouchIn(touch_crow_top_right8)

# Side Slider Pads Top Down (9=Top)
touch9 = touchio.TouchIn(touch_pad9)
touch10 = touchio.TouchIn(touch_pad10)
touch11 = touchio.TouchIn(touch_pad11)
touch12 = touchio.TouchIn(touch_pad12)
touch13 = touchio.TouchIn(touch_pad13)

current_state=0
def checkNumber(previousNum, currentNum):
    previousNumber = current_state
    # Debug
    # print("Previous Number: "+str(previousNum))
    # print("Current Number: "+str(currentNum))
    if previousNum > currentNum: # Lowered
        return True
    elif previousNum < currentNum: # Raised
        return True
    else:
        # nothing=0
        return False

def screenBrightness(percentage):
    # for board.DISPLAY.brightness
    if percentage == 100:
        print("100")
        board.DISPLAY.brightness = 1
    elif percentage == 75:
        print("75")
        board.DISPLAY.brightness = .75
    elif percentage == 50:
        print("50")
        board.DISPLAY.brightness = .50
    elif percentage == 25:
        print("25")
        board.DISPLAY.brightness = .25
    elif percentage == 0:
        print("0")
        board.DISPLAY.brightness = .05
    return 

cnt1=60
def logData():
    global cnt1
    cnt1 = cnt1 - 1
    text_area_status.text="Posting NOW: " + str(cnt1)

    tempF = sensor.temperature * 9 / 5 + 32
    tempFRound = round(tempF,2)
    tempFF = str(tempFRound)
    data  = "temperature,host=FunHouse-SHT31D,room=outside value=%s"%tempFRound
    data2  = "humidity,host=FunHouse-SHT31D,room=outside value=%s"%sensor.relative_humidity
    request = requests.post(POST_URL, data=data)
    request2 = requests.post(POST_URL, data=data2)

    print('Logging Humidity: {0}%'.format(round(sensor.relative_humidity,2)))
    print('Logging Temperature: {0}F'.format(tempFRound))
    text_area_title.color = humidColor(int(round(sensor.relative_humidity,2)))

def updateScreen():
    tempF = sensor.temperature * 9 / 5 + 32
    tempFRound = round(tempF,1)
    tempFF = str(tempFRound)
    text_area_temptext.text=str(tempFF)
    text_area_temptext.color = tempColor(tempFRound)
    text_area_degree.color = tempColor(tempFRound)
    text_area_f.color = tempColor(tempFRound)
    
    text_area_humidtext.text=str(round(sensor.relative_humidity,1))+" "
    text_area_humidtext.color = humidColor(int(round(sensor.relative_humidity,2)))
    text_area_hperc.color = humidColor(int(round(sensor.relative_humidity,2)))
    # text_area_title.color = humidColor(int(round(sensor.relative_humidity,2)))
    return

tcnt=60
while True:

    tcnt = tcnt - 1
    print(tcnt)
    text_area_status.text="" + str(tcnt) +" till post"
    
    if tcnt % 2 == 0:
        updateScreen()

    if tcnt == 0:
        logData()
        tcnt = 60

    if button_down_touched.value:
        if button_down_touched.value:
            print("1. Down Pressed")
            time.sleep(1.05)

# wtf is wrong here with this board
#     if button_up_touched.value:
#         time.sleep(0.05)
#         if button_up_touched.value:
#             print("Up Pressed")

    if button_select_touched.value:
        time.sleep(0.05)
        if button_select_touched.value:
            tempF = sensor.temperature * 9 / 5 + 32
            tempFRound = round(tempF,2)
            tempFF = str(tempFRound) + "F"
            data  = "temperature,host=FunHouse-SHT31D,room=roaming value=%s"%tempFRound
            data2  = "humidity,host=FunHouse-SHT31D,room=roaming value=%s"%sensor.relative_humidity
            request = requests.post(POST_URL, data=data)
            request2 = requests.post(POST_URL, data=data2)
            print("Select Pressed")
            print('Logging Humidity: {0}%'.format(round(sensor.relative_humidity,2)))
            # print('Temperature: {0}C'.format(sensor.temperature))
            print('Logging Temperature: {0}F'.format(tempFRound))

    if touch6.raw_value > 11452:
        print()
        print("Left Crow")
        print("Pressure: ", str(touch6.raw_value))
        print("\n" * 13)
    if touch7.raw_value > 12015:
        print()
        print("Top Left Crow")
        print("Preassure: ", str(touch7.raw_value))
        print("\n" * 13)
        logData()
        print(board.DISPLAY.brightness)
        if board.DISPLAY.brightness != 0:
            board.DISPLAY.brightness = board.DISPLAY.brightness - .25
        
    if touch8.raw_value > 12918:
        print("      ")
        print("Top Right Crow - Clear")
        print("pressure: ", str(touch8.raw_value))
        print("\n" * 13)
        print()
        print(board.DISPLAY.brightness)
        if board.DISPLAY.brightness < 1:
            board.DISPLAY.brightness = board.DISPLAY.brightness + .25

    if touch9.raw_value > 13071: # 12071 was avg lightest
        previous_state=current_state
        current_state=9
        checkIt = checkNumber(previous_state, current_state)
        # print(touch9.raw_value)
        if checkIt:
            text_area_status.text="Slide: 100%"
            sliderBar(100)
            screenBrightness(100)
            print()
            print("+" * 36)
            print("+" * 36)
            print("+" * 36)
            print()
            print()
            print("    ____   _______  _______ %")
            print("   |    | |  _    ||  _    | ")
            print("    |   | | | |   || | |   | ")
            print("    |   | | | |   || | |   | ")
            print("    |   | | |_|   || |_|   | ")
            print("    |   | |       ||       | ")
            print("    |___| |_______||_______| ")
            print("\n" * 3)

    # if touch10.raw_value > 12086: # lightest
    if touch10.raw_value > 14086:
        previous_state=current_state
        current_state=10
        checkIt = checkNumber(previous_state, current_state)
        # print(touch10.raw_value)
        if checkIt:
            text_area_status.text="Slide: 75%"
            sliderBar(75)
            screenBrightness(75)
            print()
            print()
            print(" ")
            print("++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++")
            print("+++++++++++_______  ________++++++++")
            print("          |       ||       |  ")
            print("          |___    ||   ____|        ")
            print("              |   ||  |____         ")
            print("              |   ||_____  |        ")
            print("              |   | _____| |        ")
            print("              |___||_______|        ")
            print(" ")
            print(" ")
            print(" ")
            print(" ")

    # if touch11.raw_value > 12104: #lightest
    if touch11.raw_value > 14104:
        previous_state=current_state
        current_state=11
        checkIt = checkNumber(previous_state, current_state)
        # print(touch11.raw_value)
        if checkIt:
            text_area_status.text="Slide: 50%"
            sliderBar(50)
            screenBrightness(50)
            print()
            print(" ")
            print(" ")
            print(" ")
            print(" ")
            print(" ")
            print("           _______  _______ %       ")
            print("          |       ||  _    |        ")
            print("++++++++++|   ____|| | |   |++++++++")
            print("++++++++++|  |____ | | |   |++++++++")
            print("++++++++++|_____  || |_|   |++++++++")
            print("           _____| ||       |       ")
            print("          |_______||_______|        ")
            print(" ")
            print(" ")
            print(" ")
            print(" ")

    # if touch12.raw_value > 12083: # lighest
    if touch12.raw_value > 14083:
        previous_state=current_state
        current_state=12
        checkIt = checkNumber(previous_state, current_state)
        # print(touch12.raw_value)
        if checkIt:
            text_area_status.text="Slide: 25%"
            sliderBar(25)
            screenBrightness(25)
            print()
            print(" ")
            print(" ")
            print(" ")
            print(" ")
            print("           _______  _______ %       ")
            print("          |       ||       |        ")
            print("          |____   ||   ____|        ")
            print("           ____|  ||  |____         ")
            print("          | ______||_____  |  ")
            print("++++++++++| |_____++_____| |++++++++")
            print("++++++++++|_______||_______|++++++++")
            print("++++++++++++++++++++++++++++++++++++")
            print(" ")
            print(" ")
            print(" ")

    if touch13.raw_value > 14042:
        previous_state=current_state
        current_state=13
        checkIt = checkNumber(previous_state, current_state)
        if checkIt:
            text_area_status.text="Slide: 0%"
            sliderBar(0)
            screenBrightness(0)
            print()
            print(" ")
            print(" ")
            print(" ")
            print(" ")
            print("                    _______ %  ")
            print("                   |  _    |   ")
            print("                   | | |   |   ")
            print("                   | | |   |   ")
            print("                   | |_|   |   ")
            print("                   |       |    ")
            print("                   |_______|    ")
            print(" ")
            print("++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++++++")

    # time.sleep(.09)
    # logData()
    time.sleep(.6)
    # time.sleep(60)
