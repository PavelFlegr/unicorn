set CFLAGS=-target x86_64-unknown-windows -ffreestanding -fshort-wchar -mno-red-zone -Isrc\uefi -Isrc\uefi\Uefi -Isrc\uefi\X64
set LDFLAGS=-target x86_64-unknown-windows -nostdlib -Wl,-entry:efi_main -Wl,-subsystem:efi_application -fuse-ld=lld-link
clang %CFLAGS% -c -o obj\hello.o src\hello.c
clang %LDFLAGS% -o unicorn.efi obj\hello.o