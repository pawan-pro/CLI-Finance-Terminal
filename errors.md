pawan@MacBookAir CLI-Finance-Terminal % python -m src.cli.main report --institutional --format pdf --wine-mt5
INFO:src.data.providers.wine_mt5_connector:Wine MT5 connector initialized
Using real MT5 connection (Wine connector)
Warning: Using mock MT5. For production with Wine, ensure MT5 Python package is properly installed in Wine environment.
INFO:src.analysis.enhanced_institutional_pdf:Century Gothic fonts registered successfully.
Generating institutional-grade daily investment report at 2025-09-29 21:49:52
Format: PDF
Institutional-grade report enabled
Using Wine MT5 for data fetching
INFO:src.data.providers.mt5_data:Using Wine MT5 connector for data fetching
INFO:src.data.providers.wine_mt5_connector:Wine MT5 connector initialized
INFO:src.analysis.daily_report:Generating daily investment report...
INFO:src.data.providers.mt5_data:Returning info for US500Roll from cache
INFO:src.data.providers.mt5_data:Returning info for US30Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UT100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for DE40Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UK100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for EURUSD from cache
INFO:src.data.providers.mt5_data:Returning info for GBPUSD from cache
INFO:src.data.providers.mt5_data:Returning info for USDJPY from cache
INFO:src.data.providers.mt5_data:Returning info for USDCHF from cache
INFO:src.data.providers.mt5_data:Returning info for AUDUSD from cache
INFO:src.data.providers.mt5_data:Returning info for XAUUSD from cache
INFO:src.data.providers.mt5_data:Returning info for XAGUSD from cache
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: USOIL
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: USOIL
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for USOIL
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.sd
INFO:src.data.providers.mt5_data:Symbol USOIL.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.USD
INFO:src.data.providers.mt5_data:Symbol USOIL.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.eur
INFO:src.data.providers.mt5_data:Symbol USOIL.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.gbp
INFO:src.data.providers.mt5_data:Symbol USOIL.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.jpy
INFO:src.data.providers.mt5_data:Symbol USOIL.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.chf
INFO:src.data.providers.mt5_data:Symbol USOIL.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.aud
INFO:src.data.providers.mt5_data:Symbol USOIL.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.nzd
INFO:src.data.providers.mt5_data:Symbol USOIL.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: USOIL.cad
INFO:src.data.providers.mt5_data:Symbol USOIL.cad not found in MT5
INFO:src.data.providers.mt5_data:Trying mapped symbol: OIL for original symbol: USOIL
INFO:src.data.providers.mt5_data:Mapped symbol OIL not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol USOIL or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: UKOIL
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: UKOIL
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for UKOIL
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.sd
INFO:src.data.providers.mt5_data:Symbol UKOIL.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.USD
INFO:src.data.providers.mt5_data:Symbol UKOIL.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.eur
INFO:src.data.providers.mt5_data:Symbol UKOIL.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.gbp
INFO:src.data.providers.mt5_data:Symbol UKOIL.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.jpy
INFO:src.data.providers.mt5_data:Symbol UKOIL.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.chf
INFO:src.data.providers.mt5_data:Symbol UKOIL.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.aud
INFO:src.data.providers.mt5_data:Symbol UKOIL.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.nzd
INFO:src.data.providers.mt5_data:Symbol UKOIL.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: UKOIL.cad
INFO:src.data.providers.mt5_data:Symbol UKOIL.cad not found in MT5
INFO:src.data.providers.mt5_data:Trying mapped symbol: UKOIL for original symbol: UKOIL
INFO:src.data.providers.mt5_data:Mapped symbol UKOIL not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol UKOIL or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: TLT
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: TLT
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for TLT
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.sd
INFO:src.data.providers.mt5_data:Symbol TLT.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.USD
INFO:src.data.providers.mt5_data:Symbol TLT.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.eur
INFO:src.data.providers.mt5_data:Symbol TLT.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.gbp
INFO:src.data.providers.mt5_data:Symbol TLT.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.jpy
INFO:src.data.providers.mt5_data:Symbol TLT.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.chf
INFO:src.data.providers.mt5_data:Symbol TLT.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.aud
INFO:src.data.providers.mt5_data:Symbol TLT.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.nzd
INFO:src.data.providers.mt5_data:Symbol TLT.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: TLT.cad
INFO:src.data.providers.mt5_data:Symbol TLT.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol TLT or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: IEF
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: IEF
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for IEF
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.sd
INFO:src.data.providers.mt5_data:Symbol IEF.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.USD
INFO:src.data.providers.mt5_data:Symbol IEF.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.eur
INFO:src.data.providers.mt5_data:Symbol IEF.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.gbp
INFO:src.data.providers.mt5_data:Symbol IEF.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.jpy
INFO:src.data.providers.mt5_data:Symbol IEF.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.chf
INFO:src.data.providers.mt5_data:Symbol IEF.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.aud
INFO:src.data.providers.mt5_data:Symbol IEF.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.nzd
INFO:src.data.providers.mt5_data:Symbol IEF.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: IEF.cad
INFO:src.data.providers.mt5_data:Symbol IEF.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol IEF or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: SHY
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: SHY
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for SHY
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.sd
INFO:src.data.providers.mt5_data:Symbol SHY.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.USD
INFO:src.data.providers.mt5_data:Symbol SHY.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.eur
INFO:src.data.providers.mt5_data:Symbol SHY.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.gbp
INFO:src.data.providers.mt5_data:Symbol SHY.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.jpy
INFO:src.data.providers.mt5_data:Symbol SHY.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.chf
INFO:src.data.providers.mt5_data:Symbol SHY.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.aud
INFO:src.data.providers.mt5_data:Symbol SHY.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.nzd
INFO:src.data.providers.mt5_data:Symbol SHY.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: SHY.cad
INFO:src.data.providers.mt5_data:Symbol SHY.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol SHY or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: LQD
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: LQD
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for LQD
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.sd
INFO:src.data.providers.mt5_data:Symbol LQD.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.USD
INFO:src.data.providers.mt5_data:Symbol LQD.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.eur
INFO:src.data.providers.mt5_data:Symbol LQD.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.gbp
INFO:src.data.providers.mt5_data:Symbol LQD.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.jpy
INFO:src.data.providers.mt5_data:Symbol LQD.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.chf
INFO:src.data.providers.mt5_data:Symbol LQD.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.aud
INFO:src.data.providers.mt5_data:Symbol LQD.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.nzd
INFO:src.data.providers.mt5_data:Symbol LQD.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: LQD.cad
INFO:src.data.providers.mt5_data:Symbol LQD.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol LQD or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: VIX
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: VIX
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for VIX
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.sd
INFO:src.data.providers.mt5_data:Symbol VIX.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.USD
INFO:src.data.providers.mt5_data:Symbol VIX.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.eur
INFO:src.data.providers.mt5_data:Symbol VIX.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.gbp
INFO:src.data.providers.mt5_data:Symbol VIX.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.jpy
INFO:src.data.providers.mt5_data:Symbol VIX.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.chf
INFO:src.data.providers.mt5_data:Symbol VIX.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.aud
INFO:src.data.providers.mt5_data:Symbol VIX.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.nzd
INFO:src.data.providers.mt5_data:Symbol VIX.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VIX.cad
INFO:src.data.providers.mt5_data:Symbol VIX.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol VIX or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: VXN
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: VXN
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for VXN
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.sd
INFO:src.data.providers.mt5_data:Symbol VXN.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.USD
INFO:src.data.providers.mt5_data:Symbol VXN.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.eur
INFO:src.data.providers.mt5_data:Symbol VXN.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.gbp
INFO:src.data.providers.mt5_data:Symbol VXN.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.jpy
INFO:src.data.providers.mt5_data:Symbol VXN.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.chf
INFO:src.data.providers.mt5_data:Symbol VXN.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.aud
INFO:src.data.providers.mt5_data:Symbol VXN.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.nzd
INFO:src.data.providers.mt5_data:Symbol VXN.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXN.cad
INFO:src.data.providers.mt5_data:Symbol VXN.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol VXN or any alternate versions in MT5
INFO:src.data.providers.mt5_data:Attempting to fetch symbol info for: VXD
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.data.providers.mt5_data:Symbol attempted: VXD
INFO:src.data.providers.mt5_data:Available symbols in MT5: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD', 'NZDUSD', 'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'SPX500', 'DJI30', 'NDX100', 'DAX30', 'FTSE100', 'VIX']... (17 total symbols)
WARNING:src.data.providers.mt5_data:Failed to get symbol info for VXD
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.sd
INFO:src.data.providers.mt5_data:Symbol VXD.sd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.USD
INFO:src.data.providers.mt5_data:Symbol VXD.USD not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.eur
INFO:src.data.providers.mt5_data:Symbol VXD.eur not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.gbp
INFO:src.data.providers.mt5_data:Symbol VXD.gbp not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.jpy
INFO:src.data.providers.mt5_data:Symbol VXD.jpy not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.chf
INFO:src.data.providers.mt5_data:Symbol VXD.chf not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.aud
INFO:src.data.providers.mt5_data:Symbol VXD.aud not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.nzd
INFO:src.data.providers.mt5_data:Symbol VXD.nzd not found in MT5
INFO:src.data.providers.mt5_data:Trying alternative symbol: VXD.cad
INFO:src.data.providers.mt5_data:Symbol VXD.cad not found in MT5
ERROR:src.data.providers.mt5_data:Failed to find symbol VXD or any alternate versions in MT5
INFO:src.analysis.daily_report:Successfully read economic calendar from: ./economic-calendar/ECONOMIC_CALENDAR_DATA.csv
INFO:src.analysis.daily_report:Fetching financial news...
INFO:src.analysis.daily_report:Successfully fetched 7 financial news headlines.
WARNING:src.data.providers.mt5_data:Failed to fetch data for US500Roll
WARNING:src.data.providers.mt5_data:Failed to fetch data for US30Roll
WARNING:src.data.providers.mt5_data:Failed to fetch data for UT100Roll
WARNING:src.data.providers.mt5_data:Failed to fetch data for DE40Roll
WARNING:src.data.providers.mt5_data:Failed to fetch data for UK100Roll
INFO:src.analysis.daily_report:Generating charts...
WARNING:src.data.providers.mt5_data:Failed to fetch data for US500Roll
WARNING:src.analysis.daily_report:Could not generate chart for US500Roll due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for US30Roll
WARNING:src.analysis.daily_report:Could not generate chart for US30Roll due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for UT100Roll
WARNING:src.analysis.daily_report:Could not generate chart for UT100Roll due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for DE40Roll
WARNING:src.analysis.daily_report:Could not generate chart for DE40Roll due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for UK100Roll
WARNING:src.analysis.daily_report:Could not generate chart for UK100Roll due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for GBPUSD
WARNING:src.analysis.daily_report:Could not generate chart for GBPUSD due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for USDJPY
WARNING:src.analysis.daily_report:Could not generate chart for USDJPY due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for XAUUSD
WARNING:src.analysis.daily_report:Could not generate chart for XAUUSD due to missing data.
WARNING:src.data.providers.mt5_data:Failed to fetch data for XAGUSD
WARNING:src.analysis.daily_report:Could not generate chart for XAGUSD due to missing data.
INFO:src.data.providers.mock_mt5:Mock MT5 initialized
INFO:src.data.providers.mt5_data:MT5 initialized successfully
INFO:src.data.providers.mt5_data:Returning info for US500Roll from cache
INFO:src.data.providers.mt5_data:Returning info for US30Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UT100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for DE40Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UK100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for US500Roll from cache
INFO:src.data.providers.mt5_data:Returning info for US30Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UT100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for DE40Roll from cache
INFO:src.data.providers.mt5_data:Returning info for UK100Roll from cache
INFO:src.data.providers.mt5_data:Returning info for EURUSD from cache
INFO:src.data.providers.mt5_data:Returning info for GBPUSD from cache
INFO:src.data.providers.mt5_data:Returning info for USDJPY from cache
INFO:src.data.providers.mt5_data:Returning info for USDCHF from cache
INFO:src.data.providers.mt5_data:Returning info for AUDUSD from cache
INFO:src.data.providers.mt5_data:Returning info for XAUUSD from cache
INFO:src.data.providers.mt5_data:Returning info for XAGUSD from cache
INFO:src.analysis.enhanced_institutional_pdf:Fetching bonds/ETFs data from Alpha Vantage
WARNING:src.analysis.enhanced_institutional_pdf:Alpha Vantage bonds/ETFs data fetch failed, using MT5 as fallback
INFO:src.data.providers.mt5_data:Returning symbols from cache
INFO:src.analysis.enhanced_institutional_pdf:Chart embedding attempt - received 0 chart files
INFO:src.analysis.enhanced_institutional_pdf:No chart files provided to add_charts method
INFO:src.analysis.enhanced_institutional_pdf:Enhanced institutional PDF report generated: ./reports/daily_report_20250929_214952/daily_report_20250929_214952_institutional.pdf
INFO:src.analysis.daily_report:Daily investment report saved to: ./reports/daily_report_20250929_214952/daily_report_20250929_214952_institutional.pdf
INFO:src.data.providers.mock_mt5:Mock MT5 shutdown
INFO:src.data.providers.mt5_data:MT5 connection shutdown
✅ Daily investment report generated successfully!
📄 Report saved to: ./reports/daily_report_20250929_214952/daily_report_20250929_214952_institutional.pdf