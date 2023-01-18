"""GDB SavePatch script
Evan Allen and Kyle Verna, 2021

Command format:
    patch filename start_addr end_addr

    where the arguments represent:
        filename    - the name of the file to patch.
        start_addr  - the starting address of the 
                      memory IN THE CURRENTLY
                      DEBUGGED PROCESS to patch
                      into {filename}. 
        end_addr    - the ending address of the 
                      memory IN THE CURRENTLY 
                      DEBUGGED PROCESS to patch
                      into {filename}.

This command figures out the base address of 
the process being debugged and then dumps the 
memory from the specified section of the current
process into a file at the corresponding offset.

The file offset is calculated by taking
    file_offset = debug_memory_offset - base_addr


"""


import os
import traceback
import shutil

# Format string that provides the path to the 
# file where the memory mapping of a process is stored.
# The "{0}" is a format specifier that should be filled
# in with the PID of the target process using .format().
#
# Example: A process with PID = 1234 should have
#   /proc/1234/maps
proc_map_file_format = "/proc/{0}/maps"


class PatchCommand(gdb.Command):
    """Patches a file from GDB.
    TODO: Add more documentation.
    """

    def __init__(self):
        super(PatchCommand, self).__init__(
            "patch", gdb.COMMAND_USER
        )

    def get_inferior_pid(self):
        """
        Get the PID of the current inferior in GDB
        (i.e., the current process being debugged).

        :returns: The PID of the current inferior.
        """
        inferior = gdb.selected_inferior()
        return inferior.pid

    def get_base_addr(self):
        """
        Get the base address of the current inferior in GDB.
        Reads from /proc/{pid}/maps file.

        :returns: The base address of the current inferior.
        """
        pid = self.get_inferior_pid()
        print(f"pid = {pid}")

        if pid == 0:
            print("You must be currently debugging a program" \
                  " for find_base_addr to work.")
            return 0

        # Create the actual path to the process using the
        # format string and the PID we found.
        proc_map_file_str = proc_map_file_format.format(pid)

        # The file we just found has many entries representing
        #   sections in memory.
        # 
        # Each line looks begins like this:
        #   55656f5f7000-55656f61a000 ...(more things)
        #
        # We want the starting address of the first section.
        #
        # To find this, we can just read a single line, 
        #   split the line by "-", and take the first 
        #   result.
        with open(proc_map_file_str, 'r') as procfile:
            first_line = procfile.readline()
            base_addr = first_line.split('-')[0]
            return int(base_addr, 16)

    def print_help(self):
        print("Usage: patch filename start_addr end_addr")
        print("Currently, only number literals are supported"
              "for start_addr and end_addr.")

    def do_patch(self, filename, proc_start_addr, proc_end_addr):
        """Actually patch the file."""

        mem_len = proc_end_addr - proc_start_addr
        if mem_len < 0:
            print("end_addr must be greater than start_addr")
            self.print_help()
            return

        inferior = gdb.selected_inferior()
        selected_mem = inferior.read_memory(proc_start_addr, mem_len)

        # Get the starting address of where this memory
        # should go in the file to patch.
        file_start_addr = proc_start_addr - self.get_base_addr()

        print("proc_start_addr = {0:08x}; self.get_base_addr() = {1:08x}".format(proc_start_addr, self.get_base_addr()))

        dest_filename = filename + "_patch"

        # Do the patch!
        try:
            print(f"filename = {filename}; dest_filename = {dest_filename}")
            # Create copy of binary
            shutil.copyfile(filename, dest_filename)
            shutil.copymode(filename, dest_filename)

            with open(dest_filename, "r+b") as write_file:

                # Patch copy file
                print("{0:08x} = file_start_addr".format(file_start_addr))
                write_file.seek(file_start_addr)
                write_file.write(selected_mem.tobytes())

        except Exception as e:
            print(traceback.format_exc())

    def invoke(self, args, from_tty):
        """
        Callback for when a user runs the "patch" command.

        :param args: A *single* string representing *all* the 
            arugments to this command. Use gdb.string_to_argv
            to convert to an argv-like string list.
        :param from_tty: True if the user entered this command
            at the terminal, and False otherwise.
        """
        args = gdb.string_to_argv(args)
        
        if len(args) != 3:
            self.print_help()
            return

        try:
            filename = args[0]

            # Base 0 tells `int` to figure out the base
            # itself as if the input string represented
            # an integer literal (i.e., 0x13 is in base 16,
            # 13 is in base 10, etc.).
            start_addr = int(args[1], 0)
            end_addr = int(args[2], 0)
        except ValueError:
            print("Invalid argument found.")
            self.print_help()
        else:
            self.do_patch(filename, start_addr, end_addr)
            

# Create an instance of the command.
# This must be here.
PatchCommand()
