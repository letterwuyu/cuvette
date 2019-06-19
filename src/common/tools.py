def write_string(filename, string):
    with open(filename, "w") as f:
        f.write(string+'\n')
