import argparse
from functools import wraps


def with_argparse(main_function):
    wraps(main_function)

    def wrapper():
        parser = argparse.ArgumentParser(
          description="Телефонный справочник",
          epilog="консольная версия"
        )

        parser.add_argument(
          '-v',
          '--version',
          action='version',
          version='%(prog)s 0.2.0',
          help='Версия пакета'
        )

        parser.add_argument(
          '--author',
          action='store_true',
          help='Автор проекта'
        )
        args = parser.parse_args()

        if args.author:
            print('Anton Ivanov')
            return

        if args.version:
            print('0.2.0')
        main_function()
    return wrapper
