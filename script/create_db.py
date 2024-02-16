from indexing.packageCollector import ClassPackageCollector
import pickle

sourceCodePath = "C:\\Users\\mona1\\Downloads\\core-r-metaconto-v1"


def save_instance(fileName, instances):
    with open(fileName, 'wb') as file:  # Use 'rb' to read in binary mode
        pickle.dump(instances, file)


def get_instance(fileName):
    with open(fileName, 'rb') as file:  # Use 'rb' to read in binary mode
        return pickle.load(file)


def parse_package(prefix):
    collector = ClassPackageCollector(sourceCodePath)
    collector.collect_package_info(prefix)
    collected_data = collector.get_collected_data()
    return collected_data


def create_db(prefix, save=False):
    # parser files
    data = parse_package(prefix)
    # save ParserInfo
    if save:
        save_instance("temp.pkl", data)


if __name__ == '__main__':
    # prefix = "com.intesasanpaolo.bear.sxdr0.metaconto"
    # collector = ClassPackageCollector(sourceCodePath)
    # collector.collect_package_info(prefix)
    # collected_data = collector.get_collected_data()
    collected_data = get_instance("hi.pkl")
    for package in collected_data:
        for classinfo in package.classes:
            classinfo.generate_class_index()

    save_instance("temp.pkl" ,collected_data)


