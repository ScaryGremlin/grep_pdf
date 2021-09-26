from argparse import ArgumentParser
from subprocess import run, PIPE

from PyPDF2 import PdfFileReader, PdfFileWriter


def get_cmdargs() -> dict:
    """
    Получить аргументы командной строки
    :return: Словарь аргументов командной строки
    """
    arg_parser = ArgumentParser(description="grep pdf-file")
    arg_parser.add_argument("-s", dest="source_path", help="файл-источник", required=True)
    arg_parser.add_argument("-d", dest="dest_path", help="файл-назначение", required=True)
    arg_parser.add_argument("-f", dest="fios_path", help="файл с фамилиями", required=True)
    args = arg_parser.parse_args()
    return {
        "source_path": args.source_path,
        "dest_path": args.dest_path,
        "fios_path": args.fios_path
    }


def get_fios_from_file(file_name: str) -> list:
    """
    Получить список фамилий из txt-файла.
    Каждую строку в файле разбить на список по разделителю - пробел.
    Взять последние три элемента списка, которые есть фамилия, имя и отчество.
    :param file_name: Имя файла
    :return: Список ФИО
    """
    fios = []
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            element = line.strip().strip(";").split()
            fios.append(f"{element[-3].strip()} {element[-2].strip()} {element[-1].strip()}")
    return fios


def main():
    # Получить аргументы командной строки
    cmd_args = get_cmdargs()

    input_pdf = PdfFileReader(cmd_args.get("source_path"))
    pdf_writer = PdfFileWriter()

    # Пройтись по списку фамилий
    for fio in get_fios_from_file(cmd_args.get("fios_path")):
        print(f"Поиск по ФИО: [{fio}]...")

        # Выполнить команду pdfgrep - поиск выражения в pdf-файле
        result = run(["pdfgrep", f"Я, {fio}", cmd_args.get("source_path"), "--page-number"],
                     stdout=PIPE,
                     encoding="utf-8")

        # Получить спискок страниц, на которых найдена фамилия
        pages = [element.partition(":")[0] for element in result.stdout.strip().split("\n")]

        # Если страницы найдены...
        if pages[0]:
            print(f"Найденные страницы: {pages}")
            for element in pages:
                page_number = int(element) - 1
                first_page = input_pdf.getPage(page_number)
                second_page = input_pdf.getPage(page_number + 1)
                pdf_writer.addPage(first_page)
                pdf_writer.addPage(second_page)
        else:
            print(f"По ФИО [{fio}] договоров не нашлось.")
        print("---")

    # Сгенерировать файл с результатами поиска
    with open(cmd_args.get("dest_path"), "wb") as output_file:
        pdf_writer.write(output_file)


if __name__ == "__main__":
    main()
