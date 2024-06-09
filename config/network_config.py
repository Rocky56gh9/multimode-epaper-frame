import os
import subprocess

def configure_gadget_mode():
    print("\nGadget Mode Configuration")
    print("1. Turn Gadget Mode ON")
    print("2. Turn Gadget Mode OFF")
    choice = input("Select an option: ")
    if choice == '1':
        enable_gadget_mode()
    elif choice == '2':
        disable_gadget_mode()
    else:
        print("Invalid option. Please select a valid option.")
        configure_gadget_mode()

def enable_gadget_mode():
    print("\nEnabling Gadget Mode for local USB access...")
    gadget_mode_script = """
    sudo modprobe libcomposite
    cd /sys/kernel/config/usb_gadget/
    mkdir -p g1
    cd g1
    echo 0x1d6b > idVendor # Linux Foundation
    echo 0x0104 > idProduct # Multifunction Composite Gadget
    echo 0x0100 > bcdDevice # v1.0.0
    echo 0x0200 > bcdUSB # USB2
    mkdir -p strings/0x409
    echo "fedcba9876543210" > strings/0x409/serialnumber
    echo "Manufacturer" > strings/0x409/manufacturer
    echo "Product" > strings/0x409/product
    mkdir -p configs/c.1/strings/0x409
    echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
    echo 250 > configs/c.1/MaxPower
    mkdir -p functions/ecm.usb0
    echo "DE:AD:BE:EF:00:01" > functions/ecm.usb0/host_addr || echo "Skipping host_addr configuration as it is busy."
    echo "DE:AD:BE:EF:00:02" > functions/ecm.usb0/dev_addr || echo "Skipping dev_addr configuration as it is busy."
    if [ ! -L configs/c.1/ecm.usb0 ]; then
      ln -s functions/ecm.usb0 configs/c.1/
    else
      echo "Symbolic link 'configs/c.1/ecm.usb0' already exists. Skipping link creation."
    fi
    """
    with open("/etc/rc.local", "a") as f:
        f.write(f"\n{gadget_mode_script}")
    print("Gadget mode enabled and will be activated on reboot.")

def disable_gadget_mode():
    print("\nDisabling Gadget Mode for local USB access...")
    gadget_mode_script = """
    cd /sys/kernel/config/usb_gadget/g1
    rm configs/c.1/ecm.usb0
    rmdir configs/c.1/strings/0x409
    rmdir configs/c.1
    rmdir functions/ecm.usb0
    rmdir strings/0x409
    cd ..
    rmdir g1
    sudo modprobe -r libcomposite
    """
    with open("/etc/rc.local", "a") as f:
        f.write(f"\n{gadget_mode_script}")
    print("Gadget mode disabled and will be deactivated on reboot.")

def configure_wifi():
    print("\nWiFi Configuration")
    print("1. Clear Existing WiFi Settings")
    print("2. Add New WiFi Settings")
    choice = input("Select an option: ")
    if choice == '1':
        clear_wifi_settings()
    elif choice == '2':
        add_wifi_settings()
    else:
        print("Invalid option. Please select a valid option.")
        configure_wifi()

def clear_wifi_settings():
    print("\nClearing existing WiFi settings...")
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    try:
        with open("/etc/rc.local", "a") as f:
            f.write(f"echo '' > {wifi_conf_path}\n")
        print("Existing WiFi settings will be cleared on reboot.")
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")

def add_wifi_settings():
    ssid = input("\nEnter your WiFi SSID: ")
    psk = input("Enter your WiFi password: ")
    wifi_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
    wifi_conf = f"""
network={{
    ssid="{ssid}"
    psk="{psk}"
}}
"""
    try:
        with open("/etc/rc.local", "a") as f:
            f.write(f"echo '{wifi_conf}' >> {wifi_conf_path}\n")
        print("New WiFi settings will be added on reboot.")
    except PermissionError:
        print("Permission denied. Please run this script with sudo.")

def restart_network():
    print("\nRestarting network services...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"], check=True, timeout=30)
        print("Network services restarted.")
        result = subprocess.run(["sudo", "iwgetid"], capture_output=True, text=True, timeout=10)
        if ssid in result.stdout:
            print(f"Successfully connected to {ssid}")
        else:
            print(f"Failed to connect to {ssid}. Please check your credentials or network settings.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart network services: {e}")
    except subprocess.TimeoutExpired:
        print("Network restart timed out. Please check your network settings.")

def main():
    print("\nNetwork Configuration Interface")
    print("1. Configure Gadget Mode")
    print("2. Configure WiFi")
    print("3. Exit and Reboot")

    choice = input("Select an option: ")
    if choice == '1':
        configure_gadget_mode()
    elif choice == '2':
        configure_wifi()
    elif choice == '3':
        os.system("sudo reboot")
        exit()
    else:
        print("Invalid option. Please select a valid option.")
        main()

if __name__ == "__main__":
    if not os.geteuid() == 0:
        print("This script must be run as root. Please use sudo.")
        exit()
    main()
