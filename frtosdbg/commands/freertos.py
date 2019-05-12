import frtosdbg.commands


@frtosdbg.commands.PrefixCommand()
def freertos():
    """Main FreeRTOS command."""
    for cmd_name in frtosdbg.commands.commands:
        print(cmd_name)
