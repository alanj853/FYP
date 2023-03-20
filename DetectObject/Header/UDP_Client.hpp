#pragma once

/*#include <sys/types.h>
#include <unistd.h>
#include <sys/types.h>
#include <unistd.h>
#include <memory.h>
#include <errno.h>
#include <stdlib.h>*/
#include <iostream>
//#include <winsock.h>
// #include <winsock2.h>
#include <netinet/in.h>

using namespace std;

class UDP_Client
{
public:
	UDP_Client(const char* host, const char* port_no);
	UDP_Client();
	~UDP_Client();
	int print_out(int x);
	int resolvehelper(const char* hostname, int family, const char* service,
			sockaddr_storage* pAddr);
	string int_to_string(int i);
	string double_to_string(double d);
	void set_hostname(const char* h);
	void set_port(const char* p);
	string get_hostname();
	string get_port();
	int sendDataToServer(int x);
	int sendDataToServer(int x, int y, double area);
	void close_socket();

private:
	const char* hostname;
	const char* port;
	int sock;
};
