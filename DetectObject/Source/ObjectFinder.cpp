/*
Class to track an object in an image
*/

#include <ObjectFinder.hpp>
#include <Object.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs/legacy/constants_c.h>
#include <opencv2/imgproc/types_c.h>
#include <opencv2/imgproc/imgproc_c.h>
#include <opencv2/calib3d/calib3d_c.h>
#include <PathController.hpp>

using namespace cv;
using namespace std;

ObjectFinder::ObjectFinder() {
}

ObjectFinder::~ObjectFinder() {
}

void ObjectFinder::trackObject(Object objToTrack, Mat threshold,
		Mat &cameraFeed, int mode) {
	int x, y;

	vector<Object> objects;

	Mat temp;
	threshold.copyTo(temp);

	vector<vector<Point> > contours;
	vector<Vec4i> hierarchy; // vector to store number of objects
	//find contours of filtered image using openCV findContours function
	findContours(temp, contours, hierarchy, CV_RETR_CCOMP,
			CV_CHAIN_APPROX_SIMPLE);
	//use moments method to find our filtered object
	objectFound = false;
	if (hierarchy.size() > 0) {
		int numObjects = hierarchy.size();
		//if number of objects greater than MAX_NUM_OBJECTS we have a noisy filter
		if (numObjects < MAX_NUM_OBJECTS) {
			for (int index = 0; index >= 0; index = hierarchy[index][0]) {

				Moments moment = moments((cv::Mat) contours[index]);
				double area = moment.m00;


				if (area > MIN_OBJECT_AREA) {

					Object obj;
					CURRENT_OBJECT_AREA = area;
					int x = moment.m10 / area;
					int y = moment.m01 / area;
					obj.setXPos(x);
					obj.setYPos(y);

					stringstream strs;
					strs << CURRENT_OBJECT_AREA;
					string string = strs.str();
					string = "Found object area = " + string;
					putText(cameraFeed, string, Point(0, 50), 1, 1,
							Scalar(0, 255, 255), 2);
					rectangle(cameraFeed,
							Point(x - (MIN_OBJECT_LENGTH / 2),
									y - (MIN_OBJECT_WIDTH / 2)),
							Point(x + (MIN_OBJECT_LENGTH / 2),
									y + (MIN_OBJECT_WIDTH / 2)), 20);

					if (mode != 0) {
						obj.setType(objToTrack.getType());
						obj.setColour(objToTrack.getColour());
					}
					objects.push_back(obj);

					objectFound = true;
				} else {
					objectFound = false;
				}

			}
			//let user know you found an object
			if (objectFound == true) {
				//draw object location on screen
				drawObject(objects, cameraFeed);
			}

		} else
			putText(cameraFeed, "TOO MUCH NOISE! ADJUST FILTER", Point(0, 50),
					1, 2, Scalar(0, 0, 255), 2);
	}
}

bool ObjectFinder::getObjectFound() {
	return objectFound;
}

void ObjectFinder::drawObject(vector<Object> objects, Mat &frame) {
	for (int i = 0; i < objects.size(); i++) {

		Object obj = objects.at(i);
		int x = obj.getXPos();
		int y = obj.getYPos();

		XPos = x;
		YPos = y;

		printBestPath(x, y);

		string type = obj.getType();
		Scalar colour = obj.getColour();
		string type_and_coordinates = type + " (" + intToString(x) + " , "
				+ intToString(y) + ")";
		//cout << type_and_coordinates << endl;

		circle(frame, cv::Point(x, y), 10, cv::Scalar(0, 0, 255));
		//		putText(frame, intToString(x) + " , " + intToString(y),
		//				Point(x, y + 20), 1, 1, Scalar(0, 255, 0));
		putText(frame, type_and_coordinates, Point(x, (y - 30)), 1, 2, colour);
	}
}

string ObjectFinder::intToString(int number) {

	std::stringstream ss;
	ss << number;
	return ss.str();
}

void ObjectFinder::printBestPath(int x, int y){
	int xTarget = 319;
	int yTarget = 239;

	int xDiff = x - xTarget;
	int yDiff = y - yTarget;

	if (xDiff < 1 && yDiff < 1)
		cout << "Move left and Up" << endl;

	else if (xDiff < 1 && yDiff > 1)
		cout << "Move left and Down" << endl;

	else if (xDiff > 1 && yDiff < 1)
		cout << "Move right and Up" << endl;

	else if (xDiff > 1 && yDiff > 1)
		cout << "Move right and Down" << endl;

	else if (xDiff < 1 && yDiff == 0)
		cout << "Move left" << endl;

	else if (xDiff > 1 && yDiff == 0)
		cout << "Move right" << endl;

	else if (xDiff == 0 && yDiff > 1)
		cout << "Move Down" << endl;

	else if (xDiff == 0 && yDiff < 1)
		cout << "Move Up" << endl;

	else if(xDiff == 0 && yDiff == 0)
		cout << "Dont Move" << endl;

	else
		cout << "Nothing" << endl;
}

void ObjectFinder::updateMAX_OBJECT_AREA() {
	MIN_OBJECT_AREA = MIN_OBJECT_LENGTH * MIN_OBJECT_WIDTH;
}
