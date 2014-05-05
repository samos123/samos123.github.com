Title: Remove/detach a PCI device linux (kvm VGA passthrgough Nvidia Quadro 2000)
Date: 2013-06-09 08:55
Author: Sam Stoelinga
Category: Linux
Slug: removedetach-a-pci-device-linux-kvm-vga-passthrgough-nvidia-quadro-2000

**Answer:**  

    :::bash
    echo -n "1" > /sys/bus/pci/devices/0000:02:00.0/remove

Where 0000:02:00.0 is related to your pci device address which can
be obtained from the command `lspci`

**Related story:**  
Was working on KVM vga passthrough and encountered problems with the
graphics card nvidia Quadro 2000.

This was the error I got when attaching this particular VGA card:  
libvirtError: internal error Unable to reset PCI device 0000:83:00.0:
internal error Active 0000:83:00.1 devices on bus with 0000:83:00.0, not
doing bus reset

After investigating I noticed that 0000:83:00.1 is a Sound compatible
controller on the video card. Tried lots of stuff such as disable the
drivers of that sound compatbile controller but without much success.

So in the end I decided I should just remove the pci device, but
couldn't find how to do it, so just tried some stuff and this is what I
came up with. I have no idea if it will break your system or what it
does exactly, but after removing the sound compatbile controller I was
able to pass the nvidia Quadro 2000 card to my virtual machine :)

Here is the code to remove the pci device using a simple linux command:  

    lspci -k | grep NVID -C3  
    00:83.0 VGA compatible controller: Nvidia Quadro 2000.... (Dont have
    the card anymore)  
    00:83.1 Sound device: Nvidia Quadro Audo captabiel balbalbal. 2000 GP  
    echo -n "1" > /sys/bus/pci/devices/0000:02:00.1/remove  
