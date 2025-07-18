from textual.app import App, ComposeResult
from datetime import date
from textual import on
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, Vertical, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.events import Focus
from textual.widget import Widget
from textual.widgets import Button, Digits, Footer, Header, Input , Label, MarkdownViewer, RadioButton, Rule, TextArea, Tree, Label
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

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """when a tier button is selected the others are made unclickable"""
        t1_button = self.query_one("#mg_t1", RadioButton)
        t2_button = self.query_one("#mg_t2", RadioButton)
        t3_button = self.query_one("#mg_t3", RadioButton)
        id = event.radio_button.id
        value = event.radio_button.value

        if id == "mg_t1":
            if value == False:
                t2_button.disabled = False
                t3_button.disabled = False
            else:
                t2_button.disabled = True
                t3_button.disabled = True

        elif id == "mg_t2":
            if value == False:
                t1_button.disabled = False
                t3_button.disabled = False
            else:
                t1_button.disabled = True
                t3_button.disabled = True

        elif id == "mg_t3":
            if value == False:
                t1_button.disabled = False
                t2_button.disabled = False
            else:
                t1_button.disabled = True
                t2_button.disabled = True



    def compose(self) -> ComposeResult:
        """ids prefixed with mg stands for Main Goal"""
        yield Input(placeholder="Goal Name", id="mg_goal_input")
        yield Horizontal(Vertical(Input(placeholder="Start Date (optional)", id="mg_start_date"),
                                  Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="mg_due_date"),
                                  Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="mg_difficulty", type="number"),
                                  id="mg_dates_dif_vertical"),

                         Vertical(RadioButton(label="Tier 1 (Mission critical Goal)", id="mg_t1", disabled=False),
                                  RadioButton(label="Tier 2 (High-Impact Goal)", id="mg_t2", disabled=False),
                                  RadioButton(label="Tier 3 (Growth & Improvement)", id="mg_t3", disabled=False),
                                  id="mg_tier_vertical"),
                         id="mg_main_horizontal")
        yield Label(Text("""Beyond just completing this goal, what would achieving it truly mean for you or your life? How would things be different,
                         and what impact would it have on your well-being, growth, or overall aspirations?""",style="bold"), id="mg_description_label")
        yield TextArea(id="mg_description")
        # yield Rule(line_style='heavy')

#
# class SubGoalsCollection(VerticalGroup):
#     """collecting sub goals from user which are 2nd on the hierarchy of 
#     goals in journey. These goals are the ones that must be complete before
#     the maing goal is complete"""
#
#     def compose(self) -> ComposeResult:
#             yield Input(placeholder="Goal Name", id="sg_goal_input")
#             yield Input(placeholder="Start Date (optional)", id="sg_start_date")
#             yield Input(placeholder="Due Date", id="sg_due_date")
#             yield Horizontal(RadioButton(label="Tier 1", id="sg_t1", disabled=False),
#                              RadioButton(label="Tier 2", id="sg_t2", disabled=False),
#                              RadioButton(label="Tier 3", id="sg_t3", disabled=False),
#                              Input(placeholder="Difficulty (1-3)", id="sg_difficulty", type="number"),
#                              id="sg_tier_horizontal")
#             yield Label(Text("Description (Optional)",style="bold"), id="sg_description_label")
#             yield TextArea(id="sg_description")
#

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

    # BINDINGS = [("ctrl+n", "next_screen", "Go next " ),
    #             ("ctrl+b", "previous_screen", "Go back")] #TODO make this a f string so it can say exactly what

    CSS_PATH = "styling.tcss"



    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                GoalMenu(),
                MainGoalCollection()
                , id="main_screen")

        yield Footer()

    #
    #
    # def action_next_screen(self):
    #     """moves user to the next phase of the goal inputing phase"""
    #     self.page_num += 1
    #     next_page = self.pages[self.page_num % len(self.pages)]
    #     self.app.query(self.page_ids[(self.page_num % len(self.pages)) - 1]).remove() #remove current widget 
    #     self.app.query_one("#main_screen").mount(next_page) # add next widget
    #
    #
    # def action_previous_screen(self) -> None:
    #     if self.page_num >= 1:
    #         next_page = self.pages[self.page_num % len(self.pages) - 1]
    #         self.app.query(self.page_ids[(self.page_num % len(self.pages))]).remove() #remove main_goal_vert
    #         self.app.query_one("#main_screen").mount(next_page) # add sub_goal
    #


if __name__ == "__main__":
    app = JourneyApp()
    app.run()

























