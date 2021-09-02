import os
import datetime
import sys

def walklevel(some_dir, level=3):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def find_cont_subdir(parent_directory, child_string, days_back = 72):
    '''
    Looks in parent directory for recently modified subdirectories which contain child_string
    '''

    cont_subdirs = []
    for dirname,subdirs,files in os.walk(parent_directory):
        for subdir in subdirs:

        # Get last modified date and today's date
            real_subdir = os.path.join(dirname, subdir)
            modifyDate = datetime.datetime.fromtimestamp(os.path.getmtime(real_subdir))
            todaysDate = datetime.datetime.today()
            modifyDateLimit = modifyDate + datetime.timedelta(days=days_back)

        # If the file was modified within days_back days then we append it
            if modifyDateLimit > todaysDate:
                if child_string in subdir:
                    cont_subdirs.append(real_subdir)
    return cont_subdirs

if __name__ == "__main__":
    par_dir = sys.argv[1]
    child_string = sys.argv[2]
    print(find_cont_subdir(par_dir, str(child_string), 3000))
