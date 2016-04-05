#include <opencv2/opencv.hpp>
#include <PathController.hpp>
#include <UDP_Client.hpp>
#include <Object.hpp>
#include <ObjectFinder.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/core.hpp>
#include <cmath>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <string>
#include <Window.hpp>

using namespace std;
using namespace cv;

// Headers
void pause();
Mat complementImage(Mat im, int row, int column);
void draw_rectangle(Mat img_rgb, int sub_mat_no);
void createTrackbars();
void sendDataToServer(int x, int y, int mode);
void setComp(int x);
void Switch_With_Function_Pointer(int a, void (*pt2Func)(int));

int comp = 1;
int useSavedObject = 0;
int detectObject = 0;
const string trackbarWindowName = "Trackbars";
int MIN = 0;
int MAX = 255;
VideoCapture camera;
UDP_Client client;
ObjectFinder finder;

//initial min and max HSV filter values.
//these will be changed using trackbars
int H_MIN = 0;
int H_MAX = 256;
int S_MIN = 0;
int S_MAX = 256;
int V_MIN = 0;
int V_MAX = 256;

string windowName1 = "Transformed Image (Black and White)";
string windowName2 = "Transformed Image (Black and White Inverted)";
string windowName3 = "Transformed Image (HSV)";

void on_trackbar(int, void*)
{
	cout << "useSavedObject changed to " << useSavedObject << endl;
	finder.updateMAX_OBJECT_AREA();

}

void morphOps(Mat &thresh)
{

	//create structuring element that will be used to "dilate" and "erode" image.
	//the element chosen here is a 3px by 3px rectangle

	Mat erodeElement = getStructuringElement(MORPH_RECT, Size(3, 3));
	//dilate with larger element so make sure object is nicely visible
	Mat dilateElement = getStructuringElement(MORPH_RECT, Size(8, 8));

	erode(thresh, thresh, erodeElement);
	erode(thresh, thresh, erodeElement);

	dilate(thresh, thresh, dilateElement);
	dilate(thresh, thresh, dilateElement);

}

bool determine_camera(char camera_name)
{
	/*if (camera.open(camera_name))
	 {
	 cout << "Using Camera: " << camera_name << endl;
	 return true;
	 }
	 else
	 {
	 cout << "Camera '" << camera_name << "' is not available" << endl;
	 int i = 0;
	 while (i < 5)
	 {
	 if (camera.open(i))
	 {
	 cout << "Using Camera: " << i << endl;
	 return true;
	 }
	 i++;
	 }
	 cout << "No Camera Available" << endl;
	 return false;
	 }*/
	return camera.open(1);
}

