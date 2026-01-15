//+------------------------------------------------------------------+
//|                                              CalendarExport.mq5  |
//|                Institutional Macro Data Exporter for Quantwater  |
//+------------------------------------------------------------------+
#property copyright "Quantwater Tech"
#property strict

#define CALENDAR_NO_VALUE -9223372036854775808

void OnStart()
{
   MqlCalendarValue values[];
   // Fetch 3 days back to ensure Monday runs capture Friday's late events
   datetime from = TimeCurrent() - (3 * 86400); 
   datetime to   = TimeCurrent() + (1 * 86400);

   // Generate Timestamped Filename
   datetime now = TimeCurrent();
   string timestamp = TimeToString(now, TIME_DATE|TIME_MINUTES);
   StringReplace(timestamp, ":", ""); StringReplace(timestamp, ".", ""); StringReplace(timestamp, " ", "_");
   string filename = "CALENDAR_EXPORT_" + timestamp + ".csv";

   if(CalendarValueHistory(values, from, to) > 0)
   {
      int handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
      if(handle != INVALID_HANDLE)
      {
         FileWrite(handle, "time_mt5", "currency", "event_name", "impact", "actual", "forecast");

         for(int i=0; i<ArraySize(values); i++)
         {
            MqlCalendarEvent event;
            if(CalendarEventById(values[i].event_id, event))
            {
               MqlCalendarCountry country;
               string c_code = CalendarCountryById(event.country_id, country) ? country.code : "??";
               
               string impact = "None";
               if(event.importance == CALENDAR_IMPORTANCE_LOW)      impact = "Low";
               if(event.importance == CALENDAR_IMPORTANCE_MODERATE) impact = "Medium";
               if(event.importance == CALENDAR_IMPORTANCE_HIGH)     impact = "High";

               string act = (values[i].actual_value == CALENDAR_NO_VALUE) ? "0.0" : DoubleToString((double)values[i].actual_value/1000000.0, 2);
               string forc = (values[i].forecast_value == CALENDAR_NO_VALUE) ? "0.0" : DoubleToString((double)values[i].forecast_value/1000000.0, 2);

               FileWrite(handle, TimeToString(values[i].time, TIME_DATE|TIME_MINUTES), c_code, event.name, impact, act, forc);
            }
         }
         FileClose(handle);
         Print("✅ Calendar Exported: ", filename);
      }
   }
}