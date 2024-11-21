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

    PageCognition.draw_SoM("UIAnalyzer_logs/1.png")
    PageCognition.grid("UIAnalyzer_logs/1.png")

