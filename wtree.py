# coding=UTF-8
import sys

FIX_NO_NEXT = "└─"
FIX_HAS_NEXT = "├─"
dict = {}


class Node:

    def __init__(self, father_node, leve, content, line_number):
        self.leve = leve
        self.content = content
        self.line_number = line_number
        self.father_node = father_node
        if father_node is None:
            self.fix = ""
        else:
            self.fix = FIX_NO_NEXT

    def to_string(self):
        fa_fix = self.get_fix()
        return fa_fix + self.content

    def get_fix(self):
        if self.father_node is not None:  # 有父节点的，需要把父节点fix拼接上
            fa_fix = self.father_node.get_fix()
            str = fa_fix.replace("├─", "│ ").replace("└─", "  ")
            return str + self.fix
        else:
            return ""

    @staticmethod
    def create(line, line_number):
        if "*" not in line:
            return None
        leve = get_key_size(line, "*")
        content = line.replace("*", "")
        father_node = None
        try:
            father_node = dict[leve - 1]
        except Exception, e:
            pass
        node = Node(father_node, leve, content, line_number)
        return node


def get_key_size(src, key):
    return (len(src) - len(src.replace(key, ""))) // len(key)


def has_simple_leve(node):
    for item in list:
        if item.line_number > node.line_number and item.leve == node.leve and item.father_node == node.father_node:
            return True
    return False


if __name__ == '__main__':
    input = sys.argv[1]
    lines = open(input, "r")
    list = []

    line_number = 0
    for line in lines.readlines():
        node = Node.create(line, line_number)
        line_number += 1
        if node is not None:
            list.append(node)
            dict[node.leve] = node;

    for index in range(len(list)):
        node = list[index]
        try:
            if has_simple_leve(node):
                node.fix = FIX_HAS_NEXT
        except Exception, e:
            pass
        print (node.to_string()),
