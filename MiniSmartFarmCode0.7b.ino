#include <DHT.h>
#define DHTTYPE DHT22

float Humi,Temp;
int waterLv; // Water Level 


int ACInRelayPin = 4; // 흡기 시그널핀
int ACOutRealyPin = 5; // 배기 시그널핀 
int WTInRelayPin = 6; // 수분공급 시그널핀
int WTOutRelayPin = 7; //수분배출 시그널핀
int HTS = 8;

unsigned long pro_Time = 0;
int WT = 1000;


char SLOD; //SeriaL OrderData

DHT temp(HTS, DHTTYPE);

bool AutoFan = true;
bool InFan = false;
bool OutFan = false;
bool InPump = false;
bool OutPump = false;

int EventVelue = 0;

void setup()
{
  temp.begin();
  Serial.begin(9600);
  pinMode(A3,INPUT);
  
}
void loop()
{
          if(millis() > pro_Time + WT){
          EventVelue = 0;
          Humi = temp.readHumidity();
          Temp = temp.readTemperature();
          waterLv = analogRead(A3);

          
          if(Serial.available()){ // 만일 컴퓨터로부터 값을 받았다면
            SLOD = Serial.read();

            if(SLOD == '1'){
              if(InFan == false){
              digitalWrite(ACInRelayPin,HIGH);

              AutoFan = false;
              }
              
              else if(InFan == true){
              digitalWrite(ACInRelayPin,LOW);

              AutoFan = true;
              }
             
            }

            else if(SLOD == '2'){
              if(OutFan == false){
              digitalWrite(ACOutRealyPin,HIGH);

              AutoFan = false;
              }
              else if(OutFan == true){
              digitalWrite(ACOutRealyPin,LOW);

              AutoFan = true;
              }
            }
            else if(SLOD == '3'){
              if(InPump == false){
                digitalWrite(WTInRelayPin,HIGH);   
              }
              else if(InPump == true){
                digitalWrite(WTInRelayPin,LOW); 
              }
            }
            else if(SLOD == '4'){
              if(OutPump == false){
                digitalWrite(WTOutRelayPin,HIGH);
              }
              else if(OutPump == true){
                digitalWrite(WTOutRelayPin,LOW);
              }
            }
            
            }
            
            //공조기능 자동제어가 켜져있을때만 온도,습도에따라서 팬이 돌아감
            if(AutoFan == true){//일반상태일경우
            if(Temp > 20){ //생육적온 최대20도
              digitalWrite(ACOutRealyPin,HIGH);
              digitalWrite(ACInRelayPin,LOW);
              EventVelue = EventVelue +1;
            }
            if(10 >= Temp){//생육적온 최소10도
              digitalWrite(ACInRelayPin,HIGH);
              digitalWrite(ACOutRealyPin,LOW);
              EventVelue = EventVelue +1;
            }
            //온도정상, 습도 비정상이라면
            if(Humi > 65){ //상대습도 65미만으로 설정
             digitalWrite(ACOutRealyPin,HIGH);
             EventVelue = EventVelue +2;
            }
            //온도, 습도 모두 정상이면 팬 정지
            if(EventVelue == 0){
              digitalWrite(ACInRelayPin,LOW);
              digitalWrite(ACOutRealyPin,LOW);
            }
       
            }

            
            //만일 수위가 700을 넘는다면
            if(waterLv > 700){
              digitalWrite(WTOutRelayPin,HIGH);
              EventVelue = EventVelue +4;
            }
            
            //만일 수위가 700이상이 아니면서 400미만이라면
            else if(400>waterLv){
              digitalWrite(WTInRelayPin,LOW);
              EventVelue = EventVelue +4;
            }
            //700미만 400이상 이라면
            else{
              digitalWrite(WTOutRelayPin,LOW);
              digitalWrite(WTInRelayPin,LOW);
            }
            //아두이노에서 시리얼통신으로 값 보내는 내역
            Serial.print(Temp);
            Serial.print(',');
            Serial.print(Humi);
            Serial.print(',');
            Serial.print(waterLv);
            Serial.print(',');
            Serial.println(EventVelue);
            //EventVelue 해석 : 온도변화 1 습도변화 2 물공급변화 4, 온도와 습도 = 3, 온도와 펌프제어 = 5, 습도와 물공급 6, 전부다 7
            
            pro_Time = millis();
          }
}
            
          

          
          
          
          
          
          
  
