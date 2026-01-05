//+------------------------------------------------------------------+
//|                                           MarketSnapshot.mq5     |
//|                    Exports M15 bars for the Core 50 Universe     |
//+------------------------------------------------------------------+
#property copyright "Quantwater Tech"
#property strict

// Define your winning universe here based on your metadata analysis
input string SymbolsList = "EURUSD.sd,GBPUSD.sd,USDJPY.sd,US500Roll,UT100Roll,XAUUSD.sd,USOILRoll,AAPL,NVDA,TSLA";

void OnStart() {
   string symbols[];
   StringSplit(SymbolsList, ',', symbols);
   datetime to = TimeCurrent();
   datetime from = to - (24 * 3600); // 24 Hour Lookback
   
   string timestamp = TimeToString(to, TIME_DATE|TIME_MINUTES);
   StringReplace(timestamp, ":", ""); StringReplace(timestamp, ".", "");

   for(int i=0; i<ArraySize(symbols); i++) {
      string sym = symbols[i];
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      
      int copied = CopyRates(sym, PERIOD_M15, from, to, rates);
      if(copied <= 0) { Print("Failed for ", sym); continue; }

      string file = sym + "_M15_" + timestamp + ".csv";
      int handle = FileOpen(file, FILE_WRITE|FILE_CSV|FILE_ANSI);
      
      if(handle != INVALID_HANDLE) {
         FileWrite(handle, "time_gmt,open,high,low,close,vol,spread");
         for(int j=0; j<copied; j++) {
            FileWrite(handle, TimeToString(rates[j].time), rates[j].open, rates[j].high, rates[j].low, rates[j].close, rates[j].tick_volume, SymbolInfoInteger(sym, SYMBOL_SPREAD));
         }
         FileClose(handle);
         Print("Saved: ", file);
      }
   }
}