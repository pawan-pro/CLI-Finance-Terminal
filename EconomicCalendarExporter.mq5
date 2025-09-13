//+------------------------------------------------------------------+
//|                                     EconomicCalendarExporter.mq5 |
//|                      Copyright 2025, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property description "Exports economic calendar data to a CSV file."

#include <Tools\DateTime.mqh>

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---
   EventSetTimer(21600); // 6 hours * 60 minutes * 60 seconds = 21600
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
   EventKillTimer();
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---

  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
  {
//---
   MqlCalendarValue values[];
   datetime from = TimeCurrent();
   datetime to = from + PeriodSeconds(PERIOD_W1);

   if(CalendarValueHistory(values, from, to))
     {
      string file_path = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\Files\\economic_calendar.csv";
      int file_handle = FileOpen(file_path, FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
      if(file_handle != INVALID_HANDLE)
        {
         FileWriteString(file_handle, "Time,Name,Impact,Currency,Actual,Forecast,Previous\n");

         MqlCalendarEvent event;
         for(int i = 0; i < ArraySize(values); i++)
           {
            if(CalendarEventById(values[i].event_id, event))
              {
               string impact = EnumToString((ENUM_CALENDAR_EVENT_IMPACT)event.impact);
               FileWrite(file_handle,
                         TimeToString(values[i].time, TIME_DATE|TIME_MINUTES),
                         event.name,
                         impact,
                         event.currency,
                         DoubleToString(values[i].actual_value),
                         DoubleToString(values[i].forecast_value),
                         DoubleToString(values[i].previous_value));
              }
            else
              {
               Print("Error getting event data for event_id: ", values[i].event_id, ". Error ", GetLastError());
              }
           }
         FileClose(file_handle);
         Print("Successfully exported ", ArraySize(values), " calendar events to ", file_path);
        }
      else
        {
         Print("Error opening file ", file_path, ". Error ", GetLastError());
        }
     }
   else
     {
      Print("Failed to fetch calendar events. Error ", GetLastError());
     }
  }
//+------------------------------------------------------------------+
