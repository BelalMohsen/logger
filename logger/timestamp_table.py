import datetime

from logger.utils import format_timedelta


class WeekTableRow(list):
    def __init__(self, day):
        super(WeekTableRow, self).__init__()
        self.day = day
        self._total_duration = datetime.timedelta()

    @property
    def total_duration(self):
        return self._total_duration

    @total_duration.setter
    def total_duration(self, value):
        self._total_duration = value

    @property
    def total_duration_str(self):
        return format_timedelta(self.total_duration)


class TableCell(object):
    EMPTY = 0
    START = 1
    END = 3
    FULL = 4
    PARTIAL = 5  # a cell which contains a start and an end, ie. "..|....[XXX]....|..."
    REVERSE_PARTIAL = 6  # a cell which contains an end and a start, ie. "..XX|XX]..[XX|XX.."

    EMPTY_COLOR = "#FFFFFF00"
    BACKGROUND_COLOR = "#FFFFFFFF"

    def __init__(self, row, hour, datum):
        self.row = row
        self.hour = hour
        self.state = self.EMPTY
        self.value = ""
        self.start_factor = 0.0
        self.end_factor = 0.0
        self.color = datum.color_rgba

    def set_full(self):
        self.state = self.FULL
        self.value = ""

    def set_empty(self):
        self.value = ""
        self.state = self.EMPTY
        self.color = "#FFFFFF00"

    def set_start(self, factor):
        self.state = self.START
        self.start_factor = factor
        self.end_factor = 1.0
        self.value = ""

    def set_end(self, factor):
        self.state = self.END
        self.start_factor = 0.0
        self.end_factor = factor
        self.value = ""

    def set_partial(self, start_factor, end_factor):
        self.state = self.PARTIAL
        self.start_factor = start_factor
        self.end_factor = end_factor
        self.value = ""

    def set_reverse_partial(self, start_factor, end_factor):
        self.state = self.REVERSE_PARTIAL
        self.start_factor = start_factor
        self.end_factor = end_factor
        self.value = ""

    @property
    def timestamp(self):
        if self.state == self.START:
            factor = self.start_factor
        elif self.state == self.END:
            factor = self.end_factor
        elif self.state == self.FULL:
            factor = 0
        elif self.state == self.EMPTY:
            return ""
        elif self.state == self.PARTIAL:
            return "{:0>2d}:{:0>2d} - {:0>2d}:{:0>2d}".format(self.hour, int(60 * self.start_factor),
                                                              self.hour, int(60 * self.end_factor))
        elif self.state == self.REVERSE_PARTIAL:
            return "{:0>2d}:{:0>2d} - {:0>2d}:{:0>2d}".format(self.hour, int(60 * self.start_factor),
                                                              self.hour, int(60 * self.end_factor))
        else:
            raise NotImplementedError

        return "{:0>2d}:{:0>2d}".format(self.hour, int(60 * factor))

    def render(self):
        style = ""
        attributes = ""
        if self.state == self.EMPTY:
            style = "background-color: {};".format(self.EMPTY_COLOR)
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
        elif self.state == self.REVERSE_PARTIAL:
            fill = self.end_factor - self.start_factor
            styles = [
                "border-left: none;",
                "background-color: {self.color};".format(self=self),
                "background-image: linear-gradient(to right, {self.BACKGROUND_COLOR} 0%, {self.BACKGROUND_COLOR} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-position: {}% 100%;".format(int(self.start_factor * 100)),
                "background-size: {}% 100%".format(int(fill * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)

        return '<td title="{}" class="day_cell" {}>{}</td>'.format(self.timestamp, attributes, self.value)
