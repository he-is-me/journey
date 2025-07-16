from textual.app import App, ComposeResult
from textual import on
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, Input , Label, RadioButton, TextArea, Tree, Label
from rich.text import Text


#testing a push
#this is a test


class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def insert_new_goalTree(self, main_goal_table: str, tree_id: str):
        tree: Tree[str] = Tree(main_goal_table, id=tree_id)
        tree.root.expand()
        return tree

    

    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> None:
        tree_root.root.add(goal_name)
        

    def compose(self) -> ComposeResult:
        #TODO make sure that I know this really wants to take args or not !
        yield self.insert_new_goalTree("Main Goals", "main_goals")
        yield Horizontal(Button("Edit", id="edit_goal", disabled=True),
                         Button("Remove", id="remove_goal", disabled=True),
                         id="edit_remove_horizontal")
        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")



class GoalCollection(VerticalGroup):
    """widget for collecting all user goal info"""


    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """when a tier button is selected the others are made unclickable"""
        t1_button = self.query_one("#t1", RadioButton)
        t2_button = self.query_one("#t2", RadioButton)
        t3_button = self.query_one("#t3", RadioButton)
        id = event.radio_button.id
        value = event.radio_button.value

        if id == "t1":
            if value == False:
                t2_button.disabled = False
                t3_button.disabled = False
            else:
                t2_button.disabled = True
                t3_button.disabled = True

        elif id == "t2":
            if value == False:
                t1_button.disabled = False
                t3_button.disabled = False
            else:
                t1_button.disabled = True
                t3_button.disabled = True

        elif id == "t3":
            if value == False:
                t1_button.disabled = False
                t2_button.disabled = False
            else:
                t1_button.disabled = True
                t2_button.disabled = True



    def compose(self) -> ComposeResult:
        yield VerticalScroll(
                Input(placeholder="Goal Name", id="goal_input"),
                Input(placeholder="Start Date (optional)", id="start_date"),
                Input(placeholder="Due Date", id="due_date"),
                Horizontal(RadioButton(label="Tier 1", id="t1", disabled=False),
                           RadioButton(label="Tier 2", id="t2", disabled=False),
                           RadioButton(label="Tier 3", id="t3", disabled=False)
                           , id="tier_horizontal"),
                Input(placeholder="Difficulty", id="difficulty"),
                Label(Text("Description (Optional)",style="bold"), id="description_label"),
                TextArea(id="description"),
                Horizontal(Button(label="Finish",  id="finish_button_GC", disabled=True), #GC == GoalCollection widget
                           Button(label="Back",  id="back_button_GC", disabled=True),
                           Button(label="Next", id="next_button_GC"),
                           id="progress_horizontal")
                )



class ToolTips(VerticalGroup):
    """widget for displaying tips for any object the user is focused on"""

    def compose(self) -> ComposeResult:
        yield TextArea("This is the tooltips section !",read_only=True, id="tooltips_text")




class JourneyApp(App): 
    """A comprehensive neovim terminal application"""

    CSS_PATH = "styling.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                GoalMenu(),
                GoalCollection(),
                ToolTips())
        yield Footer()


if __name__ == "__main__":
    app = JourneyApp()
    app.run()
