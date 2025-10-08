from src.cli_parser import with_argparse

# позволил себе сохранить переменную в замыкании для закрепления материала
# (в задании требуется хранить в глобальной области видимости)


@with_argparse
def launchPhoneDirectory() -> None:
    """Функция launchPhoneDirectory вызывает функцию phoneDirectory,
    объявленную в локальном контексте"""
    phoneDict = {}  # phoneDirectory замыкается на словарь phoneDict

    def phoneDirectory() -> None:
        """Функция phoneDirectory рекурсивно вызывается,
        отображая доступные действия до ввода пользователем '4'"""
        choice: int = int(
            input("""Телефонный справочник. Доступные действия: \n
            1. добавить контакт; \n
            2. вывести номера по имени; \n
            3. удалить контакты по имени. \n
            4. завершить программу \n

            Введите номер действия :
        """))
        if choice == 1:
            name = input(
                "Введите имя (может содержать только буквы и цифры):\n"
                )
            if name.isalnum():
                phoneNumber = input(
                    f"Добавьте номер без пробелов для контакта '{name}': \n")
                if phoneNumber.isdigit():
                    namePhoneList = phoneDict.get(name, [])
                    namePhoneList.append(phoneNumber)
                    phoneDict.setdefault(name, namePhoneList)
            else:
                print("Введены некорретные данные")
        elif choice == 2:
            name = input("Введите имя для просмотра контактов:\n")
            print('Имя\t\tНомер')
            for phoneNumber in phoneDict.get(name, []):
                print(f'{name}\t\t{phoneNumber}')
            if phoneDict.get(name, None) is None:
                print("В телефонном справочнике нет контактов с таким именем")
        elif choice == 3:
            name = input("Введите имя контакта для удаления:\n")
            phoneDict.pop(name, None)
        elif choice == 4:
            print("Всего доброго!")
            return
        else:
            print("Выбрана несуществующая опция")
        phoneDirectory()

    return phoneDirectory()
