### Copyright (C) 2009 Manuel Ospina <ospina.manuel@gmail.com>

# This file is part of rayuela.
#
# rayuela is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# rayuela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rayuela; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys

try:
    import pygtk
    pygtk.require('2.0')
except:
    pass
try:
    import gtk
    import gtk.glade
    import pango
except:
    print "GTK is not installed"
    sys.exit(1)
try:
    import gtkspell
except:
    print "gtkspell is not installed"
    sys.exit(1)

import configuration

class View:
    
    def __init__(self, controller, model, glade_file):

        self.controller = controller
        self.model = model
        # Register the view as an observer
        self.model.register(self)
        # Create the main window and connect signals.
        self.glade_file = glade_file
        self.widget_tree = gtk.glade.XML(self.glade_file, "window")
        dic = {"on_window_destroy": self.controller.quit,
               "on_window_delete_event": self.controller.delete_event,
               "on_new_activate": self.controller.new,
               "on_open_activate": self.controller.open,
               "on_save_activate": self.controller.save,
               "on_save_as_activate": self.controller.save_as,
               "on_quit_activate": self.controller.quit,
               "on_undo_activate": self.controller.undo,
               "on_redo_activate": self.controller.redo,
               "on_cut_activate": self.controller.cut,
               "on_copy_activate": self.controller.copy,
               "on_paste_activate": self.controller.paste,
               "on_delete_activate": self.controller.delete,
               "on_preferences_activate": self.controller.preferences,
               "on_new_character_activate": self.controller.new_character,
               "on_edit_character_activate":self.controller.edit_character,
               "on_delete_character_activate":self.controller.delete_character,
               "on_new_location_activate":self.controller.new_location,
               "on_edit_location_activate":self.controller.edit_location,
               "on_delete_location_activate":self.controller.delete_location,
               "on_spell_check_activate": self.controller.spell_check,
               "on_about_activate": self.controller.about,
               "on_new_button_clicked": self.controller.new,
               "on_open_button_clicked": self.controller.open,
               "on_add_section_button_clicked": self.controller.add_section,
               "on_save_button_clicked": self.controller.save,
               "on_undo_button_clicked": self.controller.undo,
               "on_redo_button_clicked": self.controller.redo,
               "on_cut_button_clicked": self.controller.cut,
               "on_copy_button_clicked": self.controller.copy,
               "on_paste_button_clicked": self.controller.paste,
               # [NOTE]
               # The following features are not supported on v0.1
               #"on_add_section_toolbutton_clicked": self.controller.add_section,
               "on_bold_toolbutton_clicked": self.controller.bold,
               "on_italic_toolbutton_clicked": self.controller.italic,
               "on_underline_toolbutton_clicked": self.controller.underline,
               "on_left_toolbutton_clicked": self.controller.justify_left,
               "on_center_toolbutton_clicked": self.controller.justify_center,
               "on_right_toolbutton_clicked": self.controller.justify_right,
               "on_fill_toolbutton_clicked": self.controller.justify_fill,
               #.
              }

        self.widget_tree.signal_autoconnect(dic)

        window = self.widget_tree.get_widget('window')
        window.maximize()

        # Project Treeview
        self._set_tree_view_()

        # Character Treeview
        self._set_character_tree_view_()

        # Location Treeview
        self._set_location_tree_view_()

        # [NOTE]
        # Not supported in v0.1
        #self._set_add_section_box_()
        #.

        self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)

        self.tag_table = self._create_tag_table_()
    
    def _set_tree_view_(self):
        # (Filename/Section title, page number, section ID)
        treestore = gtk.TreeStore(str, int, str)
        treeview = self.widget_tree.get_widget('project_treeview')
        # Columns
        file_column = gtk.TreeViewColumn('Project')
        # Cells
        cell = gtk.CellRendererText()
        file_column.pack_start(cell, True)
        file_column.add_attribute(cell, 'text', 0)
        # Treeview
        treeview.connect('button_press_event', self._project_tree_row_press_)
        treeview.set_model(treestore)
        treeview.append_column(file_column)
    
    def _set_character_tree_view_(self):
        # (Project/Character name, project page, character ID)
        treestore = gtk.TreeStore(str, int, str)
        treeview = self.widget_tree.get_widget('character_treeview')
        # Columns
        name_column = gtk.TreeViewColumn('Name')
        # Cells
        cell = gtk.CellRendererText()
        name_column.pack_start(cell, True)
        name_column.add_attribute(cell, 'text', 0)
        # Treeview
        treeview.connect('button_press_event', self._generic_tree_row_press_)
        treeview.set_model(treestore)
        treeview.append_column(name_column)

    def _set_location_tree_view_(self):
        # (Project/Location name, project page, location ID)
        treestore = gtk.TreeStore(str, int, str)
        treeview = self.widget_tree.get_widget('location_treeview')
        # Columns
        name_column = gtk.TreeViewColumn('Name')
        # Cells
        cell = gtk.CellRendererText()
        name_column.pack_start(cell, True)
        name_column.add_attribute(cell, 'text', 0)
        # Treeview
        treeview.connect('button_press_event', self._generic_tree_row_press_)
        treeview.set_model(treestore)
        treeview.append_column(name_column)
   
    # [TODO]
    # The _project_tree_row_press_ and the _generic_tree_row_press_ have a few
    # differences, refactor!.
    def _project_tree_row_press_(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, iter = obj.get_selection().get_selected()
            if iter == None:
                return
            page = model.get_value(iter, 1)
            section_id = model.get_value(iter, 2)
            notebook = self.widget_tree.get_widget("main_notebook")
            notebook.set_current_page(page)
            document = self.model.get_document_by_page(page)
            if section_id:
                section = document.get_section_by_id(section_id)
                # Fix me!
                mark = document.buffer.get_mark(section_id)
                iter = document.buffer.get_iter_at_mark(mark)
                document.buffer.place_cursor(iter)
                #.
            else:
                section = document.synopsis
            self.section_dialog(section)
    
    def _generic_tree_row_press_(self, obj, event):
        widget_name = obj.get_name()
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, iter = obj.get_selection().get_selected()
            if iter == None:
                return
            page = model.get_value(iter, 1)
            id = model.get_value(iter, 2)
            notebook = self.widget_tree.get_widget("main_notebook")
            notebook.set_current_page(page)
            document = self.model.get_document_by_page(page)
            if not id:
                return
            if widget_name == 'character_treeview':
                profile = document.get_character_by_id(id)
                self.character_dialog(profile)
            elif widget_name == 'location_treeview':
                location = document.get_location_by_id(id)
                self.location_dialog(location)
            else:
                error_dialog("NotImplementedError")
    #.

    # [NOTE]
    # This features are not supported in v0.1
    def _set_add_section_box_(self):
        sections = ["dedication", "section"]
        store = gtk.ListStore(str)
        for section in sections:
            store.append([section])
        boxentry = self.widget_tree.get_widget("section_comboboxentry")
        boxentry.set_model(store)
        boxentry.set_text_column(0)
        boxentry.set_active(0)

    def get_section_to_add(self):
        boxentry = self.widget_tree.get_widget("section_comboboxentry")
        model = boxentry.get_model()
        index = boxentry.get_active()
        section = model[index][0]
        return section
    #.
    
    def section_dialog(self, section):

        result = gtk.RESPONSE_CANCEL

        widget_tree = gtk.glade.XML(self.glade_file, "section_dialog")
        dialog = widget_tree.get_widget("section_dialog")
        
        if section.id:
            # Title
            title_widget = widget_tree.get_widget("section_title_entry")
            title_widget.set_text(section.title)
            
            # Synopsis
            widget = widget_tree.get_widget("synopsis_textview")
            buffer = widget.get_buffer()
            buffer.set_text(section.synopsis)

            # Note
            widget = widget_tree.get_widget("section_notes_textview")
            buffer = widget.get_buffer()
            buffer.set_text(section.notes)
            
            # [NOTE]
            # The dialog is modal by default. But it doesn't matter whether is
            # modal or not, pygtk doesn't allow dialogs to be modal.
            dialog.set_modal(True)
            #.

        else:
            section.set_id()

        result = dialog.run()
        if result == gtk.RESPONSE_OK:

            # Title
            title_widget = widget_tree.get_widget("section_title_entry")
            section.title = title_widget.get_text()
            
            # Synopsis
            widget = widget_tree.get_widget("synopsis_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            section.synopsis = buffer.get_text(start, end)

            # Note
            widget = widget_tree.get_widget("section_notes_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            section.notes = buffer.get_text(start, end)
        
        dialog.destroy()

        return result
    
    def character_dialog(self, profile):

        result = gtk.RESPONSE_CANCEL

        widget_tree = gtk.glade.XML(self.glade_file, "character_dialog")
        dialog = widget_tree.get_widget("character_dialog")
        
        if profile.id:
            # Name
            widget = widget_tree.get_widget("character_name_entry")
            widget.set_text(profile.name)

            # Age
            widget = widget_tree.get_widget("character_age_entry")
            widget.set_text(profile.age)

            # Job
            widget = widget_tree.get_widget("character_job_entry")
            widget.set_text(profile.job)

            # Origin
            widget = widget_tree.get_widget("character_origin_entry")
            widget.set_text(profile.origin)

            # Residency
            widget = widget_tree.get_widget("character_residency_entry")
            widget.set_text(profile.residency)

            # Religion
            widget = widget_tree.get_widget("character_religion_entry")
            widget.set_text(profile.religion)

            # physical
            widget = widget_tree.get_widget("character_physical_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.physical)

            # psychological
            widget = widget_tree.get_widget("character_psychological_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.psychological)

            # social
            widget = widget_tree.get_widget("character_social_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.social)

            # notes
            widget = widget_tree.get_widget("character_notes_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.notes)
                        
            # [NOTE]
            # The dialog is modal by default. But it doesn't matter whether is
            # modal or not, pygtk doesn't allow dialogs to be modal.
            dialog.set_modal(True)
            #.

        else:
            profile.set_id()

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            
            # Name
            widget = widget_tree.get_widget("character_name_entry")
            profile.name = widget.get_text()

            # Age
            widget = widget_tree.get_widget("character_age_entry")
            profile.age = widget.get_text()

            # Job
            widget = widget_tree.get_widget("character_job_entry")
            profile.job = widget.get_text()

            # Origin
            widget = widget_tree.get_widget("character_origin_entry")
            profile.origin = widget.get_text()

            # Residency
            widget = widget_tree.get_widget("character_residency_entry")
            profile.residency = widget.get_text()

            # Religion
            widget = widget_tree.get_widget("character_religion_entry")
            profile.religion = widget.get_text()

            # physical
            widget = widget_tree.get_widget("character_physical_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.physical = buffer.get_text(start, end)

            # psychological
            widget = widget_tree.get_widget("character_psychological_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.psychological = buffer.get_text(start, end)

            # social
            widget = widget_tree.get_widget("character_social_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.social = buffer.get_text(start, end)

            # notes
            widget = widget_tree.get_widget("character_notes_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.notes = buffer.get_text(start, end)
        
        dialog.destroy()

        return result

    def location_dialog(self, profile):

        result = gtk.RESPONSE_CANCEL

        widget_tree = gtk.glade.XML(self.glade_file, "location_dialog")
        dialog = widget_tree.get_widget("location_dialog")
        
        if profile.id:
            # Name
            widget = widget_tree.get_widget("location_name_entry")
            widget.set_text(profile.name)

            # description
            widget = widget_tree.get_widget("location_description_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.description)

            # landscape
            widget = widget_tree.get_widget("location_landscape_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.landscape)

            # weather
            widget = widget_tree.get_widget("location_weather_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.weather)

            # tradition
            widget = widget_tree.get_widget("location_tradition_textview")
            buffer = widget.get_buffer()
            buffer.set_text(profile.weather)

            # The dialog is modal by default. But it doesn't matter whether is
            # modal or not, pygtk doesn't allow dialogs to be modal.
            dialog.set_modal(True)
            #.

        else:
            profile.set_id()

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            
            # Name
            widget = widget_tree.get_widget("location_name_entry")
            profile.name = widget.get_text()

            # description
            widget = widget_tree.get_widget("location_description_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.description = buffer.get_text(start, end)
            
            # landscape
            widget = widget_tree.get_widget("location_landscape_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.landscape = buffer.get_text(start, end)

            # weather
            widget = widget_tree.get_widget("location_weather_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.weather = buffer.get_text(start, end)
            
            # tradition
            widget = widget_tree.get_widget("location_tradition_textview")
            buffer = widget.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            profile.tradition = buffer.get_text(start, end)
        
        dialog.destroy()

        return result
        
    def preferences_dialog(self):
        result = gtk.RESPONSE_CANCEL

        widget_tree = gtk.glade.XML(self.glade_file, "preferences_dialog")
        dialog = widget_tree.get_widget("preferences_dialog")
        
        if "language" in configuration.options:
            widget = widget_tree.get_widget("preferences_language_entry")
            widget.set_text(configuration.options["language"])
        
        if "spellcheck" in configuration.options:
            if configuration.options["spellcheck"] == "True":
                spellcheck = True
            else:
                spellcheck = False
            widget = widget_tree.get_widget("activate_spellcheck_checkbutton")
            widget.set_active(spellcheck)

        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            
            # Language
            widget = widget_tree.get_widget("preferences_language_entry")
            configuration.options["language"] = widget.get_text()

            # Spellcheck?
            widget = widget_tree.get_widget("activate_spellcheck_checkbutton")
            configuration.options["spellcheck"] = str(widget.get_active())
            
        dialog.destroy()

        return result


    def _create_tag_table_(self):
        tag_table = gtk.TextTagTable()
            
        tag = gtk.TextTag("bold")
        tag.set_property("weight", pango.WEIGHT_BOLD)
        tag_table.add(tag)
        
        tag = gtk.TextTag("italic")
        tag.set_property("style", pango.STYLE_ITALIC)
        tag_table.add(tag)
        
        tag = gtk.TextTag("underline")
        tag.set_property("underline", pango.UNDERLINE_SINGLE)
        tag_table.add(tag)
        
        tag = gtk.TextTag("center")
        tag.set_property("justification", gtk.JUSTIFY_CENTER)
        tag_table.add(tag)
        
        tag = gtk.TextTag("left")
        tag.set_property("justification", gtk.JUSTIFY_LEFT)
        tag_table.add(tag)
        
        tag = gtk.TextTag("right")
        tag.set_property("justification", gtk.JUSTIFY_RIGHT)
        tag_table.add(tag)
        
        # [TODO]
        # priority = Very low 
        #tag = gtk.TextTag("fill")
        #tag.set_property("justification", gtk.JUSTIFY_FILL)
        #tag_table.add(tag)
        #.
               
        tag = gtk.TextTag("invisible")
        tag.set_property("invisible", True)
        tag.set_property("editable", False)
        tag_table.add(tag)

        tag = gtk.TextTag("uneditable")
        tag.set_property("editable", False)
        tag_table.add(tag)

        return tag_table

    def add_textview(self):
        notebook = self.widget_tree.get_widget("main_notebook")
        tree = gtk.glade.XML(self.glade_file, 'scrolledwindow')
        page = tree.get_widget('scrolledwindow')
        page.show()
        i = notebook.append_page(page)
        notebook.set_current_page(i)
        for children in page.get_children():
            if children.get_name() == 'textview':
                return children
        return None
        
    def set_spellcheck(self):         
        notebook = self.widget_tree.get_widget("main_notebook")
        n_pages = notebook.get_n_pages()
        for i in range(n_pages):
            page = notebook.get_nth_page(i)
            for children in page.get_children():
                for child in children.get_children():
                    if child.get_name() == 'textview':
                        self._set_spellcheck_(child)

    def _set_spellcheck_(self, textview):
        if 'spellcheck' in configuration.options:
            # Deactivate previous spell
            try:
                spell = gtkspell.get_from_text_view(textview)
            except:
                pass
            else:
                spell.detach()
            # Activate new spell if necessary
            activate_spellcheck = configuration.options["spellcheck"]
            if activate_spellcheck == "True":
                spell = gtkspell.Spell(textview)
                # [TODO]
                # Priority: medium/high
                # Each project should have their own language settings.
                if 'language' in configuration.options:
                    language = configuration.options["language"]
                    if language:
                        spell.set_language(language)
                #.

    def update(self):
        project_tree = self.widget_tree.get_widget('project_treeview')
        project_store = project_tree.get_model()
        project_store.clear()
        for document in self.model.documents:
            if not document.filename:
                document.filename = 'untitled'
            root = project_store.append(None, [document.filename, 
                                               document.page, 
                                               ''])
            for section in document:
                node = project_store.append(root, [section.title, 
                                                   document.page,
                                                   section.id])
                
        # Characters
        tree = self.widget_tree.get_widget('character_treeview')
        store = tree.get_model()
        store.clear()
        for document in self.model.documents:
            if not document.filename:
                document.filename = 'untitled'
            root = store.append(None, [document.filename, 
                                       document.page, 
                                       ''])
            for n in document.character:
                node = store.append(root, [n.name, 
                                           document.page,
                                           n.id])
        # Locations 
        tree = self.widget_tree.get_widget('location_treeview')
        store = tree.get_model()
        store.clear()
        for document in self.model.documents:
            if not document.filename:
                document.filename = 'untitled'
            root = store.append(None, [document.filename, 
                                       document.page, 
                                       ''])
            for n in document.location:
                node = store.append(root, [n.name, 
                                           document.page,
                                           n.id])
        # [TODO]
        # * update the tab of the main notebook

def dialog(message, txt):
    msg = gtk.MessageDialog(None, 0, message, gtk.BUTTONS_OK, txt)
    msg.run()  
    msg.destroy()

def error_dialog(txt):
    dialog(gtk.MESSAGE_ERROR, txt)
    
def info_dialog(txt): 
    dialog(gtk.MESSAGE_INFO, txt)

def request_dialog(title, txt):
    msg_label = gtk.Label(txt)
    msg = gtk.Dialog(title, None, gtk.DIALOG_MODAL,
                     (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                      gtk.STOCK_OK, gtk.RESPONSE_OK))
    msg.resize(350, 250)
    msg.vbox.pack_start(msg_label)
    msg.show_all()
    result = msg.run()
    if result == gtk.RESPONSE_OK:
        return True
    msg.destroy()
 
def file_chooser(txt, action):
    filename = ''
    chooser = gtk.FileChooserDialog(txt, None, action,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                     gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    ret = chooser.run()
    if ret == gtk.RESPONSE_OK:
        filename = chooser.get_filename()
    chooser.destroy()
    return filename

if __name__ == "__main__": pass
