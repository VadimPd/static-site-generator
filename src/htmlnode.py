class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        if self.tag is None:
            return self.value or ""
        props_str = ""
        if self.props is not None:
            for key, value in self.props.items():
                props_str += f" {key}='{value}'"
        children_str = ""
        if self.children is not None:
            for child in self.children:
                children_str += child.to_html()
        if self.value:
            children_str += self.value
        return f"<{self.tag}>{children_str}</{self.tag}>"



    def props_to_html(self):
        result_string = ""
        if self.props is None or self.props == {}:
            return ""
        for key, value in self.props.items():
            result_string += f' {key}="{value}"'
        return result_string

    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

class LeafNode(HTMLNode):
    VOID_TAGS = {"img", "br", "hr", "meta", "link", "input"}
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if self.tag is None:
            if self.value is None:
                raise ValueError("LeafNode cannot be None")
            return self.value
        props_to_html = self.props_to_html()
        if self.tag == "img":
            return f"<{self.tag}{props_to_html}>"
        if self.value is None or self.value == "":
            raise ValueError
        return f"<{self.tag}{props_to_html}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        html = ""
        if self.tag is None:
            raise ValueError("ParentNode tag cannot be None")
        if self.children is None:
            raise ValueError("ParentNode must have children")
        for child in self.children:
            html += child.to_html()
        return f"<{self.tag}>{html}</{self.tag}>"

    