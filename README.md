# nvidia-fedora-secureboot


1) Add rpmfusion repos:
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

2) Full update of sysytem:
```
sudo dnf upgrade --refresh
```
3) Reboot!

4) Install signing modules:
```
sudo dnf install kmodtool akmods mokutil openssl
```
5) Generate a key:
```
sudo kmodgenca -a
```
6) Import your key, and set password to it, no need for complex passwords:
```
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
```
7) Reboot!

8) MOK manager will ask you, if you want to proceed with boot, or import the key. Pick import the key, type in a password created in (7)

9) Install NVIDIA drivers:
```
sudo dnf install gcc kernel-headers kernel-devel akmod-nvidia xorg-x11-drv-nvidia xorg-x11-drv-nvidia-libs xorg-x11-drv-nvidia-libs.i686
```
10) Wait for modules to build! You can check build process via htop, or by typing:
```
modinfo -F version nvidia
```
It should return you driver verion like this:
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/ee673c2c-74db-4bd9-abc5-d50ae1c5404a" width="800">

If it shows ERROR: Module nvidia not found - modules are still building, keep waiting.

11) Recheck, that modules built:
```
sudo akmods --force
```
12) Recheck boot image update:
```
sudo dracut --force
```
13) Reboot!
