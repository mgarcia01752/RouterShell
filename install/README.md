


```markdown
# RouterShell Installation Guide

This guide provides step-by-step instructions for installing and uninstalling RouterShell on your Linux system. RouterShell is a powerful tool for managing network configurations.

## Prerequisites

- You must have sudo privileges to run some installation steps.
- Make sure your Linux system is connected to the internet to download required packages.

## Tested
   Ubuntu 22.x, 23.x
   RedHat 

## Installation

### Step 1: Install RouterShell (as sudo)

1. Open a terminal.

2. Navigate to the installation directory:

   ```bash
   cd /path/to/RouterShell/install
   ```

3. Run the installation script as sudo:

   ```bash
   sudo ./install.sh
   ```

   This script will install RouterShell and its dependencies.

### Step 2: Install pip3 (as a regular user)

1. Open a terminal.

2. Navigate to the installation directory:

   ```bash
   cd /path/to/RouterShell/install
   ```

3. Run the installation script as a regular user:

   ```bash
   ./install-pip.sh
   ```

   This script will install pip3 and necessary Python packages.

## Uninstallation

### Step 1: Uninstall RouterShell

1. Open a terminal.

2. Navigate to the installation directory:

   ```bash
   cd /path/to/RouterShell/install
   ```

3. Run the uninstallation script as sudo:

   ```bash
   sudo ./uninstall.sh
   ```

   This script will remove RouterShell and its dependencies.

### Step 2: Uninstall pip3 (as a regular user)

1. Open a terminal.

2. Navigate to the installation directory:

   ```bash
   cd /path/to/RouterShell/install
   ```

3. Run the uninstallation script as a regular user:

   ```bash
   ./uninstall-pip.sh
   ```

   This script will remove pip3 and the installed Python packages.

## Enjoy using RouterShell!

You have successfully installed and uninstalled RouterShell. For usage instructions, please refer to the documentation or user guide.
```

Replace `/path/to/RouterShell/install` with the actual path to your installation directory. This README provides clear instructions for both installation and uninstallation of RouterShell and related components.