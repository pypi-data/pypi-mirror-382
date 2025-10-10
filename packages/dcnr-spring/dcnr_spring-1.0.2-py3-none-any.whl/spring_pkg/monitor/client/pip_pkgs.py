import subprocess


def _split_pip_show_line(line:str):
    try:
        first = line.index(': ')
        if first > 0:
            return line[:first].lower(), line[first+2:].strip()
    except Exception:
        return None, None

def _group_values(array:list, group_size:int):
    grouped = []
    curr_group = []
    for item in array:
        curr_group.append(item)
        if len(curr_group)>=group_size:
            grouped.append(curr_group)
            curr_group = []
    if len(curr_group)>0:
        grouped.append(curr_group)
    return grouped

def get_pip_packages():
    data = {}
    pkgs_list = []
    pf = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    for line in pf.stdout.split('\n'):
        lparts = line.split('==')
        if len(lparts)==2:
            pkgs_list.append(lparts[0])
    pkgs_grouped = _group_values(pkgs_list, 20)
    for pkg_group in pkgs_grouped:
        pf = subprocess.run(['pip', 'show'] + pkg_group, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf8')
        if isinstance(pf.stdout,str):
            lines = pf.stdout.split('\n')
        else:
            print(type(pf.stdout))
            lines = []
            
        _process_pip_show_output(data, lines)

    return data

def _process_pip_show_output(data, lines):
    curr_pkg = {}
    for line in lines:
        tag, api_value = _split_pip_show_line(line)
        if tag == 'name':
            curr_pkg = { tag: api_value }
            data[api_value] = curr_pkg
        elif tag == 'version':
            curr_pkg[tag] = api_value
        elif tag in ['requires', 'required-by']:
            api_value = [v.strip() for v in api_value.split(',')]
            curr_pkg[tag] = api_value
