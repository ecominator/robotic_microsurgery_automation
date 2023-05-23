/*****************************************************************************
 * File name:   ASM.ino
 * Project:     Robotic Surgery Software
 * Part:        Arudino Stepper Motor
 * Author:      Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
 *              erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
 * Version:     22.0
 * Description: Arduino code for interacting with the Arduino Stepper Motor 
 *              (ASM) which is responsible for actuating the mounted 
 *              end-effectors of the SmarActTTTRRR robot 
 *****************************************************************************/
 
// stepper properites
#define PIN_DIR       (2)
#define PIN_STEP      (3)
#define PIN_ENABLE    (7)
#define DIR_CW        (LOW)
#define DIR_CCW       (HIGH)
#define ENABLE_ON     (LOW)
#define ENABLE_OFF    (HIGH)
#define STEP_HIGH     (HIGH)
#define STEP_LOW      (LOW)

// serial communication
#define BUFFER_SIZE   (64)    // maximum length of the buffer
#define CMD_OFFSET    (3)
#define MAX_DIGITS    (5)     // for example, +1000 or -1000 has 5 digits at max.

// commands
#define CMD_GNM       ("GNM") // getting the controller name
#define CMD_MOV       ("MOV") // moving for the desired number of steps in the desired direction
#define CMD_GPO       ("GPO") // getting the current position which is always 0 in the beginning
#define CMD_GDL       ("GDL") // getting the delay between each step
#define CMD_SDL       ("SDL") // setting the delay between each step

// states
#define ST_NME        ("ASM") // name: Arduino Stepper Motor
#define ST_ERR        ("ERR") // return "ERR" if the command is not recognized.
#define ST_COK        ("COK") // return "COK" if the command is recognized.
#define ST_DNE        ("DNE") // return "DNE" when movement is finished.

// flags
#define FL_ERR        (-1)    // when getIntArg function does not terminate correclty
#define FL_OK         (1)     // when getIntArg function terminates correctly
 
// ASCII constants
#define ASCII_NGT     (45)    // ASCII code for - (negative) sign
#define ASCII_ZRO     (48)    // ASCII code for 0 

// global variables
static int pow10[MAX_DIGITS] = {1, 10, 100, 1000};
int pos = 0;        // postion of the stepper which is a relative property, but it is set to 0 in the beginning. 
int stepDelay = 1;  // [ms] as the default and minimum delay between each step

// getting the number of steps to move the motor as digit array (also handles the space/no space issue) 
int getIntArg(const char* command, int &num) {
  int idx = CMD_OFFSET; // idx stands for index
  if (command[idx] == '\n') {
    return FL_ERR;         
  }
  int digit[MAX_DIGITS];
  int digitIdx = 0;     // digit index
  bool isNegative = false;
  while(command[idx] != '\n') {
    if (command[idx] == ASCII_NGT) { 
      isNegative = true;
    } else {
      digit[digitIdx] = (int)command[idx] - ASCII_ZRO;
      if (digit[digitIdx] < 0 || digit[digitIdx] > 9) {
        return FL_ERR;
      }
      digitIdx = digitIdx + 1;
      if (digitIdx > MAX_DIGITS) { 
        return FL_ERR;
      }
    }
    idx = idx + 1;
  }
  if (digitIdx == 0) {  // when while loop is ignored anyhow
    return FL_ERR;
  }
  
  // converting the digit array to an integer number
  num = 0;
  for (int i = 0; i < digitIdx; i++) {
    num += digit[i] * pow10[digitIdx - i - 1];
  }
  if (isNegative == true) {
    num = -num;
  }
  return FL_OK;
}

void process_command(const char* command) {
  if (strncmp(command, CMD_MOV, 3) == 0) {
    int steps = 0;
    int flag = getIntArg(command, steps);      // "steps" also gets updated because of the referencing operator & in getIntArg function.
    if (flag == FL_ERR) {
      Serial.println(ST_ERR);
    } else {
      Serial.println(ST_COK);
      digitalWrite(PIN_ENABLE, ENABLE_ON);    // setting enable pin to low to allow motor control
      moveBy(steps);                          // moving desired number of steps in the desired direction
      pos = pos + steps; 
      resetDriverPins();                      // once the requested action is completed, the pins must be set back to the default state to prevent unexpected or unwanted motor behavior.
      Serial.println(ST_DNE);
    }
  } else if (strncmp(command, CMD_GPO, 3) == 0) {
    Serial.println(pos);
  } else if (strncmp(command, CMD_SDL, 3) == 0) {
    int delayVal;
    int flag = getIntArg(command, delayVal);  // "delayVal" also gets updated because of referencing operator & in getIntArg function.
    if (flag == FL_ERR || delayVal < 1) {
      Serial.println(ST_ERR); 
    } else {
      Serial.println(ST_COK);
      stepDelay = delayVal;
      Serial.println(ST_DNE);
    }
  } else if (strncmp(command, CMD_GDL, 3) == 0) {
    Serial.println(stepDelay);
  } else if (strncmp(command, CMD_GNM, 3) == 0) {
    Serial.println(ST_NME);
  } else {
    Serial.println(ST_ERR);
  }
}
  
void processIncomingByte(const byte inByte) {
  static char input_line[BUFFER_SIZE];
  static unsigned int input_pos = 0;
  switch (inByte) {
    case '\n':
      input_line[input_pos] = '\n';
      process_command(input_line);
      input_pos = 0;              //for incoming serial data
      break;
    case '\r':
      break;
    default:
      if (input_pos < (BUFFER_SIZE - 1)) {
        input_line[input_pos++] = inByte;
      }
      break;
  }
}

void moveBy(int steps) {
  if (steps > 0) {
    digitalWrite(PIN_DIR, DIR_CCW);
  } else {
    digitalWrite(PIN_DIR, DIR_CW);
  }
  for (int i = 0; i < abs(steps); i++) {
    digitalWrite(PIN_STEP, STEP_HIGH);
    delay(stepDelay);
    digitalWrite(PIN_STEP, STEP_LOW);
    delay(stepDelay);
  }
}

void resetDriverPins() {
  digitalWrite(PIN_STEP, LOW);
  digitalWrite(PIN_DIR, LOW);
  digitalWrite(PIN_ENABLE, HIGH);
}

void setup() {
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_ENABLE, OUTPUT);
  resetDriverPins();  // setting step, direction, and enable pins to default states (low, low, high)
  Serial.begin(9600); // starting serial communication (and setting data rate to 9600 bps)
}

void loop() {
  while (Serial.available() > 0) {      // getting the number of bytes (characters) available for reading from the serial port (replying only after receiving data)
    processIncomingByte(Serial.read());
  }
}
