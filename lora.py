#!/usr/bin/env .venv/bin/python

import serial
import time
import modbus_crc as modbus
import os

device = "USB1"
pre_payload = "<TPK:A0B765AF40D2,80,AF:"
fin_payload = ":100>"


def delay(ms): #delay en milisegundos
    time.sleep(ms/1000)

def Psend(command):
    Psend_AT = f"AT+PSEND={command}\r\n"
    
    ser.write(Psend_AT.encode())

    return True

def modbuscrc(msg: str) -> int:
    # Convertimos el string de texto plano a bytes reales (ej: "HOLA" -> b'HOLA')
    msg_bytes = msg.encode('ascii') 
    
    crc = 0xFFFF
    for byte in msg_bytes:
        # Ahora 'byte' es el valor numérico de la letra (ej: 'H' es 72)
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

########################################################################################################
#EJECUCION PRINCIPAL

ser = serial.Serial(f'/dev/tty{device}', 115200)
delay(100)

try:
    while True:
        comando = input("Ingrese el comando a enviar: ")
        os.system("clear")        

        crc_num = modbuscrc(f"{comando}#")
        crc_ascii = f"{crc_num:04X}"

        print(f"CRC: {crc_ascii}")

        #PAYLOAD PARA ENVIAR LORA
        payload = f"{pre_payload}{comando}#{crc_ascii}{fin_payload}"
        payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas

        print(f"payload: {payload}")
        print(f"payload HEX: {payload_hex}")

        Psend(payload_hex) #Envio mensaje LoRa

        #IMPRIME SERIAL
        line_bytes = ser.readline()
        line_str = line_bytes.decode('utf-8').rstrip() # Decodifica en UTF-8
        print(f"{line_str}")

except KeyboardInterrupt:
    print("Programa terminado por el usuario")
