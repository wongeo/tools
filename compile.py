# coding=UTF-8
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib


class Compiler:

    def __init__(self, content, compile, group, name, version, type):
        self.str = content
        self.compile = compile
        self.group = group
        self.name = name
        self.version = version
        self.type = type

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
            elif content.__contains__("- com"):
                content = content.replace(" ", "")
                res = re.search("-(.*)\.(.*?)\.version=(.*)", content)
                group = res.group(1).strip()
                name = res.group(2).strip()
                version = res.group(3).strip()
                compiler = Compiler(content, None, group, name, version, None)
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


def get_base(base_path):
    base_compilers = []
    bases = open(base_path, "r")
    for line in bases.readlines():
        if line.__contains__("- com"):
            compiler = Compiler.create(line)
            if compiler is not None:
                base_compilers.append(compiler)
    return base_compilers


def get_base2(base_path):
    base_versions = {}
    j = json.load(open(base_path, "r"))
    for i in j['mainDex']:
        group, name, type, version = i.split(':')
        base_versions[group + name] = version
    return base_versions


def replace(base_path, input_path):
    print "基础依赖：" + base_path

    base_versions = get_base2(base_path)
    file = open(input_path, "r")
    total = 0
    ucount = 0
    lines = file.readlines()

    writer = open(input_path, "w")

    for line in lines:
        compiler = Compiler.create(line)
        if compiler is not None:
            total += 1
            version = get_version2(base_versions, compiler.name, compiler.group)
            if version is not None:
                ucount += 1
                spaces = ""
                for space in range(compiler.start_index):
                    spaces += " "
                nline = spaces + compiler.compile + "('" + compiler.group + ":" + compiler.name + ":" + version + "@" + compiler.type + "')"
                out(writer, nline)
            else:
                line = line.replace("\n", "")
                line += "//未更新版本"
                out(writer, line)
        else:
            out(writer, line)


def out(file, count):
    if "\n" in count:
        print (count),
        file.write(count)
    else:
        file.write(count + "\n")


def download(url, path):
    if os.path.exists(path):
        print "文件存在，跳过下载"
        return
    print "开始下载:" + url

    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)

    urllib.urlretrieve(url, tmp)
    os.rename(tmp, path)
    print "下载完成"


if __name__ == "__main__":
    uri = sys.argv[1]
    deps = sys.argv[2]

    base_path = "base_versions.des"
    download(uri, base_path)

    dir = tempfile.gettempdir()
    replace(base_path, deps)

    if os.path.exists(base_path):
        os.remove(base_path)
