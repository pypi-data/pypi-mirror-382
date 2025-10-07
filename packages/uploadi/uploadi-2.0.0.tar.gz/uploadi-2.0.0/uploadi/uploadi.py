from argparse import ArgumentParser
import sys
import os

class CustomArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Ошибка: {message}", file=sys.stderr)
        sys.exit(1)

def find_egg_info_folder():
    '''Находим папку с именем ".egg-info"'''
    current_directory = os.getcwd()
    for item in os.listdir(current_directory):
        if os.path.isdir(item) and ".egg-info" in item:
            return item
    return None


def uploadi():
    # Получаем аргументы из командной строки
    parser = CustomArgumentParser(description="Код для загрузки проектов python на PyPI или TestPyPI")
    parser.add_argument('-t', action='store_true', help='Загрузка будет происходить на TestPyPI')
    parser.add_argument('-p', action='store_true', help='Загрузка будет происходить на PyPI')
    args = parser.parse_args()
    
    # Проверяем наличие одного из флагов
    # Если указагы оба флага или ни один
    if (args.t and args.p) or (not args.t and not args.p):
        print('Надо выбрать один флаг. -t или -p')
        return

    # Проверяем, есть ли setup.py
    listdir = os.listdir()
    if 'setup.py' not in listdir:
        print('Отсутствует файл загрузки setup.py')
        return

    # Определяем комманду выгрузки
    command = ''
    if args.t:
        command = 'twine upload --repository-url https://test.pypi.org/legacy/ dist/*'
    else:
        ask = input('Вы уверены, что хотите выгрузить на PyPI? (y/n): ')
        if ask.lower() != 'y':
            print('Выгрузка отменена.')
            return
        command = 'twine upload dist/*'

    # Выполняем выгрузку
    os.system('python setup.py sdist bdist_wheel')
    os.system(command)
    eggInfo = find_egg_info_folder()
    os.system(f'rmdir /s /q build dist {eggInfo}')


if __name__ == "__main__":
    uploadi()
