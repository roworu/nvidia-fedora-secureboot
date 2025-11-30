import os
import sys
import time
import logging
import subprocess
from pathlib import Path


INSTALL_CUDA = os.environ.get('INSTALL_CUDA', "True").lower().split() == "true"
DISABLE_GSP = os.environ.get('DISABLE_GSP', "True").lower().split() == "true"


_log = logging.getLogger(__name__)


def run(cmd, **kwargs):
    _log.debug(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd, **kwargs)


def prepare_rpm_fusion_repos():
    fedora_version = subprocess.check_output(["rpm", "-E", "%fedora"], text=True).strip()

    rpmfusion_free_repo = \
        f"https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm"
    rpmfusion_non_free_repo = \
        f"https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm"

    _log.info(f"Checking for rpmfusion repos for Fedora {fedora_version}")

    free_installed = subprocess.run(
        ["rpm", "-q", "rpmfusion-free-release"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

    nonfree_installed = subprocess.run(
        ["rpm", "-q", "rpmfusion-nonfree-release"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0

    if not free_installed:
        _log.info("Installing rpmfusion free repo...")
        run(["sudo", "dnf", "install", "-y", rpmfusion_free_repo], check=True)

    if not nonfree_installed:
        _log.info("Installing rpmfusion non-free repo...")
        run(["sudo", "dnf", "install", "-y", rpmfusion_non_free_repo], check=True)

    _log.info("RPM Fusion repositories are ready.")


def prompt_yes(message):
    return input(message).strip().lower().startswith("y")


def do_reboot():
    run(["sudo", "systemctl", "reboot"], check=True)
    sys.exit(0)


def update_system():
    _log.info("Performing full system upgrade...")
    upgrade = run(
        ["sudo", "dnf", "upgrade", "--refresh", "-y"],
        text=True, capture_output=True, check=False
    )

    stdout = upgrade.stdout or ""
    if "Nothing to do." in stdout:
        _log.info("System already up-to-date.")
        return False

    if "Complete!" in stdout:
        _log.info("System updated.")
        return True

    raise Exception(f"Unable to parse system upgrade output: {stdout}")


def install_signing_modules():
    _log.info("Installing signing modules")
    run([
        "sudo", "dnf", "install", "-y",
        "kmodtool", "akmods", "mokutil", "openssl"
    ], check=True)


def generate_and_import_key():
    _log.info("Generating and importing MOK key. Use any simple password.")
    run(["sudo", "kmodgenca", "-a"], check=True)
    run(["sudo", "mokutil", "--import", "/etc/pki/akmods/certs/public_key.der"], check=True)


def ensure_kernel_devel_matches():
    kernel_running = subprocess.check_output(["uname", "-r"], text=True).strip()
    kernel_devel = subprocess.check_output(
        ["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}.%{ARCH}\n", "kernel-devel"],
        text=True,
    ).strip()

    if kernel_running != kernel_devel:
        _log.error(
            f"kernel-devel ({kernel_devel}) does not match running kernel ({kernel_running})."
        )
        if prompt_yes("Reboot now? (y/n): "):
            do_reboot()


def install_nvidia_drivers():
    _log.info("Installing NVIDIA drivers...")
    run([
        "sudo", "dnf", "install", "-y",
        "gcc", "kernel-headers", "kernel-devel", "akmod-nvidia",
        "xorg-x11-drv-nvidia", "xorg-x11-drv-nvidia-libs",
        "xorg-x11-drv-nvidia-libs.i686",
    ], check=True)


def install_cuda():
    _log.info("Installing CUDA...")
    run(["sudo", "dnf", "install", "-y", "xorg-x11-drv-nvidia-cuda"], check=True)


def wait_for_nvidia_modules(timeout=1800):
    _log.info("Waiting for NVIDIA modules to build...")
    start = time.time()

    while True:
        result = run(
            ["modinfo", "-F", "version", "nvidia"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            break

        if time.time() - start > timeout:
            _log.error("ERROR: NVIDIA module build timeout.")
            sys.exit(1)

        time.sleep(30)


def rebuild_modules():
    _log.info("Rebuilding akmods...")
    run(["sudo", "akmods", "--force"], check=True)

    _log.info("Rebuilding initramfs (dracut)...")
    run(["sudo", "dracut", "--force"], check=True)


def disable_gsp_firmware():
    _log.info("Disabling NVIDIA GSP firmware...")
    run([
        "sudo", "grubby",
        "--update-kernel=ALL",
        "--args=nvidia.NVreg_EnableGpuFirmware=0",
    ], check=True)


def preprocessing():
    home = Path.home()
    upgrade_flag = home / ".nvidia-upgrade-done"
    mok_flag = home / ".nvidia-mok-done"

    prepare_rpm_fusion_repos()

    # 1) System upgrade
    if not upgrade_flag.exists():
        if update_system():
            _log.info("Upgrade complete. Reboot required.")
            upgrade_flag.touch()
            do_reboot()
        else:
            _log.info("System upgrade not needed.")
            upgrade_flag.touch()

    # 2) MOK key generation/import
    if not mok_flag.exists():
        install_signing_modules()
        generate_and_import_key()

        _log.info(
            "Reboot required to enroll MOK.\n"
            "During boot: select 'Enroll MOK' -> 'Continue' and enter your password."
        )

        mok_flag.touch()
        do_reboot()


def main():
    preprocessing()

    ensure_kernel_devel_matches()
    install_nvidia_drivers()

    if INSTALL_CUDA:
        install_cuda()

    wait_for_nvidia_modules()
    rebuild_modules()

    if DISABLE_GSP:
        disable_gsp_firmware()

    _log.info("Setup completed. Perform a final reboot to activate NVIDIA drivers.")


if __name__ == "__main__":
    main()
