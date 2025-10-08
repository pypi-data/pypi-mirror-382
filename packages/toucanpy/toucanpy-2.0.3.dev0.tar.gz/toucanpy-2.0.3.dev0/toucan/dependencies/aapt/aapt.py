#!/usr/bin/env python3

"""
File: /aapt.py
Project: aapt
Description:
Created By: Tao.Hu 2019-07-08
-----
Last Modified: 2019-07-08 02:01:41 pm
Modified By: Tao.Hu
-----
"""

import io
import os
import pathlib
import platform
import re
import stat
import subprocess


def current_folder():
    return pathlib.Path(__file__).parent.resolve()


def aapt(args='--help'):
    try:
        # Darwin: macOS Linux Windows
        system_name = platform.system()
        if system_name != 'Darwin' and system_name != 'Linux' and system_name != 'Windows':
            raise TypeError('unknown system type, only support Darwin、Linux、Windows')

        aapt_path = os.path.join(current_folder(), 'bin', system_name, 'aapt_64')
        if system_name == 'Windows':
            aapt_path += '.exe'

        if system_name != 'Windows' and os.access(aapt_path, os.X_OK) is not True:
            os.chmod(aapt_path, stat.S_IRWXU)

        out = subprocess.getoutput(f'{aapt_path} {args}')  # noqa: S605
        return out
    except Exception as e:
        print('aapt error:', e)
        raise e


def ls(file_path):
    return aapt('l ' + file_path)


def dump(file_path, values):
    return aapt('d ' + values + ' ' + file_path)


def packagecmd(file_path, command):
    return aapt('p ' + command + ' ' + file_path)


def remove(file_path, files):
    return aapt('r ' + file_path + ' ' + files)


def add(file_path, files):
    return aapt('a ' + file_path + ' ' + files)


def crunch(resource, output_folder):
    return aapt('c -S ' + resource + ' -C ' + output_folder)


def single_crunch(input_file, output_file):
    return aapt('s -i ' + input_file + ' -o ' + output_file)


def version():
    return aapt('v')


def get_apk_info(file_path):
    try:
        stdout = dump(file_path, 'badging')
        match = re.compile("package: name='(\\S+)' versionCode='(\\d+)' versionName='(\\S+)'").match(stdout)
        if not match:
            raise Exception("can't get packageinfo:\n " + stdout)
        package_name = match.group(1)
        version_code = match.group(2)
        version_name = match.group(3)
        match = re.compile("application: label='([\u4e00-\u9fa5_a-zA-Z0-9-\\S]+)'").search(stdout)
        app_name = match.group(1)
        match = re.compile("application: label='([\u4e00-\u9fa5_a-zA-Z0-9-\\S]+)' icon='(\\S+)'").search(stdout)
        icon_path = (match and match.group(2)) or None
        return {
            'package_name': package_name,
            'version_code': version_code,
            'version_name': version_name,
            'app_name': app_name,
            'icon_path': icon_path,
        }
    except Exception as e:
        raise e


def get_apk_and_icon(file_path):
    try:
        apk_info = get_apk_info(file_path)
        if apk_info['icon_path']:
            out = subprocess.check_output('unzip' + ' -p ' + file_path + ' ' + apk_info['icon_path'], shell=True)  # noqa: S602
            byte_stream = io.BytesIO(out)
            apk_info['icon_byte_value'] = byte_stream.getvalue()
            byte_stream.close()
        else:
            apk_info['icon_byte_value'] = None
        return apk_info
    except Exception as e:
        raise e
