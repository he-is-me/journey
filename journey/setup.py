from ast import Tuple, TypeAlias
from fileinput import filename
from tokenize import Number
from textual.app import App, ComposeResult
from pathlib import Path
from datetime import date, datetime
from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, Vertical, VerticalGroup, VerticalScroll
from textual.css.types import TextAlign
from textual.reactive import reactive
from textual.events import Focus
from textual.validation import Integer, Length, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Button, Digits, Footer, Header, Input , Label, MarkdownViewer, Pretty, RadioButton, Rule, Static, TextArea, Tree, Label
from textual import log 
from rich.text import Text

#testing a push
#this is a test

class GoalMenu(VerticalGroup):
    """The main goals area tree"""

    def insert_root_node(self, tree_root: str, tree_id: str):
        tree: Tree[str] = Tree(Text(tree_root,style="bold underline"), id=tree_id)
        tree.root.expand()
        return tree




    def on_tree_node_selected(self, event: Tree.NodeSelected):
        ...


    

    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> Tree:
        tree_root.root.add(goal_name)
        return tree_root
        

    def compose(self) -> ComposeResult:
        #TODO make sure that I know this really wants to take args or not !
        yield self.insert_root_node("Goals", "goals_tree")

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
        #TODO add tooltips to all of the inputs and description
        yield Input(placeholder="Goal Name", id="mg_goal_input", valid_empty=False,
                    validate_on=['blur','changed'],
                    validators=[Length(minimum=1, maximum=500, failure_description="Goal too short !")])

        yield Horizontal(Vertical(Input(placeholder="Start Date (optional)", id="mg_start_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator()],valid_empty=True),

                                  Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="mg_due_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator(),
                                                    DateRangeValidator()]),

                                  Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="mg_difficulty", 
                                        type="number", validators=[Integer(minimum=1, maximum=3)], validate_on=["blur","submitted"]),
                         id="mg_dates_dif_vertical",),

                         Vertical(RadioButton(label="Tier 1 (Mission critical Goal)", id="mg_t1", disabled=False),
                                  RadioButton(label="Tier 2 (High-Impact Goal)", id="mg_t2", disabled=False),
                                  RadioButton(label="Tier 3 (Growth & Improvement)", id="mg_t3", disabled=False),
                         id="mg_tier_vertical"),

              id="mg_main_horizontal")

        yield Label(Text("""Beyond just completing this goal, what would achieving it truly mean for you or your life? How would things be different,
                         and what impact would it have on your well-being, growth, or overall aspirations?""",style="bold"), id="mg_description_label")
        yield TextArea(id="mg_description")
        yield Static(content="",id="mg_notification")
        # yield Rule(line_style='heavy')


    @on(Input.Changed)
    def validator_fail_notification(self, event: Input.Changed):
        """when input valifator failed tell user why at bottom of screen"""
        #TODO remove later
        if event.validation_result != None:
            notification = self.query_one("#mg_notification", Static)
            if not event.validation_result.is_valid: 
                notification.update("\n".join(event.validation_result.failure_descriptions))
            else:
                notification.update("")
        else:
            return

    




class DateValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if self.check_date(value):
            return self.success()
        return self.failure("Invalid Date")


    @staticmethod
    def check_date(value: str, get_date: bool=False) -> bool|datetime:
        format_opt = "%m/%d/%y"
        try:
            converted_date = datetime.strptime(value,format_opt)
            if get_date:
                return converted_date
            return True
        except Exception as e:
            #TODO log this
            return False



class DateRangeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if self.check_range(value):
            return self.success()
        return self.failure("Invalid date range, start date > due date !")



    @staticmethod
    def check_range(value) -> bool:
        """checks that start date is less than or equal to due date"""
        start_date = app.query_one("#mg_start_date", Input).value
        try:
            start = DateValidator.check_date(start_date, get_date=True)
            end = DateValidator.check_date(value, get_date=True)
        except Exception as e:
            return False
        else:
            if isinstance(start,datetime) and isinstance(end,datetime):
                return start <= end
            return False







    




