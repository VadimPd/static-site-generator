import unittest
from converters import *
from main import *

class ConverterTest(unittest.TestCase):
    def test_text_to_html(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

        node2 = TextNode("This is a text node", TextType.BOLD)
        html_node = text_node_to_html_node(node2)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

        node3 = TextNode("Click me!", TextType.LINK, "https://www.google.com")
        html_node = text_node_to_html_node(node3)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click me!")
        self.assertEqual(html_node.props,{''"href": "https://www.google.com"''})

        node4 = TextNode("An image", TextType.IMAGE, "image.png")
        html_node = text_node_to_html_node(node4)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "image.png", "alt": "An image"})

    def test_split_nodes_delimiter(self):
        node = TextNode("This is a text node with the **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("This is a text node with the ", TextType.TEXT), TextNode("bold", TextType.BOLD), TextNode(" word", TextType.TEXT)])

        node2 = TextNode("This is a text node with the _italic_ word", TextType.TEXT)
        new_nodes2 = split_nodes_delimiter([node2], "_", TextType.ITALIC)
        self.assertEqual(new_nodes2, [TextNode("This is a text node with the ", TextType.TEXT), TextNode("italic", TextType.ITALIC), TextNode(" word", TextType.TEXT)])

        node3 = TextNode("This is a text node with the `code` word", TextType.TEXT)
        new_nodes3 = split_nodes_delimiter([node3], "`", TextType.CODE)
        self.assertEqual(new_nodes3, [TextNode("This is a text node with the ", TextType.TEXT), TextNode("code", TextType.CODE), TextNode(" word", TextType.TEXT)])

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    def test_extract_markdown_links(self):
        matches = extract_markdown_links("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)")
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_nodes_link_no_links(self):
        node = TextNode("Just plain text, no links here.", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(new_nodes, [node])

    def test_split_nodes_image_no_images(self):
        node = TextNode("Just plain text, no images here.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertEqual(new_nodes, [node])

    def test_text_to_textnodes(self):
        text = text_to_text_nodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        self.assertEqual(text, [
        TextNode("This is ", TextType.TEXT),
        TextNode("text", TextType.BOLD),
        TextNode(" with an ", TextType.TEXT),
        TextNode("italic", TextType.ITALIC),
        TextNode(" word and a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" and an ", TextType.TEXT),
        TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        TextNode(" and a ", TextType.TEXT),
        TextNode("link", TextType.LINK, "https://boot.dev"),
        ])

    def test_markdown_to_blocks(self):
            md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
            blocks = markdown_to_blocks(md)
            self.assertEqual(
                blocks,
                [
"This is **bolded** paragraph",
"This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
"- This is a list\n- with items",
                ],
            )

    def test_block_to_block(self):
        block = "2. Awooga\n4. Bazooga"
        self.assertEqual(block_to_block(block), BlockType.PARAGRAPH)
        block2 = "> Bigger isn't always better\n> Said I. Newton"
        self.assertEqual(block_to_block(block2), BlockType.QUOTE)
        block3 = "# I remember eating a banana"
        self.assertEqual(block_to_block(block3), BlockType.HEADING)
        block4 = "####### I do NOT remember eating a banana"
        self.assertEqual(block_to_block(block4), BlockType.PARAGRAPH)
        block5 = "```\ndef your_mother(fat)```"
        self.assertEqual(block_to_block(block5), BlockType.CODE)
        block6 = "- wake up\n- pee\n- get out of bed"
        self.assertEqual(block_to_block(block6), BlockType.UNORDERED_LIST)
        block7 = "1. wake up\n2. pee\n3. get out of bed"
        self.assertEqual(block_to_block(block7), BlockType.ORDERED_LIST)
        block8 = "Today I went for a lovely walk"
        self.assertEqual(block_to_block(block8), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_nodes(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_nodes(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")
        self.assertEqual(extract_title("# Hello\nSome paragraph text"), "Hello")
        with self.assertRaises(Exception):
            extract_title("## Not H1")
        with self.assertRaises(Exception):
            extract_title("### Also Not H1")
        with self.assertRaises(Exception):
            extract_title("Just some text\nAnother line")
        self.assertEqual(extract_title("Intro text\n# My Title\nMore text"), "My Title")
        with self.assertRaises(Exception):
            extract_title("#")
        with self.assertRaises(Exception):
            extract_title("#Title")
