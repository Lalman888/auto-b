from url_filter import extract_domain

def parse_file(file_path):
    search_list = []
    for line in file_path.getvalue().decode('utf-8').splitlines():
        search_dict = {}
        parts = line.split(" ", 1)  # split at the first space
        if len(parts) == 2:
            search_dict["search_url"] = extract_domain(parts[0])
            search_dict["search_keyword"] = parts[1].strip()  # remove the trailing newline
            search_list.append(search_dict)
    return search_list

if __name__ == "__main__":
    search_list = parse_file('search.txt')
    for search in search_list:
        print(search)
