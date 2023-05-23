/*****************************************************************************
* File name:	smaract.cpp
* Project:		Robotic Surgery Software
* Part:   		SmarAct
* Editor:		Erfan ETESAMI and Ece OZELCI, MICROBS, EPFL, 2022
*				erfan.etesami@epfl.ch, ece.ozelci@epfl.ch
* Version:		22.0
* Description:	This file manages the communication with the SmarAct
*				channels and controls their movements.
*****************************************************************************/


#include "../include/headers/smaract.h"
#include <iostream>
using namespace std;
#include <Windows.h>
#include <fstream>


// Constructor
SmarAct::SmarAct() :
	isFound_(false),
	referencingStatus_(REFERENCING_DEFAULT)
{
	usbLocator_[0] = 0;
}

// Destructor
SmarAct::~SmarAct() {
	SA_STATUS status = SA_CloseSystem(getMCSHandle());
}

// Initialize the SmarAct controller
int SmarAct::initialize() {
	SA_STATUS status;
	SA_PACKET packet;

	// Finding the USB ID of the SmarAct connected to the PC via a USB port
	unsigned int bufferSize = sizeof(usbLocator_);
	status = SA_FindSystems("", usbLocator_, &bufferSize);
	if (status != SA_OK) {
		//// when status == SA_OK:
		//// usbLocators holds the locator strings, separated by '\n'.
		//// bufferSize holds the number of bytes written to usbLocators.
		return status;
	}
	//// If no USB locator is found, return the NOT_FOUND error
	if (usbLocator_[0] == 0) { return ERR_NOT_FOUND; }
	//// Initializing the system and getting its index
	status = SA_OpenSystem(&mcsHandle_, usbLocator_, ASYNC);
	if (status != SA_OK) { return status; }
	setIsFound(true);

	// Checking whether the sensors (for all channels) are enabled or not.
	status = SA_GetSensorEnabled_A(getMCSHandle());
	//// Waiting for answer, but not longer than PACKET_TIMEOUT
	status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
	if (status != SA_OK) {
		return status;
	}
	else {
		if (packet.packetType == SA_SENSOR_ENABLED_PACKET_TYPE) {
			unsigned int sensorMode = packet.data1;
			if (sensorMode != SA_SENSOR_ENABLED) {
				status = SA_SetSensorEnabled_A(getMCSHandle(), SA_SENSOR_ENABLED);
				if (status != SA_OK) { return status; }
			}
		}
		else {
			return ERR_INVALID_PACKET;
		}
	}

	// Disabling the relaitve position accumulation 
	for (int channelIndex = CHANNEL_X; channelIndex <= CHANNEL_BETA; channelIndex++) {
		status = SA_SetAccumulateRelativePositions_A(getMCSHandle(), channelIndex, SA_NO_ACCUMULATE_RELATIVE_POSITIONS);
	if (status != SA_OK) { return status; }
	}
	
	return SA_OK;
}

// Close the SmarAct controller
int SmarAct::close() {
	SA_STATUS status = SA_CloseSystem(getMCSHandle());
	return status;
}

// Getters
SA_INDEX SmarAct::getMCSHandle() {
	return mcsHandle_;
}

bool SmarAct::getIsFound() {
	return isFound_;
}

int SmarAct::getReferencingStatus() {
	return referencingStatus_;
}

char* SmarAct::getUSBLocator() {
	return usbLocator_;
}

long SmarAct::getChannelPosition(SA_INDEX channelIndex) {
	if ((channelIndex == CHANNEL_X) || (channelIndex == CHANNEL_Y) || (channelIndex == CHANNEL_Z)) {
		SA_STATUS status;
		SA_PACKET packet;
		long position;
		// Requesting the current position
		status = SA_GetPosition_A(getMCSHandle(), channelIndex);
		// Waiting for am answer, but not longer than the PACKET_TIMEOUT
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		} 
		else {
			if ((packet.packetType == SA_POSITION_PACKET_TYPE) && (packet.channelIndex == channelIndex)) { //  && (packet.channelIndex == channelIndex)
				position = static_cast<long>(packet.data2);
				return position;
			}
			else {
				return ERR_INVALID_PACKET;
			}
		} 
	}
	else if ((channelIndex == CHANNEL_ALPHA) || (channelIndex == CHANNEL_BETA)) {
		SA_STATUS status;
		SA_PACKET packet;
		unsigned int angle;
		signed int revolution;
		long position;
		// Requesting the current position
		status = SA_GetAngle_A(getMCSHandle(), channelIndex);
		// Waiting for an answer, but not longer than the PACKET_TIMEOUT
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		} 
		else {
			if ((packet.packetType == SA_ANGLE_PACKET_TYPE) && (packet.channelIndex == channelIndex)) {
				angle = packet.data1;
				revolution = packet.data2;
				position = static_cast<long>(angle) + static_cast<long>(revolution) * REVOLUTION_TO_DEGREES * DEGREES_TO_MICRO_DEGREES;
				return position;
			}
			else {
				// Handling the packet otherwise
				return ERR_INVALID_PACKET;
			}
		} 
	}
}

