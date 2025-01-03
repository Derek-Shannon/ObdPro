import datetime
import math, obd, time

class ObdPro:
    def __init__(self):
        self.port = "/dev/ttyUSB0"
        self.connection = None
        self.connect()

        self.f = open("output.txt", "a")
        self.names = []
        self.querryReferences = []
        self.querryOutput = []

    def connect(self):
        while True:
            try:
                # Attempt to connect to the OBD-II device
                self.connection = obd.OBD(self.port)  # Adjust port for Windows
                status = self.connection.status()
                
                if status != obd.OBDStatus.NOT_CONNECTED:  # Check if connected
                    print(f"Connection successful! Status: {status}")
                    break  # Exit the loop once connected
                else:
                    print(f"Connection status: {status}, retrying...")
            except Exception as e:
                print(f"Error connecting: {e}, retrying...")
            print("")
            time.sleep(2)  # Wait for 2 seconds before retrying

    def addValue(self, name: str, querryReference):
        self.names.append(name)
        self.querryReferences.append(querryReference)
        self.querryOutput.append(None)
    def _getNameString(self):
        string = "Day Time "
        for name in self.names:
            string += ""+name+" "
        return string + "\n"
    def _getDataString(self):
        string = ""
        for i in range(len(self.querryReferences)):
            self.querryOutput[i] = self.connection.query(self.querryReferences[i])
            self.querryOutput[i] = str(self.querryOutput[i]).strip().split()[0]
            #removes extra wording on data
            string += str(self.querryOutput[i]+"          ")[:10] + " " #new code!! limit data
        return string + "\n"
    def getQuerruOutput(self, name: str) -> str:
        return self.queryOutput[self.names.index(name)]
    def displayLoop(self):
        #Header
        string = self._getNameString()
        print(f"{string}")
        self.f.write(string)
        self.f.close()
        #Data
        while True:
            self.f = open("output.txt", "a")
            string = self._getDataString()

            now = datetime.datetime.now()
            self.f.write(now.strftime("%Y-%m-%d %H:%M:%S "))
            print(f"{string}")
            self.f.write(string)
            self.f.close()
            time.sleep(1)
        #closing data
        self.f.write("\n")
        self.f.close()

#main
obdPro = ObdPro()
obdPro.addValue("Speed", obd.commands.SPEED)
obdPro.addValue("Rpm", obd.commands.RPM)
obdPro.addValue("Engine_Load", obd.commands.ENGINE_LOAD)
obdPro.addValue("MAF", obd.commands.MAF)
obdPro.addValue("Intake_Temp", obd.commands.INTAKE_TEMP)
obdPro.addValue("Ambiant_Air_Temp", obd.commands.AMBIANT_AIR_TEMP)
#obdPro.addValue("Barometric_Pressure", obd.commands.BAROMETRIC_PRESSURE)
obdPro.addValue("Coolant_temp", obd.commands.COOLANT_TEMP)
obdPro.addValue("Spark_adv", obd.commands.TIMING_ADVANCE)


obdPro.displayLoop()