mcl_USB_To_IO_64.dll - ActiveX COM Object for programmers

This DLL file can be used by programmers of Visual Basic,VC++,Delphi,C#
LabView or any other program that support ActiveX COM Object DLL file.

mcl_USB_To_IO_64.dll file should be referenced to the program project.

The DLL file include the following methods:

1. int Connect(Optional *string SN)  :

SN parameter is needed in case of using more than 1 Switch Box.
SN is the Serial Number of the Switch Box and can be ignored if using only one box.


2. void Disconnect()

Recommanded to Disconnect the device while end of program


3. Int Get_Available_SN_List(string SN_List)

string SN_List is returned with all avaliable line stretchers connected to USB.
the function return the Number of line stretchers.

4. int GetStatus()

Function return the connection status. when connected , status is >0.

5. int Read_ModelName(string ModelName) As Integer
The Model Name returned in ModelName parameter.
function return non zero number on success.

6. int Read_SN(string SN ) 
The Serial Number returned in SN parameter.
The function return non zero number on success.
if success function return non zero number.

7. int Set_ByteA(val As Byte)
Set entire Byte A (A0 to A7) with val  .
if success function return non zero number.

8. int Set_ByteB(val As Byte)
Set entire Byte B (B0 to B7) with val  .
if success function return non zero number.

9. int Set_ByteA_As_Output()
Config the entire byte A as Output Byte. Output is the Default configuration
if success function return non zero number.

10. int Set_ByteA_As_Input()
Config the entire byte A as Input Byte.
if success function return non zero number.

11. int Set_ByteB_As_Output()
Config the entire byte B as Output Byte. Output is the Default configuration
if success function return non zero number.

12. int Set_ByteB_As_Input()
Config the entire byte B as Input Byte.
if success function return non zero number.

13 int Set_Relay(int RelayNo , int On_OFF)
Set RelayNo ( from 0 to 7 ) to  On_OFF state ( can be 0 or 1).  1-Common to NO 0=Common to NC
if success function return non zero number.

14 int Set_RelayByte(Byte val)
Set the entire Relays byte (0 to 7) with the val. 
Example: Set_RelayByte(25) will set ON relays:0,3 and 4.
if success function return non zero number.

15 int Set_TTLBit(string BitName, int BitVal). Example: Set_TTLBit("B3",1) 
BitName is the specific Bit can be "A0","A1",..."A7","B0","B1",..."B7".
BitVal can be 1 to setthe Bit in High Logic or 0 to set the bit Logic Low. 
if success function return non zero number.

16. int Set_SPI_PulseWidth(int PulsWidth )
Set the pulse width of Clock, Data and LE in micro seconds.
PulsWidth cab be any integer number from 0 to 255.
if success function return non zero number.


17. int SPI_OUT(string ClockBit,string DataBit,string LEBit,string RegData)
Send SPI Data:
ClockBit is the Bit for the clock for Example "B0"
DataBit  is the bit for the data  for example: "B1"
LEBit is the Bit for the LE  for example: "B3"
RegData string represents the binary value of the data to send. example: "0110011101"
if success function return non zero number.

18. int SPI_OUT_Trigg(string RegData,int Trigger)
Send SPI Data with trigger bit that will rise and fall same time with LE.
SPI_OUT_Trigg uses the following bits: B0 for Clock. B1 for Data. B2 for LE. B3 for the trigger.
RegData string represents the binary value of the data to send. example: "0110011101"
Trigger parameter should be 1 if trigger is required and 0 if trigger is not required.
if success function return non zero number.

19. int GetByte( string ByteName As String, byte ReturnedByteVal)
GetByte - receive the value of byte.
ByteName should containg the requested Byte name example: "B"
ReturnedByteVal - string returned with the byte value.
if success function return non zero number.
Example: GetByte("B",RetVal)

20. int Read_Relays_Byte(byte RetVal )
Reading the Relays Byte status - (all 8 relays status).
RetVal the returned value of the relays byte.
if success function return non zero number.

21. int ReadBit(string BitRequest, Byte Ret_BitVal )
Reading the value of specific bit.
BitRequest should have the requested Bit eg: "A5"
Ret_BitVal returned with the Bit value 1 if logic high 0 if logic low.
if success function return non zero number.
example: ReadBit("B0",RetBit)

22. int ReadByteA(byte Ret_ByteVal )
Read the value of byteA
Ret_ByteVal is the returned value of byte A
if success function return non zero number.

23. int ReadByteB(byte Ret_ByteVal )
Read the value of byteB
Ret_ByteVal is the returned value of byte B
if success function return non zero number.



program Example in VB:

Dim IO1 As New mcl_USB_To_IO_64.USB_IO,Status as integer
Status=IO1.Connect
Status = IO1.Set_Relay(5,1) ' Set Relay5 ON
IO1.Disconnect

 

program Example in Visual C++:

mcl_USB_To_IO_64::USB_IO ^IO1 = gcnew mcl_USB_To_IO_64::USB_IO();
short Status = 0;
System::String ^SN = "";
Status = IO1->Connect(SN);
Statuse=IO1->Set_Relay(5,1);
IO1->Disconnect();




      