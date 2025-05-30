import os


def file_fixtures(file):
    if "code" in os.listdir(os.getcwd()):
        file_path = os.path.join("code", "tests/fixtures", file)
    else:
        file_path = os.path.join("tests/fixtures", file)
    return file_path
