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
	//private String y_coor = "Not assigned";

	public ServerThread(DatagramSocket socket, int port) throws IOException {
		this.socket = socket;
		this.current_port = port;

	}

	public void run() {
		while (!shutdown_signal) {
			try {
				System.out.println("Waiting for connection");
				String incoming_message = receive();
				if (incoming_message.contains("CPP:Client") && !shutdown_signal)
					setCoordinates(incoming_message);
				else if (incoming_message.contains("CF:Client-Request_Coordinates"))
					sendReply(bestMatrix);
				else
					sendReply("I don't know you");

			} catch (Exception e) {
				System.err.println(e.getMessage());
				socket.close();
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
