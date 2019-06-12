#include <Servo.h>

//-------------------------------------------------------------------------INITIALISING LINE SENSOR INPUTS & VARIABLES-------------------------------------------------------------------------
int analogPin1 = 0;  
int analogPin2 = 2;
int analogPin3 = 4;
int value1 = 0;
int value2 = 0;
int value3 = 0;
int value = 0;
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//--------------------------------------------------------------------------INITIALISING SERVO INPUTS & VARIABLES------------------------------------------------------------------------------
Servo servo1;
Servo servo2;
/*int start1 = ;
int end1 = ;
int start2 = ;
int end2 = ;
*/
//--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//int Buzzer = 13;2



void setup()
{
  Serial.begin(9600);
  servo1.attach(3);
  servo2.attach(9);
  servo1.write(0);
  servo2.write(0);
 //pinMode(Buzzer,OUTPUT);
}

/* -------------------------------------------------------------------------NEED TO CHECK SERVO VALUES----------------------------------------------------------------------------------------
void servoMotion()
{  
  for(angle1 = start1; angle1 < end1; angle1 += 1)    // command to move from 0 degrees to 180 degrees 
  {                                  
    servo1.write(angle1);                 //command to rotate the servo to the specified angle
    delay(15);                       
  } 
  delay(1000);
  
  for(angle2 = start2; angle2 < end2; angle2 += 1)    // command to move from 0 degrees to 180 degrees 
  {                                  
    servo2.write(angle2);                 //command to rotate the servo to the specified angle
    delay(5);                       
  } 
 
  delay(500);
  
  for(angle1 = end1; angle1>=start1; angle1-=5)     // command to move from 180 degrees to 0 degrees 
  {                                
    servo1.write(angle1);              //command to rotate the servo to the specified angle
    delay(15);                       
  } 
    delay(1000);
  
  for(angle2 = end2; angle2>=start2; angle2-=5)     // command to move from 180 degrees to 0 degrees 
  {                                
    servo2.write(angle2);              //command to rotate the servo to the specified angle
    delay(15);                       
  } 
    delay(1000);  
}
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*/


void lineSensor()
{
  int Direction;
  value1 = analogRead(analogPin1); 
  Serial.println(value1);
  Serial.print(" "); 
  
  value2 = analogRead(analogPin2);
  Serial.print(value2);
  Serial.print(" ");
  
  value3 = analogRead(analogPin3);
  Serial.print(value3);
  Serial.print(" ");

//NOT FOR TURNS FROM NODE, IT'S JUST TO MAKE SURE THE BOT STAYS ON THE BLACK LINE.
//SINCE IN PROGRESS TASK, THE BOT MUST ONLY GO STRAIGHT

  if((value1>100 && value2<100 && value3<100)|| (value1>100 && value2>100 && value3<100))
  {
    Direction = 1 ;
    //Serial.println(Direction);//TURN THE RIGHT WHEEL
  }
  else if((value1<100 && value2>100 && value3<100)/*|| (value1>100 && value2>100 && value3>100)*/)
  {
    Direction = 2 ; 
    //Serial.println(Direction);//DIRECTION OF WHEEL //Straight
  }
  else if((value1<100 && value2<100 && value3>100)||(value1<100 && value2>100 && value3>100))
  {
    Direction = 3 ; 
    //Serial.println(Direction);//DIRECTION OF WHEEL //Left
  }
  else if((value1<100 && value2<100 && value3<100))
  {
    Direction = 4;              //STOP
    //Serial.println(Direction);
  }
  else if(value1>100 && value2>100 && value3>100)
  {
    Direction = 5;                      //NODE Detected
   // Serial.println(Direction);  
  }
  
  //Serial.write(Direction);
  //Serial.println(Direction);
}

void loop()
{ 
  lineSensor();
  delay(100);  
}