int run_all(char args[])
{
	// initialise UDP Client
	client.set_hostname("127.0.0.1");
	client.set_port("4446");

	Mat im_gray;   // no need to load the Mat with anything when declaring it.
	Mat im_rgb;
	Mat img_bw;
	Mat img_bw_comp;
	Mat HSV;
	Mat threshold;
	PathController pc;
	string path = "";

	if (!determine_camera(args[1])) // if camera cannot be found
		return 0;

	createTrackbars(); //create slider bars for HSV filtering

	int i = 0;
	while (1)
	{

		camera.read(im_rgb);
		cvtColor(im_rgb, im_gray, CV_RGB2GRAY); // convert image to grayscale
		cvtColor(im_rgb, HSV, COLOR_BGR2HSV);
		inRange(HSV, Scalar(H_MIN, S_MIN, V_MIN), Scalar(H_MAX, S_MAX, V_MAX),
				threshold);

		if (detectObject == 0)
		{
			destroyWindow(windowName3);

			cv::threshold(im_gray, img_bw, MIN, MAX, THRESH_BINARY); // convert image to binary
			img_bw_comp = complementImage(img_bw, img_bw.rows, img_bw.cols); // complement binary image
			morphOps(img_bw_comp);
			pc.determineBestPath(img_bw_comp);
			// while still determining path...
			while (pc.get_calulation_status() == false)
				cout << "Determining path..." << endl;

			namedWindow(windowName1, WINDOW_NORMAL);
			morphOps(img_bw);
			imshow(windowName1, img_bw);

			namedWindow(windowName2, WINDOW_NORMAL);
			morphOps(img_bw_comp);
			imshow(windowName2, img_bw_comp);

			sendDataToServer(pc.best_sub_matrix,0,detectObject);

		}

		else
		{
			destroyWindow(windowName1);
			destroyWindow(windowName2);

			Object obj1("obj1");

			if (useSavedObject == 1)
			{
				obj1.setType("SavedObject2");
			}

			else
			{
				obj1.setHSVmin(Scalar(H_MIN, S_MIN, V_MIN));
				obj1.setHSVmax(Scalar(H_MAX, S_MAX, V_MAX));
			}

			inRange(HSV, obj1.getHSVmin(), obj1.getHSVmax(), threshold);
			morphOps(threshold);
			finder.trackObject(obj1, threshold, im_rgb, useSavedObject);

			namedWindow(windowName3, WINDOW_NORMAL);
			morphOps(threshold);
			imshow(windowName3, threshold);

			sendDataToServer(finder.XPos,finder.YPos,detectObject);
		}

		namedWindow("Original", WINDOW_NORMAL);
		draw_rectangle(im_rgb, pc.best_sub_matrix);
		imshow("Original", im_rgb);

		int no1 = threshold.dims; //threshold.cols*threshold.rows;
		int no2 = img_bw_comp.dims; //img_bw_comp.cols*img_bw_comp.rows;
		int no3 = img_bw.dims; //img_bw.cols*img_bw.rows;
		cout << "Size 1 = " << no1 << " Size 2 = " << no2 << " Size 3 = " << no3
				<< endl;


		//delay 30ms so that screen can refresh.
		//image will not appear without this waitKey() command
		int x = waitKey(30);
		if ((char) x == 'd')
			break;
		i++;
	}

	camera.release();
	return 1;
}

int main(int argc, char *argv[])
{
	char args[] = { '1', '0', '2' };
	int result = run_all(args);
	cout << "Result of program: " << result << endl;
	//pause();
	return 0;
}

void pause()
{
	cout << "Press Enter to Continue..." << endl;
	cin.get();
}

Mat complementImage(Mat im, int rows, int cols)
{
	Mat newmat = Mat::zeros(im.rows, im.cols, CV_8UC1);

	int byte = 0;
	int zero = 0;
	int one = 255;

	for (int i = 0; i < rows; i++)
		for (int j = 0; j < cols; j++)
		{
			byte = im.at<unsigned char>(i, j);
			if (byte != 0)
				newmat.at<unsigned char>(i, j) = zero; // set value at i,j to zero
			else
				newmat.at<unsigned char>(i, j) = one;
		}
	return newmat;
}

// function for drawing rectangle around most suitable quadrant
void draw_rectangle(Mat img_rgb, int best_sub_matrix)
{
	double cols = (double) img_rgb.cols;
	double rows = (double) img_rgb.rows;

	int bm_c = 1;
	int bm_r = 1;

	switch (best_sub_matrix)
	{
	case 1:
		bm_c = 0;
		bm_r = 0;
		break;
	case 2:
		bm_c = 1;
		bm_r = 0;
		break;
	case 3:
		bm_c = 2;
		bm_r = 0;
		break;
	case 4:
		bm_c = 0;
		bm_r = 1;
		break;
	case 5:
		bm_c = 1;
		bm_r = 1;
		break;
	case 6:
		bm_c = 2;
		bm_r = 1;
		break;
	case 7:
		bm_c = 0;
		bm_r = 2;
		break;
	case 8:
		bm_c = 1;
		bm_r = 2;
		break;
	case 9:
		bm_c = 2;
		bm_r = 2;
		break;
	default:
		bm_c = 1;
		bm_r = 1;

	}

	int x_start = floor((cols / 3)) * bm_c;
	int y_start = floor((rows / 3)) * bm_r;
	int x_finish = floor((cols / 3)) * (bm_c + 1);
	int y_finish = floor((rows / 3)) * (bm_r + 1);

	rectangle(img_rgb, Point(x_start, y_start), Point(x_finish, y_finish),
			Scalar(255, 255, 0), 3);
}

