# GDB-binary-patch

**Evan Allen @evallen, Melanie Verna @kverna**

This repository contains a plugin for the GNU Debugger (GDB) 
that allows users to patch a binary on disk with granular
control. 

## Installation
1. Download the `patch.py` file to a directory of your
choice such as `~/scripts`.
That's it!

## Usage

1. Open the executable you intend to patch in GDB.
2. Make the intended changes to the executable in memory
as you normally would. For example, you might
use the `set` command to change a certain byte.
3. Import the patch script using GDB's `source` command, e.g.:
```gdb
source ~/scripts/patch.py
```
4. Run the patch command:
  ```gdb
  patch <filename> <start_addr> <end_addr>
  ```
  where
  * `<filename>` refers to the name of the original executable you
  would like to patch.
  * `<start_addr>` refers to the address of the first byte of 
  memory _in the GDB process_ that you would like to save to the 
  patched file.
  * `<end_addr>` refers to the address of the last byte of memory
  _in the GDB process_ that you would like to save to the patched
  file. 

After running the command, a new file will be created with the same
name as the original executable with "`_patch`" added to the end
of the filename. This file will be a copy of the original
executable file, but with the user's selected memory patched in.
This allows you to patch a binary without having to worry about
accidentally overwriting the original file.

However, if a file with "`<executable>_patch`" already exists
(where `<executable>` is the name of the original executable
file), then it will be overwritten when the `patch` command 
is executed.

### Example Usage

```gdb
set {int}0x0000555555555152 = 0x06
patch ../test 0x000055555555514d 0x000055555555515d
```

## Implementation Details

Our `patch` command operates by completing the following steps
upon execution:
1. It reads the memory the user wants to save a patch for from
the process currently being debugged.
2. It determines the equivalent file addresses of the memory the
user selected. For example, if the base address of the process
is `0x10000`, then the process memory address `0x1BEEF` corresponds
to the file address `0x0BEEF`. 
3. It copies the original executable and appends "`_patch`" to it.
4. It copies the memory it read from the user's process in GDB
into the calculated equivalent file addresses of the copied
executable on disk. This effectively 
saves the memory the user selected, allowing the user to save any
patches they have made in GDB permanently. 

## Other files in repository
The repository contains a simple test program, `test.c` with
a compiled `test` x86 executable to try this script on.

## Alternatives

* GDB `set write on` command

