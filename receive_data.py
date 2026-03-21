import serial
import os.path
import time

ser = serial.Serial(port = 'COM3', baudrate = 9600)  #Open the serial port with the specified port and baud rate
header = "Time,Temperature (F),Pressure (hPa),Humidity (%),Gas (KOhms),Altitude (ft)\n"
attempt = 0

def write_data(data, timestamp, header, attempt):
    if os.path.exists("data.csv"):
            if attempt == 0:
                print("File exists") #On first attempt, check if file exists and print message. On subsequent attempts, skip this step to avoid redundant messages.

            with open("data.csv", "a") as file:
                file.write(timestamp + "," + data +"\n")  # Append the data to the CSV file

    else:
            if attempt == 0:
                print("File does not exist. Creating new file.") #On first attempt, check if file exists and print message. On subsequent attempts, skip this step to avoid redundant messages.
                
            with open("data.csv", "w") as file: #If the file does not exist, create a new file and write the header and data.
                file.write(header)
                file.write(timestamp + "," + data + "\n")

print("connected to " + ser.portstr)

while True:
    if ser.in_waiting > 0: # Check if there is data waiting to be read from the serial port
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        data = ser.readline().decode('utf-8').rstrip()  # Read a line of data and decode it
        write_data(data, timestamp, header, attempt) # Call the function to write the data to the CSV file
        
        attempt = 1 

    # Create a new CSV file and write the data