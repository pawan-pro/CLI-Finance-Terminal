//+------------------------------------------------------------------+
//|                                   SymbolDiscovery_Exporter.mq5   |
//|                           Quantwater Tech - Market Data Lake     |
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Quantwater Tech"
#property version   "1.00"
#property description "Export all available symbols with metadata for data lake ingestion"

//--- Input parameters
input bool ExportAllSymbols = true;          // Export all symbols (false = Market Watch only)
input string OutputFilePrefix = "SymbolMetadata"; // Output file prefix
input bool IncludeSpreadStats = true;        // Include spread statistics
input bool IncludeSessionInfo = true;        // Include trading session info
input bool FilterByAssetClass = false;       // Filter symbols by asset class
input string AssetClassFilter = "FX,INDEX,COMMODITY,STOCK,ETF"; // Comma-separated classes

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("SymbolDiscovery_Exporter initialized");
   Print("Ready to export symbol metadata on demand");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert tick function (runs export on first tick)                  |
//+------------------------------------------------------------------+
void OnTick()
{
   static bool exported = false;
   if(!exported)
   {
      ExportSymbolMetadata();
      exported = true;
      Print("Export completed. Remove EA from chart or restart for new export.");
   }
}

//+------------------------------------------------------------------+
//| Main export function                                              |
//+------------------------------------------------------------------+
void ExportSymbolMetadata()
{
   datetime now = TimeCurrent();
   string timestamp = TimeToString(now, TIME_DATE|TIME_MINUTES);
   timestamp = StringReplace(timestamp, ":", "");
   timestamp = StringReplace(timestamp, ".", "");
   timestamp = StringReplace(timestamp, " ", "_");
   
   string filename = OutputFilePrefix + "_" + timestamp + "_GMT.csv";
   
   int file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
   
   if(file_handle == INVALID_HANDLE)
   {
      Print("Error opening file: ", GetLastError());
      return;
   }
   
   // Write header
   WriteCSVHeader(file_handle);
   
   // Get total number of symbols
   int total_symbols = SymbolsTotal(ExportAllSymbols ? false : true);
   Print("Total symbols to export: ", total_symbols);
   
   int exported_count = 0;
   int skipped_count = 0;
   
   // Loop through all symbols
   for(int i = 0; i < total_symbols; i++)
   {
      string symbol = SymbolName(i, ExportAllSymbols ? false : true);
      
      if(symbol == NULL || symbol == "")
      {
         skipped_count++;
         continue;
      }
      
      // Select symbol in Market Watch to ensure data access
      if(!SymbolSelect(symbol, true))
      {
         Print("Warning: Could not select symbol: ", symbol, " Error: ", GetLastError());
         skipped_count++;
         continue;
      }
      
      // Get symbol metadata
      SymbolMetadata meta;
      if(GetSymbolMetadata(symbol, meta))
      {
         // Apply asset class filter if enabled
         if(FilterByAssetClass)
         {
            if(StringFind(AssetClassFilter, meta.asset_class) < 0)
            {
               skipped_count++;
               continue;
            }
         }
         
         WriteSymbolToCSV(file_handle, meta);
         exported_count++;
         
         if(exported_count % 50 == 0)
            Print("Exported ", exported_count, " symbols...");
      }
      else
      {
         Print("Warning: Could not get metadata for: ", symbol);
         skipped_count++;
      }
   }
   
   FileClose(file_handle);
   
   Print("===== Export Summary =====");
   Print("Total symbols scanned: ", total_symbols);
   Print("Successfully exported: ", exported_count);
   Print("Skipped: ", skipped_count);
   Print("Output file: ", filename);
   Print("File location: MQL5/Files/", filename);
}
struct SymbolMetadata
{
   string   symbol;
   string   description;
   string   asset_class;
   string   base_currency;
   string   quote_currency;
   int      digits;
   double   point;
   double   tick_size;
   double   tick_value;
   double   contract_size;
   double   min_lot;
   double   max_lot;
   double   lot_step;
   int      spread_current;
   double   spread_avg;
   bool     trade_allowed;
   string   trade_mode;
   int      sessions_count;
   string   trading_hours;
   double   volume_min;      // Changed from long to double
   double   volume_max;      // Changed from long to double
   double   margin_initial;
   string   currency_margin;
   string   path;
};


