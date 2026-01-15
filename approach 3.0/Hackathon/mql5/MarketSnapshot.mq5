//+------------------------------------------------------------------+
//|                                           MarketSnapshot.mq5     |
//|             Aggressive Sync Exporter for Quantwater Lake         |
//+------------------------------------------------------------------+
#property copyright "Quantwater Tech"
#property strict

input int BarsToExport = 96; 

input string FX_Pairs = "EURUSD.sd,GBPUSD.sd,USDJPY.sd,USDCHF.sd,AUDUSD.sd,NZDUSD.sd,USDCAD.sd,EURJPY.sd,GBPJPY.sd,AUDJPY.sd,EURGBP.sd,USDCNH.sd,USDMXN.sd,USDNOK.sd,USDSEK.sd,USDZAR.sd,NZDJPY.sd,CADJPY.sd,CHFJPY.sd";
input string Indices = "US500Roll,UT100Roll,US30Roll,DE40Roll,JP225Roll,HK50Roll,UK100Roll,VIXRoll";
input string Commodities = "XAUUSD.sd,XAGUSD.sd,USOILRoll,UKOILRoll,XPTUSD.sd";
input string Stocks = "Apple,Microsoft,NVIDIA,Tesla,Amazon,Facebook,Alphabet,Boeing,CAT,Chevron,Exxon,CME,Citigroup";
input string Crypto = "BTCUSD.lv,ETHUSD.lv,SOLUSD.lv,LINKUSD.lv,DOGEUSD.lv";

void OnStart() {
   string all_symbols[];
   string lists[] = {FX_Pairs, Indices, Commodities, Stocks, Crypto};
   for(int l=0; l<ArraySize(lists); l++) {
      string temp[];
      int n = StringSplit(lists[l], ',', temp);
      int prev_size = ArraySize(all_symbols);
      ArrayResize(all_symbols, prev_size + n);
      ArrayCopy(all_symbols, temp, prev_size, 0, WHOLE_ARRAY);
   }

   datetime to = TimeCurrent();
   string timestamp = TimeToString(to, TIME_DATE|TIME_MINUTES);
   StringReplace(timestamp, ":", ""); StringReplace(timestamp, ".", ""); StringReplace(timestamp, " ", "_");

   int success = 0; int fail = 0;
   Print("🚀 Starting Aggressive Snapshot for ", ArraySize(all_symbols), " symbols...");

   for(int i=0; i<ArraySize(all_symbols); i++) {
      string sym = all_symbols[i];
      StringTrimLeft(sym); StringTrimRight(sym);

      if(!SymbolSelect(sym, true)) { fail++; continue; }
      
      MqlRates rates[];
      ArraySetAsSeries(rates, true);
      int copied = 0;
      int retries = 3;

      // AGGRESSIVE SYNC: Force broker to send latest bars
      while(retries > 0) {
         copied = CopyRates(sym, PERIOD_M15, 0, BarsToExport, rates);
         // Check if latest bar is within 1 hour of server time
         if(copied > 0 && rates[0].time >= to - 3600) break; 
         
         Print("⏳ ", sym, " stale. Forcing refresh (Retry ", 4-retries, ")...");
         MqlRates tmp[]; CopyRates(sym, PERIOD_H1, 0, 1, tmp); // Forces server handshake
         Sleep(1000); 
         retries--;
      }

      if(copied < 10) {
         Print("❌ REJECTED: ", sym, " - History download failed.");
         fail++; continue;
      }

      string file = sym + "_M15_" + timestamp + ".csv";
      int handle = FileOpen(file, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
      if(handle != INVALID_HANDLE) {
         FileWrite(handle, "time_gmt", "open", "high", "low", "close", "vol", "spread");
         int digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
         for(int j=0; j<copied; j++) {
            FileWrite(handle, TimeToString(rates[j].time, TIME_DATE|TIME_MINUTES), 
               DoubleToString(rates[j].open, digits), DoubleToString(rates[j].high, digits), 
               DoubleToString(rates[j].low, digits), DoubleToString(rates[j].close, digits), 
               (string)rates[j].tick_volume, (string)SymbolInfoInteger(sym, SYMBOL_SPREAD));
         }
         FileClose(handle);
         success++;
      }
   }
   Print("🏁 Snapshot Complete. ✅ Success: ", success, " ❌ Failed: ", fail);
}