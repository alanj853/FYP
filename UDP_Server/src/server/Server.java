package server;

import java.io.*;
import java.net.DatagramSocket;

public class Server {

	
    public Server(int port)
    {
        try {
        	if (port < 2000 || port >60000)
        		port  = 54000;
            DatagramSocket socket = new DatagramSocket(port);
            System.out.println("Message From Server: Waiting for connection...");

            Thread t = new Thread(new ServerThread(socket, port));
            t.start();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
    	//int port  = Integer.parseInt(args[0]);
    	int port = 4446;
        Server myServer = new Server(port);
    }
}