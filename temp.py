from core.console_input_getter import ConsoleInputGetter

command_argument = 'dummyCommand'
argument_list = ['--address=']
argument_list1 = ['--alias=a', '--coco=1', '--coco=2', '--address=3', 'bytecode=12412341234143141241']
argument_list0 = ['--alias=a', '--address=1', '--address=2', '--address=3']
argument_list2 = ['--address=0x1', '--address=0x2', '--gas=1', '--gas=2', '--address=0x3', '--bytecode=12412341234143141241']
ConsoleInputGetter().get_gnosis_input_command_argument(command_argument, argument_list2, [])
