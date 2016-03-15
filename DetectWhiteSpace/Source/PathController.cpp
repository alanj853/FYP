#include <PathController.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/core.hpp>
#include <cmath>

using namespace cv;
using namespace std;

PathController::PathController()
{
	set_calulation_status(true);
}
PathController::~PathController()
{
}

string PathController::printrowscols(Mat curr_frame)
{
	calculation_done = false;
	Mat frame = curr_frame;
	int no_rows = frame.rows;
	int no_cols = frame.cols;
	cout << "Rows: " << no_rows << " Cols: " << no_cols << endl;
	calculation_done = true;
	return "Hello";
}

int PathController::determine_cols(Mat f)
{
	double cols = (double) f.cols;
	double ans = 0;
	if ((cols / 3) == floor(cols / 3))
		ans = cols;
	else if (((cols - 1) / 3) == floor((cols - 1) / 3))
		ans = cols - 1;
	else
		ans = cols - 2;

	return (int) ans;
}

int PathController::determine_rows(Mat f)
{
	double rows = (double) f.rows;
	double ans = 0;
	if ((rows / 3) == floor(rows / 3))
		ans = rows;
	else if (((rows - 1) / 3) == floor((rows - 1) / 3))
		ans = rows - 1;
	else
		ans = rows - 2;

	return (int) ans;
}

// method to determine best path pased on RGB image
string PathController::determineBestPath(Mat curr_frame)
{
	frame_being_analysed = curr_frame;
	calculation_done = false;
	int no_rows = determine_rows(frame_being_analysed);
	int no_cols = determine_cols(frame_being_analysed);

	int frame_mat_rows = 3;
	int frame_mat_cols = 3;
	Mat x = Mat::zeros(frame_mat_rows, frame_mat_cols, CV_8UC1);

	int row_cnt = 0;
	int col_cnt = 0;

	int new_no_rows = no_rows / frame_mat_rows;
	int new_no_cols = no_cols / frame_mat_cols;
	create_sub_matrices(new_no_rows, new_no_cols);
	int sub_mat_cnt = 0;



	for (int i = 0; i < no_rows; i = i + new_no_rows)
	{
		col_cnt = 0;
		for (int j = 0; j < no_cols; j = j + new_no_cols)
		{
			int row_start = i;
			int col_start = j;
			int one_cnt = 0;
			int zero_cnt = 0;
			int verdict = 0;

			int sub_mat_row = 0;

			for (int r_idx = row_start; r_idx < (row_start + new_no_rows);
					r_idx++)
			{
				int sub_mat_col = 0;
				for (int c_idx = col_start; c_idx < (col_start + new_no_cols);
						c_idx++)
				{
					int val = getMatrixValue(frame_being_analysed, r_idx,
							c_idx);

					//cout << "Setting " << val << " to (" << sub_mat_row << "," << sub_mat_col << ")" << " in sub mat " << sub_mat_cnt <<  endl;
					setMatrixValue(sub_mats[sub_mat_cnt], sub_mat_row,
							sub_mat_col, val);
					sub_mat_col++;
					if (val == 0)
						zero_cnt++;
					else
						one_cnt++;
				}
				sub_mat_row++;
			}
			sub_mat_cnt++;
			if (one_cnt > zero_cnt)
				verdict = 1;
			else
				verdict = 0;
			setMatrixValue(x, row_cnt, col_cnt, verdict);

			col_cnt++;
		}
		row_cnt++;
	}

	determine_most_free_space(sub_mats);
	string path = determineDirection();
	cout << "Best path is: " << path << endl;
	calculation_done = true;
	return path;
}

void PathController::setMatrixValue(Mat image, int row, int column, int value)
{
	image.at<unsigned char>(row, column) = value;
}

int PathController::getMatrixValue(Mat image, int row, int column)
{
	int byte = image.at<unsigned char>(row, column);
	return byte;
}

string PathController::determineDirection()
{
	string instruction1 = "Maintain Current Thrust";
	string instruction2 = "Maintain Current Roll";

	switch (best_sub_matrix)
	{
	case 1:
		return "Increase Thrust & Roll Left";
	case 2:
		return "Increase Thrust & Maintain Current Roll";
	case 3:
		return "Increase Thrust & Roll Right";
	case 4:
		return "Maintain Current Thrust & Roll Left";
	case 5:
		return "Maintain Current Thrust & Maintain Current Roll";
	case 6:
		return "Maintain Current Thrust & Roll Right";
	case 7:
		return "Decrease Thrust & Roll Left";
	case 8:
		return "Decrease Thrust & Maintain Current Roll";
	case 9:
		return "Decrease Thrust & Roll Right";
	default:
		return "Maintain Current Thrust % Maintain Current Roll";
	}
}

bool PathController::get_calulation_status()
{
	return calculation_done;
}

void PathController::set_calulation_status(bool val)
{
	calculation_done = val;
}

void PathController::create_sub_matrices(int rows, int cols)
{
	for (int i = 0; i < 9; i++)
		sub_mats[i] = Mat::zeros(rows, cols, CV_8UC1);
	best_sub_matrix = 5;
}

void PathController::determine_most_free_space(Mat mats[])
{
	int most_free_space = 0;
	int best_option = 5;

	for (int i = 0; i < 9; i++)
	{
		int counter = 0;
		int mat_size = mats[i].rows*mats[i].cols;
		for (int r_idx = 0; r_idx < mats[i].rows; r_idx++)
		{
			for (int c_idx = 0; c_idx < mats[i].cols; c_idx++)
			{
				int val = getMatrixValue(mats[i], r_idx, c_idx);

				if (val != 0)
					counter++;
			}
		}

		if (counter > most_free_space )
		{
			best_option = i;
			most_free_space = counter;
		}
		if(counter > mat_size)
			best_option = -1;
		cout << "val fo sub mat " << (i + 1) << " = " << counter << endl;
	}

	best_sub_matrix = best_option + 1;
}

