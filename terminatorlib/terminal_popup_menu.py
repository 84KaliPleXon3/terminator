#!/usr/bin/python
# Terminator by Chris Jones <cmsj@tenshu.net>
# GPL v2 only
"""terminal_popup_menu.py - classes necessary to provide a terminal context 
menu"""

import gtk

from version import APP_NAME
from translation import _
from encoding import TerminatorEncoding

class TerminalPopupMenu(object):
    """Class implementing the Terminal context menu"""
    terminal = None

    def __init__(self, terminal):
        """Class initialiser"""
        self.terminal = terminal

    def show(self, widget, event=None):
        """Display the context menu"""
        terminal = self.terminal

        menu = gtk.Menu()
        url = None
        button = None
        time = None

        if event:
            url = terminal.check_for_url(event)
            button = event.button
            time = event.time

        if url:
            if url[1] == terminal.matches['email']:
                nameopen = _('_Send email to...')
                namecopy = _('_Copy email address')
            elif url[1] == terminal.matches['voip']:
                nameopen = _('Ca_ll VoIP address')
                namecopy = _('_Copy VoIP address')
            else:
                nameopen = _('_Open link')
                namecopy = _('_Copy address')

            icon = gtk.image_new_from_stock(gtk.STOCK_JUMP_TO,
                                            gtk.ICON_SIZE_MENU)
            item = gtk.ImageMenuItem(nameopen)
            item.set_property('image', icon)
            item.connect('activate', lambda x: terminal.open_url(url, True))
            menu.append(item)

            item = gtk.MenuItem(namecopy)
            item.connect('activate', 
                         lambda x: terminal.clipboard.set_text(url[0]))
            menu.append(item)

            menu.append(gtk.MenuItem())

        item = gtk.ImageMenuItem(gtk.STOCK_COPY)
        item.connect('activate', lambda x: terminal.vte.copy_clipboard())
        item.set_sensitive(terminal.vte.get_has_selection())
        menu.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_PASTE)
        item.connect('activate', lambda x: terminal.paste_clipboard())
        menu.append(item)

        menu.append(gtk.MenuItem())

        if not terminal.is_zoomed():
            item = gtk.ImageMenuItem('Split H_orizontally')
            image = gtk.Image()
            image.set_from_icon_name(APP_NAME + '_horiz', gtk.ICON_SIZE_MENU)
            item.set_image(image)
            if hasattr(item, 'set_always_show_image'):
                item.set_always_show_image(True)
            item.connect('activate', lambda x: terminal.emit('split-horiz'))
            menu.append(item)

            item = gtk.ImageMenuItem('Split V_ertically')
            image = gtk.Image()
            image.set_from_icon_name(APP_NAME + '_vert', gtk.ICON_SIZE_MENU)
            item.set_image(image)
            if hasattr(item, 'set_always_show_image'):
                item.set_always_show_image(True)
            item.connect('activate', lambda x: terminal.emit('split-vert'))
            menu.append(item)

            item = gtk.MenuItem(_('Open _Tab'))
            item.connect('activate', lambda x: terminal.emit('tab-new'))
            menu.append(item)

            menu.append(gtk.MenuItem())

        item = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        item.connect('activate', lambda x: terminal.emit('close-term'))
        menu.append(item)

        menu.append(gtk.MenuItem())

        if not terminal.is_zoomed():
            item = gtk.MenuItem(_('_Zoom terminal'))
            item.connect('activate', terminal.zoom)
            menu.append(item)

            item = gtk.MenuItem(_('Ma_ximise terminal'))
            item.connect('activate', terminal.maximise)
            menu.append(item)

            menu.append(gtk.MenuItem())
        else:
            item = gtk.MenuItem(_('_Restore all terminals'))
            item.connect('activate', terminal.unzoom)
            menu.append(item)

            menu.append(gtk.MenuItem())

        item = gtk.CheckMenuItem(_('Show _scrollbar'))
        item.set_active(terminal.scrollbar.get_property('visible'))
        item.connect('toggled', lambda x: terminal.do_scrollbar_toggle())
        menu.append(item)

        item = gtk.CheckMenuItem(_('Show _titlebar'))
        item.set_active(terminal.titlebar.get_property('visible'))
        item.connect('toggled', lambda x: terminal.do_title_toggle())
        if terminal.group:
            item.set_sensitive(False)
        menu.append(item)

        item = gtk.MenuItem(_('Ed_it profile'))
        item.connect('activate', lambda x:
                     terminal.terminator.edit_profile(terminal))
        menu.append(item)

        self.add_encoding_items(menu)

        menu.show_all()
        menu.popup(None, None, None, button, time)

        return(True)


    def add_encoding_items(self, menu):
        """Add the encoding list to the menu"""
        terminal = self.terminal
        active_encodings = terminal.config['active_encodings']
        item = gtk.MenuItem (_("Encodings"))
        menu.append (item)
        submenu = gtk.Menu ()
        item.set_submenu (submenu)
        encodings = TerminatorEncoding ().get_list ()
        encodings.sort (lambda x, y: cmp (x[2].lower (), y[2].lower ()))

        current_encoding = terminal.vte.get_encoding ()
        group = None

        if current_encoding not in active_encodings:
            active_encodings.insert (0, _(current_encoding))

        for encoding in active_encodings:
            if encoding == terminal.default_encoding:
                extratext = " (%s)" % _("Default")
            elif encoding == current_encoding and \
                 terminal.custom_encoding == True:
                extratext = " (%s)" % _("User defined")
            else:
                extratext = ""
    
            radioitem = gtk.RadioMenuItem (group, _(encoding) + extratext)
    
            if encoding == current_encoding:
                radioitem.set_active (True)
    
            if group is None:
                group = radioitem
    
            radioitem.connect ('activate', terminal.on_encoding_change, 
                               encoding)
            submenu.append (radioitem)
    
        item = gtk.MenuItem (_("Other Encodings"))
        submenu.append (item)
        #second level
    
        submenu = gtk.Menu ()
        item.set_submenu (submenu)
        group = None
    
        for encoding in encodings:
            if encoding[1] in active_encodings:
                continue

            if encoding[1] is None:
                label = "%s %s"%(encoding[2], terminal.vte.get_encoding ())
            else:
                label = "%s %s"%(encoding[2], encoding[1])
    
            radioitem = gtk.RadioMenuItem (group, label)
            if group is None:
                group = radioitem
    
            if encoding[1] == current_encoding:
                radioitem.set_active (True)

            radioitem.connect ('activate', terminal.on_encoding_change, 
                               encoding[1])
            submenu.append (radioitem)

