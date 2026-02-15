import re
from textnode import *
from htmlnode import *
from blocktype import *


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

def split_nodes_delimiter(old_nodes, delimiter, text_type):
        new_nodes = []
        for node in old_nodes:
            if node.text_type != TextType.TEXT:
                new_nodes.append(node)
                continue

            if delimiter not in node.text:
                new_nodes.append(node)
                continue

            if delimiter in node.text:
                if node.text.count(delimiter) % 2 != 0:
                    raise Exception("Invalid delimiter")
                parts = node.text.split(delimiter)
                for i, part in enumerate(parts):
                    if part == "":
                        continue
                    if i % 2 == 0:
                        new_nodes.append(TextNode(part, TextType.TEXT))  # outside delimiters
                    else:
                        new_nodes.append(TextNode(part, text_type))

        return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def find_image_position(text):
    start_end_indexes = []
    matches = re.finditer(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    for match in matches:
        start_index = match.start()
        end_index = match.end()
        start_end_indexes.append((start_index, end_index))
    return start_end_indexes

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def find_link_position(text):
    start_end_indexes = []
    matches = re.finditer(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    for match in matches:
        start_index = match.start()
        end_index = match.end()
        start_end_indexes.append((start_index, end_index))
    return start_end_indexes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        cursor = 0
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        for start, end in find_link_position(node.text):
            link_url_substring = extract_markdown_links(node.text[start:end])
            link_text, link_url = link_url_substring[0]
            if node.text[cursor:start] != "":
                new_nodes.append(TextNode(node.text[cursor:start], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            cursor = end
        if node.text[cursor:] != "":
            new_nodes.append(TextNode(node.text[cursor:], TextType.TEXT))
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        cursor = 0
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        for start, end in find_image_position(node.text):
            image_url_substring = extract_markdown_images(node.text[start:end])
            image_text, image_url = image_url_substring[0]
            if node.text[cursor:start] != "":
                new_nodes.append(TextNode(node.text[cursor:start], TextType.TEXT))
            new_nodes.append(TextNode(image_text, TextType.IMAGE, image_url))
            cursor = end
        if node.text[cursor:] != "":
            new_nodes.append(TextNode(node.text[cursor:], TextType.TEXT))
    return new_nodes

def text_to_text_nodes(text):
    text_list = [TextNode(text, TextType.TEXT)]
    result_list = split_nodes_delimiter(text_list, "**", TextType.BOLD)
    result_list = split_nodes_delimiter(result_list, "_", TextType.ITALIC)
    result_list = split_nodes_delimiter(result_list, "`", TextType.CODE)
    result_list = split_nodes_link(result_list)
    result_list = split_nodes_image(result_list)
    return result_list

def markdown_to_blocks(markdown):
    split_list = markdown.split("\n")
    blocks = []
    current = []
    for sentence in split_list:
        if sentence.strip() == "":
            if current != []:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(sentence.strip())
    if current != []:
        blocks.append("\n".join(current))
    return blocks

def block_to_block(block):
    lines = block.splitlines()
    line = lines[0]
    hash_count = len(line) - len(line.lstrip("#"))
    quote_count = 0
    dash_count = 0
    ordered_list_count = 1
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if 1 <= hash_count <= 6 and len(line) > hash_count and line[hash_count] == " ":
        return BlockType.HEADING
    for ln in lines:
        if ln.startswith(">"):
            quote_count += 1
        if ln.startswith("- "):
            dash_count += 1
        if ln.startswith(f"{ordered_list_count}. "):
            ordered_list_count += 1
    if quote_count == len(lines):
        return BlockType.QUOTE
    if dash_count == len(lines):
        return BlockType.UNORDERED_LIST
    if ordered_list_count == len(lines)+1:
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def text_to_children(text):
    textnodes = text_to_text_nodes(text)
    return [text_node_to_html_node(n) for n in textnodes]

def block_to_html(block, block_type):
    lines = block.splitlines()
    line = lines[0]
    hash_count = len(line) - len(line.lstrip("#"))
    if block_type != BlockType.CODE:
        textnodes = text_to_text_nodes(block)
        htmlnodes = [text_node_to_html_node(n) for n in textnodes]

    if block_type == BlockType.PARAGRAPH:
        text = " ".join(block.splitlines())
        children = text_to_children(text)
        return ParentNode(tag="p", children=children)
    elif block_type == BlockType.CODE:
        raw_text = "\n".join(lines[1:-1]) + "\n"
        code_leaf = LeafNode(None, raw_text)
        code_node = ParentNode(tag="code", children=[code_leaf])
        return ParentNode(tag="pre", children=[code_node])
    elif block_type == BlockType.QUOTE:
        cleaned_lines = []
        for line in lines:
            line = line[1:]
            if line.startswith(" "):
                line = line[1:]
            cleaned_lines.append(line)
        quote_text = "\n".join(cleaned_lines).strip()
        children = text_to_children(quote_text)
        return ParentNode("blockquote", children)
    elif block_type == BlockType.UNORDERED_LIST:
        li_nodes = []
        for line in lines:
            item_text = line[2:]
            children = text_to_children(item_text)
            li_nodes.append(ParentNode(tag="li", children=children))
        return ParentNode(tag="ul", children=li_nodes)
    elif block_type == BlockType.ORDERED_LIST:
        li_nodes = []
        for line in lines:
            item_text = line.split(". ", 1)[1]
            children = text_to_children(item_text)
            li_nodes.append(ParentNode(tag="li", children=children))
        return ParentNode(tag="ol", children=li_nodes)
    elif block_type == BlockType.HEADING:
        content = line[hash_count + 1:]
        children = text_to_children(content)
        return ParentNode(tag=f"h{hash_count}", children=children)




def markdown_to_html_nodes(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block(block)
        children.append(block_to_html(block, block_type))
    return ParentNode(tag="div", children=children)




