# SoftEng 370 Assignment 1
# Python3 shell
# Michael Lo
# mlo450
# 5530588

# Resources:
# https://idea.popcount.org/2012-12-11-linux-process-states/

import os
import signal
import shlex
import sys


# Commands in the CommandHistory list will include pipes, &, and multiple commands.
# Most Commands used in the program itself will represent a single program execution with arguments.
class Command:
    def __init__(self, command, arguments):
        self.command = command
        self.arguments = arguments
        if len(self.arguments) == 0:
            self.arguments = ['']

    def get_command(self):
        return self.command

    def get_arguments(self):
        return self.arguments

    def get_full_command(self):
        return self.command + ' [' + ', '.join(self.arguments) + ']'

    def call_again(self):
        do_full_command(" ".join(self.arguments))


# This class manages the list of recently entered input strings.
class CommandHistory:
    def __init__(self):
        # Entries stored as strings.
        self.commandList = []

    def add_command(self, command):
        self.commandList.append(command)

    def remove_command(self, index):
        self.commandList.pop(index - 1)

    def get_command(self, index):
        if len(self.commandList) >= index:
            return self.commandList[index - 1]

    def set_command(self, index, command):
        self.commandList[index - 1] = command

    def print_commands(self):
        for i in range(0, len(self.commandList)):
            if i >= len(self.commandList) - 10:
                print ('%d: %s' % (i + 1, ''.join(self.commandList[i].get_arguments())))

    @property
    def num_commands(self):
        return len(self.commandList)


# This class represents a single background process.
# class Job:
#     def __init__(self, pid, unique_id):
#         self.pid = pid
#         self.unique_id = unique_id
#
#     def get_pid(self):
#         return self.pid
#
#     def get_unique_id(self):
#         return self.unique_id
#
#     def check_state(self):
#         # Use provided code to get state of process.
#         state = get_state_by_pid(self.pid)
#         return state
#
#     def foreground(self):
#         # Bring this process to the foreground.
#         return
#
#     def background(self):
#         # Send this process to the background.
#         return


# This class manages the list of jobs (background processes).
# class JobsList:
#     def __init__(self):
#         self.jobList = []
#         self.next_unique_id = 1
#
#     def add_job(self, pid):
#         job = Job(pid, self.next_unique_id)
#         self.jobList.append(job)
#         self.next_unique_id += 1
#         return job
#
#     def remove_job(self, index):
#         self.jobList.pop(index - 1)
#
#     def remove_job(self, job):
#         self.jobList.remove(job)
#
#     def get_job(self, index):
#         return self.jobList[index - 1]
#
#     def get_all_jobs(self):
#         return self.jobList
#
#     @property
#     def num_jobs(self):
#         return len(self.jobList)


# When the key combination CTRL+Z is pressed, the correct shell function is called.
def intercept_ctrl_z(signum, frame):
    sc_ctrl_z()

# Lists the commands that will be executed by this shell rather than the system.
shellCommandList = ['pwd', 'cd', 'h', 'history', 'bg', 'fg', 'kill', 'q', 'quit', 'exit', 'jobs']

command_history = CommandHistory()
# job_list = JobsList()
home_dir = os.getcwd()

# Intercepts CTRL+Z key presses to perform our own functionality, rather than this shell being sent to background.
signal.signal(signal.SIGTSTP, intercept_ctrl_z)


# Accepts user input, and runs the commands when they are entered.
# noinspection PyProtectedMember
def main():
    while 1:
        try:
            # for job in job_list.get_all_jobs():
            #     state = job.check_state()
            #     if state is None:
            #         job_list.remove_job(job)
            #         print()
            #     elif state == 'Z':
            #         os.wait()
            #     else:
            #         print("Job[" + str(job.get_pid()) + "] = " + state)

            user_input = input('psh> ')
            if user_input.strip() != '':
                try:
                    do_full_command(user_input)
                # After catching any exception, exit the cloned child process that contained the system call.
                # Otherwise there would be two running instances of the shell.
                except FileNotFoundError:
                    print (parse_input(user_input)[0] + ': command not found')
                    os._exit(1)
                except IndexError:
                    print("Invalid input")
                    os._exit(1)
        except KeyboardInterrupt:
            print('')


# Saves the user's input in history, parses the string into is separate command[s] and arguments,
# then determines if a given command with arguments should be executed by the shell or the system.
def do_full_command(user_input):
    command_with_args = parse_input(user_input)
    command = Command(command_with_args[0], command_with_args)

    command_history.add_command(Command(command, command_with_args))

    amper = '&' in command_with_args

    if amper:
        # We know there was an ampersand in the input, it doesn't need to be passed in as an argument to a program.
        command_with_args.pop(len(command_with_args) - 1)

    child_pid = os.fork()

    if child_pid == 0:
        # Pipe(s) exist in command - multiple commands in succession.
        if '|' in command_with_args:

            # Returns a list of (Command objects)
            commands_to_pipe = split_by_pipes(command_with_args)
            pipe_commands(commands_to_pipe)

            # Ensure all child processes terminate rather than returning to the main shell while loop..
            os._exit(0)

        #Only one command to execute.
        else:
            do_command(command)

    else:
        # if amper:
        #     # Add process child_pid to the list of background jobs.
        #     job = job_list.add_job(child_pid)
        #     print("[" + str(job.get_unique_id()) + "]    " + str(job.get_pid()))
        # else:
            os.waitpid(child_pid, 0)
    return


