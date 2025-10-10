

class Node:
    def __init__(self, parent, childs, content, spaces):
        self.parent:Node = parent
        self.childs:list[Node] = childs
        self.content:str = content
        self.spaces:int = spaces

    def show_tree(self, prefix: str = "", is_last: bool = True):
        connector = "└── " if is_last else "├── "
        if self.parent is None:
            # 根节点直接打印
            print(self.content)
            child_prefix = ""  # 注意这里，不要加空格
        else:
            print(prefix + connector + self.content)
            child_prefix = prefix + ("    " if is_last else "│   ")

        # 遍历孩子
        for i, child in enumerate(self.childs):
            last_child = (i == len(self.childs) - 1)
            child.show_tree(child_prefix, last_child)
def get_name(string):
    if ':' in string:
        return string.split(':')[0].strip()
    return None

def get_parent_node(node: Node, spaces: int):
    if node.spaces == spaces:
        return node.parent
    return get_parent_node(node.parent, spaces)


def b_model_tree(model):
    split_string_lst = str(model).split('\n')
    root = Node(None, [], split_string_lst[0][:-1], 0)

    split_string_lst = split_string_lst[1:-1]
    count_space_lst = [len(line) - len(line.lstrip()) for line in split_string_lst]

    point = root
    for idx, spaces in enumerate(count_space_lst):
        if name := get_name(split_string_lst[idx]):
            if spaces>point.spaces:
                new_node = Node(point, [], name, spaces)
                point.childs.append(new_node)
                point = new_node
            elif spaces<=point.spaces:
                point = get_parent_node(point, spaces)
                new_node = Node(point, [], name, spaces)
                point.childs.append(new_node)
                point = new_node
    root.show_tree()

if __name__ == '__main__':
    string = \
    """SpikingResNet(
      (conv1): Conv2d(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False, step_mode=s)
      (bn1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
      (sn1): IFNode(
        v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
        (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
      )
      (maxpool): MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False, step_mode=s)
      (layer1): Sequential(
        (0): BasicBlock(
          (conv1): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (1): BasicBlock(
          (conv1): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (2): BasicBlock(
          (conv1): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
      )
      (layer2): Sequential(
        (0): BasicBlock(
          (conv1): Conv2d(64, 128, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (downsample): Sequential(
            (0): Conv2d(64, 128, kernel_size=(1, 1), stride=(2, 2), bias=False, step_mode=s)
            (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          )
        )
        (1): BasicBlock(
          (conv1): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (2): BasicBlock(
          (conv1): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (3): BasicBlock(
          (conv1): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
      )
      (layer3): Sequential(
        (0): BasicBlock(
          (conv1): Conv2d(128, 256, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (downsample): Sequential(
            (0): Conv2d(128, 256, kernel_size=(1, 1), stride=(2, 2), bias=False, step_mode=s)
            (1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          )
        )
        (1): BasicBlock(
          (conv1): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (2): BasicBlock(
          (conv1): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (3): BasicBlock(
          (conv1): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (4): BasicBlock(
          (conv1): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (5): BasicBlock(
          (conv1): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(256, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
      )
      (layer4): Sequential(
        (0): BasicBlock(
          (conv1): Conv2d(256, 512, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (downsample): Sequential(
            (0): Conv2d(256, 512, kernel_size=(1, 1), stride=(2, 2), bias=False, step_mode=s)
            (1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          )
        )
        (1): BasicBlock(
          (conv1): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
        (2): BasicBlock(
          (conv1): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn1): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn1): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
          (conv2): Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1), bias=False, step_mode=s)
          (bn2): BatchNorm2d(512, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True, step_mode=s)
          (sn2): IFNode(
            v_threshold=1.0, v_reset=0.0, detach_reset=False, step_mode=s, backend=torch
            (surrogate_function): Sigmoid(alpha=4.0, spiking=True)
          )
        )
      )
      (avgpool): AdaptiveAvgPool2d(output_size=(1, 1), step_mode=s)
      (fc): Linear(in_features=512, out_features=1000, bias=True)
    )"""
    b_model_tree(string)