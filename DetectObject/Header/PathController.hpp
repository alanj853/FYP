#pragma once

#include <opencv2/opencv.hpp>
#include <iostream>

using namespace std;
//using namespace cv;

class PathController
{
public:
	PathController();
	~PathController();
	string determineBestPath(cv::Mat frame);
	bool get_calulation_status();
	void set_calulation_status(bool val);
	string printrowscols(cv::Mat curr_frame);
	int determine_rows(cv::Mat frame);
	int determine_cols(cv::Mat frame);
	int best_sub_matrix;
	int* determineBestPath(int x, int y);

private:
	int getMatrixValue(cv::Mat image, int row, int column);
	void setMatrixValue(cv::Mat image, int row, int column, int value);
	string determineDirection();
	bool calculation_done;
	cv::Mat frame_being_analysed;
	cv::Mat sub_mats[9];
	void create_sub_matrices(int x, int y);
	void determine_most_free_space(cv::Mat mats[]);


};
