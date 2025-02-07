import os
import shutil

def sanitize_logs(logs):
    log_str = '\n'.join(logs)
    log_str = str.replace(log_str, '\x00', '\n')
    logs = log_str.split('\n')
    logs_out = []
    for line in logs:
        if len(line) > 5:
            logs_out.append(('    ' + line) if line[0].isascii() else line[2:] + '\n')
    del logs
    return logs_out

def main():
    with open('expdb', 'r', encoding='ISO-8859-1') as f:
        lines = f.readlines()

    dumps = []
    # Initialize dump with both keys to avoid KeyError
    dump = {'pl_lk': [], 'linux': []}
    reading_pllk = False
    reading_linux = False

    for line in lines:
        if "Preloader Start=" in line:
            reading_pllk = True
            reading_linux = False
            # If dump already contains data, save it before resetting
            if dump['pl_lk'] or dump['linux']:
                dumps.append(dump)
            dump = {'pl_lk': [], 'linux': []}
        elif "[LK]jump to K64" in line:
            reading_pllk = False
            reading_linux = True

        if reading_pllk:
            dump['pl_lk'].append(line)
        if reading_linux:
            dump['linux'].append(line)

    # Append the final dump if it contains data
    if dump['pl_lk'] or dump['linux']:
        dumps.append(dump)

    if os.path.isdir('out'):
        shutil.rmtree('out')
    os.mkdir('out')

    for i, d in enumerate(dumps):
        ddir = os.path.join('out', str(i + 1))
        os.mkdir(ddir)
        with open(os.path.join(ddir, 'pl_lk'), 'w', encoding='ISO-8859-1') as f:
            f.writelines(d['pl_lk'])
        with open(os.path.join(ddir, 'linux'), 'w', encoding='ISO-8859-1') as f:
            f.writelines(sanitize_logs(d['linux']))

if __name__ == '__main__':
    main()
