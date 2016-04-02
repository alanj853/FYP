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
	PathController pc;
	int XPos = 0;
	int YPos = 0;

private:
	int MAX_NUM_OBJECTS = 50;
	int MIN_OBJECT_AREA = 75 * 75;
	bool objectFound = false;

};