class SubGoalCollection(VerticalGroup):
    """collecting sub goals from user which are 2nd on the hierarchy of 
    goals in journey. These goals are the ones that must be complete before
    the maing goal is complete"""

    def compose(self) -> ComposeResult:
            yield Input(placeholder="Goal Name", id="sg_goal_input")
            yield Input(placeholder="Start Date (optional)", id="sg_start_date")
            yield Input(placeholder="Due Date", id="sg_due_date")
            yield Horizontal(RadioButton(label="Tier 1", id="sg_t1", disabled=False),
                             RadioButton(label="Tier 2", id="sg_t2", disabled=False),
                             RadioButton(label="Tier 3", id="sg_t3", disabled=False),
                             Input(placeholder="Difficulty (1-3)", id="sg_difficulty", type="number"),
                             id="sg_tier_horizontal")
            yield Label(Text("Description (Optional)",style="bold"), id="sg_description_label")
            yield TextArea(id="sg_description")


class ToolTips(VerticalGroup):
    """widget for displaying tips for any object the user is focused on"""


    def fetch_dialog(self, header: str):
        """Reads the dialog.md file and gets the correct lines of text
        and gives it to the text area and updates it"""
        dialogs = {}
        buff = []
        in_block = False
        with open(Path("dialog.md"), 'r') as file:
            contents = file.read()
            for line in contents.splitlines():
                if line.startswith("## ") and header in line[3:]:
                    in_block = True
                    continue
                if in_block: # --- means end of the block 
                    if line.startswith("---"):
                        break
                    buff.append(line)
        dialogs[header] = '\n'.join(buff).strip()
        return dialogs[header]



    def compose(self) -> ComposeResult:
        yield MarkdownViewer(markdown=self.fetch_dialog("tooltips_main_goal_name"),
                             id="tooltips_md", show_table_of_contents=False)




class JourneyApp(App): 
    """A comprehensive neovim terminal application"""

    BINDINGS = [("ctrl+n", "next_screen", "Go next " ),
                ("ctrl+b", "previous_screen", "Go back"),
                Binding("ctrl+a", "add_goal_type", "Add Goal", priority=True)] 

    CSS_PATH = "styling.tcss"

    page_num = 0
    page_ids = ["MainGoalCollection", "SubGoalCollection"]
    main_goal_page = MainGoalCollection(id="main_goal_page")
    sub_goal_page = SubGoalCollection(id="sub_goal_page")
    pages = [main_goal_page, sub_goal_page]


    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                GoalMenu(),
                MainGoalCollection()
                , id="screen")

        yield Footer()




    def action_add_goal_type(self):
        """this is only for adding main goals, sub goals and task
        are added throguh selected events handling"""
        if self.page_num == 0:
            self.add_main_goal_action()




    def add_main_goal_action(self):
        """controls adding main goal to goal tree"""

        main_goal_tree = self.app.query_one("#goals_tree", Tree)
        goal_input_data = self.app.query_one("#mg_goal_input", Input)
        start_date = self.app.query_one("#mg_start_date", Input)
        due_date = self.app.query_one("#mg_due_date", Input)
        difficulty = self.app.query_one("#mg_difficulty", Input)
        description = self.app.query_one("#mg_description", TextArea)
        tiers = [self.app.query_one("#mg_t1", RadioButton),
                self.app.query_one("#mg_t2", RadioButton),
                self.app.query_one("#mg_t3", RadioButton)]

        selected_tier = ""
        for tier  in tiers:
            if tier.value == True:
                selected_tier = tier.label
                if "1" in str(selected_tier):
                    selected_tier = 1
                elif "2" in str(selected_tier):
                    selected_tier = 2
                else:
                    selected_tier = 3
                
        node = main_goal_tree.root.add(goal_input_data.value, 
                                       data={"start_date": start_date.value,
                                             "due_date": due_date.value,
                                             "difficulty": difficulty.value,
                                             "tier": selected_tier,
                                             "description": description.text})
        #NOTE could use node var to store in file just in case user exits or wants to finish later
        #the whole node tree and ALL data will be saved and can be easily put back in the tree




    def action_next_screen(self):
        """moves user to the next phase of the goal inputing phase"""
        self.page_num += 1
        next_page = self.pages[self.page_num % len(self.pages)]
        self.app.query(self.page_ids[(self.page_num % len(self.pages)) - 1]).remove() #remove current widget 
        self.app.query_one("#screen").mount(next_page) # add next widget


    def action_previous_screen(self) -> None:
        if self.page_num >= 1:
            next_page = self.pages[(self.page_num % len(self.pages)) - 1]
            self.app.query(self.page_ids[(self.page_num % len(self.pages))]).remove() #remove main_goal_vert
            self.page_num -= 1
            self.app.query_one("#screen").mount(next_page) # add sub_goal



if __name__ == "__main__":
    app = JourneyApp()
    app.run()


