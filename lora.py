#!/usr/bin/env /home/andrew/Documents/PROGRAMAS_USO_PROPIO/lora_payload_RAK11720_python/.venv/bin/python

import serial
import time
import os
import readline
import subprocess as sp

device = "USB1"
# pre_payload = "<TPK:A0B765AF40D2,80,AF:"
pre_payload = "<TPK:2A,AE:"
fin_payload = ">"

msg_inicial = "&93@"
msg_ack = "&81@"

def delay(ms): #delay en milisegundos
    time.sleep(ms/1000)


ser = serial.Serial(f'/dev/tty{device}', 115200)
delay(100)

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


def opcion_1():
    global ser
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

def opcion_2():
    global msg_inicial
    global msg_ack

    try:
        while True:
            try: 
                line_bytes = ser.readline()
                line_str = line_bytes.decode('utf-8').rstrip() # Decodifica en UTF-8
                # print(f"{line_str}")

                init_msg = line_str.find("&00")
                other_msg = line_str.find("TPK")

                if init_msg != -1:
                    print(f"{line_str}")
                    crc_num = modbuscrc(f"{msg_inicial}#")
                    crc_ascii = f"{crc_num:04X}"
        
                    print(f"CRC: {crc_ascii}")
        
                    #PAYLOAD PARA ENVIAR LORA
                    payload = f"{pre_payload}{msg_inicial}#{crc_ascii}{fin_payload}"
                    payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas
        
                    print(f"Enviando Payload: {payload}")
                    print(f"payload HEX: {payload_hex}")
                    print("...................................................................\r\n")
        
                    Psend(payload_hex) #Envio mensaje LoRa
                    init_msg = -1

                elif init_msg == -1 and other_msg != -1: 
                    print(f"{line_str}")
                    crc_num = modbuscrc(f"{msg_ack}#")
                    crc_ascii = f"{crc_num:04X}"
        
                    print(f"CRC: {crc_ascii}")
        
                    #PAYLOAD PARA ENVIAR LORA
                    payload = f"{pre_payload}{msg_ack}#{crc_ascii}{fin_payload}"
                    payload_hex = payload.encode('ascii').hex().upper() #codifica en ascii, convierte en hex y convierte todo a mayusculas
        
                    print(f"Enviando Payload: {payload}")
                    print(f"payload HEX: {payload_hex}")
                    print("...................................................................\r\n")
        
                    Psend(payload_hex) #Envio mensaje LoRa
                    other_msg = -1
                
                    

            except ValueError:
                continue

    except KeyboardInterrupt:
        print("Programa terminado por el usuario")


def menu():
    try:
        while True:
            print('''   
            -----------------
            Menu de opciones
            -----------------
            1) Modo Manual
            2) Modo ACK
    
            0) Quit
            ''')

            try:
                seleccion = int(input("Ingrese el numero del menu: "))
                if seleccion == 0:
                    print("Saliendo del programa")
                    print("____________________________________________________________\r\n")
                    exit()
                elif seleccion == 1:
                    sp.run(["clear"])
                    print("                     MODO MANUAL ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_1()
                elif seleccion == 2:
                    sp.run(["clear"])
                    print("                     MODO ACK ACTIVADO")
                    print("____________________________________________________________\r\n")
                    opcion_2()
              
                else:
                    print("Seleccione una opcion valida")
                    print("____________________________________________________________\r\n")

            except ValueError:
                print("Error reintente!")
    except KeyboardInterrupt:
        sp.run(["clear"])
        print("Programa interrupido por el usuario")


def main(): #Funcion principal
    

    sp.run(["clear"])
    menu()


########################################################################################################
#EJECUCION PRINCIPAL


if __name__ == "__main__":
    
    main()