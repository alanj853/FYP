#pragma once;
#include <string>
#include <opencv2/opencv.hpp>
#include <Object.hpp>
#include <PathController.hpp>

using namespace std;
using namespace cv;

class ObjectFinder
{
public:
	ObjectFinder();
	~ObjectFinder();
	void trackObject(Object obj, Mat threshold, Mat &cameraFeed, int mode);
	void drawObject(vector<Object> objects, Mat &cameraFeed);
	string intToString(int number);
	bool getObjectFound();
	void updateMAX_OBJECT_AREA();
	PathController pc;
	int XPos = 0;
	int YPos = 0;
	int MIN_OBJECT_LENGTH = 75;
	int MIN_OBJECT_WIDTH = 75;

private:
	int MAX_NUM_OBJECTS = 50;

	int MIN_OBJECT_AREA = MIN_OBJECT_LENGTH * MIN_OBJECT_WIDTH;
	bool objectFound = false;

};
