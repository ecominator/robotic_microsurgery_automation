/*****************************************************************************
* File name:	smaract.h
* Project:		Robotic Surgery Software
* Part:   		SmarAct
* Editor:		Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
*				erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
* Version:		22.0
* Description:	This file is the header file for the SmarAct class
*               which is responsible for controlling the SmarAct channels.
*****************************************************************************/


#ifndef SMARACT_H
#define SMARACT_H
#define _CRT_SECURE_NO_WARNINGS


#include <string>
#include <vector>
#include "MCSControl.h"


// Error codes
const int ERR_NOT_FOUND = 1001;
const int ERR_INVALID_PACKET = 1002;
const int ERR_INVALID_SENSOR_TYPE = 1003;
// Channel indices
const SA_INDEX CHANNEL_X = 0;
const SA_INDEX CHANNEL_Y = 1;
const SA_INDEX CHANNEL_Z = 2;
const SA_INDEX CHANNEL_ALPHA = 3;
const SA_INDEX CHANNEL_BETA = 4;
const SA_INDEX CHANNEL_GAMMA = 5;
// Communication
const char ASYNC[] = "async";
const int BUFFER_SIZE = 4096;			// [bytes], SmarActDoc - page 34
const int PACKET_TIMEOUT = 1000;			// [ms] = 1s
// Timeings
const int POSITIONER_HOLD_TIME = 0;			// [ms] = 0ms, Maximum allowed value is 60,000 ms (infinite) (SmarActDoc - page 72)
// Scales
const int ALPHA_SCALE_SHIFT = 0;	// [micro degree] = 0 degrees
const int BETA_SCALE_SHIFT = 0;			// [micro degree] = 0 degree
// Movements		
const int ANGULAR_POSITIONER_CURRENT_REVOLUTION = 0;
const int OPEN_LOOP_AMPLITUDE = 2048;			// Determines the step width. The range is from 0 corresponding to 0V to 4,095 corresponding to 100V. (SmarActDoc - page 91)
// Referencing
const int REFERENCING_DEFAULT = 0;
const int REFERENCING_X_DONE = 1;
const int REFERENCING_X_FAILED = 2;
const int REFERENCING_X_NOT = 3;
const int REFERENCING_Y_DONE = 4;
const int REFERENCING_Y_FAILED = 5;
const int REFERENCING_Y_NOT = 6;
const int REFERENCING_Z_DONE = 7;
const int REFERENCING_Z_FAILED = 8;
const int REFERENCING_Z_NOT = 9;
const int REFERENCING_ALPHA_DONE = 10;
const int REFERENCING_ALPHA_FAILED = 11;
const int REFERENCING_ALPHA_NOT = 12;
const int REFERENCING_BETA_DONE = 13;
const int REFERENCING_BETA_FAILED = 14;
const int REFERENCING_BETA_NOT = 15;
const int REFERENCING_STATUS_DONE = 16;
// Unit conversions
const int REVOLUTION_TO_DEGREES		= 360; 
const int DEGREES_TO_MICRO_DEGREES	= 1000000;

class SmarAct {
public:
	// Class constructor
	SmarAct();
	// Class destructor
	~SmarAct();
	// Initialize the SmarAct controller
	int initialize();
	// Close the SmarAct controller
	int close();
	// Getters
	SA_INDEX getMCSHandle();
	bool getIsFound();
	int getReferencingStatus();
	char* getUSBLocator();
	long getChannelPosition(SA_INDEX channelIndex);
	// Setters
	void setIsFound(bool isFound);
	void setReferencingStatus(int referencingStatus);
	// General
	int waitUntilCalibrationIsDone(SA_INDEX channelIndex);
	int waitUntilReferencingIsDone(SA_INDEX channelIndex);
	int isChannelReferenced(SA_INDEX channelIndex);
	int referenceChannel(SA_INDEX channelIndex);
	int moveChannel(SA_INDEX channelIndex, double movement, unsigned int speed);
	int moveChannelToPosition(SA_INDEX channelIndex, double position, unsigned int speed);
	int stopChannel(SA_INDEX channelIndex);

private:
	bool isFound_;
	int referencingStatus_;
	char usbLocator_[BUFFER_SIZE];
	SA_INDEX mcsHandle_;
};

#endif // SMARACT_H