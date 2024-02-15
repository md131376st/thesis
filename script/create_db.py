from indexing.packageCollector import ClassPackageCollector

sourceCodePath = "C:\\Users\\mona1\\Downloads\\core-r-metaconto-v1"

if __name__ == '__main__':
    prefix = "com.intesasanpaolo.bear.sxdr0.metaconto"
    collector = ClassPackageCollector(sourceCodePath)
    collector.collect_package_info(prefix)
    collected_data = collector.get_collected_data()
