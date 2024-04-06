# Fedora + Nvidia + Secureboot

This is a short instruction I mostly wrote for myself. In this here is presented a quide on how to install **latest** Nvidia drivers for Fedora desktop.
I don't know if it will also work for "Silverblue" edition, you probably need to check full instruction from official rpmfusion sources, as this instruction mostly based on it:

https://rpmfusion.org/Howto/NVIDIA
https://rpmfusion.org/Howto/Secure%20Boot

Please, also note, that this will only work y

## Preconditions:
1) This method tested for **Fedora 39/40** and **latest NVIDIA** drivers! NO matter if you use KDE or Gnome or anything else.
2) Secure Boot is **turned ON in setup mode**
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
#### 8) MOK manager will ask you, if you want to proceed with boot, or enroll the key. Pick "Enroll MOK", type in a password created in (7)
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
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/ee673c2c-74db-4bd9-abc5-d50ae1c5404a" width="800">

If it shows ERROR: Module nvidia not found - modules are still building, keep waiting.

#### 12) Recheck, that modules built:
```
sudo akmods --force
```
#### 13) Recheck boot image update:
```
sudo dracut --force
```
#### 13) Reboot!

