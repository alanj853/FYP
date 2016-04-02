#pragma once;

#include <string>
#include <opencv2/opencv.hpp>
using namespace std;
using namespace cv;

class Object
{
public:
	Object();
	Object(string name);
	~Object();
	int getXPos();
	void setXPos(int x);
	int getYPos();
	void setYPos(int y);
	Scalar getHSVmin();
	Scalar getHSVmax();
	void setHSVmin(Scalar min);
	void setHSVmax(Scalar max);

	string getType();
	void setType(string type);

	void setColour(Scalar c);
	Scalar getColour();

private:
	int xPos, yPos;
	string type;
	Scalar HSVmin, HSVmax;
	Scalar colour;
};
