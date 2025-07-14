
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, HorizontalScroll, VerticalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header , Label, Tree, Label
from rich.text import Text


class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def insert_new_goalTree(self, tree_label: str, tree_id: str):
        tree: Tree[str] = Tree(tree_label, id=tree_id)
        tree.root.expand()
        main_goals = tree.root.add("Testing", expand=True)
        tree.root.add_leaf('SUB GOALS')
        [main_goals.add_leaf(str(i)) for i in range(8)]
        return tree

    def compose(self) -> ComposeResult:
        yield Label(Text('Goals', style="bold red underline", justify='center'))
        yield self.insert_new_goalTree("Main Goals", "main_goals")
        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")



class JourneyApp(App): 
    """A comprehensive neovim terminal application"""
    

    CSS_PATH = "styling.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        yield GoalMenu()
        yield Footer()


if __name__ == "__main__":
    app = JourneyApp()
    app.run()
