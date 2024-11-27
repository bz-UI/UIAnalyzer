import os

from UIAnalyzer.PageCognition import PageCognition
from UIAnalyzer.XML import XML
from anytree import RenderTree


if __name__ == "__main__":
    # xml = XML("UIAnalyzer_logs/with_layer.xml")
    # nodes = xml.group_interactive_nodes()
    # for node in nodes:
    #     print(node)
    #
    # tree = RenderTree(xml.build_tree(xml.root))
    # for pre, _, node in tree:
    #     print(f"{pre},{node.xml_node.attrib}")

    for root, _, files in os.walk("UIAnalyzer_logs"):
        for file in files:
            if file.endswith(".png"):
                PageCognition.draw_SoM(os.path.join(root, file), enable_ocr=True)
