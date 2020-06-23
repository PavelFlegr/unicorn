rm hd.vhd
new-item mnt -itemtype directory >$null
$partition = New-VHD -Path hd.vhd -fixed -SizeBytes 500mb | Mount-VHD -Passthru |Initialize-Disk -Passthru |New-Partition -Size 200mb
$partition |Add-PartitionAccessPath -PassThru -AccessPath (Resolve-Path mnt) |Format-Volume -FileSystem FAT32 >$null
cp unicorn.efi mnt\unicorn.efi
$partition |Remove-PartitionAccessPath -AccessPath (Resolve-Path mnt)
Dismount-VHD -Path hd.vhd
rm mnt
