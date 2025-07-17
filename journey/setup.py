from pathlib import Path
from textual.app import App, ComposeResult
from datetime import date
from textual import on
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, Vertical, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.events import Focus
from textual.widgets import Button, Digits, Footer, Header, Input , Label, MarkdownViewer, RadioButton, TextArea, Tree, Label
from rich.text import Text


#testing a push
#this is a test


class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def insert_new_goalTree(self, main_goal_table: str, tree_id: str):
        tree: Tree[str] = Tree(main_goal_table, id=tree_id)
        tree.root.expand()
        return tree

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        event.node.label = "FUCCCK"


    

    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> None:
        tree_root.root.add(goal_name)
        

    def compose(self) -> ComposeResult:
        #TODO make sure that I know this really wants to take args or not !
        yield self.insert_new_goalTree("Main Goals", "main_goals")
        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")



class MainGoalCollection(VerticalGroup):
    """widget for collecting all user goal info"""

    goal_name = reactive("")
    start_date = reactive("")
    due_date = reactive("")
    tier = reactive("")
    difficulty= reactive("")
    description= reactive("")

                        


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
        #NOTE change the id's to be prefixed with "maingoal" for easier understanding of .tcss file
        yield Vertical(
                Input(placeholder="Goal Name", id="goal_input"),
                Input(placeholder="Start Date (optional)", id="start_date"),
                Input(placeholder="Due Date", id="due_date"),
                Horizontal(RadioButton(label="Tier 1", id="t1", disabled=False),
                           RadioButton(label="Tier 2", id="t2", disabled=False),
                           RadioButton(label="Tier 3", id="t3", disabled=False),
                           Input(placeholder="Difficulty (1-3)", id="difficulty", type="number"),
                           id="tier_horizontal"),
                Label(Text("Description (Optional)",style="bold"), id="description_label"),
                TextArea(id="description"),
                Horizontal(id="progress_horizontal"), id="main_goal_vertical")


class SubGoalsCollection(VerticalGroup):
    """collecting sub goals from user which are 2nd on the hierarchy of 
    goals in journey. These goals are the ones that must be complete before
    the maing goal is complete"""

    def compose(self) -> ComposeResult:
        yield Vertical(
                Input(placeholder="Goal Name", id="subgoal_input"),
                Input(placeholder="Due Date", id="subgoal_due_date"),
                Horizontal(RadioButton(label="Tier 1", id="t1", disabled=False),
                           RadioButton(label="Tier 2", id="t2", disabled=False),
                           RadioButton(label="Tier 3", id="t3", disabled=False),
                           Input(placeholder="Difficulty (1-3)", id="difficulty", type="number"),
                           id="tier_horizontal"),
                Label(Text("Description (Optional)",style="bold"), id="description_label"),
                TextArea(id="description"),
                Horizontal(id="progress_horizontal"))


#Deprecated until further notice
# class ToolTips(VerticalGroup):
#     """widget for displaying tips for any object the user is focused on"""
#
#
#
#
#
#
#     def fetch_dialog(self, header: str):
#         """Reads the dialog.md file and gets the correct lines of text
#         and gives it to the text area and updates it"""
#         dialogs = {}
#         buff = []
#         in_block = False
#         with open(Path("dialog.md"), 'r') as file:
#             contents = file.read()
#             for line in contents.splitlines():
#                 if line.startswith("## ") and header in line[3:]:
#                     in_block = True
#                     continue
#                 if in_block: # --- means end of the block 
#                     if line.startswith("---"):
#                         break
#                     buff.append(line)
#         dialogs[header] = '\n'.join(buff).strip()
#         return dialogs[header]
#
#
#
#     def compose(self) -> ComposeResult:
#         yield MarkdownViewer(markdown=self.fetch_dialog("tooltips_main_goal_name"),
#                              id="tooltips_md", show_table_of_contents=False)
#



class JourneyApp(App): 
    """A comprehensive neovim terminal application"""

    BINDINGS = [("n", "next_screen", "Go to next page" )] #TODO make this a f string so it can say exactly what
                                                          #the next page is for example it would say: "Go to subgoals"
    CSS_PATH = "styling.tcss"

    page_num = 0
    pages = [MainGoalCollection, SubGoalsCollection]
    
    def action_next_screen(self):
        """moves user to the next phase of the goal inputing phase"""
        #TODO this shit does NOT work, fix it
        self.page_num += 1
        next_page = self.pages[self.page_num]
        self.app.query_one("#main_goal_vertical").remove() #remove main_goal_vert
        self.app.query_one("#main_goal_vertical").mount(next_page) # add sub_goal


    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                GoalMenu(),
                MainGoalCollection()
                )
        yield Footer()


if __name__ == "__main__":
    app = JourneyApp()
    app.run()
