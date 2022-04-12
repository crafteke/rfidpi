#include <SPI.h>
#include <MFRC522.h>


#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          3          // Configurable, see typical pin layout above


#define READER_ID       5

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

bool rfid_tag_present_prev = false;
bool rfid_tag_present = false;
int _rfid_error_counter = 0;
bool _tag_found = false;

void setup() {
 Serial.begin(115200);		// Initialize serial communications with the PC
 while (!Serial);		// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
 SPI.begin();			// Init SPI bus
 mfrc522.PCD_Init();		// Init MFRC522
 mfrc522.PCD_DumpVersionToSerial();

}

//byte tag_read[]
void loop() {
 rfid_tag_present_prev = rfid_tag_present;

 _rfid_error_counter += 1;
 if(_rfid_error_counter > 2){
   _tag_found = false;
 }

 // Detect Tag without looking for collisions
 byte bufferATQA[2];
 byte bufferSize = sizeof(bufferATQA);

 // Reset baud rates
 mfrc522.PCD_WriteRegister(mfrc522.TxModeReg, 0x00);
 mfrc522.PCD_WriteRegister(mfrc522.RxModeReg, 0x00);
 // Reset ModWidthReg
 mfrc522.PCD_WriteRegister(mfrc522.ModWidthReg, 0x26);

 MFRC522::StatusCode result = mfrc522.PICC_RequestA(bufferATQA, &bufferSize);

 if(result == mfrc522.STATUS_OK){
   if ( ! mfrc522.PICC_ReadCardSerial()) { //Since a PICC placed get Serial and continue
     return;
   }
   _rfid_error_counter = 0;
   _tag_found = true;

 }

 rfid_tag_present = _tag_found;

 // rising edge
 if (rfid_tag_present && !rfid_tag_present_prev){
   sendData("TAG_FOUND");
   sendTag();
 }

 // falling edge
 if (!rfid_tag_present && rfid_tag_present_prev){
    sendData("TAG_GONE");
 }
}

void sendTag(){
  String tag="";
  for(int i=0;i<mfrc522.uid.size;i++){
    tag.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    tag.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  sendData(tag);
}
void sendTagSpaced(){
  String tag="";
  for(int i=0;i<mfrc522.uid.size;i++){
    if(i==0 && mfrc522.uid.uidByte[i] < 0x10){
      tag.concat("0");
    } else{
      tag.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
    }
    tag.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  sendData(tag);
}

void sendData(String s){
  Serial.print(READER_ID);
  Serial.println(":"+s);
}
