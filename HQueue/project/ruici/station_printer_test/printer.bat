@echo off
taskkill /f /im python.exe

echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin
REM
python station_printer.py >printer.log