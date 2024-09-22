# Fedora <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/2337478d-d34d-43df-9e8b-15c8edc2ff5c" width="20"> + Nvidia <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/118ae093-5c31-4aef-9c24-c58edc522630" width="20"> + Secureboot <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/0d7e652b-8ae4-485c-8098-a6b024308c7b" width="20">

This is a short instruction I mostly wrote for myself. Here is presented a guide on how to install **latest** Nvidia drivers for Fedora desktop.
I don't know if it will also work for "Silverblue" edition, you probably need to check full instruction from official rpmfusion sources, as this instruction mostly based on it:

https://rpmfusion.org/Howto/NVIDIA \
https://rpmfusion.org/Howto/Secure%20Boot


## Preconditions:
1) This method tested for **Fedora 39/40** and **latest NVIDIA** drivers! NO matter if you use KDE or Gnome or anything else.
2) In BIOS, Secure Boot is **turned ON in setup mode**
3) Delete ALL older NVIDIA installations! 
4) You could also turn OFF 'quiet' boot option, for easier debugging, with following command:
```
sudo grubby --update-kernel=ALL --remove-args='quiet'
```
It is not requierment, but could ease your life in case of some errors.

## Processing:

#### 1) Add rpmfusion repos:

free:
```
sudo dnf install \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```
nonfree:
```
sudo dnf install \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
```

#### 2) Full update of system:
```
sudo dnf upgrade --refresh
```
#### 3) Reboot!
```
sudo systemctl reboot
```
#### 4) Install signing modules:
```
sudo dnf install kmodtool akmods mokutil openssl
```
#### 5) Generate a key:
```
sudo kmodgenca -a
```
#### 6) Import your key, and set password to it, no need for complex passwords:
```
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
```
#### 7) Reboot!
```
sudo systemctl reboot
```
#### 8) MOK manager will ask you, if you want to proceed with boot, or enroll the key. Pick "Enroll MOK" -> "Continue", type in a password created in (7)
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/dec5b957-e562-4e9e-bd22-678007aecdcf" width="600">

#### 9) Install NVIDIA drivers:
```
sudo dnf install gcc kernel-headers kernel-devel akmod-nvidia xorg-x11-drv-nvidia xorg-x11-drv-nvidia-libs xorg-x11-drv-nvidia-libs.i686
```
#### 10) Also, you can install CUDA support, in case you need it and your GPU supports it:
```
sudo dnf install xorg-x11-drv-nvidia-cuda
```
#### 11) Wait for modules to build! You can check build process via htop, or by typing:
```
modinfo -F version nvidia
```
It should return you driver version like this:
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/d754d785-339a-4e03-97c7-f59e5b2b86b3" width="800">

If it shows ERROR: Module nvidia not found - modules are still building, keep waiting.

#### 12) Recheck, that modules built for currently running kernel:
```
sudo akmods --force
```
#### 13) Recheck boot image update:
```
sudo dracut --force
```
#### 13) Reboot and we are done!

![Screenshot from 2024-04-06 14-10-49](https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/458f4f30-82fb-426c-bdd0-a0029f68f2fd)
*<small>Task manager app on screenshot: https://flathub.org/apps/io.missioncenter.MissionCenter </small>*

#### upd: 14) Disable GSP Firmware 

```
# For latest drivers (555-560) + wayland you might want to also disable GSP Firmware to reduce lags in Gnome/KDE
# source: https://forums.developer.nvidia.com/t/major-kde-plasma-desktop-frameskip-lag-issues-on-driver-555/293606
sudo grubby --update-kernel=ALL --args=nvidia.NVreg_EnableGpuFirmware=0
```



