rm hd.vhd
New-VHD -Path hd.vhd -fixed -SizeBytes 500mb | Mount-VHD -Passthru |Initialize-Disk -FriendlyName "EFI System Partition" -Passthru |New-Partition -DriveLetter K -Size 200mb |Format-Volume -FileSystem FAT32
cp refind K:/EFI/refind -recurse
Dismount-VHD -Path hd.vhd
