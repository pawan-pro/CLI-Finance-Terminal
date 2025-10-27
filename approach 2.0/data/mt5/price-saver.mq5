//+------------------------------------------------------------------+
//|                                         PriceDataExporter_v4.mq5 |
//|                                  Copyright 2025, Quantwater Tech |
//|                                      https://www.quantwater.tech |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantwater Tech"
#property link      "https://www.quantwater.tech"
#property version   "4.00" // Daily file creation logic added

//--- Global variable for the file handle
int ExtFileHandle = INVALID_HANDLE;

//--- [VALIDATED] Final list of 41 assets for the report ---
string ExtAssets[] =
  {
   // Indices (11) #Russell 2000 not presently available
   "US500m", "US30m", "USTECm","DE30m", "FR40m", "UK100m", "STOXX50m", "AUS200m", "JP225m", "HK50m", "IN50m",

   // Commodities (4)
   "XAUUSDm", "XAGUSDm", "USOILm", "XNGUSDm",

   // Crypto (6)
   "BTCUSDm", "ETHUSDm", "XRPUSDm", "ADAUSDm", "LTCUSDm", "SOLUSDm",

   // Forex (7)
   "EURUSDm", "USDJPYm", "GBPUSDm", "AUDUSDm", "USDCADm", "USDCHFm", "USDSEKm",

   // Key Stocks (13)
   "AAPLm", "MSFTm", "GOOGLm", "AMZNm", "NVDAm", "FBm", "JPMm", "BACm", "JNJm", "PFEm", "XOMm", "TSLAm", "MCDm"
  };

//+------------------------------------------------------------------+
//| Function to get the dynamic CSV filename (yyyymmdd.csv)          |
//+------------------------------------------------------------------+
string GetDailyCSVFileName()
  {
   // Get the current server time
   datetime currentTime = TimeCurrent();
   
   // Format the time to "yyyy.mm.dd"
   string dateString = TimeToString(currentTime, TIME_DATE);
   
   // Remove the dots to get "yyyymmdd"
   StringReplace(dateString, ".", "");
   
   // Return the final filename with the .csv extension
   return dateString + ".csv";
  }

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Set a timer to trigger every 60 seconds
   EventSetTimer(60);
   Print("PriceDataExporter v4.0 started. Tracking ", ArraySize(ExtAssets), " symbols.");
   Print("Data will be saved to a new file each day in MQL5\\Files\\ (format: yyyymmdd.csv).");
   
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Clean up the timer when the EA is stopped
   EventKillTimer();
   Print("PriceDataExporter v4.0 stopped.");
   
   // Ensure the file handle is closed if it was left open
   if(ExtFileHandle != INVALID_HANDLE)
     {
      FileClose(ExtFileHandle);
     }
  }

//+------------------------------------------------------------------+
//| Timer function - This is the main logic loop                     |
//+------------------------------------------------------------------+
void OnTimer()
  {
   // Get the filename for the current day
   string csvFileName = GetDailyCSVFileName();
   
   // Ensure the file for today exists and has a header.
   WriteHeaderIfNeeded(csvFileName);
   
   // Open the daily CSV file in append mode.
   ExtFileHandle = FileOpen(csvFileName, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(ExtFileHandle == INVALID_HANDLE)
     {
      Print("CRITICAL ERROR: Could not open ", csvFileName, " for writing. Error: ", GetLastError());
      return; // Stop this run if the file can't be opened
     }

   // Move the file pointer to the end of the file to append new data
   FileSeek(ExtFileHandle, 0, SEEK_END);

   MqlRates rates[1]; // Array to hold the bar data

   // Loop through every asset in our list
   for(int i = 0; i < ArraySize(ExtAssets); i++)
     {
      string symbol = ExtAssets[i];
      
      // Attempt to copy the most recently COMPLETED M1 bar
      if(CopyRates(symbol, PERIOD_M1, 1, 1, rates) > 0)
        {
         MqlRates latest_bar = rates[0];
         
         int symbol_digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);

         string time_str = TimeToString(latest_bar.time, TIME_DATE | TIME_MINUTES);
         string data_to_write =
           time_str + "," +
           symbol + "," +
           DoubleToString(latest_bar.open, symbol_digits) + "," +
           DoubleToString(latest_bar.high, symbol_digits) + "," +
           DoubleToString(latest_bar.low, symbol_digits) + "," +
           DoubleToString(latest_bar.close, symbol_digits) + "," +
           IntegerToString(latest_bar.tick_volume);

         FileWrite(ExtFileHandle, data_to_write);
        }
      else
        {
         Print("Could not get M1 rates for ", symbol, ". Error: ", GetLastError());
        }
     }

   // Close the file handle ONCE after all symbols have been processed.
   FileClose(ExtFileHandle);
   ExtFileHandle = INVALID_HANDLE;
   
   Print("Data for all ", ArraySize(ExtAssets), " assets processed and saved to ", csvFileName);
  }

//+------------------------------------------------------------------+
//| Function to write the CSV header if the file does not exist      |
//+------------------------------------------------------------------+
void WriteHeaderIfNeeded(string filename)
  {
   // Try to open for reading. If it fails, the file doesn't exist.
   int fileHandle = FileOpen(filename, FILE_READ, ',');

   if(fileHandle == INVALID_HANDLE) // File does not exist
     {
      Print("New day detected. Creating new file: ", filename);
      // Create the file and write the header
      fileHandle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
      if(fileHandle != INVALID_HANDLE)
        {
         FileWrite(fileHandle, "time", "symbol", "open", "high", "low", "close", "volume");
         FileClose(fileHandle); // Close it immediately after writing header
         Print("CSV header written successfully.");
        }
      else
        {
         Print("CRITICAL ERROR: Could not create ", filename, ". Error: ", GetLastError());
        }
     }
   else // File already exists
     {
      FileClose(fileHandle); // Just close it; we're ready to append.
     }
  }
//+------------------------------------------------------------------+