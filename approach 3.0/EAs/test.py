//+------------------------------------------------------------------+
//| Export_EURUSDsd_M15_Windows.mq5                                   |
//| Exports EURUSD.sd M15 OHLCV for last N hours into CSV             |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs

input string InpSymbol = "EURUSD.sd";
input ENUM_TIMEFRAMES InpTF = PERIOD_M15;

void OnStart()
{
   int windows[] = {1,2,4,6,12,24};

   // Use GMT timestamps for consistent downstream processing
   datetime t_to   = TimeGMT();                 // [web:72]
   string ts       = TimeToString(t_to, TIME_DATE|TIME_MINUTES);
   StringReplace(ts, ".", "");
   StringReplace(ts, ":", "");
   StringReplace(ts, " ", "_");

   string filename = InpSymbol + "_M15_windows_" + ts + "GMT.csv";
   int fh = FileOpen(filename, FILE_WRITE|FILE_CSV);   // [web:71]
   if(fh == INVALID_HANDLE)
   {
      Print("FileOpen failed. error=", GetLastError());
      return;
   }

   // Header
   FileWrite(fh, "symbol","timeframe","window_hours","time_gmt","open","high","low","close","tick_volume","spread"); // [web:71]

   for(int wi=0; wi<ArraySize(windows); wi++)
   {
      int h = windows[wi];
      datetime t_from = t_to - (h * 3600);

      MqlRates rates[];
      int copied = CopyRates(InpSymbol, InpTF, t_from, t_to, rates); // [web:70]
      if(copied <= 0)
      {
         Print("CopyRates failed for window=", h, "h. error=", GetLastError());
         continue;
      }

      for(int i=0; i<copied; i++)
      {
         // Write each bar
         FileWrite(
            fh,
            InpSymbol,
            "M15",
            h,
            TimeToString(rates[i].time, TIME_DATE|TIME_MINUTES),
            rates[i].open,
            rates[i].high,
            rates[i].low,
            rates[i].close,
            (long)rates[i].tick_volume,
            (int)rates[i].spread
         ); // [web:71]
      }
   }

   FileClose(fh);
   Print("Export complete: ", filename, " (saved in MQL5/Files)");
}
