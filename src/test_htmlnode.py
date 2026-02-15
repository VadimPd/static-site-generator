import unittest
from htmlnode import *

class HTMLNodeTest(unittest.TestCase):
    def test_html_node(self):
        node = HTMLNode(props=None)
        assert node.props_to_html() == ""
        node2 = HTMLNode(props={})
        assert node2.props_to_html() == ""
        node3 = HTMLNode(props={"href": "http://example.com"})
        expected = ' href="http://example.com"'
        actual = node3.props_to_html()
        assert actual == expected, f"{actual!r} != {expected!r}"
        node4 = HTMLNode(props={"href": "http://example.com", "target": "_blank"})
        assert node4.props_to_html() == ' href="http://example.com" target="_blank"'

    def test_leaf_node(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        node2 = LeafNode("a", "Hello, world!")
        self.assertEqual(node2.to_html(), "<a>Hello, world!</a>")
        node3 = LeafNode("a", "Click me!", props={''"href": "https://www.google.com"''})
        self.assertEqual(node3.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    def test_to_html_with_no_children(self):
        parent_node = LeafNode("p", "parent")
        self.assertEqual(parent_node.to_html(), "<p>parent</p>")

    def test_to_html_with_grandgrandchildren(self):
        grandgrandchild_node = LeafNode("b", "grandgrandchild_node")
        grandchild_node = ParentNode("span", [grandgrandchild_node])
        child_node = ParentNode("div", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(), "<div><div><span><b>grandgrandchild_node</b></span></div></div>",
        )