# This function takes in a list of commands, each of which pipes its output into the next, and calls them.
def pipe_commands(commands_to_pipe):



# Executes a single Command object.
def do_command(command):
    if is_shell_command(command):
        do_shell_command(command)
    else:
        do_system_command(command)
    os._exit(0)


# Calls the relevant shell function for this command, passing in its arguments.
def do_shell_command(command):
    shellCommands[command.get_command()](command.get_arguments())
    return


# Calls the relevant system command, passing in its arguments.
def do_system_command(command):
    os.execvp(command.get_command(), command.get_arguments())
    return


# Takes in the full typed string and returns the command split into its component arguments.
def parse_input(user_input):
    lexer = shlex.shlex(user_input, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args


# Takes in a complicated line of user input with piping,
# and splits it into its component commands and their respective sets of arguments.
def split_by_pipes(command_with_args):
    multiple_commands_with_args = []
    while '|' in command_with_args:
        temp_command_with_args = command_with_args
        index_of_first_pipe = temp_command_with_args.index('|')

        # Create Command object of first command, and append it to the list to be returned.
        multiple_commands_with_args.append(Command(temp_command_with_args[0], command_with_args[0:index_of_first_pipe]))

        # Remove first command, its arguments, and the following pipe from the original list of strings.
        del command_with_args[:index_of_first_pipe + 1]

    # Add last command and its arguments to the list.
    multiple_commands_with_args.append(Command(command_with_args[0], command_with_args))

    return multiple_commands_with_args


# Checks if a given command should be executed by this shell, or simply passed on to the system.
def is_shell_command(command):
    return command.get_command() in shellCommandList


# Shell command functions follow:
# Print working directory.
def sc_pwd(arguments):
    print(os.getcwd())
    return arguments


# Change directory.
def sc_cd(arguments):
    if len(arguments) == 1:
        new_path = home_dir

    elif arguments[1].startswith('..'):
        new_path = arguments[1]

    elif arguments[1].startswith('.'):
        add_to_path = (arguments[1])[1:]
        new_path = os.getcwd() + add_to_path

    elif arguments[1].startswith('/'):
        new_path = arguments[1]

    elif arguments[1].startswith('~'):
        new_path = os.path.expanduser(arguments[1])

    else:
        new_path = os.getcwd() + '/' + arguments[1]

    if os.path.isdir(new_path):
        os.chdir(new_path)
    else:
        print('psh: cd: ' + arguments[1] + ': No such file or directory')
    return


# History. With no arguments, returns the last ten commands used.
# With a numerical argument, calls the command with that index again.
def sc_h(arguments):
    if len(arguments) == 1:
        command_history.print_commands()
    else:
        command = command_history.get_command(int(arguments[1]))
        command_history.set_command(command_history.num_commands, command)
        command.call_again()


# Sends a process to the background.
# NOT YET IMPLEMENTED
def sc_bg(arguments):
    #os.kill(process.pid, signal.SIGCONT)
    return arguments


# Brings a process to the foreground.
# NOT YET IMPLEMENTED
def sc_fg(arguments):
    #os.kill(process.pid, signal.SIGCONT)
    return arguments


# Forces a process to stop.
# NOT YET IMPLEMENTED
def sc_kill(arguments):
    #os.kill(process.pid, signal.SIGKILL)
    return arguments


# Forces a process to sleep/wait.
# NOT YET IMPLEMENTED
def sc_ctrl_z():
    #os.kill(process.pid, signal.SIGSTOP)
    return


# Quits this shell
def sc_q(arguments):
    if len(arguments) > 1:
        print (' '.join(arguments[1:]))
    parent_pid = os.getppid()
    os.kill(parent_pid, signal.SIGKILL)
    os._exit(0)


# Lists the current background processes and their states
def sc_jobs(arguments):
    return arguments


# Uses the /proc/pid/state file to find the state of a process.
def get_state_by_pid(pid):
    try:
        for line in open("/proc/%d/status" % pid).readlines():
            if line.startswith("State:"):
                # Possible return values:
                # R = Running
                # S = Sleeping (Interruptible)
                # D = Sleeping (Uninterruptible)
                # Z = Zombie
                # T = Stopped
                return line.split(":", 1)[1].strip().split(' ')[0]
    except FileNotFoundError:
        return None

# Map the inputs to the function blocks.
shellCommands = {
    shellCommandList[0]: sc_pwd,
    shellCommandList[1]: sc_cd,
    shellCommandList[2]: sc_h,
    shellCommandList[3]: sc_h,
    shellCommandList[4]: sc_bg,
    shellCommandList[5]: sc_fg,
    shellCommandList[6]: sc_kill,
    shellCommandList[7]: sc_q,
    shellCommandList[8]: sc_q,
    shellCommandList[9]: sc_q,
    shellCommandList[10]: sc_jobs
}

if __name__ == '__main__':
    main()