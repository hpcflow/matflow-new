from damask_parse.readers import read_spectral_stdout


def read_log(damask_stdout_file):
    try:
        return read_spectral_stdout(path=damask_stdout_file, encoding="utf8")
    except UnicodeDecodeError:
        # Docker on Windows...
        return read_spectral_stdout(path=damask_stdout_file, encoding="utf16")
