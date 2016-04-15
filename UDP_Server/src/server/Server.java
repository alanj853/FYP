package server;

import java.io.*;
import java.net.DatagramSocket;

public class Server {

	
    public Server(int port)
    {
        try {
        	DatagramSocket socket = new DatagramSocket(port);
            System.out.println("Message From Server: Waiting for connection...");

            Thread t = new Thread(new ServerThread(socket, port));
            t.start();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // main method. User can pass in a single argument to the program. Must be a number between 2000 and 60000
    public static void main(String[] args) throws IOException {
    	int port = 54000;
    	try{
    		int x  = Integer.parseInt(args[0]);
    		port = x;
    		if (port < 2000 || port > 60000){
    			System.out.println("Port must be between 2000 - 60000");
    			port = 54000;
    		}
    	}
    	catch(NullPointerException | ArrayIndexOutOfBoundsException e){
    		System.out.println("No value entered.");
    	}
    	System.out.println("Using port Number: " + port);
    	Server myServer = new Server(port);

        
    }
}