// Setters
void SmarAct::setIsFound(bool isFound) {
	isFound_ = isFound;
}

void SmarAct::setReferencingStatus(int referencingStatus) {
	referencingStatus_ = referencingStatus;
}

// General
int SmarAct::waitUntilReferencingIsDone(SA_INDEX channelIndex) {
	SA_STATUS status;
	SA_PACKET packet;
	int positionerStatus = 9; // 9 is out of the meaningful status codes of positioners (SmarAct Doc - page 138)

	do {
		status = SA_GetStatus_A(getMCSHandle(), channelIndex);
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		} else {
			if ((packet.packetType == SA_STATUS_PACKET_TYPE) && (packet.channelIndex == channelIndex)) {
				positionerStatus = packet.data1;
			} else {
				return ERR_INVALID_PACKET;
			}
		}
	} while (positionerStatus != SA_STOPPED_STATUS);
}

int SmarAct::waitUntilCalibrationIsDone(SA_INDEX channelIndex) {
	SA_STATUS status;
	SA_PACKET packet;
	int positionerStatus = 9; // 9 is out of the meaningful status codes of positioners (SmarAct Doc - page 138)

	do {
		status = SA_GetStatus_A(getMCSHandle(), channelIndex);
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		} else {
			if ((packet.packetType == SA_STATUS_PACKET_TYPE) && (packet.channelIndex == channelIndex)) {
				positionerStatus = packet.data1;
			} else {
				return ERR_INVALID_PACKET;
			}
		}
	} while (positionerStatus != SA_STOPPED_STATUS);
}

int SmarAct::isChannelReferenced(SA_INDEX channelIndex) {
	SA_STATUS status;
	SA_PACKET packet;
	status = SA_GetPhysicalPositionKnown_A(getMCSHandle(), channelIndex);
	if (status != SA_OK) {
		return status;
	}
	else {
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		}
		else {
			if ((packet.packetType == SA_PHYSICAL_POSITION_KNOWN_PACKET_TYPE) && (packet.channelIndex == channelIndex)) {
				if (packet.data1 != SA_PHYSICAL_POSITION_KNOWN) {
					switch (channelIndex) {
					case CHANNEL_X:
						return REFERENCING_X_NOT;
					case CHANNEL_Y:
						return REFERENCING_Y_NOT;
					case CHANNEL_Z:
						return REFERENCING_Z_NOT;
					case CHANNEL_ALPHA:
						return REFERENCING_ALPHA_NOT;
					case CHANNEL_BETA:
						return REFERENCING_BETA_NOT;
					default:
						return SA_OTHER_ERROR;
					}
				}
			}
			else {
				return ERR_INVALID_PACKET;
			}
		}
	}
	return SA_OK;
}

int SmarAct::referenceChannel(SA_INDEX channelIndex) {
	SA_STATUS status;
	SA_PACKET packet;
	status = SA_GetPhysicalPositionKnown_A(getMCSHandle(), channelIndex);
	if (status != SA_OK) {
		return status;
	}
	else {
		status = SA_ReceiveNextPacket_A(getMCSHandle(), PACKET_TIMEOUT, &packet);
		if (status != SA_OK) {
			return status;
		}
		else {
			if ((packet.packetType == SA_PHYSICAL_POSITION_KNOWN_PACKET_TYPE) && (packet.channelIndex == channelIndex)) {
				if (packet.data1 != SA_PHYSICAL_POSITION_KNOWN) {
					// The sensors of linear channels are of type (LED) meaning that they have mechanical end stop. (SmarAct Doc - page 140)
					// Therefore, the direction parameter in SA_FindReferenceMark_A is ignored and will be replaced by the direction set in SA_SetSafeDirection_A. (SmarAct Doc - page 48, 85)
					// Besides, for these sensors, we must configure the safe direction with SA_SetSafeDirection_S and call SA_CalibrateSensor_S before the positioner can be properly referenced. (SmarAct Doc - page 48)
					// The sensors of angular channels (Alpha and Beta) are of type (SR) meaning that they have reference marks. (SmarAct Doc - page 139)
					// Therefore, SA_SetSafeDirection_A has no effect on these channels. (SmarAct Doc - page 48)
					if (channelIndex == CHANNEL_X || channelIndex == CHANNEL_Y || channelIndex == CHANNEL_Z) {
						status = SA_SetSafeDirection_A(getMCSHandle(), channelIndex, SA_BACKWARD_DIRECTION);
						if (status != SA_OK) { return status; }
						status = SA_CalibrateSensor_A(getMCSHandle(), channelIndex);
						if (status != SA_OK) { return status; }
						status = waitUntilCalibrationIsDone(channelIndex);
						if (status != SA_OK) { return status; }
						status = SA_FindReferenceMark_A(getMCSHandle(), channelIndex, SA_BACKWARD_DIRECTION, POSITIONER_HOLD_TIME, SA_AUTO_ZERO);
						if (status != SA_OK) { return status; }
						status = waitUntilReferencingIsDone(channelIndex);
						if (status != SA_OK) { return status; }
					}
					else if (channelIndex == CHANNEL_ALPHA) {
						status = SA_FindReferenceMark_A(getMCSHandle(), channelIndex, SA_FORWARD_DIRECTION, POSITIONER_HOLD_TIME, SA_AUTO_ZERO);
						if (status != SA_OK) { return status; }
						status = waitUntilReferencingIsDone(channelIndex);
						if (status != SA_OK) { return status; }
					}
					else if (channelIndex == CHANNEL_BETA) {
						status = SA_FindReferenceMark_A(getMCSHandle(), channelIndex, SA_BACKWARD_DIRECTION, POSITIONER_HOLD_TIME, SA_AUTO_ZERO);
						if (status != SA_OK) { return status; }
						status = waitUntilReferencingIsDone(channelIndex);
						if (status != SA_OK) { return status; }
						// status = SA_SetScale_A(getMCSHandle(), channelIndex, BETA_SCALE_SHIFT, SA_TRUE);
						// if (status != SA_OK) { return status; }
					}
				}
			}
			else {
				return ERR_INVALID_PACKET;
			}
		}
	}
	return SA_OK;
}

