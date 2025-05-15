import os
class MatchingFile:
    def __init__(self):
        pass
    def write_hpc_files(self):
        for path, directories, files in os.walk("./HPC_output"):
            for file in files:
                if os.path.splitext(file)[1] == '.json':
                    print(os.path.join(path, file))
                    f = open("CompletedFiles.txt", "a")
                    f.write(os.path.join(path, file)+"\n")
                    f.close()

    def match(self):
        completed_sections = []
        with open("CompletedFiles.txt") as file:
            for line in file:
                parts = line.split("/")
                neededStr = parts[2]
                part = neededStr.replace("/","_")
                part = part.split(".")
                #print(part)
                completed_sections.append(part[0])

        all_files = []
        with open("filepaths.txt") as file:
            for line in file:
                #line.split("/")
                #parts[2]+"/"+parts[3]
                all_files.append(line)

        for file in all_files:
            parts = file.split("/")
            neededSection =  parts[2] + "_" + parts[3]
            #print(neededSection," ",completed_sections[0])

            if neededSection in completed_sections:
                pass
            else:
                with open("uncompletedFiles.txt", "a") as uf:
                    uf.write(file)






if __name__ == '__main__':
    mf = MatchingFile().match()