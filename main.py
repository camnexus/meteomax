'''
Camnexus
MeteoPlus
Temperatura Ambiental + Humedad Ambiental + PH
juan.ocampos@camnexus.co.uk
camnexus.co.uk.com 2019
SHT20 y Analog Sensor PH DFRobot
'''

import pycom
from machine import I2C, Pin, Timer
from network import WLAN
from ADS1115 import ADS1115
import ubinascii
import struct
from network import LoRa
import socket
import binascii
import config
import math
#from CayenneLPP import CayenneLPP
import cayenneLPP
import gc
import time
import array
import SI7006A20
from pysense import Pysense
from SI7006A20 import SI7006A20
# Use the built in LED as a status indicator
sck_pin = 'P10'
data_pin = 'P9'

status_led = Pin('G16', mode=Pin.OUT, value=1)
stat = 1
# Setup ADS1115 using defaults (0x70 address and 4.096V max range)
py = Pysense()
si = SI7006A20(py)
lora = LoRa(mode=LoRa.LORAWAN)
dev_addr = struct.unpack(">l", binascii.unhexlify('01d718dc'))[0]
nwk_swkey = binascii.unhexlify('b1f7ee78c46c0cac1faabeeb5d3bbc8e')
app_swkey = binascii.unhexlify('91c75e7e055fd203637e39b4b7824d73')

for channel in range(0, 72):
    lora.remove_channel(channel)

# set all channels to the same frequency (must be before sending the OTAA join request)
for channel in range(0, 8):
    #f = config.LORA_FREQUENCY  + channel * 200000
    #lora.add_channel(channel, frequency=f, dr_min=0, dr_max=4)
    lora.add_channel(channel, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=3)

lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
while not lora.has_joined():
    time.sleep(2.5)
#    print('Not yet joined...')
#print('Joined LoRa Network')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)

# make the socket blocking
s.setblocking(False)

#while True:
consumo = py.read_battery_voltage()
temperature_int = si.temperature()
i2c = I2C(1, I2C.MASTER)
adc = ADS1115(i2c)

lpp = cayenneLPP.CayenneLPP(size = 100, sock = s)
    #status_led.toggle()
#print("\nChannel 0 voltage: {}V".format(adc.get_voltage(0)))
#print("Channel 0 ADC value: {}\n".format(adc.read(0)))
ph=15.803-5.8754*(adc.get_voltage(0)-0.01028)
#print("Ph calculado: {}\n".format(ph))

_STATUS_LSBMASK     = 0b11111100

#SHT20 Temperature command (use no hold master only commands --> 0xF3 )
command = array.array('B', [0xF3])

i2c.writeto(0x40, command)
time.sleep(0.1)
vals = i2c.readfrom(0x40, 3)
(temphigh, templow, crc) = struct.unpack('BBB', vals)
temp = (temphigh << 8) | (templow & _STATUS_LSBMASK)
temperature = -46.85 + (175.72 * temp) / 2**16
#print('temperatura:')
#print(temperature)

#SHT20 Temperature command (use no hold master only commands --> 0xF3 )
command = array.array('B', [0xF5])
i2c.writeto(0x40, command)
time.sleep(0.1)
vals = i2c.readfrom(0x40, 3)
(humhigh, humlow, crc) = struct.unpack('BBB', vals)
humid = (humhigh << 8) | (humlow & _STATUS_LSBMASK)
humedad = -6 + (125 * humid) / 2**16
#print(humedad)
i2c.deinit()
#print('1')
lpp.add_relative_humidity(humedad,120)
#print('2')
lpp.add_temperature(temperature,114)
#print('3')
lpp.add_analog_input(ph,129)
#print('4')
#print('HumSoil:')
#print(humiditySoil)
lpp.add_temperature(temperature_int,113)
#print('temperatureSoil:')
#print(temperatureSoil)
lpp.add_analog_output(consumo,110)
lpp.send(reset_payload = True)

#print('inicio 5 segundos')
time.sleep(0.1)
#print('termino de 5 segundos')

py.setup_sleep(900)

py.go_to_sleep()
