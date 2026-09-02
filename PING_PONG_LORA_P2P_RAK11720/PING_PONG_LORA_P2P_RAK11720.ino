/****************************************************************************/
/***        Include files                                                 ***/
/****************************************************************************/
#include <stdio.h>
#include <string.h>
/****************************************************************************/
/***        Macro Definitions                                             ***/
/****************************************************************************/
    
#define CLS "\033[2J"
#define HOME "\033[H"
#define DISCONECT_TIMEOUT 2400000
#define LORA_FREQ 915000000



/****************************************************************************/
/***        Variables                                                     ***/
/****************************************************************************/

long startTime;
bool rx_done = false;
double myFreq = LORA_FREQ;
uint16_t sf = 12, bw = 0, cr = 0, preamble = 8, txPower = 22;

bool send_result;
uint8_t contador = 0;
/****************************************************************************/
/***        Local Functions                                               ***/
/****************************************************************************/
void recv_cb(rui_lora_p2p_recv_t data)
{
  Serial.println("__________________________________________________________________________________");
  rx_done = true;
  if (data.BufferSize == 0) {
      Serial.println("Empty buffer.");
      return;
  }
  // Variables de datos de llegada
  char receivedStream[data.BufferSize + 1];
  memcpy(receivedStream, data.Buffer, data.BufferSize);
  receivedStream[data.BufferSize] = '\0';

  char buff[92];
  sprintf(buff, "Incoming message, length: %d, RSSI: %d, SNR: %d",
      data.BufferSize, data.Rssi, data.Snr);
  Serial.println(buff);
  Serial.print("Rcvd Message: ");
  for (int i = 0; i < data.BufferSize; i++){
    Serial.print(receivedStream[i]);
  }
  Serial.println("");
}

/****************************************************************************/
/***        Main Setup                                                    ***/
/****************************************************************************/

void setup()
{
    Serial.begin(115200);
    Serial.println(CLS);
    Serial.println(HOME);
    Serial.println("LoRa P2P PING PONG");
    Serial.println("------------------------------------------------------");

    // Conf de Lora P2P si no está en Lora P2P
    if(api.lora.nwm.get() != 0)
    {
        Serial.printf("Set Node device work mode %s\r\n",
            api.lora.nwm.set() ? "Success" : "Fail");
        api.system.reboot();
    }
    //Configuración de parámetros LoRa especificos
    Serial.println("P2P Start");
    Serial.printf("Set P2P freq %3.3f: %s\r\n", (myFreq / 1e6),
  		api.lora.pfreq.set(myFreq) ? "Scss" : "Fail");
    Serial.printf("Set P2P spreading factor %d: %s\r\n", sf,
  		api.lora.psf.set(sf) ? "Scss" : "Fail");
    Serial.printf("Set P2P bandwidth %d: %s\r\n", bw,
  		api.lora.pbw.set(bw) ? "Scss" : "Fail");
    Serial.printf("Set P2P rate 4/%d: %s\r\n", (cr + 5),
  		api.lora.pcr.set(cr) ? "Scss" : "Fail");
    Serial.printf("Set P2P preamble length %d: %s\r\n", preamble,
  		api.lora.ppl.set(preamble) ? "Scss" : "Fail");
    Serial.printf("Set P2P tx power %d: %s\r\n", txPower,
  		api.lora.ptp.set(txPower) ? "Scss" : "Fail");

    api.lora.registerPRecvCallback(recv_cb);
    // api.lora.registerPSendCallback(send_cb);
    Serial.printf("P2P Rx mode %s\r\n",
  		api.lora.precv(65533) ? "Scss" : "Fail");

}

/****************************************************************************/
/***        Main Loop                                                     ***/
/****************************************************************************/

void loop()
{

}



/****************************************************************************/
/***        END OF FILE                                                   ***/
/****************************************************************************/