Tante Emma Laden: Waage-Drucker
===============================


# Setup:

Ubuntu/Debian:

    sudo apt install python3 python3-netifaces python3-pil

## configure output language

    sudo dpkg-reconfigure locale

Set system locale to de_DE or de_Ch for german output


## allow access to /dev/usb/lp0

    sudo usermod -a -G lp $USER

## autostart

put the following line into /etc/rc.locale:

    sudo -u pi python3 /home/pi/houdini_thermoprinter/main.py &
    
alternatively start as service (automaticaly restarts on error):

    sudo cp printerApp.service /etc/systemd/system/printerApp.service
    sudo systemctl daemon-reload
    sudo systemctl restart printerApp.service
