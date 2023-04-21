import os
import logging
import sys
from os.path import isfile, join
import hashlib
import argparse
import re

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, help='An optional integer argument')


def delete_duplicates_by_md5(directory):
    files = sorted([f for f in os.listdir(directory) if isfile(join(directory, f))])
    md5_by_files = {}
    for file in files:
        md5 = hashlib.md5(open(os.path.join(directory, file), 'rb').read()).hexdigest()
        if md5 not in md5_by_files:
            md5_by_files[md5] = [file]
        else:
            md5_by_files[md5].append(file)

    duplicated_files = []
    for md5 in md5_by_files:
        for i in range(0, len(md5_by_files[md5]) - 1):
            duplicated_files.append(md5_by_files[md5][i])

    for duplicated_file in duplicated_files:
        os.remove(os.path.join(directory, duplicated_file))
        logger.info(f"deleted (md5): {os.path.join(directory, duplicated_file)}")


def delete_duplicates_by_name_and_size(directory):
    files = sorted([f for f in os.listdir(directory) if isfile(join(directory, f))])
    files_that_seems_to_be_duplicated = {}
    re_exp = r'\ \(\d+\)'
    for file in files:
        if re.search(re_exp, file):
            original_name = re.sub(re_exp, '', file)

            if original_name not in files_that_seems_to_be_duplicated:
                files_that_seems_to_be_duplicated[original_name] = [file]
            else:
                files_that_seems_to_be_duplicated[original_name].append(file)

    for file_that_seems_to_be_duplicated in files_that_seems_to_be_duplicated:
        maybe_same_files = files_that_seems_to_be_duplicated[file_that_seems_to_be_duplicated]
        for maybe_same_file in maybe_same_files:

            if not os.path.isfile(os.path.join(directory, file_that_seems_to_be_duplicated)):
                os.rename(
                    os.path.join(directory, maybe_same_file),
                    os.path.join(directory, file_that_seems_to_be_duplicated)
                )
                logger.info(f"renamed: {file_that_seems_to_be_duplicated}")
            else:
                size_01 = os.path.getsize(os.path.join(directory, maybe_same_file))
                size_02 = os.path.getsize(os.path.join(directory, file_that_seems_to_be_duplicated))

                if size_01 == size_02:
                    to_delete = os.path.join(directory, maybe_same_file)
                    os.remove(to_delete)
                    logger.info(f"deleted (name and size): {to_delete}")


if __name__ == '__main__':
    args = parser.parse_args()
    selected_dir = os.getcwd() if not args.dir else args.dir
    logger.info(f"dir: {selected_dir}")

    delete_duplicates_by_md5(selected_dir)
    delete_duplicates_by_name_and_size(selected_dir)
    logger.info(f"done.")