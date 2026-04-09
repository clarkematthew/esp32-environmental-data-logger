import serial
import os.path
import time
import pandas as pd
import os

ser = serial.Serial(port = 'COM3', baudrate = 9600)  #Open the serial port with the specified port and baud rate
header = "Time,Temperature (F),Pressure (hPa),Humidity (%),Gas (KOhms),Altitude (ft)\n"

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

def archive_data(df=pd.DataFrame(), quartile_size=int, columns=list):
    quartiles = [
        df.iloc[0:quartile_size],
        df.iloc[quartile_size:2*quartile_size],
        df.iloc[2*quartile_size:3*quartile_size],
        df.iloc[3*quartile_size:]
    ]

    date = df.tail(1)["Time"].iloc[0][:10]
    archive_lines = ["Date:," + date + "\n"]  # Newest archive block goes first, like pushing onto a stack.
    for i, quartile in enumerate(quartiles):
        means = []
        for column in columns:
            mean = quartile[column].mean() #Calculate the mean of the current column in the current quartile
            means.append(mean) 
        archive_lines.append(f"Quartile {i+1}," + ",".join(map(str, means)) + "\n")

    if os.path.exists("archive.csv"):
        with open("archive.csv", "r") as file:
            existing_contents = file.read()
    else:
        existing_contents = ""

    with open("archive.csv", "w") as file:
        file.writelines(archive_lines)
        file.write(existing_contents)

    # os.remove("data.csv") #Remove the original CSV file after archiving the data to start fresh with a new file for incoming data.
    #Call the function to check if the data needs to be archived based on the dates of the last two entries in the CSV file.

def reset_data_file_for_new_day(latest_row, header):
    if os.path.exists("data.csv"):
        os.remove("data.csv")

    row_values = [str(value) for value in latest_row.tolist()]
    with open("data.csv", "w") as file:
        file.write(header)
        file.write(",".join(row_values) + "\n")

def main():
    attempt = 0
    while True:
        
        if ser.in_waiting > 0: # Check if there is data waiting to be read from the serial port
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            data = ser.readline().decode('utf-8').rstrip()  # Read a line of data and decode it
            write_data(data, timestamp, header, attempt) # Call the function to write the data to the CSV file
            
            attempt = 1

        if not os.path.exists("archive.csv"):
            with open("archive.csv", "w"):
                pass

        df= pd.read_csv("data.csv") 
        if not os.path.exists("archive.csv") or os.path.getsize("archive.csv") == 0:
            archive_df = pd.DataFrame()
        else:
            archive_df = pd.read_csv("archive.csv")
        current_date = df.tail(1)["Time"].iloc[0][:10]
        previous_date = df.iloc[-2]["Time"][:10] if len(df) > 1 else current_date
        with open("archive.csv", "r") as file:
            lines = file.readlines()

        if len(lines) == 0:
            archive_date = None
        else:
            archive_date = lines[0].split(",")[1].strip()
        
        number_of_rows = df.shape[0] #Get the number of rows in the CSV file to determine if it is empty or not.
        quartile_size = len(df) // 4 #Calculate the size of each quartile based on the total number of rows in the CSV file.
        columns = df.columns[1:] #Get the column names from the DataFrame, excluding the first column which is the timestamp.

        if current_date != previous_date and current_date != archive_date:
            previous_day_df = df.iloc[:-1].copy()

            if not previous_day_df.empty:
                previous_day_quartile_size = len(previous_day_df) // 4
                archive_data(previous_day_df, previous_day_quartile_size, columns)
                reset_data_file_for_new_day(df.iloc[-1], header)
                continue
        elif archive_date is None:
            archive_data(df, quartile_size, columns)
        
        
        pass
      
        # If the date of the second to last entry is different from the date of the last entry, call the function to archive the data and start a new file for incoming data.

if __name__ == "__main__":
    main()
print("connected to " + ser.portstr) #pring to console



    # Create a new CSV file and write the data
