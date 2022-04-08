'''
说明: 通过subprocess 合并ts为mp4文件
mac和linux: cat 1.ts 2.ts > xxx.mp4
windows: copy /b 1.ts+2.ts xxx.mp4
'''
import os
import platform
import subprocess
from typing import List


def merge_in_mac_linux(list, source_path, target_file):
    res = subprocess.run(
        ['cd', source_path, '&&', 'cat', ' '.join(list), '>', target_file])
    return res.returncode


def merge_in_win(list, source_path, target_file):
    print(source_path, '+'.join(list), target_file)
    res = subprocess.run(
        ['cd', source_path, '&&', 'copy', '/b', '+'.join(list), target_file],
        shell=True,
        stdout=subprocess.DEVNULL)
    return res.returncode


def merge_ts(os_name: str,
             content_list: List,
             parent_dir: str,
             source_path: str,
             target_file_name: str,
             target_path: str = '',
             is_long: bool = True):
    '''
    is_long: 如果合并的文件太多,会有长度限制, 所以一般超过800个ts文件[如果用数字命名:1.ts,2.t3,3.ts...],我就会使用这个参数
    '''
    source_path_abs = os.path.join(parent_dir, source_path)
    target_path_abs = os.path.join(parent_dir, target_path)
    if not os.path.isdir(target_path_abs):
        os.makedirs(target_path_abs)
    target_file_abs = os.path.join(target_path_abs, target_file_name)
    res = -1
    bash_file_name = 'ts_sh'
    if os_name == 'windows':
        # 拷贝不同磁盘的时候, 完整路径都要加上
        content_list = [
            f'{os.path.join(source_path_abs,i)}' for i in content_list
        ]
        ts_str = '+'.join(content_list)
        bash_str = f'cd "{source_path_abs}" && copy /b {ts_str} "{target_file_abs}"'
        if is_long:
            bash_file_path = os.path.join(source_path_abs,
                                          f'{bash_file_name}.cmd')
            with open(bash_file_path, mode='w', encoding='utf8') as f:
                f.write(bash_str)
            bash_str = bash_file_path
    elif os_name == 'linux' or os_name == 'darwin':
        ts_str = ' '.join(content_list)
        bash_str = f'cd "{source_path_abs}" && cat {ts_str} > "{target_file_abs}"'
        if is_long:
            bash_file_path = os.path.join(source_path_abs,
                                          f'{bash_file_name}.sh')
            with open(bash_file_path, mode='w', encoding='utf8') as f:
                f.write(bash_str)
            bash_str = f'chmod +x {bash_file_path} && {bash_file_path}'

    try:
        res = subprocess.run(bash_str,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        res_code = res.returncode
        if res_code != 0:
            print(res.stdout.decode("utf8"))
            return -1
        return 0
    except Exception as e:
        print(e)
        return -1


def encoding_to_utf8(os_name):
    if os_name == 'linux' or os_name == 'darwin':
        return
    # 设置编码为utf8, 为了防止windows系统乱码
    subprocess.run(['chcp', '65001'], shell=True, stdout=subprocess.DEVNULL)


def merge():
    content_list = ['1.ts', '2.ts']
    source_path = 'ts'
    targete_path = 'out'
    target_file_name = '1.mp4'
    os_name = platform.system().lower()
    encoding_to_utf8(os_name)
    parent_dir = os.path.dirname(__file__)
    res = merge_ts(os_name, content_list, parent_dir, source_path,
                   target_file_name, targete_path, True)
    if res != 0:
        print('合并失败')
        return
    print(f'合并成功 {target_file_name}')


if __name__ == '__main__':
    merge()
