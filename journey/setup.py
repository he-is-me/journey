
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, HorizontalScroll, VerticalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header , Label, Tree


class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def main_goals_tree(self):
        tree: Tree[str] = Tree("Main Goals", id="goals_tree")
        tree.root.expand()
        main_goals = tree.root.add("Testing", expand=True)
        [main_goals.add_leaf(str(i)) for i in range(8)]
        return tree

    def compose(self) -> ComposeResult:
        yield Tree("")



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
