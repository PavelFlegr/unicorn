# Unicorn OS
## Build on Windows

> git clone https://github.com/PavelFlegr/unicorn

install hyper-v

install clang
```
cd unicorn
build.bat
powershell ./makehd.ps1
```

create virtualbox(or other) vm

use built hd.vhd as hard disk for a virtualbox

enable efi

run vm and in efi shell:
```
f0:
unicorn.efi
```