//+------------------------------------------------------------------+
//| Get comprehensive metadata for a symbol                           |
//+------------------------------------------------------------------+
bool GetSymbolMetadata(string symbol, SymbolMetadata &meta)
{
   meta.symbol = symbol;
   
   // Basic symbol info
   meta.description = SymbolInfoString(symbol, SYMBOL_DESCRIPTION);
   meta.path = SymbolInfoString(symbol, SYMBOL_PATH);
   meta.base_currency = SymbolInfoString(symbol, SYMBOL_CURRENCY_BASE);
   meta.quote_currency = SymbolInfoString(symbol, SYMBOL_CURRENCY_PROFIT);
   meta.currency_margin = SymbolInfoString(symbol, SYMBOL_CURRENCY_MARGIN);
   
   // Classify asset based on path and name
   meta.asset_class = ClassifySymbol(symbol, meta.path);
   
   // Price precision
   meta.digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   meta.point = SymbolInfoDouble(symbol, SYMBOL_POINT);
   
   // Tick information
   meta.tick_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   meta.tick_value = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   
   // Contract specifications
   meta.contract_size = SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   
   // Lot specifications
   meta.min_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   meta.max_lot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   meta.lot_step = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   
   // Spread
   meta.spread_current = (int)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
   if(IncludeSpreadStats)
      meta.spread_avg = CalculateAverageSpread(symbol);
   else
      meta.spread_avg = meta.spread_current;
   
   // Trading permissions
   meta.trade_allowed = (bool)SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_DISABLED;
   meta.trade_mode = GetTradeMode(symbol);
   
   // Margin
   meta.margin_initial = SymbolInfoDouble(symbol, SYMBOL_MARGIN_INITIAL);
   
   // Volume constraints
   meta.volume_min = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   meta.volume_max = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
   
   // Trading sessions
   if(IncludeSessionInfo)
   {
      meta.trading_hours = GetTradingHours(symbol);
      meta.sessions_count = CountTradingSessions(symbol);
   }
   else
   {
      meta.trading_hours = "N/A";
      meta.sessions_count = 0;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Classify symbol into asset class                                  |
//+------------------------------------------------------------------+
string ClassifySymbol(string symbol, string path)
{
   string upper_symbol = symbol;
   string upper_path = path;
   
   // Use built-in StringToUpper - it modifies the string in-place
   StringToUpper(upper_symbol);
   StringToUpper(upper_path);
   
   // FX classification
   if(StringFind(upper_path, "FOREX") >= 0 || StringFind(upper_path, "FX") >= 0 ||
      StringFind(upper_path, "CURRENCIES") >= 0)
      return "FX";
   
   if((StringLen(symbol) == 6 || StringLen(symbol) == 9) && 
      (StringFind(upper_symbol, "USD") >= 0 || StringFind(upper_symbol, "EUR") >= 0 ||
       StringFind(upper_symbol, "GBP") >= 0 || StringFind(upper_symbol, "JPY") >= 0))
      return "FX";
   
   // Metals/Commodities
   if(StringFind(upper_symbol, "XAU") >= 0 || StringFind(upper_symbol, "GOLD") >= 0)
      return "COMMODITY";
   if(StringFind(upper_symbol, "XAG") >= 0 || StringFind(upper_symbol, "SILVER") >= 0)
      return "COMMODITY";
   if(StringFind(upper_symbol, "OIL") >= 0 || StringFind(upper_symbol, "WTI") >= 0 ||
      StringFind(upper_symbol, "BRENT") >= 0)
      return "COMMODITY";
   if(StringFind(upper_path, "COMMODIT") >= 0 || StringFind(upper_path, "METAL") >= 0 ||
      StringFind(upper_path, "ENERGY") >= 0)
      return "COMMODITY";
   
   // Indices
   if(StringFind(upper_symbol, "US500") >= 0 || StringFind(upper_symbol, "SPX") >= 0 ||
      StringFind(upper_symbol, "NAS") >= 0 || StringFind(upper_symbol, "US30") >= 0 ||
      StringFind(upper_symbol, "GER") >= 0 || StringFind(upper_symbol, "UK100") >= 0 ||
      StringFind(upper_symbol, "JP225") >= 0 || StringFind(upper_symbol, "HK50") >= 0)
      return "INDEX";
   if(StringFind(upper_path, "INDICES") >= 0 || StringFind(upper_path, "INDEX") >= 0)
      return "INDEX";
   
   // Stocks
   if(StringFind(upper_path, "STOCK") >= 0 || StringFind(upper_path, "EQUIT") >= 0 ||
      StringFind(upper_path, "SHARES") >= 0)
      return "STOCK";
   
   // ETFs
   if(StringFind(upper_symbol, "SPY") >= 0 || StringFind(upper_symbol, "QQQ") >= 0 ||
      StringFind(upper_symbol, "ETF") >= 0)
      return "ETF";
   if(StringFind(upper_path, "ETF") >= 0)
      return "ETF";
   
   // Crypto
   if(StringFind(upper_symbol, "BTC") >= 0 || StringFind(upper_symbol, "ETH") >= 0 ||
      StringFind(upper_path, "CRYPTO") >= 0)
      return "CRYPTO";
   
   return "OTHER";
}


//+------------------------------------------------------------------+
//| Get trade mode description                                        |
//+------------------------------------------------------------------+
string GetTradeMode(string symbol)
{
   ENUM_SYMBOL_TRADE_MODE mode = (ENUM_SYMBOL_TRADE_MODE)SymbolInfoInteger(symbol, SYMBOL_TRADE_MODE);
   
   switch(mode)
   {
      case SYMBOL_TRADE_MODE_DISABLED: return "DISABLED";
      case SYMBOL_TRADE_MODE_LONGONLY: return "LONG_ONLY";
      case SYMBOL_TRADE_MODE_SHORTONLY: return "SHORT_ONLY";
      case SYMBOL_TRADE_MODE_CLOSEONLY: return "CLOSE_ONLY";
      case SYMBOL_TRADE_MODE_FULL: return "FULL";
      default: return "UNKNOWN";
   }
}

//+------------------------------------------------------------------+
//| Calculate average spread (simplified - use last known spread)     |
//+------------------------------------------------------------------+
double CalculateAverageSpread(string symbol)
{
   // In a production version, you could maintain a rolling average
   // For now, return current spread
   return (double)SymbolInfoInteger(symbol, SYMBOL_SPREAD);
}

//+------------------------------------------------------------------+
//| Get trading hours summary                                         |
//+------------------------------------------------------------------+
string GetTradingHours(string symbol)
{
   // Simplified - return whether 24h or session-based
   datetime from, to;
   if(SymbolInfoSessionTrade(symbol, MONDAY, 0, from, to))
   {
      int from_seconds = (int)from % 86400;
      int to_seconds = (int)to % 86400;
      
      if(from_seconds == 0 && to_seconds >= 86399)
         return "24h";
      else
         return TimeToString(from, TIME_MINUTES) + "-" + TimeToString(to, TIME_MINUTES);
   }
   return "UNKNOWN";
}

//+------------------------------------------------------------------+
//| Count trading sessions                                            |
//+------------------------------------------------------------------+
int CountTradingSessions(string symbol)
{
   int count = 0;
   datetime from, to;
   
   for(int session = 0; session < 10; session++)
   {
      if(SymbolInfoSessionTrade(symbol, MONDAY, session, from, to))
         count++;
      else
         break;
   }
   
   return count;
}

//+------------------------------------------------------------------+
//| Write CSV header                                                  |
//+------------------------------------------------------------------+
void WriteCSVHeader(int file_handle)
{
   string header = "symbol,description,asset_class,base_currency,quote_currency," +
                   "digits,point,tick_size,tick_value,contract_size," +
                   "min_lot,max_lot,lot_step,spread_current,spread_avg," +
                   "trade_allowed,trade_mode,sessions_count,trading_hours," +
                   "volume_min,volume_max,margin_initial,currency_margin,path";
   
   FileWrite(file_handle, header);
}

//+------------------------------------------------------------------+
//| Write symbol metadata to CSV                                      |
//+------------------------------------------------------------------+
void WriteSymbolToCSV(int file_handle, SymbolMetadata &meta)
{
   FileWrite(file_handle,
          meta.symbol,
          CleanCSVField(meta.description),
          meta.asset_class,
          meta.base_currency,
          meta.quote_currency,
          meta.digits,
          DoubleToString(meta.point, 8),
          DoubleToString(meta.tick_size, 8),
          DoubleToString(meta.tick_value, 8),
          DoubleToString(meta.contract_size, 2),
          DoubleToString(meta.min_lot, 4),
          DoubleToString(meta.max_lot, 4),
          DoubleToString(meta.lot_step, 4),
          meta.spread_current,
          DoubleToString(meta.spread_avg, 2),
          meta.trade_allowed ? "YES" : "NO",
          meta.trade_mode,
          meta.sessions_count,
          meta.trading_hours,
          DoubleToString(meta.volume_min, 4),    // Changed to DoubleToString
          DoubleToString(meta.volume_max, 4),    // Changed to DoubleToString
          DoubleToString(meta.margin_initial, 2),
          meta.currency_margin,
          CleanCSVField(meta.path)
         );

}

//+------------------------------------------------------------------+
//| Clean CSV field (escape commas and quotes)                        |
//+------------------------------------------------------------------+
string CleanCSVField(string field)
{
   if(StringFind(field, ",") >= 0 || StringFind(field, "\"") >= 0)
   {
      StringReplace(field, "\"", "\"\"");
      return "\"" + field + "\"";
   }
   return field;
}


//+------------------------------------------------------------------+
