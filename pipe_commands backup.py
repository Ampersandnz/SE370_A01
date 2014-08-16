# This function takes in a list of commands, each of which pipes its output into the next, and calls them.
def pipe_commands(commands_to_pipe):
    
    # Keep a single pipe outside the loop, so that each iteration's output
    # can be piped into the next one's input, if necessary.
    next_pipe_read, next_pipe_write = os.pipe()

    # Don't want to redirect input of first command in first iteration of loop.
    first_iteration = True
    # Don't want to redirect output of last command in last iteration of loop.
    last_iteration = False

    while len(commands_to_pipe) > 1:
        print('' + str(len(commands_to_pipe)))
        # Last iteration is when there are no commands remaining in the list.
        if len(commands_to_pipe) < 3:
            print("THIS IS THE LAST ITERATION")
            last_iteration = True

        # Only one command left. It will take its input from the previous loop iteration and print its output to stdout.
        if len(commands_to_pipe) == 1:
            command_pid = os.fork()
            print('ONLY ONE COMMAND LEFT')
            if command_pid == 0:
                # Redirect previous iteration's output into this command's input.
                os.dup2(next_pipe_read, sys.stdin.fileno())
                print("DOING LAST COMMAND WITH INPUT FROM PREVIOUS ITERATION")
                # Child process does command
                do_command(first_command)
            else:
                print("REMOVING LAST COMMAND")
                commands_to_pipe.pop(0)

        # Two or more commands remaining.
        else:
            # Create a pipe to redirect the output of command 1 into the input of command 2.
            pipe_read, pipe_write = os.pipe()

            # Each iteration of the loop only operates on the current first two commands in the list.
            first_command = commands_to_pipe[0]
            second_command = commands_to_pipe[1]

            # Fork the process - child will perform command 1, with its output sent to the pipe, then terminate.
            # Parent will continue through the loop.
            pipe_command_1_pid = os.fork()

            if pipe_command_1_pid == 0:
                # Standard output now goes to pipe.
                print ("COMMAND 1 OUTPUT REDIRECTED")
                os.dup2(pipe_write, sys.stdout.fileno())

                if not first_iteration:
                    # Get input to this command from the previous pipe in the series.
                    os.dup2(next_pipe_read, sys.stdin.fileno())

                # Child process does command
                do_command(first_command)

            else:
                # Re-initialise the outside pipe variables.
                # Otherwise each iteration of the loop will receive the output of all the others,
                # not just the one preceding it.
                next_pipe_read, next_pipe_write = os.pipe()

            # Fork the parent process again - this child will perform command 2, with its input read from the pipe,
            # then terminate.
            # Parent will again continue through the loop.
            pipe_command_2_pid = os.fork()

            if pipe_command_2_pid == 0:
                # Standard input now comes from the pipe.
                print ("COMMAND 2 INPUT REDIRECTED")
                os.dup2(pipe_read, sys.stdin.fileno())
                if not last_iteration:
                    # Pipe output of this command as input to the next pipe in the series.
                    print ("COMMAND 2 OUTPUT REDIRECTED")
                    os.dup2(next_pipe_write, sys.stdout.fileno())
                print ("ABOUT TO EXECUTE COMMAND 2")

                do_command(second_command)

            else:
                first_iteration = False
                # First two commands have been executed; remove them from the list.
                print("REMOVING FIRST TWO COMMANDS FROM LIST")
                commands_to_pipe.pop(0)
                commands_to_pipe.pop(0)
                print("REMAINING COMMANDS = " + str(len(commands_to_pipe)))
                os.wait()