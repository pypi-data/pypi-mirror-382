import os

def startup():
    # print("startup ",sys.argv)
    
    ''' if called with no arguments send shutdown to pipe, wait 2 seconds delete pipe file and launch application. if called with arguments send args to pipe if it exist otherwise ''' 

    parser = argparse.ArgumentParser(
                    # prog='ProgramName',
                    # description='What the program does',
                    # epilog='Text at the bottom of help'
                    )

    parser.add_argument('task',nargs='?')             # optional positional argument
    parser.add_argument('-s', '--debug_systems', nargs="*", default=[])      # option that takes a value
    parser.add_argument('-l', '--debug_level', default=1)       # option that takes a value
    parser.add_argument('-f', '--force', action='store_true', help="Force restart by deleting existing named pipe")  # on/off flag
    # parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag

    args = parser.parse_args()
    print(args)

    conf.debug_level = int(args.debug_level)
    conf.debug_systems = args.debug_systems

    if args.force:
        print("Lanched with --force flag, forcibly deleting old pipe")
        try:
            os.remove(pipe_file)
        except Exception as e:
            print(e)
            
    try:
        os.mkfifo(pipe_file)

        signal.signal(signal.SIGUSR1, Application.signal_handler) 
        app = Application()

        if args.task:
            print("Writing args.task to pipe", args.task)
            with open(pipe_file, "w") as pipeout:
                pipeout.write(args.task)
                pipeout.close()


    except FileExistsError:
        print("Named pipe exists, application must be running (or improperly shut down.) ")

        # if args: pass to pipe and exit
        if args.task:
            pipe_line = args.task
        else:
            pipe_line = "open_task_window"
        

        print("Writing arg ",pipe_line," to pipe")

        with open(pipe_file, "w") as pipeout:
            pipeout.write(pipe_line)
            pipeout.close()

        exit()



    except Exception as e:
        print(f"Named pipe creation failed: {e}")

