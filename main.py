import sqlite3
import os
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

# Set window size for testing (remove for mobile)
Window.size = (360, 640)

class DatabaseManager:
    def __init__(self):
        self.db_path = 'diary.db'
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_entry(self, title, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        date = datetime.now().isoformat()
        cursor.execute(
            'INSERT INTO diary_entries (title, content, date) VALUES (?, ?, ?)',
            (title, content, date)
        )
        conn.commit()
        conn.close()
    
    def get_all_entries(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diary_entries ORDER BY date DESC')
        entries = cursor.fetchall()
        conn.close()
        return entries
    
    def update_entry(self, entry_id, title, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE diary_entries SET title = ?, content = ? WHERE id = ?',
            (title, content, entry_id)
        )
        conn.commit()
        conn.close()
    
    def delete_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM diary_entries WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        title_label = Label(
            text='My Personal Diary',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_x=0.7
        )
        
        menu_btn = Button(
            text='Menu',
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 1, 1)
        )
        menu_btn.bind(on_press=self.show_menu)
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(menu_btn)
        
        # Entries list
        self.scroll = ScrollView()
        self.entries_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.entries_layout.bind(minimum_height=self.entries_layout.setter('height'))
        
        self.scroll.add_widget(self.entries_layout)
        
        # Add entry button
        add_btn = Button(
            text='+ Add New Entry',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        add_btn.bind(on_press=self.add_entry)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(self.scroll)
        main_layout.add_widget(add_btn)
        
        self.add_widget(main_layout)
        self.load_entries()
    
    def load_entries(self):
        self.entries_layout.clear_widgets()
        entries = self.db.get_all_entries()
        
        if not entries:
            empty_label = Label(
                text='No diary entries yet\nTap "Add New Entry" to start writing',
                text_size=(None, None),
                halign='center',
                valign='middle',
                font_size='16sp',
                color=(0.5, 0.5, 0.5, 1)
            )
            self.entries_layout.add_widget(empty_label)
        else:
            for entry in entries:
                entry_widget = self.create_entry_widget(entry)
                self.entries_layout.add_widget(entry_widget)
    
    def create_entry_widget(self, entry):
        entry_id, title, content, date_str = entry
        
        # Parse date
        try:
            date_obj = datetime.fromisoformat(date_str)
            formatted_date = date_obj.strftime('%b %d, %Y - %I:%M %p')
        except:
            formatted_date = date_str
        
        # Create entry layout
        entry_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(10),
            spacing=dp(5)
        )
        
        # Title
        title_label = Label(
            text=title,
            font_size='16sp',
            bold=True,
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(0.2, 0.2, 0.2, 1)
        )
        
        # Content preview
        content_preview = content[:100] + '...' if len(content) > 100 else content
        content_label = Label(
            text=content_preview,
            font_size='14sp',
            text_size=(None, None),
            halign='left',
            valign='top',
            color=(0.4, 0.4, 0.4, 1)
        )
        
        # Date
        date_label = Label(
            text=formatted_date,
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1),
            text_size=(None, None),
            halign='left',
            valign='bottom'
        )
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        
        view_btn = Button(
            text='View',
            size_hint_x=0.33,
            background_color=(0.2, 0.6, 1, 1)
        )
        view_btn.bind(on_press=lambda x: self.view_entry(entry))
        
        edit_btn = Button(
            text='Edit',
            size_hint_x=0.33,
            background_color=(0.8, 0.6, 0.2, 1)
        )
        edit_btn.bind(on_press=lambda x: self.edit_entry(entry))
        
        delete_btn = Button(
            text='Delete',
            size_hint_x=0.34,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_press=lambda x: self.confirm_delete(entry_id))
        
        btn_layout.add_widget(view_btn)
        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(delete_btn)
        
        entry_layout.add_widget(title_label)
        entry_layout.add_widget(content_label)
        entry_layout.add_widget(date_label)
        entry_layout.add_widget(btn_layout)
        
        return entry_layout
    
    def add_entry(self, instance):
        self.manager.current = 'add_edit'
        self.manager.get_screen('add_edit').setup_for_new_entry()
    
    def edit_entry(self, entry):
        self.manager.current = 'add_edit'
        self.manager.get_screen('add_edit').setup_for_edit(entry)
    
    def view_entry(self, entry):
        self.manager.current = 'view'
        self.manager.get_screen('view').display_entry(entry)
    
    def confirm_delete(self, entry_id):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text='Are you sure you want to delete this entry?'))
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        cancel_btn = Button(text='Cancel', background_color=(0.5, 0.5, 0.5, 1))
        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        delete_btn.bind(on_press=lambda x: self.delete_entry(entry_id, popup))
        
        popup.open()
    
    def delete_entry(self, entry_id, popup):
        self.db.delete_entry(entry_id)
        popup.dismiss()
        self.load_entries()
    
    def show_menu(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        about_btn = Button(text='About', background_color=(0.2, 0.6, 1, 1))
        privacy_btn = Button(text='Privacy Policy', background_color=(0.2, 0.6, 1, 1))
        contact_btn = Button(text='Contact Us', background_color=(0.2, 0.6, 1, 1))
        terms_btn = Button(text='Terms of Service', background_color=(0.2, 0.6, 1, 1))
        close_btn = Button(text='Close', background_color=(0.5, 0.5, 0.5, 1))
        
        content.add_widget(about_btn)
        content.add_widget(privacy_btn)
        content.add_widget(contact_btn)
        content.add_widget(terms_btn)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Menu',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        about_btn.bind(on_press=lambda x: self.navigate_to('about', popup))
        privacy_btn.bind(on_press=lambda x: self.navigate_to('privacy', popup))
        contact_btn.bind(on_press=lambda x: self.navigate_to('contact', popup))
        terms_btn.bind(on_press=lambda x: self.navigate_to('terms', popup))
        close_btn.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def navigate_to(self, screen_name, popup):
        popup.dismiss()
        self.manager.current = screen_name
    
    def on_enter(self):
        self.load_entries()

class AddEditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_entry = None
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        self.title_label = Label(
            text='New Entry',
            font_size='18sp',
            bold=True,
            size_hint_x=0.4
        )
        
        save_btn = Button(
            text='Save',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        save_btn.bind(on_press=self.save_entry)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(self.title_label)
        header_layout.add_widget(save_btn)
        
        # Title input
        title_label = Label(
            text='Title:',
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left'
        )
        
        self.title_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size='16sp'
        )
        
        # Content input
        content_label = Label(
            text='Write your thoughts:',
            size_hint_y=None,
            height=dp(30),
            text_size=(None, None),
            halign='left'
        )
        
        self.content_input = TextInput(
            multiline=True,
            font_size='16sp'
        )
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(title_label)
        main_layout.add_widget(self.title_input)
        main_layout.add_widget(content_label)
        main_layout.add_widget(self.content_input)
        
        self.add_widget(main_layout)
    
    def setup_for_new_entry(self):
        self.current_entry = None
        self.title_label.text = 'New Entry'
        self.title_input.text = ''
        self.content_input.text = ''
    
    def setup_for_edit(self, entry):
        self.current_entry = entry
        self.title_label.text = 'Edit Entry'
        self.title_input.text = entry[1]  # title
        self.content_input.text = entry[2]  # content
    
    def save_entry(self, instance):
        title = self.title_input.text.strip()
        content = self.content_input.text.strip()
        
        if not title or not content:
            self.show_message('Please fill in both title and content')
            return
        
        if self.current_entry:
            # Update existing entry
            self.db.update_entry(self.current_entry[0], title, content)
            message = 'Entry updated successfully'
        else:
            # Create new entry
            self.db.add_entry(title, content)
            message = 'Entry saved successfully'
        
        self.show_message(message)
        Clock.schedule_once(lambda dt: self.go_back(None), 1)
    
    def show_message(self, message):
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class ViewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='View Entry',
            font_size='18sp',
            bold=True,
            size_hint_x=0.4
        )
        
        edit_btn = Button(
            text='Edit',
            size_hint_x=0.3,
            background_color=(0.8, 0.6, 0.2, 1)
        )
        edit_btn.bind(on_press=self.edit_entry)
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        header_layout.add_widget(edit_btn)
        
        # Content area
        scroll = ScrollView()
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll.add_widget(self.content_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def display_entry(self, entry):
        self.current_entry = entry
        self.content_layout.clear_widgets()
        
        entry_id, title, content, date_str = entry
        
        # Parse date
        try:
            date_obj = datetime.fromisoformat(date_str)
            formatted_date = date_obj.strftime('%B %d, %Y - %I:%M %p')
        except:
            formatted_date = date_str
        
        # Title
        title_label = Label(
            text=title,
            font_size='20sp',
            bold=True,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        title_label.bind(texture_size=title_label.setter('size'))
        
        # Date
        date_label = Label(
            text=formatted_date,
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        date_label.bind(texture_size=date_label.setter('size'))
        
        # Separator
        separator = Label(text='─' * 50, size_hint_y=None, height=dp(20))
        
        # Content
        content_label = Label(
            text=content,
            font_size='16sp',
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        content_label.bind(texture_size=content_label.setter('size'))
        
        self.content_layout.add_widget(title_label)
        self.content_layout.add_widget(date_label)
        self.content_layout.add_widget(separator)
        self.content_layout.add_widget(content_label)
    
    def edit_entry(self, instance):
        self.manager.current = 'add_edit'
        self.manager.get_screen('add_edit').setup_for_edit(self.current_entry)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='About',
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        
        # Content
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        about_text = """Personal Diary
Version 1.0.0

About Personal Diary:
Personal Diary is a simple, secure, and private diary application that allows you to record your thoughts, memories, and daily experiences. Your entries are stored locally on your device, ensuring complete privacy and security.

Key Features:
✓ Create and edit diary entries
✓ Organize entries by date and time
✓ Simple and intuitive interface
✓ Complete privacy - all data stored locally
✓ No internet connection required
✓ Clean, distraction-free writing experience

Developer Information:
Developed with ❤️ using Python and Kivy
For support and feedback, please contact us.

Contact: tangsabas@gmail.com"""
        
        about_label = Label(
            text=about_text,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            font_size='14sp',
            size_hint_y=None
        )
        about_label.bind(texture_size=about_label.setter('size'))
        
        content_layout.add_widget(about_label)
        scroll.add_widget(content_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class PrivacyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='Privacy Policy',
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        
        # Content
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        privacy_text = """Privacy Policy for Personal Diary
Last updated: December 2024

Introduction:
Personal Diary ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we handle information when you use our Personal Diary mobile application.

Information We Collect:
Personal Diary is designed with privacy in mind. We do NOT collect, store, or transmit any personal information or diary content to external servers. All your diary entries are stored locally on your device only.

Data Storage:
All diary entries, including titles, content, and timestamps, are stored locally on your device using SQLite database. This data never leaves your device and is not accessible to us or any third parties.

Data Security:
Since all data is stored locally on your device, the security of your diary entries depends on your device's security measures. We recommend using device lock screens and keeping your device secure.

Third-Party Services:
Personal Diary does not integrate with any third-party services that collect personal information. We do not use analytics, advertising, or tracking services.

Children's Privacy:
Our Service is suitable for users of all ages. Since we do not collect any personal information, there are no special provisions for children under 13.

Changes to Privacy Policy:
We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy in the app.

Contact Us:
If you have any questions about this Privacy Policy, please contact us at tangsabas@gmail.com"""
        
        privacy_label = Label(
            text=privacy_text,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            font_size='12sp',
            size_hint_y=None
        )
        privacy_label.bind(texture_size=privacy_label.setter('size'))
        
        content_layout.add_widget(privacy_label)
        scroll.add_widget(content_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class ContactScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='Contact Us',
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        
        # Content
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        contact_text = """Get in Touch

We'd love to hear from you! Whether you have questions, feedback, or need support, don't hesitate to reach out.

Email Support:
tangsabas@gmail.com

What can we help you with?
🐛 Report a bug or issue
💡 Suggest a new feature
❓ Ask questions about the app
⭐ Share your feedback
🔒 Privacy and security concerns

Response Time:
We typically respond to emails within 24-48 hours. For urgent issues, please mention "URGENT" in your subject line.

Subject Line Format:
Personal Diary App - [Your Issue/Question]

Thank you for using Personal Diary!"""
        
        contact_label = Label(
            text=contact_text,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            font_size='14sp',
            size_hint_y=None
        )
        contact_label.bind(texture_size=contact_label.setter('size'))
        
        content_layout.add_widget(contact_label)
        scroll.add_widget(content_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='Terms of Service',
            font_size='18sp',
            bold=True,
            size_hint_x=0.7
        )
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title_label)
        
        # Content
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        terms_text = """Terms of Service
Last updated: December 2024

Acceptance of Terms:
By downloading, installing, or using the Personal Diary mobile application, you agree to be bound by these Terms of Service.

Description of Service:
Personal Diary is a mobile application that allows users to create, edit, and store personal diary entries locally on their device.

User Responsibilities:
• Maintaining the security of your device
• Backing up your diary entries if desired
• Using the app in accordance with applicable laws
• Not using the app for illegal or harmful purposes

Data and Privacy:
All diary entries are stored locally on your device. We do not collect, access, or transmit your personal data.

Intellectual Property:
The Personal Diary app and its original content are owned by us and are protected by copyright laws. You retain ownership of your diary entries.

Disclaimer of Warranties:
The Service is provided "as is" without warranties of any kind.

Limitation of Liability:
We shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the Service.

Contact Information:
For questions about these Terms of Service, please contact us at tangsabas@gmail.com"""
        
        terms_label = Label(
            text=terms_text,
            text_size=(Window.width - dp(40), None),
            halign='left',
            valign='top',
            font_size='12sp',
            size_hint_y=None
        )
        terms_label.bind(texture_size=terms_label.setter('size'))
        
        content_layout.add_widget(terms_label)
        scroll.add_widget(content_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class PersonalDiaryApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Add all screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddEditScreen(name='add_edit'))
        sm.add_widget(ViewScreen(name='view'))
        sm.add_widget(AboutScreen(name='about'))
        sm.add_widget(PrivacyScreen(name='privacy'))
        sm.add_widget(ContactScreen(name='contact'))
        sm.add_widget(TermsScreen(name='terms'))
        
        return sm

if __name__ == '__main__':
    PersonalDiaryApp().run()