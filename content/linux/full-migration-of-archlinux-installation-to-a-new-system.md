Title: Full migration/clone of linux installation to a new system(Without reinstalling)
Date: 2012-11-14 13:26
Author: Sam Stoelinga
Category: Linux
Tags: archlinux, geek, linux, migration
Slug: full-migration-of-archlinux-installation-to-a-new-system

I'm switching to a new laptop, but don't want to have to install
Archlinux again. So instead of re-installing I will try to copy all
files and hope the system will work. In this blogpost I will describe
the steps and issues I encountered while doing so.

  **Status: Succeeded!!!!**

Summary of plan: Boot from a live usb on the new system, create
partitions with gparted, copy all the files over, change /etc/fstab to
partition uuids, regenerate the mkinitcpio stuff (Still should read what
this actually is).

On the new laptop:
Boot from a Ubuntu live cd and start gparted
Create a / partition (ext4)
Create a /home parition (ext4)
Create a /boot partition (ext2)
Mount the newly created partitions under /mnt/
Copy all files of old / /home to new / /home using rsync
Chroot into the copied files on the new laptop
Change the /etc/fstab to point to the new partition UUIDs
Install grub on new harddrive and reconfigure Grub
Recreate the ramdisk:

Environment:
Old Laptop:
Archlinux 64 bits, 8GB memory, crappy processor
IP: 192.168.1.108
Connected to router via internet cable, WIFI was way too slow to copy files

New laptop:
Previously got Ubuntu installed but will totally wipe that away.
IP: 192.168.1.111

Detailed steps:
Boot from a live ubuntu USB on the new laptop and do the following:
Use gparted or fdisk to create the following partitions:
/dev/sda1 filesystem: ext2 size: 512mb label: boot (100mb is needed, but had enough space will become /boot)
/dev/sda2 filesystem: ext4 size: 30gb label: root(will become root /)
/dev/sda3 filesystem: ext4 size: 180gb label: home(will become home /home)

After you've created the partitions successfully, mount all partitions to /mnt
[bash]
mount /dev/sda2 /mnt
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot
mkdir /mnt/home
mount /dev/sda3 /mnt/home
[/bash]

Now go back to the old Archlinux laptop and copy all files to the newly created partitions:
[bash]rsync -azv --progress --exclude=/dev --exclude=/sys / root@192.168.1.111:/mnt/[/bash]

This may take a while..................

After everything is copied over:
Change /etc/fstab to look as follows:
[bash]tmpfs /tmp tmpfs nodev,nosuid 0 0
LABEL=root / ext4 defaults,noatime 0 1
LABEL=home /home ext4 defaults,noatime 0 2
LABEL=boot /boot ext2 defaults,noatime 0 2[/bash]

Reinstall Grub on the hard drive:
[bash]grub-install --force --target=i386-pc --recheck --debug /dev/sda[/bash]

Why the --force?
I encountered the following error: will not proceed with blocklists archlinux so after reading the wiki it said I could fix this by using --force.

Regenerate grub config:
[bash]grub-mkconfig -o /boot/grub/grub.cfg[/bash]

Regenerate initial ramdisk:
[bash]mkinitcpio -p linux[/bash]

Reboot the system

I also had to update my modules.d/xxx to not load some specific AMD modules for laptop-mode tools as the new laptop has an intel processor.
Also has to remove the ati driver and change to intel open source
driver:
[bash]
yaourt -Rs xf86-video-ati
yaourt -S xf86-video-nouveau
[/bash]

The reason I'm switching: My current HP 625 laptop has served it's
purpose for nearly 2 years. The CPU seems to be nearly burnt out, when I
opened the laptop few days ago, the CPU was totally black, but still
working lol. And the CPU often get's too hot, hence I'm switching to my
gf's laptop which specs are better.

References I used:
Archlinux wiki: Migrate installation to new
hardware https://wiki.archlinux.org/index.php/Migrate_installation_to_new_hardware
Forum post which basically does the same
thing https://bbs.archlinux.org/viewtopic.php?id=145025
