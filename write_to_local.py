def write_to_local(filename, revision, content):
    """
    Accepts filename, revision, and content
    Creates a filename called filename_revision.txt
    Writes content to the file
    Closes the file
    """
    f = open(f"{filename}_{revision}.txt", "w")
    f.write(f'{content}')
    f.close()