/*
Class for creating 'Tracked Object' objects ;)
*/

#include <Object.hpp>
#include <opencv2/opencv.hpp>

Object::Object() {
}

Object::~Object() {
}

Object::Object(string name) {

	setType(name);

}




int Object::getXPos() {
	return Object::xPos;
}

void Object::setXPos(int x) {
	Object::xPos = x;
}

int Object::getYPos() {
	return Object::yPos;
}

void Object::setYPos(int y) {
	Object::yPos = y;
}

void Object::setHSVmax(Scalar val) {
	Object::HSVmax = val;
}

Scalar Object::getHSVmax() {
	return Object::HSVmax;
}

void Object::setHSVmin(Scalar val) {
	Object::HSVmin = val;
}

Scalar Object::getHSVmin() {
	return Object::HSVmin;
}

string Object::getType() {
	return Object::type;
}

void Object::setType(string type) {
	Object::type = type;
	
	// some predefined hardcoded objects. Have HSV thresholds set already					
	if (type == "SavedObject1") {
								setHSVmin(Scalar(103, 28, 21));
								setHSVmax(Scalar(152, 256, 147));
								setColour(Scalar(255, 0, 255)); // blue
							}
	if (type == "SavedObject2") {
									setHSVmin(Scalar(66, 229, 0));
									setHSVmax(Scalar(256, 256, 256));
									setColour(Scalar(255, 0, 255)); // blue
								}
}

Scalar Object::getColour() {
	return Object::colour;
}

void Object::setColour(Scalar c) {
	Object::colour = c;
}
