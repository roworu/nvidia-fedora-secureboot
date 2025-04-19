# Fedora <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/2337478d-d34d-43df-9e8b-15c8edc2ff5c" width="20"> + Nvidia <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/118ae093-5c31-4aef-9c24-c58edc522630" width="20"> + Secureboot <img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/0d7e652b-8ae4-485c-8098-a6b024308c7b" width="20">

This guide provides instructions on installing the latest NVIDIA drivers on a Fedora desktop.
It is primarily written for personal use, but it may also be useful (hopefully) for you.

⚠️ Note: This guide is based on the official RPM Fusion instructions. If you're using **Fedora Silverblue**, you may need to refer to the full documentation:

    https://rpmfusion.org/Howto/NVIDIA

    https://rpmfusion.org/Howto/Secure%20Boot


## Preconditions:
1) This method has been tested on Fedora 39/40/41/42 with the latest NVIDIA drivers. It works with KDE, GNOME, or any other desktop environment/window manager.
2) Secure Boot must be enabled in setup mode in your BIOS/UEFI settings (some BIOS versions call this "Custom Mode").
3) Remove any existing NVIDIA drivers before proceeding:

```bash
dnf remove xorg-x11-drv-nvidia\*
```

🔄 Reboot after removing old drivers.

4) For easier debugging, you can disable the 'quiet' boot option:
```bash
# Disable 'quiet' mode
sudo grubby --update-kernel=ALL --remove-args=quiet

# Re-enable 'quiet' mode
sudo grubby --update-kernel=ALL --args=quiet
```
(This is optional but can help debug if errors occur.)

## Process:

#### 1) Add RPM Fusion repositories:

```bash
# Free
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
# Non-Free
sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
```

#### 2) Fully update the system:
```bash
sudo dnf upgrade --refresh
```

#### 3) Install signing modules:
```bash
sudo dnf install kmodtool akmods mokutil openssl
```

#### 4) Generate a key:
```bash
sudo kmodgenca -a
```

#### 5) Import your key and set a password for it (no need for a complex password):
```bash
sudo mokutil --import /etc/pki/akmods/certs/public_key.der
```

#### 6) Reboot:
```bash
sudo systemctl reboot
```

#### 7) MOK manager will ask if you want to proceed with booting or enroll the key. Choose "Enroll MOK" -> "Continue" and enter the password created in step 6.
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/dec5b957-e562-4e9e-bd22-678007aecdcf" width="600">

#### 8) Install NVIDIA drivers:
```bash
sudo dnf install gcc kernel-headers kernel-devel akmod-nvidia \
 xorg-x11-drv-nvidia xorg-x11-drv-nvidia-libs.{i686,x86_64} \
 libva-nvidia-driver.{i686,x86_64} xorg-x11-drv-nvidia-cuda
```

#### 9) Wait for the modules to build! You can monitor the build process using `htop` or by typing:
```bash
modinfo -F version nvidia
```
It should return the driver version like this:
<img src="https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/d754d785-339a-4e03-97c7-f59e5b2b86b3" width="800">

If it shows `ERROR: Module nvidia not found`, the modules are still building—keep waiting.

#### 10) Ensure the modules are built for the currently running kernel and boot image:
```bash
sudo akmods --force && sudo dracut --force
```

#### 11) Disable GSP Firmware

For newer NVIDIA drivers (555-570) + Wayland, you may want to disable GSP firmware to reduce stuttering in GNOME/KDE.

However, this issue varies by system, and you may not need to disable it. Test your setup first before applying this change.

To disable GSP firmware, run:

```bash
sudo grubby --update-kernel=ALL --args=nvidia.NVreg_EnableGpuFirmware=0
```
Sources:

    https://forums.developer.nvidia.com/t/major-kde-plasma-desktop-frameskip-lag-issues-on-driver-555/293606

    https://forums.developer.nvidia.com/t/stutering-and-low-fps-scrolling-in-browsers-on-wayland-when-gsp-firmware-is-enabled/311127/15

    https://forums.developer.nvidia.com/t/570-release-feedback-discussion/321956/69


#### 12) Reboot, and you're done!

![Screenshot from 2024-04-06 14-10-49](https://github.com/roworu/nvidia-fedora-secureboot/assets/36964755/458f4f30-82fb-426c-bdd0-a0029f68f2fd)  
*<small>Task manager app in the screenshot: https://flathub.org/apps/io.missioncenter.MissionCenter</small>*
