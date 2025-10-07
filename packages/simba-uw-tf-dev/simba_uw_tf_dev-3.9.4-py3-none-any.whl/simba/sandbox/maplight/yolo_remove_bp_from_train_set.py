from simba.utils.read_write import recursive_file_search



def yolo_remove_bp_from_train_set(in_dir: str):

    file_paths = recursive_file_search(directory=in_dir, extensions=['txt'])
    for file_path in file_paths:
        results = ''
        with open(file_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            line_data = line.split()[:-3]
            results += " ".join(line_data)
            results += '\n'

        with open(file_path, "w") as f:
            f.write(results)


yolo_remove_bp_from_train_set(in_dir=r'E:\yolo_resident_intruder')