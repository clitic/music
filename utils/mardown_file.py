import re
from typing import Dict, List, Union
from rich.console import Console
from rich.markdown import Markdown


class MarkdownFile:
    """Class for supporting variables in markdown
    """
    
    def __init__(self, text: str) -> None:
        """Class for supporting variables in markdown

        Args:
            text (str): markdown string
        """
        self.text = text
        
        self.variable_data: Dict[str, str] = {}
        for var in re.findall(r"<!--\s\$\w*\s-->", self.text):
            key_var = str(var).replace("<!-- $", "").replace(" -->", "")
            self.variable_data[key_var] = var
    
    @classmethod
    def from_file(cls, filepath: str):
        """Construct MarkdownFile class from a markdown file

        Args:
            filepath (str): markdown file path

        Returns:
            MarkdownFile: instance of MarkdownFile class
        """
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
        
        return cls(text)      
                  
    def __repr__(self) -> str:
        Console().print(Markdown(self.text))
        return ""

    def __getitem__(self, key: str) -> list:
        if key not in self.variable_data.keys():
            raise KeyError(f"{key} variable not found in {self}")
        else:
            return self.variable_data[key]
        
    def __setitem__(self, key: str, value: Union[str, List[str]]):
        var_text = self.__getitem__(key)
        
        if isinstance(value, str):
            self.variable_data[key] = value
        elif isinstance(value, list):
            self.variable_data[key] = var_text + "".join(value)
        else:
            raise TypeError(f"unsupported type {type(value)}, only str and List[str] supported")
    
    def flush(self):
        """flush updated variable values into MarkdownFile.text property
        """
        for var, var_text in self.variable_data.items():
            self.text = self.text.replace(f"<!-- ${var} -->", var_text)    

    def save(self, filepath: str):
        """save new markdown file on disk

        Args:
            filepath (str): markdown file path
        """
        self.flush()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.text)

def _test():
    my_md = MarkdownFile("<!-- $timestamp --> <!-- $timestamp -->")
    my_md["timestamp"] = "12:00"
    my_md["timestamp"] += " AM"
    my_md.flush()
    assert my_md.text == "12:00 AM 12:00 AM"
    