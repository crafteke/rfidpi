#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          3          // Configurable, see typical pin layout above


//#define READER_ID       04242
//#define READER_ID       0
int READER_ID=0;
String correct_tags[]={"0415911acdc826","0415917a9b5728","0415910a76d926","0415910a66c326","0415918a11ac28","0415911a2ce826"};

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

bool rfid_tag_present_prev = false;
bool rfid_tag_present = false;
int _rfid_error_counter = 0;
bool _tag_found = false;
bool refresh_request=false;
bool eeprom_id_calibrate=false;
void setup() {
 Serial.begin(115200);		// Initialize serial communications with the PC
 while (!Serial);		// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
 SPI.begin();			// Init SPI bus
 mfrc522.PCD_Init();		// Init MFRC522
 mfrc522.PCD_DumpVersionToSerial();
 READER_ID=EEPROM.read(0);

}

//byte tag_read[]
void loop() {
  while (Serial.available() > 0) {
     // read the incoming byte:
     int d=Serial.readString().toInt();
       //   Serial.print("DEBUG:");
       // Serial.print(READER_ID);
       // Serial.print(": refresh request. DATA=");
       // Serial.println(d, DEC); // here, DEC means Decimal
     if(d==1){
       rfid_tag_present_prev = false;
       rfid_tag_present = false;
       _rfid_error_counter = 0;
       _tag_found = false;
       refresh_request=true;
     }
     if(d==2){
       rfid_tag_present_prev = false;
       rfid_tag_present = false;
       _rfid_error_counter = 0;
       _tag_found = false;
       eeprom_id_calibrate=true;
     }
   }
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
   //sendData("TAG_FOUND"); useless: just send tag and we know there was something
   sendTag();
   if(eeprom_id_calibrate){
     calibrateEEPROM();
   }
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
  if(refresh_request){
    s=s+':'+'R';
    refresh_request=false;
  }
  Serial.println(":"+s);
}
void calibrateEEPROM(){
  String tag="";
  for(int i=0;i<mfrc522.uid.size;i++){
    tag.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    tag.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  for(int i=0;i<6;i++){
    if(tag==correct_tags[i]){
      EEPROM.update(0, i);
    }
  }
  READER_ID=EEPROM.read(0);
  Serial.print("CALIBRATED:");
  Serial.println(READER_ID);
  eeprom_id_calibrate=false;
}
