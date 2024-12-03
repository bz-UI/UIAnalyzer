import os
import subprocess
import time
import xml.dom.minidom


def execute_adb(adb_command):
    # print(adb_command)
    result = subprocess.run(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(1)
    if result.returncode == 0:
        return result.stdout.strip()
    print(f"Command execution failed: {adb_command}")
    print(result.stderr, "red")
    return "ERROR"


def get_device():
    adb_command = "adb devices"
    result = execute_adb(adb_command)
    if result != "ERROR":
        devices = result.split("\n")[1:]
        # 只返回第一个设备名
        for device in devices:
            if device.endswith("device"):
                device_name = device.split("\t")[0]
                return device_name
    raise Exception("No device found")

def format_xml(xml_file):
    try:
        dom = xml.dom.minidom.parse(xml_file)
        pretty_xml_as_string = dom.toprettyxml(indent="  ")
        with open(xml_file, 'w') as f:
            f.write(pretty_xml_as_string)
        print(f"XML formatted and saved to {xml_file}")
    except Exception as e:
        print(f"Error formatting XML: {e}")


def get_next_screenshot_name(dir_path):
    # 返回下一个数字标号
    max_number = -1
    # 遍历目录下的所有文件
    for filename in os.listdir(dir_path):
        # 检查文件名是否符合纯数字命名的规则
        number_str = filename.split('.')[0]
        number = int(number_str)
        max_number = max(max_number, number)  # 更新找到的最大数字
    return max_number + 1 if max_number != -1 else 0


def get_screenshot_and_xml(dir_path='.', filename='0'):
    device = get_device()
    filename = str(get_next_screenshot_name(dir_path))
    # xml
    mobile_xml_path = "/sdcard/temp.xml"
    mac_xml_path = os.path.join(dir_path, f"{filename}.xml")
    dump_command = f"adb -s {device} shell uiautomator dump {mobile_xml_path}"
    pull_command = f"adb -s {device} pull {mobile_xml_path} {mac_xml_path}"
    execute_adb(dump_command)
    execute_adb(pull_command)
    format_xml(mac_xml_path)

    # screenshot
    mobile_screenshot_path = "/sdcard/temp.png"
    mac_screenshot_path = f"{dir_path}/{filename}.png"
    capture_command = f"adb -s {device} shell screencap -p {mobile_screenshot_path}"
    pull_command = f"adb -s {device} pull {mobile_screenshot_path} {mac_screenshot_path}"
    execute_adb(capture_command)
    execute_adb(pull_command)

