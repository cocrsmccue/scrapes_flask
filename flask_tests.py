import re

def find_and_modify_six_char_routes(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return [], []

    route_pattern = re.compile(r"@app\.route\('/(\w{6})/")

    six_char_routes = []
    modified_routes = []
    co_count = 0
    tx_count = 0
    
    for line in lines:
        match = route_pattern.search(line)
        if match:
            route_segment = match.group(1)
            six_char_routes.append(route_segment)
            modified_segment = route_segment[:3].upper() + route_segment[3:]
            modified_routes.append(modified_segment)
            print(f"Modified route: {modified_segment}")
            
            if route_segment.startswith('co'):
                co_count += 1
            elif route_segment.startswith('tx'):
                tx_count += 1
    
    total_count = len(six_char_routes)
    print(f"Total routes found: {total_count}")
    print(f"CO = {co_count}")
    print(f"TX = {tx_count}")

    return six_char_routes, modified_routes

# Example usage
# original_routes, modified_routes = find_and_modify_six_char_routes('path_to_your_file.txt')


if __name__ == '__main__':
    app_py_path = 'app.py'
    find_and_modify_six_char_routes(app_py_path)
# Example usage
# find_and_modify_six_char_routes('path_to_your_file.txt')