void createTrackbars()
{
	//create window for trackbars

	cv::namedWindow(trackbarWindowName, 0);
	//create memory to store trackbar name on window
	char TrackbarName[50];
	sprintf(TrackbarName, "MIN", MIN);
	sprintf(TrackbarName, "MAX", MAX);
	sprintf(TrackbarName, "MIN", 0);
	sprintf(TrackbarName, "MAX", 2);

	sprintf(TrackbarName, "H_MIN", H_MIN);
	sprintf(TrackbarName, "H_MAX", H_MAX);
	sprintf(TrackbarName, "S_MIN", S_MIN);
	sprintf(TrackbarName, "S_MAX", S_MAX);
	sprintf(TrackbarName, "V_MIN", V_MIN);
	sprintf(TrackbarName, "V_MAX", V_MAX);
	sprintf(TrackbarName, "SavedObject", useSavedObject);

	//create trackbars and insert them into window
	//3 parameters are: the address of the variable that is changing when the trackbar is moved(eg.H_LOW),
	//the max value the trackbar can move (eg. H_HIGH),
	//and the function that is called whenever the trackbar is moved(eg. on_trackbar)
	//                                  ---->    ---->     ---->

	createTrackbar("MIN", trackbarWindowName, &MIN, MAX, on_trackbar);
	createTrackbar("MAX", trackbarWindowName, &MAX, MAX, on_trackbar);
	createTrackbar("DETECT OBJECT", trackbarWindowName, &detectObject, 1,
			on_trackbar);
	createTrackbar("DETECT OBJECT Length", trackbarWindowName, &finder.MIN_OBJECT_LENGTH, 200,
				on_trackbar);
	createTrackbar("DETECT OBJECT Width", trackbarWindowName, &finder.MIN_OBJECT_WIDTH, 200,
					on_trackbar);

	createTrackbar("H_MIN", trackbarWindowName, &H_MIN, H_MAX, on_trackbar);
	createTrackbar("H_MAX", trackbarWindowName, &H_MAX, H_MAX, on_trackbar);
	createTrackbar("S_MIN", trackbarWindowName, &S_MIN, S_MAX, on_trackbar);
	createTrackbar("S_MAX", trackbarWindowName, &S_MAX, S_MAX, on_trackbar);
	createTrackbar("V_MIN", trackbarWindowName, &V_MIN, V_MAX, on_trackbar);
	createTrackbar("V_MAX", trackbarWindowName, &V_MAX, V_MAX, on_trackbar);

	createTrackbar("SavedObject", trackbarWindowName, &useSavedObject, 1,
			on_trackbar);
	//Window w;
	//w.createCheckBox();
	//createButton("Button 1", Switch_With_Function_Pointer(2,&setComp), NULL, CV_CHECKBOX, 0);

}

//void Switch_With_Function_Pointer(int a, void (*pt2Func)(int, void))
//{
//   pt2Func(a,void);    // call using function pointer
//
//   //cout << "Switch replaced by function pointer: 2-5=";  // display result
//}

void setComp(int x)
{
	comp = x;
}

void sendDataToServer(int x, int y ,int mode)
{

	// convert string to int
	int best_sub_matrix = x;
	std::string buf = "";
	char str[20];
	buf += itoa(best_sub_matrix, str, 10);

	//string command = "java -jar UDP_client.jar " + client.get_hostname + " " + client.get_port + " " + buf;
	//system(command.c_str());

	if (mode == 0)
		client.create_new_socket(best_sub_matrix);
	else
		client.create_new_socket(x,y);
}