int SmarAct::moveChannel(SA_INDEX channelIndex, double movement, unsigned int speed) {
	SA_STATUS status;
	SA_PACKET packet;
	// X, Y, and Z channels
	if ((channelIndex == CHANNEL_X) || (channelIndex == CHANNEL_Y) || (channelIndex == CHANNEL_Z)) {
		status = SA_SetClosedLoopMoveSpeed_A(getMCSHandle(), channelIndex, speed);
		if (status != SA_OK) { return status; }
		int relativeMovement = static_cast<int>(movement);
		status = SA_GotoPositionRelative_A(getMCSHandle(), channelIndex, relativeMovement, POSITIONER_HOLD_TIME);
		if (status != SA_OK) { return status; }
	}
	// Alpha and Beta channels
	else if ((channelIndex == CHANNEL_ALPHA) || (channelIndex == CHANNEL_BETA)) {
		status = SA_SetClosedLoopMoveSpeed_A(getMCSHandle(), channelIndex, speed);
		if (status != SA_OK) { return status; }
		int relativeMovement = static_cast<int>(movement);
		status = SA_GotoAngleRelative_A(getMCSHandle(), channelIndex, relativeMovement, ANGULAR_POSITIONER_CURRENT_REVOLUTION, POSITIONER_HOLD_TIME);
		if (status != SA_OK) { return status; }
	}
	// Gamma channel
	else if (channelIndex == CHANNEL_GAMMA) {
		unsigned int frequency = speed;
		int relativeMovement = static_cast<int>(movement);
		status = SA_StepMove_A(getMCSHandle(), channelIndex, relativeMovement, OPEN_LOOP_AMPLITUDE, frequency);
		if (status != SA_OK) { return status; }
	}
	return SA_OK;
}

int SmarAct::moveChannelToPosition(SA_INDEX channelIndex, double position, unsigned int speed) {
	SA_STATUS status;
	SA_PACKET packet;
	// X, Y, and Z channels
	if ((channelIndex == CHANNEL_X) || (channelIndex == CHANNEL_Y) || (channelIndex == CHANNEL_Z)) {
		status = SA_SetClosedLoopMoveSpeed_A(getMCSHandle(), channelIndex, speed);
		if (status != SA_OK) { return status; }
		int absolutePosition = static_cast<int>(position);
		status = SA_GotoPositionAbsolute_A(getMCSHandle(), channelIndex, absolutePosition, POSITIONER_HOLD_TIME);
		if (status != SA_OK) { return status; }
	}
	// Alpha and Beta channels
	else if ((channelIndex == CHANNEL_ALPHA) || (channelIndex == CHANNEL_BETA)) {
		status = SA_SetClosedLoopMoveSpeed_A(getMCSHandle(), channelIndex, speed);
		if (status != SA_OK) { return status; }
		int absolutePosition = static_cast<int>(position);
		status = SA_GotoAngleAbsolute_A(getMCSHandle(), channelIndex, absolutePosition, ANGULAR_POSITIONER_CURRENT_REVOLUTION, POSITIONER_HOLD_TIME);
		if (status != SA_OK) { return status; }
	}
	return SA_OK;
}

int SmarAct::stopChannel(SA_INDEX channelIndex) {
	SA_STATUS status;
	status = SA_Stop_A(getMCSHandle(), channelIndex);
	if (status != SA_OK) { return status; }
	return SA_OK;
}
