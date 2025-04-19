# Fedora <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/2337478d-d34d-43df-9e8b-15c8edc2ff5c" width="20"> + Nvidia <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/118ae093-5c31-4aef-9c24-c58edc522630" width="20"> + Secureboot <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/0d7e652b-8ae4-485c-8098-a6b024308c7b" width="20">

This is a short instruction I mostly wrote for myself. Here is a guide on how to install the **latest** Nvidia drivers for Fedora desktop.  
I don't know if it will also work for the "Silverblue" edition; you might need to check the full instructions from the official RPM Fusion sources, as this guide is mostly based on them:

https://rpmfusion.org/Howto/NVIDIA \
https://rpmfusion.org/Howto/Secure%20Boot

## Preconditions:
1) This method has been tested for **Fedora 39/40/41/42** and **latest NVIDIA** drivers! It doesn’t matter if you use KDE, Gnome, or any other DE/WM.
2) In BIOS, Secure Boot must be **turned ON in setup mode** (Some BIOS setups may call it "Custom Mode.").
3) Delete ALL older NVIDIA installations!
4) You can also turn OFF the 'quiet' boot option for easier debugging with the following command:
```
# To remove:

sudo grubby --update-kernel=ALL --remove-args=quiet

# To return:

sudo grubby --update-kernel=ALL --args=quiet
```
This is not a requirement but can make troubleshooting easier if errors occur.

## Process:

#### 1) Add RPM Fusion repositories:

**Free:**
```
sudo dnf install \
 https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```
**Non-free:**
```
sudo dnf install \
 https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
```

#### 2) Fully update the system:
```
sudo dnf upgrade --refresh
```

#### 3) Install signing modules:
```
sudo dnf install kmodtool akmods mokutil openssl
```

#### 4) Generate a key:
```
sudo kmodgenca -a
```

#### 5) Import your key and set a password for it (no need for a complex password):
```
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
```

#### 6) Reboot:
```
sudo systemctl reboot
```

#### 7) MOK manager will ask if you want to proceed with booting or enroll the key. Choose "Enroll MOK" -> "Continue" and enter the password created in step 6.
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/dec5b957-e562-4e9e-bd22-678007aecdcf" width="600">

#### 8) Install NVIDIA drivers:
```
sudo dnf install gcc kernel-headers kernel-devel akmod-nvidia \
 xorg-x11-drv-nvidia xorg-x11-drv-nvidia-libs xorg-x11-drv-nvidia-libs.i686
```

#### 8) (Optional) Install CUDA support if needed and supported by your GPU:
```
sudo dnf install xorg-x11-drv-nvidia-cuda
```

#### 10) Wait for the modules to build! You can monitor the build process using `htop` or by typing:
```
modinfo -F version nvidia
```
It should return the driver version like this:
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/d754d785-339a-4e03-97c7-f59e5b2b86b3" width="800">

If it shows `ERROR: Module nvidia not found`, the modules are still building—keep waiting.

#### 11) Ensure the modules are built for the currently running kernel and boot image:
```
sudo akmods --force && sudo dracut --force
```

#### 11.1) Disable GSP Firmware:  
For newer drivers (555-560) + Wayland, you may want to disable GSP Firmware to reduce lags in Gnome/KDE:
```
sudo grubby --update-kernel=ALL --args=nvidia.NVreg_EnableGpuFirmware=0
```
*Source:* https://forums.developer.nvidia.com/t/major-kde-plasma-desktop-frameskip-lag-issues-on-driver-555/293606

#### 12) Reboot, and you're done!

![Screenshot from 2024-04-06 14-10-49](https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/458f4f30-82fb-426c-bdd0-a0029f68f2fd)  
*<small>Task manager app in the screenshot: https://flathub.org/apps/io.missioncenter.MissionCenter</small>*
