#!/bin/bash

# Check if preprocessing is already done
if [[ -f /var/tmp/nvidia-setup-done ]]; then
    echo "Preprocessing already completed. Skipping to NVIDIA drivers installation..."
else
    echo "Starting the setup process..."
    
    # Add RPM Fusion repositories
    rpm -q rpmfusion-free-release > /dev/null 2>&1 || sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
    rpm -q rpmfusion-nonfree-release > /dev/null 2>&1 || sudo dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

    # Update the system
    echo "Updating the system..."
    if sudo dnf upgrade --refresh -y | grep -q "Complete!"; then
        reboot_required=true
    else
        reboot_required=false
    fi

    # Reboot if necessary
    if [[ "$reboot_required" == "true" ]]; then
        echo "Rebooting system. Run the script again after reboot."
        echo -n "Reboot now? (y/n): "
        read reboot_confirm
        [[ "$reboot_confirm" =~ ^[Yy]$ ]] && sudo systemctl reboot && exit 0
    fi

    # Install signing modules
    echo "Installing signing modules..."
    sudo dnf install -y kmodtool akmods mokutil openssl

    # Generate and import key
    echo "Generating key and importing it. Set a password for the key when prompted. No need for complex password."
    sudo kmodgenca -a
    sudo mokutil --import /etc/pki/akmods/certs/public_key.der

    # Final reboot before NVIDIA installation
    echo "Final reboot required. During boot MOK manager will ask if you want to proceed with booting or enroll the key. Choose "Enroll MOK" -> "Continue" and enter the password created in the previous step."
    echo -n "Reboot now? (y/n): "
    read reboot_confirm
    [[ "$reboot_confirm" =~ ^[Yy]$ ]] && touch /var/tmp/nvidia-setup-done && sudo systemctl reboot && exit 0
fi

# Install NVIDIA drivers
echo "Installing NVIDIA drivers..."
sudo dnf install -y gcc kernel-headers kernel-devel akmod-nvidia xorg-x11-drv-nvidia xorg-x11-drv-nvidia-libs xorg-x11-drv-nvidia-libs.i686

# Optional CUDA support
echo -n "Install CUDA support? (y/n): "
read install_cuda
[[ "$install_cuda" =~ ^[Yy]$ ]] && sudo dnf install -y xorg-x11-drv-nvidia-cuda

# Wait for NVIDIA module build
echo "Waiting for NVIDIA modules to build..."
start_time=$(date +%s)
while ! modinfo -F version nvidia 2>/dev/null; do
    elapsed_time=$(( $(date +%s) - start_time ))
    [[ $elapsed_time -gt 1800 ]] && echo "ERROR: NVIDIA module build timeout." && exit 1
    echo "NVIDIA module not ready, retrying in 30s..."
    sleep 30
done

# Ensure modules are built for the current kernel
sudo akmods --force
sudo dracut --force

# Disable GSP Firmware if needed
echo -n "Disable GSP Firmware? (y/n): "
read disable_gsp
[[ "$disable_gsp" =~ ^[Yy]$ ]] && sudo grubby --update-kernel=ALL --args=nvidia.NVreg_EnableGpuFirmware=0

# Cleanup
test -f /var/tmp/nvidia-setup-done && rm /var/tmp/nvidia-setup-done

echo "Setup process completed! Perform reboot to start using Nvidia drivers."
