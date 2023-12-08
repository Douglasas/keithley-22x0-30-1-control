PYTHON    = python3

THIS_PATH = $(abspath .)
VENV_PATH = $(THIS_PATH)/venv
REQ_FILE  = $(THIS_PATH)/requirements.txt

DESKTOP_FILE_NAME       = keithley-power-supply-control.desktop 
DESKTOP_PICTURE         = $(THIS_PATH)/img/power-supply.png
DESKTOP_TARGET_LOCATION = ~/.local/share/applications/

DEVICE_VENDOR_ID  = 05e6
DEVICE_PRODUCT_ID = 2230

UDEV_RULES_FILE = /etc/udev/rules.d/99-garmin.rules

venv:
	rm -rf $(VENV_PATH)
	$(PYTHON) -m venv $(VENV_PATH)
	$(VENV_PATH)/bin/pip install -r $(REQ_FILE)

configure-linux-udev-rules:
	@echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$(DEVICE_VENDOR_ID)\", ATTR{idProduct}==\"$(DEVICE_PRODUCT_ID)\", MODE=\"666\"" | sudo tee $(UDEV_RULES_FILE)
	@echo "Created file $(UDEV_RULES_FILE)"
	sudo udevadm control --reload-rules && sudo udevadm trigger
	@echo "Reconnect USB cable!"

remove-linux-udev-rules:
	@echo "Removing $(UDEV_RULES_FILE)"
	sudo rm $(UDEV_RULES_FILE)
	sudo udevadm control --reload-rules && sudo udevadm trigger

install-desktop:
	@echo "[Desktop Entry]"                                                                         >  $(DESKTOP_FILE_NAME)
	@echo "Name=Keithley 22x0 Power Supply Control"                                                 >> $(DESKTOP_FILE_NAME)
	@echo "Exec=$(VENV_PATH)/bin/python $(THIS_PATH)/KeithleyGUI.py -u $(DEVICE_VENDOR_ID) $(DEVICE_PRODUCT_ID)" >> $(DESKTOP_FILE_NAME)
	@echo "Icon=$(DESKTOP_PICTURE)"                                                                 >> $(DESKTOP_FILE_NAME)
	@echo "Terminal=false"                                                                          >> $(DESKTOP_FILE_NAME)
	@echo "Type=Application"                                                                        >> $(DESKTOP_FILE_NAME)
	@echo "Categories=Electronics;"                                                                 >> $(DESKTOP_FILE_NAME)
	@echo "Moving desktop file to $(DESKTOP_TARGET_LOCATION)/$(DESKTOP_FILE_NAME)"
	mv -f $(THIS_PATH)/$(DESKTOP_FILE_NAME) $(DESKTOP_TARGET_LOCATION)

remove-desktop:
	@echo "Removing $(DESKTOP_TARGET_LOCATION)/$(DESKTOP_FILE_NAME)"
	rm $(DESKTOP_TARGET_LOCATION)/$(DESKTOP_FILE_NAME)
    
gui: venv
	$(VENV_PATH)/bin/python KeithleyGUI.py -u $(DEVICE_VENDOR_ID) $(DEVICE_PRODUCT_ID)
