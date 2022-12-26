from transitions.extensions import GraphMachine


class TocMachine(GraphMachine):
    state_text = None

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.state_text = "USER"

    def is_going_to_state1(self, event):
        text = event.message.text
        return (text.lower() == "search" or text.lower() == "track")

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "artist"

    def is_going_to_state3(self, event):
        text = event.message.text
        return text.lower() == "billboard"

    def is_going_to_user(self, event):
        text = event.message.text
        return text.lower() == "exit"

    def on_enter_state1(self, event):
        self.state_text = "SEARCH"
        print("I'm entering state1")

    def on_exit_state1(self, event):
        self.state_text = "USER"
        print("Leaving state1")

    def on_enter_state2(self, event):
        self.state_text = "ARTIST"
        print("I'm entering state2")

    def on_exit_state2(self, event):
        self.state_text = "USER"
        print("Leaving state2")

    def on_enter_state3(self, event):
        self.state_text = "BILLBOARD"
        print("I'm entering state3")

    def on_exit_state3(self, event):
        self.state_text = "USER"
        print("Leaving state3")

    def welcome_message(self):
        welcome_text = "welcome!\n"
        welcome_text += 'now in ' + self.state_text + " mode\n"

        if self.state_text == "SEARCH":
            welcome_text += '*search for your track!\n'
        elif self.state_text == "ARTIST":
            welcome_text += '*search for your artist!\n'
        welcome_text += '*or enter help for more'
        return welcome_text

    def help_text(self):
        help_text = "now in " + \
            self.state_text + " mode\nINSTRUCTION SET:\n"
        if self.state_text == "USER":
            help_text += "search   : enter search mode\n"
            help_text += "random : random song\n"
            help_text += "preview : listen to the song\n"
        elif self.state_text == "SEARCH":
            help_text += "*       : search tracks!\n"
            help_text += "exit  : exit search mode\n"
            help_text += "next : next relevant track\n"
            help_text += "artist: switch to search artist!\n"
        elif self.state_text == "ARTIST":
            help_text += "*       : search artist!\n"
            help_text += "exit  : exit search mode\n"
            help_text += "next : next relevant artist\n"
            help_text += "track: switch to search track!\n"
        elif self.state_text == "BILLBOARD":
            help_text += "*int: get the ranked track!\n"
            help_text += "exit  : exit billboard mode\n"
            help_text += "next : next track on chart\n"
        help_text += "/*    all command are none    */\n"
        help_text += "/*          case sensitive           */"
        return help_text
