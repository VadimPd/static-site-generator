from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    CODE = "code"
    HEADING = "heading"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


