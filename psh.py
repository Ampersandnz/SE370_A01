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
        self.fd_in = sys.stdin.fileno()
        self.fd_out = sys.stdout.fileno()
        self.is_job = False
        self.is_part_of_pipe = False
        self.history_with_pipe = '|' in arguments

    def get_command(self):
        return self.command

    def get_arguments(self):
        return self.arguments

    def __str__(self):
        to_string = " ".join(self.arguments)
        if self.is_job:
            to_string += " &"
        return to_string

    def set_fd_in(self, fd_in):
        self.fd_in = fd_in

    def set_fd_out(self, fd_out):
        self.fd_out = fd_out

    def set_is_job(self, is_job):
        self.is_job = is_job

    def set_is_part_of_pipe(self, is_part_of_pipe):
        self.is_part_of_pipe = is_part_of_pipe

    def set_history_with_pipe(self, history_with_pipe):
        self.history_with_pipe = history_with_pipe

    def execute(self):
        if self.history_with_pipe:
            do_full_command(str(self))
        else:
            if self.command in shellCommandList:
                if self.is_part_of_pipe:
                    child_pid = os.fork();
                    if child_pid == 0:
                        os.dup2(self.fd_in, sys.stdin.fileno())
                        os.dup2(self.fd_out, sys.stdout.fileno())
                        shellCommands[self.command](self.arguments)
                    elif self.is_job:
                        job_list.add_job(child_pid)
                        job_list.print_all()
                    else:
                        os.wait()
                else:
                    shellCommands[self.command](self.arguments)

            else:
                child_pid = os.fork();
                if child_pid == 0:
                    os.dup2(self.fd_in, sys.stdin.fileno())
                    os.dup2(self.fd_out, sys.stdout.fileno())
                    os.execvp(self.command, self.arguments)
                elif self.is_job:
                    job_list.add_job(child_pid)
                    job_list.print_all()
                else:
                    os.wait()


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
                print ('%d: %s' % (i + 1, str(self.commandList[i])))

    @property
    def num_commands(self):
        return len(self.commandList)


# This class represents a single background process.
class Job:
    def __init__(self, pid, unique_id):
        self.pid = pid
        self.unique_id = unique_id

    def get_pid(self):
        return self.pid

    def get_unique_id(self):
        return self.unique_id

    def check_state(self):
        # Use provided code to get state of process.
        state = get_state_by_pid(self.pid)
        return state

    def __str__(self):
        return '[' + str(self.unique_id) + '] ' + str(self.pid)


# This class manages the list of jobs (background processes).
class JobsList:
    def __init__(self):
        self.job_list = []
        self.next_unique_id = 1

    def add_job(self, pid):
        job = Job(pid, self.next_unique_id)
        self.job_list.append(job)
        self.next_unique_id += 1
        return job

    def remove_job(self, job):
        self.job_list.remove(job)

    def get_job(self, index):
        return self.job_list[index - 1]

    def get_all_jobs(self):
        return self.job_list

    def print_all(self):
        for job in self.job_list:
            print(str(job))

    @property
    def num_jobs(self):
        return len(self.job_list)


# When the key combination CTRL+Z is pressed, the correct shell function is called.
def intercept_ctrl_z(signum, frame):
    sc_ctrl_z()

# Lists the commands that will be executed by this shell rather than the system.
shellCommandList = ['pwd', 'cd', 'h', 'history', 'bg', 'fg', 'kill', 'q', 'quit', 'exit', 'jobs']

command_history = CommandHistory()
job_list = JobsList()
home_dir = os.getcwd()

# Intercepts CTRL+Z key presses to perform our own functionality, rather than this shell being sent to background.
signal.signal(signal.SIGTSTP, intercept_ctrl_z)


# Accepts user input, and runs the commands when they are entered.
def main():
    while 1:
        try:
            check_jobs()

            user_input = input('psh> ')
            if user_input.strip() != '':
                try:
                    do_full_command(user_input)
                # After catching any exception, exit the cloned child process that contained the system call.
                # Otherwise there would be two running instances of the shell.
                except FileNotFoundError:
                    print (parse_input(user_input)[0] + ': command not found')
                except IndexError:
                    print("Invalid input")
        except KeyboardInterrupt:
            print('')
        except EOFError:
            exit()


#Finds jobs that have finished since the last loop of the main function, and prints the corresponding output.
def check_jobs():
    for job in job_list.get_all_jobs():
        state = job.check_state()
        if state is None:
            job_list.remove_job(job)
            print()
        elif state == 'Z':
            os.waitpid(job.get_pid(), 0)
        else:
            print("Job [" + str(job.get_pid()) + "] = " + state)


# Saves the user's input in history, parses the string into is separate command[s] and arguments,
# then determines if a given command with arguments should be executed by the shell or the system.
def do_full_command(user_input):
    command_with_args = parse_input(user_input)

    amper = '&' in command_with_args
    piping = '|' in command_with_args

    add_to_history = Command(command_with_args[0], command_with_args)

    if amper:
        add_to_history.set_is_job(True)
    if piping:
        add_to_history.set_history_with_pipe(True)

    command_history.add_command(add_to_history)

    command = add_to_history

    if amper:
        # We know there was an ampersand in the input, it doesn't need to be passed in as an argument to a program.
        command_with_args.pop(len(command_with_args) - 1)

    # Pipe(s) exist in command - multiple commands in succession.
    if piping:

        child_pid = os.fork()

        if child_pid == 0:
            # Returns a list of (Command objects)
            commands_to_pipe = split_by_pipes(command_with_args)
            pipe_commands(commands_to_pipe)

        elif not amper:
            os.wait()

    #Only one command to execute.
    else:
        command.set_is_job(False)
        if amper:
            command.set_is_job(True)
        command.execute()
    return


# This function takes in a list of commands, each of which pipes its output into the next, and calls them.
def pipe_commands(commands_to_pipe):
    old_read = sys.stdin.fileno()

    for command in commands_to_pipe[:-1]:
        new_read, new_write = os.pipe()
        command.set_fd_in(old_read)
        command.set_fd_out(new_write)
        command.set_is_job(True)
        command.set_is_part_of_pipe(True)
        command.execute()

        old_read = new_read

    commands_to_pipe[-1].set_is_job(True)
    commands_to_pipe[-1].set_is_part_of_pipe(True)
    commands_to_pipe[-1].set_fd_in(old_read)
    commands_to_pipe[-1].execute()

    exit()


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

        # Remove the h <num> call from the history list; it will be replaced by the actual command executed.
        if command.history_with_pipe:
            command_history.remove_command(command_history.num_commands)
        else:
            command_history.set_command(command_history.num_commands, command)
        command.execute()


# Sends a process to the background.
def sc_bg(arguments):
    target_pid = os.getpid()
    if len(arguments) > 1:
        target_pid = int(arguments[1])
    os.kill(target_pid, signal.SIGCONT)


# Brings a process to the foreground.
def sc_fg(arguments):
    target_pid = os.getpid()
    if len(arguments) > 1:
        target_pid = int(arguments[1])
    os.kill(target_pid, signal.SIGCONT)


# Forces a process to stop.
def sc_kill(arguments):
    target_pid = os.getpid()
    if len(arguments) > 1:
        target_pid = int(arguments[1])
    os.kill(target_pid, signal.SIGKILL)


# Forces a process to sleep/wait.
def sc_ctrl_z():
    os.kill(os.getpid(), signal.SIGSTOP)


# Quits this shell
def sc_q(arguments):
    exit()


# Lists the current background processes and their states
def sc_jobs(arguments):
    job_list.print_all()


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