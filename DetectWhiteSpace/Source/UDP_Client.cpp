#include <UDP_Client.hpp>

#include <sys/types.h>
#include <unistd.h>
#include <sys/types.h>
#include <unistd.h>
#include <memory.h>
#include <errno.h>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <string>
#include <winsock.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>


UDP_Client::UDP_Client(const char* host, const char* port_no) {
	port = port_no;
	hostname = host;
}

UDP_Client::UDP_Client() {
}

UDP_Client::~UDP_Client() {

}

int UDP_Client::resolvehelper(const char* hostname, int family,
		const char* service, sockaddr_storage* pAddr) {
	int result;
	addrinfo* result_list = NULL;
	addrinfo hints = { };
	hints.ai_family = family;
	hints.ai_socktype = SOCK_DGRAM; // without this flag, getaddrinfo will return 3x the number of addresses (one for each socket type).
	result = getaddrinfo(hostname, service, &hints, &result_list);
	if (result == 0) {
		//ASSERT(result_list->ai_addrlen <= sizeof(sockaddr_in));
		memcpy(pAddr, result_list->ai_addr, result_list->ai_addrlen);
		freeaddrinfo(result_list);
	}

	return result;
}

int UDP_Client::run(int best_matrix_pos) {
	int result = 0;
	sock = socket(AF_INET, SOCK_DGRAM, 0);

	char szIP[100];

	sockaddr_in addrListen = { }; // zero-int, sin_port is 0, which picks a random port for bind.
	addrListen.sin_family = AF_INET;
	cout << addrListen.sin_family << endl;
	cout << sizeof(addrListen) << endl;
	result = bind(sock, (sockaddr*) &addrListen, sizeof(addrListen));
	if (result == -1) {
		int lasterror = WSAGetLastError();
		std::cout << "error: " << lasterror;
		exit(1);
	}

	sockaddr_storage addrDest = { };
	result = resolvehelper(hostname, AF_INET, port, &addrDest);
	if (result != 0) {
		int lasterror = 0;
		std::cout << "error: " << lasterror;
		exit(1);
	}



	string best_matrix = "<x=" + int_to_string(best_matrix_pos) + ";>" ;
	string header = "<CPP:Client>";

	string message = header + best_matrix;
	const char* msg = message.c_str();

	size_t msg_length = strlen(msg);

	result = sendto(sock, msg, msg_length, 0, (sockaddr*) &addrDest,
			sizeof(addrDest));

	//cout << result << " Message sent: " << message << endl;

	//return 0;

}

int UDP_Client::print_out(int x) {
	cout << "This is bestMatrix: " << x <<endl;
	return 0;
}

string UDP_Client::int_to_string(int i) {
	stringstream strs;
	strs << i;
	string string = strs.str();
	return string;
}

void UDP_Client::set_port(const char* p) {
	port = p;
}

void UDP_Client::set_hostname(const char* h) {
	hostname = h;
}

string UDP_Client::get_port() {
	return port;
}

string UDP_Client::get_hostname() {
	return hostname;
}

void UDP_Client::close_socket(){
	closesocket(sock);
	    WSACleanup();
}

int UDP_Client::create_new_socket(int best_matrix_pos){

	int BUFLEN = 512;
	unsigned short int PORT = 4446;
	const char* SERVER = "127.0.0.1";


	 struct sockaddr_in si_other;
	    int s, slen=sizeof(si_other);
	    char buf[BUFLEN];
	    //char message[BUFLEN];
	    WSADATA wsa;

	    //Initialise winsock
	    printf("\nInitialising Winsock...");
	    if (WSAStartup(MAKEWORD(2,2),&wsa) != 0)
	    {
	        printf("Failed. Error Code : %d",WSAGetLastError());
	        exit(EXIT_FAILURE);
	    }
	    printf("Initialised.\n");

	    //create socket
	    if ( (s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == SOCKET_ERROR)
	    {
	        printf("socket() failed with error code : %d" , WSAGetLastError());
	        exit(EXIT_FAILURE);
	    }

	    //setup address structure
	    memset((char *) &si_other, 0, sizeof(si_other));
	    si_other.sin_family = AF_INET;
	    si_other.sin_port = htons(PORT);
	    si_other.sin_addr.S_un.S_addr = inet_addr(SERVER);


	    string best_matrix = "<x=" + int_to_string(best_matrix_pos) + ";>" ;
	    	string header = "<CPP:Client>";

	    	string message = header + best_matrix;
	    	const char* msg = message.c_str();

	    //start communication
	    //while(1)
	    {

	        //send the message
	        if (sendto(s, msg, strlen(msg) , 0 , (struct sockaddr *) &si_other, slen) == SOCKET_ERROR)
	        {
	            printf("sendto() failed with error code : %d" , WSAGetLastError());
	            exit(EXIT_FAILURE);
	        }

	        //receive a reply and print it
	        //clear the buffer by filling null, it might have previously received data
	       /* memset(buf,'\0', BUFLEN);
	        //try to receive some data, this is a blocking call
	        if (recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *) &si_other, &slen) == SOCKET_ERROR)
	        {
	            printf("recvfrom() failed with error code : %d" , WSAGetLastError());
	            exit(EXIT_FAILURE);
	        }

	        puts(buf);*/
	    }

	    closesocket(s);
	    WSACleanup();

	    return 0;
}





































