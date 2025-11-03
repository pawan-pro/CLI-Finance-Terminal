//+------------------------------------------------------------------+
//|                                         PriceDataExporter_v4.mq5 |
//|                                  Copyright 2025, Quantwater Tech |
//|                                      https://www.quantwater.tech |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, Quantwater Tech"
#property link      "https://www.quantwater.tech"
#property version   "4.01" // Updated for Equiti standard account symbols (.sd suffix)

//--- Global variable for the file handle
int ExtFileHandle = INVALID_HANDLE;

//--- [VALIDATED] Final list of 41 assets for Equiti Standard Account (.sd suffix for forex, .lv for stocks/crypto, rolling indices/commodities)
// Indices use rolling contract notation "Roll" suffix where applicable
string ExtAssets[] =
  {
   // Indices (11)
   "US500Roll", "US30Roll", "UT100Roll", "DE40Roll", "FRA40Roll", "UK100Roll", "EU50Roll", "AUS200Roll", "JP225Roll", "HK50Roll", "India50Roll",

   // Commodities (4)
   "XAUUSD", "XAGUSD", "USOILRoll", "NGDec25", "XPTUSD",  // Natural Gas quarterly contract, confirm symbol on your platform

   // Volatility Indices (3)
   "VIXRoll", 
   // Crypto (6) - .lv suffix
   "BTCUSD.lv", "ETHUSD.lv", "XRPUSD.lv", "ADAUSD.lv", "LTCUSD.lv", "SOLUSD.lv",

   // Forex (7) - .sd suffix
   "EURUSD.sd", "USDJPY.sd", "GBPUSD.sd", "AUDUSD.sd", "USDCAD.sd", "USDCHF.sd", "USDSEK.sd",

   // Key Stocks (13) - .lv suffix
   "Apple", "Microsoft", "Alphabet", "Amazon", "NVIDIA", "Tesla", "Facebook", "JPMorgan", "Johnson&Johnson", "Walmart", "Visa", "Procter&Gamble", "Mastercard", "Disney","McDonalds"
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
   Print("PriceDataExporter v4.01 started. Tracking ", ArraySize(ExtAssets), " symbols.");
   Print("Data will be saved to a new file each day in MQL5\\Files\\ (format: yyyymmdd.csv).");
   Print("Configured for Equiti Standard Account symbols (.sd for forex, .lv for stocks/crypto).");
   
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Clean up the timer when the EA is stopped
   EventKillTimer();
   Print("PriceDataExporter v4.01 stopped.");
   
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
   string csvFileName = GetDailyCSVFileName();
   WriteHeaderIfNeeded(csvFileName);
   
   ExtFileHandle = FileOpen(csvFileName, FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(ExtFileHandle == INVALID_HANDLE)
     {
      Print("CRITICAL ERROR: Could not open ", csvFileName, " for writing. Error: ", GetLastError());
      return;
     }

   FileSeek(ExtFileHandle, 0, SEEK_END);

   MqlRates rates[1];

   for(int i = 0; i < ArraySize(ExtAssets); i++)
     {
      string symbol = ExtAssets[i];
      
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

   FileClose(ExtFileHandle);
   ExtFileHandle = INVALID_HANDLE;
   
   Print("Data for all ", ArraySize(ExtAssets), " assets processed and saved to ", csvFileName);
  }

//+------------------------------------------------------------------+
//| Function to write the CSV header if the file does not exist      |
//+------------------------------------------------------------------+
void WriteHeaderIfNeeded(string filename)
  {
   int fileHandle = FileOpen(filename, FILE_READ, ',');

   if(fileHandle == INVALID_HANDLE)
     {
      Print("New day detected. Creating new file: ", filename);
      fileHandle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
      if(fileHandle != INVALID_HANDLE)
        {
         FileWrite(fileHandle, "time", "symbol", "open", "high", "low", "close", "volume");
         FileClose(fileHandle);
         Print("CSV header written successfully.");
        }
      else
        {
         Print("CRITICAL ERROR: Could not create ", filename, ". Error: ", GetLastError());
        }
     }
   else
     {
      FileClose(fileHandle);
     }
  }
//+------------------------------------------------------------------+



