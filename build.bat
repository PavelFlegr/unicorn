set CFLAGS=-target x86_64-unknown-windows -ffreestanding -fshort-wchar -mno-red-zone -Isrc\gnu-efi\inc -Isrc\gnu-efi\inc\x86_64 -Isrc\gnu-efi\inc\protocol
set LDFLAGS=-target x86_64-unknown-windows -nostdlib -Wl,-entry:efi_main -Wl,-subsystem:efi_application -fuse-ld=lld-link
clang %CFLAGS% -c -o obj\hello.o src\hello.c
clang %CFLAGS% -c -o obj\data.o src\gnu-efi\lib\data.c
clang %LDFLAGS% -o BOOTX64.EFI obj\hello.o obj\data.o