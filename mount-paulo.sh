#!/bin/sh

FICHIER=/media/jm/Elements/backup/xen/paulo
sudo mount -o loop,offset=32256 $FICHIER /mnt/paulo/
sudo mount -o loop,offset=3159359488 $FICHIER /mnt/paulo/home/
sudo mount -o loop /media/jm/Elements/backup/xen/paulo-home /mnt/paulo-old-home/