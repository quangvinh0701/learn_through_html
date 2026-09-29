@echo off
REM Tao lai masterclass-all-in-one.html tu cac file module hien tai,
REM sau do MA HOA LAI index.html + masterclass-protected.html cho dong bo.
REM Chay file nay moi khi them/sua bat ky module nao.
cd /d "%~dp0"
echo Dang chay build.py ...
py build.py 2>nul || python build.py 2>nul || python3 build.py
echo.
set /p PW=Nhap mat khau ma hoa (Enter = bo qua buoc ma hoa):
if "%PW%"=="" goto skip
echo Dang ma hoa index.html ...
py make-protected.py "%PW%" masterclass-all-in-one.html index.html 2>nul || python make-protected.py "%PW%" masterclass-all-in-one.html index.html
echo Dang ma hoa masterclass-protected.html ...
py make-protected.py "%PW%" masterclass-all-in-one.html masterclass-protected.html 2>nul || python make-protected.py "%PW%" masterclass-all-in-one.html masterclass-protected.html
goto done
:skip
echo BO QUA ma hoa — LUU Y: index.html / masterclass-protected.html dang LOI THOI so voi ban vua build.
:done
echo.
echo ============================================================
echo Xong. Mo masterclass-all-in-one.html de kiem tra noi dung.
echo ============================================================
pause
