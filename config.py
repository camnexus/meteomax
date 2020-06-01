from machine import UART
import machine
import os

uart = UART(0, baudrate=115200)
os.dupterm(uart)


LORA_FREQUENCY = 916800000

# for Chile
#LORA_FREQUENCY = 902300000 original
LORA_GW_DR = "SF7BW125" # DR_3
LORA_NODE_DR = 3
