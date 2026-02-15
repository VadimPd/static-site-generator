import shutil
import sys

from converters import *
from textnode import TextNode
import os

def copy_content(folder_path:str, destination_folder:str):
    if os.path.abspath(folder_path) == os.path.abspath(destination_folder):
        raise ValueError("dumbass the two folders gotta be different")
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
        print(f"Removed folder {destination_folder}")
    os.makedirs(destination_folder)
    print(f"Created folder {destination_folder}")
    for entry in os.listdir(folder_path):
        src_path = os.path.join(folder_path, entry)
        dst_path = os.path.join(destination_folder, entry)
        if os.path.isdir(src_path):
            copy_content(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
        print(f"Copied {src_path} to {dst_path}")
    print(f"Copied {folder_path} to {destination_folder}")

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            line = line[1:]
            return line.strip()
    raise Exception("heading not found", lines)

def generate_page(from_path, template_path, dest_path, basepath):
    print("CWD:", os.getcwd())
    print("ABS dest:", os.path.abspath(dest_path))
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as from_file:
        from_file_content = from_file.read()
    with open(template_path, "r") as template_file:
        template_file_content = template_file.read()
    html_node = markdown_to_html_nodes(from_file_content)
    html_string = html_node.to_html()
    title = extract_title(from_file_content)
    page = template_file_content.replace("{{ Title }}", title).replace("{{ Content }}", html_string)
    page = page.replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as dest_file:
        print("Wrote file OK:", os.path.abspath(dest_path))
        dest_file.write(page)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    os.makedirs(dest_dir_path, exist_ok=True)

    entries = os.listdir(dir_path_content)

    for entry in entries:
        content_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isdir(content_path):
            generate_pages_recursive(content_path, template_path, dest_path, basepath)
            continue

        if not entry.endswith(".md"):
            continue

        with open(content_path, "r") as f:
            markdown = f.read()

        with open(template_path, "r") as f:
            template = f.read()

        html_node = markdown_to_html_nodes(markdown)
        html_string = html_node.to_html()

        title = extract_title(markdown)

        dest_html_path = os.path.splitext(dest_path)[0] + ".html"
        page = template.replace("{{ Title }}", title).replace("{{ Content }}", html_string)
        page = page.replace('href="/', f'href="{basepath}')
        page = page.replace('src="/', f'src="{basepath}')

        with open(dest_html_path, "w") as f:
            f.write(page)


def main():
    try:
        basepath = sys.argv[1]
    except IndexError:
        basepath = "/"

    textNode = TextNode("This is some anchor text", "link", "https://www.boot.dev")
    print(textNode)
    copy_content("static", "public")
    generate_pages_recursive("content/", "template.html", "docs/", basepath)

print("CWD:", os.getcwd())
print("public exists?", os.path.exists("public"))
print("public/index.html exists?", os.path.exists("public/index.html"))

main()