
from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, VerticalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, Input , Label, Tree, Label
from rich.text import Text


class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def insert_new_goalTree(self, main_goal_table: str, tree_id: str):
        tree: Tree[str] = Tree(main_goal_table, id=tree_id)
        tree.root.expand()
        return tree

    

    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> None:
        tree_root.root.add(goal_name)
        

    def compose(self) -> ComposeResult:
        yield self.insert_new_goalTree("Main Goals", "main_goals")
        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")



class GoalCollection(VerticalGroup):
    """widget for collecting all user goal info"""

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
                Input(placeholder="Goal Name", id="goal_input"),
                Input(placeholder="Due Date", id="due_date")
                ) 



class JourneyApp(App): 
    """A comprehensive neovim terminal application"""
    

    CSS_PATH = "styling.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        yield GoalMenu()
        yield GoalCollection()
        yield Footer()


if __name__ == "__main__":
    app = JourneyApp()
    app.run()
