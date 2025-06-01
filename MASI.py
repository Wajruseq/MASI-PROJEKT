from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.graphics import Color, Line, Ellipse
import sqlite3

# Klasa zarządzająca bazą danych (bez zmian)
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('MASI.sqlite3')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS operations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            Name TEXT NOT NULL, 
                            Description TEXT NOT NULL,
                            term_A TEXT NOT NULL, 
                            term_B TEXT NOT NULL,
                            term_P_A TEXT NOT NULL, 
                            term_P_B TEXT NOT NULL,
                            OP_P TEXT NOT NULL,
                            OP TEXT NOT NULL)''')
        self.conn.commit()

    def add_params(self, name, desc, a, b, ap, bp, op, op_p):
        self.c.execute(
            '''INSERT INTO operations 
               (Name, Description, term_A, term_B, term_P_A, term_P_B, OP_P, OP) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, desc, a, b, ap, bp, op, op_p)
        )
        self.conn.commit()

    def del_params(self, name):
        self.c.execute("DELETE FROM operations WHERE Name=?", (name,))
        self.conn.commit()

    def get_params(self):
        self.c.execute("SELECT * FROM operations")
        return self.c.fetchall()

    def get_names(self):
        self.c.execute("SELECT Name, Description FROM operations")
        return self.c.fetchall()

    def get_data(self, name, desc):
        self.c.execute("SELECT term_A, term_B, term_P_A, term_P_B, OP_P, OP FROM operations WHERE Name IS ? AND Description IS ?", (name, desc))
        return self.c.fetchall()

# Widget do rysowania na canvas
class CanvasWidget(Widget):
    def add_text(self, text, x, y, tags=None):
        with self.canvas:
            Label(text=text, pos=(x, y), font_size=12)

# Główna klasa GUI
class MainScreen(BoxLayout):
    term_a_var = StringProperty('')
    term_b_var = StringProperty('')
    term_a_var_p = StringProperty('')
    term_b_var_p = StringProperty('')
    name_var = StringProperty('')
    desc_var = StringProperty('')
    op_var = StringProperty(';')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.operation_popup = None

    def savef(self):
        term_a = self.term_a_var.strip()
        term_b = self.term_b_var.strip()
        term_ap = self.term_a_var_p.strip()
        term_bp = self.term_b_var_p.strip()
        operator = self.op_var
        operator_p = ';'  # Domyślna wartość dla OP_P, nie używana w sekwencjonowaniu
        name = self.name_var.strip()
        description = self.desc_var.strip()

        if not name or not description or not term_a or not term_b or not operator:
            self.show_popup("Missing Data", "Insert terms before saving.")
            return

        self.db.add_params(name, description, term_a, term_b, term_ap, term_bp, operator, operator_p)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.5, 0.5))
        popup.open()

    def clear_canvas(self):
        self.ids.canvas_widget.canvas.clear()
        self.term_a_var = ''
        self.term_b_var = ''
        self.term_a_var_p = ''
        self.term_b_var_p = ''

    def loadf(self):
        names = self.db.get_names()
        content = BoxLayout(orientation='vertical', spacing=5)
        content.add_widget(Label(text="Load data:", font_size=20))
        for name in names:
            btn = Button(text=str(name), size_hint_y=None, height=40)
            btn.bind(on_press=lambda x, n=name: self.load_selection(n))
            content.add_widget(btn)
        popup = Popup(title="Load", content=content, size_hint=(0.5, 0.8))
        popup.open()

    def load_selection(self, name):
        data = self.db.get_data(name[0], name[1])
        self.draw_alt(data)
        self.parent.parent.dismiss()

    def changef(self):
        term_a = self.term_a_var.strip()
        term_b = self.term_b_var.strip()

        if not term_a or not term_b:
            self.show_popup("Missing Data", "Insert terms before clicking 'Change'.")
            return

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Zamiana unitermu w sekwencjonowaniu", font_size=20))
        btn_frame = BoxLayout()
        btn1 = Button(text="Zamień term_A na term_P_A", size_hint_x=0.5)
        btn2 = Button(text="Zamień term_B na term_P_B", size_hint_x=0.5)
        btn_frame.add_widget(btn1)
        btn_frame.add_widget(btn2)
        content.add_widget(btn_frame)

        def term1(*args):
            self.draw_sequencing(self.term_a_var_p, self.term_b_var, self.op_var)
            popup.dismiss()

        def term2(*args):
            self.draw_sequencing(self.term_a_var, self.term_b_var_p, self.op_var)
            popup.dismiss()

        btn1.bind(on_press=term1)
        btn2.bind(on_press=term2)
        popup = Popup(title="Zamiana unitermu", content=content, size_hint=(0.5, 0.5))
        popup.open()

    def draw_sequencing(self, term_a, term_b, operator):
        self.ids.canvas_widget.canvas.clear()
        result = f"{term_a} {operator} {term_b}"
        text_width = len(result) * 10
        margin = 20
        x1 = 80
        x2 = x1 + text_width + margin
        y1 = 20
        y2 = 80
        with self.ids.canvas_widget.canvas:
            Color(0.68, 0.85, 0.9, 1)
            Line(ellipse=(x1, y1, x2, y2, 0, 180), width=2)
            self.ids.canvas_widget.add_text(result, (x1 + x2) / 2, y2 - 35)

    def sequencing_button(self):
        content = BoxLayout(orientation='vertical', spacing=5)
        self.op_var = ';'
        term_a_input = TextInput(text=self.term_a_var, multiline=False)
        term_b_input = TextInput(text=self.term_b_var, multiline=False)
        content.add_widget(Label(text="Term A"))
        content.add_widget(term_a_input)
        content.add_widget(Label(text="Term B"))
        content.add_widget(term_b_input)
        content.add_widget(Label(text="Operacje:"))
        radio1 = Button(text=";", on_press=lambda x: setattr(self, 'op_var', ';'))
        radio2 = Button(text=",", on_press=lambda x: setattr(self, 'op_var', ','))
        content.add_widget(radio1)
        content.add_widget(radio2)
        add_button = Button(text="ADD", on_press=lambda x: self.sequencing(term_a_input.text, term_b_input.text))
        content.add_widget(add_button)
        self.operation_popup = Popup(title="Sequencing", content=content, size_hint=(0.5, 0.5))
        self.operation_popup.open()

    def sequencing(self, term_a, term_b):
        self.term_a_var = term_a
        self.term_b_var = term_b
        self.draw_sequencing(term_a, term_b, self.op_var)
        if self.operation_popup:
            self.operation_popup.dismiss()

    def draw_alt(self, data):
        self.term_a_var = data[0][0]
        self.term_b_var = data[0][1]
        self.term_a_var_p = data[0][2]
        self.term_b_var_p = data[0][3]
        self.op_var = data[0][5]
        self.draw_sequencing(data[0][0], data[0][1], data[0][5])

class MASIApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    MASIApp().run()
