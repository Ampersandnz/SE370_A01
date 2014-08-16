
    # Keep a single pipe outside the loop, so that each iteration's output
    # can be piped into the next one's input, if necessary.
    pipe_read, pipe_write = os.pipe()

    # Don't want to redirect input of first command in first iteration of loop.
    first_iteration = True
    last_iteration = False

    while len(commands_to_pipe) > 0:
        command = commands_to_pipe[0]

        last_iteration = len(commands_to_pipe) == 1

        pipe_pid = os.fork()

        # Process pipe_pid will execute the command, then terminate.
        if pipe_pid == 0:

            if not first_iteration:
                print ('not first iteration')
                os.dup2(pipe_read, sys.stdin.fileno())

            # Reinitialise pipe so that commands only get the output of their single predecessor, not all of them.
            pipe_read, pipe_write = os.pipe()
            print('pipe recreated')

            if not last_iteration:
                print ('not last iteration')
                os.dup2(pipe_write, sys.stdout.fileno())

            do_command(command)
            os._exit(0)

        else:
            print('about to start waiting for child process')
            sleep(0.5)

            first_iteration = False
            # First two commands have been executed; remove them from the list.
            print("REMOVING FIRST COMMAND FROM LIST")
            commands_to_pipe.pop(0)
            print("REMAINING COMMANDS = " + str(len(commands_to_pipe)))
    print('loop finished')