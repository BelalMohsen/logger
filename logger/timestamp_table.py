class TableCell(object):
    EMPTY = 0
    START = 1
    END = 3
    FULL = 4
    PARTIAL = 5

    def __init__(self):
        self.state = self.EMPTY
        self.value = "?"
        self.start_factor = 0.0
        self.end_factor = 0.0
        self.color = "#222222"

        self.set_empty()

    def set_full(self):
        self.state = self.FULL
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_empty(self):
        self.value = ""
        self.state = self.EMPTY
        self.color = "#FFFFFF00"

    def set_start(self, factor):
        self.state = self.START
        self.start_factor = factor
        self.end_factor = 1.0
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_end(self, factor):
        self.state = self.END
        self.start_factor = 0.0
        self.end_factor = factor
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_partial(self, start_factor, end_factor):
        self.state = self.PARTIAL
        self.start_factor = start_factor
        self.end_factor = end_factor
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def render(self):
        style = ""
        attributes = ""
        if self.state == self.EMPTY:
            style = "background-color: {};".format(self.color)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.FULL:
            styles = [
                "border-left: none;",
                "background-color: {};".format(self.color)
            ]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.START:
            styles = [
                "background-image: linear-gradient(to left, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-position: 100% 100%;",
                "background-size: {}% 100%".format(int((1 - self.start_factor) * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.END:
            styles = [
                "border-left: none;",
                "background-image: linear-gradient(to right, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-size: {}% 100%".format(int(self.end_factor * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.PARTIAL:
            fill = self.end_factor - self.start_factor
            styles = [
                "background-image: linear-gradient(to right, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-position: {}% 100%;".format(int(self.start_factor * 100)),
                "background-size: {}% 100%".format(int(fill * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)

        return '<td class="day_cell" {}>{}</td>'.format(attributes, self.value)