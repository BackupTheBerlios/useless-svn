from useless.kdebase.actions import BaseItem, BaseAction


#################
# main window actions
#################

class NewEntityWindowAction(BaseAction):
    def __init__(self, slot, parent):
        item = BaseItem('Open a new Entity Window', 'personal',
                        'Open a new Entity Window', 'Open a new Entity Window')
        BaseAction.__init__(self, item, slot, parent, 'NewEntityWindow')

class NewRadioWindowAction(BaseAction):
    def __init__(self, slot, parent):
        item = BaseItem('Open a new Radio Window', 'radio',
                        'Open a new Radio Window', 'Open a new Radio Window')
        BaseAction.__init__(self, item, slot, parent, 'NewRadioWindow')
        
class NewRtorrentWindowAction(BaseAction):
    def __init__(self, slot, parent):
        item = BaseItem('Open a new rtorrent window', 'bt',
                        'Open a new rtorrent window', 'Open a new rtorrent window')
        BaseAction.__init__(self, item, slot, parent, 'NewRtorrentWindow')
        
##################
# entity window actions
##################

class NewTagItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'New Tag', 'add', 'Create a new tag', 'Create a new tag')

class NewTagAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, NewTagItem(), slot, parent, name='NewTagAction')

