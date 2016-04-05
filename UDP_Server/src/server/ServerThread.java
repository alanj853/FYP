package server;

import java.io.*;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.DatagramPacket;

public class ServerThread extends Thread {

	protected DatagramSocket socket = null;
	private String hostname = "127.0.0.1";
	private int current_port = 0;
	private boolean shutdown_signal = false;
	private String bestMatrix = "Not assigned";
	// private String y_coor = "Not assigned";
	private String xErr = "0";
	private String yErr = "0";
	private String objectArea = "0";
	String error = "";

	public ServerThread(DatagramSocket socket, int port) throws IOException {
		this.socket = socket;
		this.current_port = port;
		System.out.println("Socket running on port " + port);

	}

	public void run() {
		while (!shutdown_signal) {
			try {
				System.out.println("Waiting for connection");
				String incoming_message = receive();
				if (incoming_message.contains("CPP:Client") && !shutdown_signal) {
					if (incoming_message.contains("DetectWhiteSpace"))
						setCoordinates(incoming_message);
					else if (incoming_message.contains("DetectObject")) {
						setXerror(incoming_message);
						setYerror(incoming_message);
						setObjectArea(incoming_message);
					} else
						System.out.println("Unknow Cpp request");

				} else if (incoming_message.contains("CF:Client-Request_DetectWhiteSpace"))
					sendReply(bestMatrix);
				 else if (incoming_message.contains("CF:Client-Request_DetectObject_Xerr"))
						sendReply(xErr);
				 else if (incoming_message.contains("CF:Client-Request_DetectObject_Yerr"))
						sendReply(yErr);
				 else if (incoming_message.contains("CF:Client-Request_DetectObject_ObjectArea"))
						sendReply(objectArea);
				
				else 
					sendReply("I don't know you");

			} catch (Exception e) {
				System.err.println(e.getMessage());
				error = e.getMessage();
				socket.close();
				shutdown_signal = true;
			}
				
		}
		socket.close();

	}

	private void setCoordinates(String string) throws IOException, ArrayIndexOutOfBoundsException {
		String x = "";
		String[] arr = string.split("");
		for (int i = 0; i < arr.length; i++) {
			if (arr[i].equals("x")) {
				int j = i + 2;
				while (!arr[j].equals(";")) {
					x = x + arr[j];
					j++;
				}
			}
		}
		this.bestMatrix = x;
		sendReply("Set bestMatrix = " + bestMatrix);
	}

	private void setXerror(String string) throws IOException {
		String x = "";
		String[] arr = string.split("");
		for (int i = 0; i < arr.length; i++) {
			if (arr[i].equals("x")) {
				int j = i + 2;
				while (!arr[j].equals(";")) {
					x = x + arr[j];
					j++;
				}
			}
		}
		this.xErr = x;
		sendReply("Set xErr = " + xErr);
	}

	private void setYerror(String string) throws IOException {
		String y = "";
		String[] arr = string.split("");
		for (int i = 0; i < arr.length; i++) {
			if (arr[i].equals("y")) {
				int j = i + 2;
				while (!arr[j].equals(";")) {
					y = y + arr[j];
					j++;
				}
			}
		}
		this.yErr = y;
		sendReply("Set yErr = " + yErr);
	}
	
	private void setObjectArea(String string) throws IOException {
		String a = "";
		String[] arr = string.split("");
		for (int i = 0; i < arr.length; i++) {
			if (arr[i].equals("a")) {
				int j = i + 2;
				while (!arr[j].equals(";")) {
					a = a + arr[j];
					j++;
				}
			}
		}
		this.objectArea = a;
		sendReply("Set Area = " + objectArea);
	}

	private void sendReply(String reply_message) throws IOException {
		// this.socket = new DatagramSocket();

		// sending file itself

		byte[] buf = new byte[1024];
		buf = reply_message.getBytes();
		InetAddress address = InetAddress.getByName(hostname);
		DatagramPacket packet2 = new DatagramPacket(buf, buf.length, address, current_port);
		System.out.println("Sending " + reply_message);

		socket.send(packet2);
		System.out.println("Sent " + reply_message);

	}

	// MEthod to tell server whether it is receiving a file or sending one
	public String receive() throws IOException {

		String message = null;
		byte[] buf = new byte[1024];
		DatagramPacket packet = new DatagramPacket(buf, buf.length);
		socket.receive(packet);
		message = new String(packet.getData(), 0, packet.getLength());
		this.current_port = packet.getPort();
		System.out.println("Updated port to " + this.current_port);
		System.out.println("Got " + message);

		if (message.contains("CPP:Client:shutdown"))
			this.shutdown_signal = true;
		return message;

	}
}
