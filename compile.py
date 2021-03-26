# coding=UTF-8
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib


class Compiler:
    other = None

    def __init__(self, content, compile, group, name, version, type):
        self.str = content
        self.compile = compile
        self.group = group
        self.name = name
        self.version = version
        self.type = type

        if "{" in content:
            x = content.split("{", 1)
            if len(x) == 2:
                self.other = "{" + x[1]
        elif "//" in content:
            x = content.split("//", 1)
            if len(x) == 2:
                self.other = "//" + x[1]

        self.start_index = 0
        for index in range(len(content)):
            c = content[index]
            if c is not ' ':
                self.start_index = index
                break

    @staticmethod
    def create(content):
        try:
            if "vmdCompile" in content or "compile" in content or "providedCompile" in content:
                content = content.replace("(", "").replace(")", "")  # 统一清理括号
                content = content.replace("\"", "'")  # 统一单引号标准
                res = re.search("(.*?)'(.*?):(.*?):(.*?)@(.*?)'", content)
                compile = res.group(1).strip()
                group = res.group(2).strip()
                name = res.group(3).strip()
                version = res.group(4).strip()
                type = res.group(5).strip()
                compiler = Compiler(content, compile, group, name, version, type)
                return compiler
        except Exception, e:
            return None


# 基础依赖中获得版本号
def get_version(bases, name, group):
    for item in bases:
        if item.name == name and item.group == group:
            return item.version
    return None


def get_version2(base_versions, name, group):
    version = base_versions.get(group + name)
    return version


def get_base2(base_path):
    base_versions = {}
    j = json.load(open(base_path, "r"))
    for i in j['mainDex']:
        group, name, type, version = i.split(':')
        base_versions[group + name] = version
    return base_versions


def replace(base_path, input_path):
    print "基础依赖：" + base_path

    # 获得基础依赖里面的版本号字典，key是【group + name】
    base_versions = get_base2(base_path)
    file = open(input_path, "r")
    total = 0
    update_count = 0
    lines = file.readlines()

    writer = open(input_path, "w")

    for line in lines:
        compiler = Compiler.create(line)
        if compiler is not None:
            total += 1
            version = get_version2(base_versions, compiler.name, compiler.group)
            if version is not None:
                update_count += 1
                spaces = ""
                for space in range(compiler.start_index):
                    spaces += " "
                newline = spaces + compiler.compile + "('" + compiler.group + ":" + compiler.name + ":" + version + "@" + compiler.type + "')"
                if compiler.other is not None:
                    newline = newline + compiler.other
                out(writer, newline)
            else:
                line = line.replace("\n", "")
                out(writer, line)
        else:
            # 没有匹配成compiler的源文输出
            out(writer, line)
    print "匹配" + str(total) + "条依赖 更新" + str(update_count) + "条依赖"


def out(file, count):
    if "\n" in count:
        file.write(count)
    else:
        file.write(count + "\n")


def download(url, path):
    if os.path.exists(path):
        print "文件存在，跳过下载"
        return
    print "开始下载：" + url

    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)

    urllib.urlretrieve(url, tmp)
    os.rename(tmp, path)
    print "下载完成"


def getpath(url, suffix):
    m2 = hashlib.md5()
    m2.update(url)
    return m2.hexdigest() + suffix


if __name__ == "__main__":
    uri = sys.argv[1]
    deps = sys.argv[2]

    base_path = getpath(uri, ".json")
    download(uri, base_path)

    # 开始遍历替换版本
    replace(base_path, deps)

    if os.path.exists(base_path):
        os.remove(base_path)
