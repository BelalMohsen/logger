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

    def set_span_end(self, cell_index):
        cells_to_update = []
        start = end = None
        for cell in reversed(self[:cell_index + 1]):
            if cell.state == TableCell.START:
                cells_to_update.append(cell)
                start = cell.start_timestamp
                break
            elif cell.state == TableCell.PARTIAL:
                cells_to_update.append(cell)
                start = cell.start_timestamp
                end = cell.end_timestamp
                break
            elif cell.state == TableCell.FULL:
                cells_to_update.append(cell)
                if cell.hour == 23:
                    end = cell.end_timestamp
            elif cell.state == TableCell.END:
                cells_to_update.append(cell)
                end = cell.end_timestamp
            elif cell.state == TableCell.EMPTY:
                break
            elif cell.state == TableCell.REVERSE_PARTIAL:
                cells_to_update.append(cell)
                start = cell.end_timestamp
                break
            else:
                raise NotImplementedError

        delta = end - start

        delta_str = format_timedelta(delta, use_days=False)

        title = "{} - {} ({})".format(start.strftime("%H:%M:%S"), end.strftime("%H:%M:%S"), delta_str)

        for cell in cells_to_update:
            cell.title = title


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
        self.start_timestamp = None
        self.end_timestamp = None
        self.start_factor = 0.0
        self.end_factor = 0.0
        self.color = datum.color_rgba
        self.title = "NO TITLE"

    def set_full(self):
        self.state = self.FULL
        self.value = ""

    def set_empty(self):
        self.value = ""
        self.state = self.EMPTY
        self.color = "#FFFFFF00"

    def set_start(self, timestamp):
        self.state = self.START
        self.start_timestamp = timestamp
        self.start_factor = timestamp.minute / 60
        self.end_timestamp = None
        self.end_factor = 1.0
        self.value = ""

    def set_end(self, timestamp):
        self.state = self.END
        self.start_timestamp = None
        self.start_factor = 0.0
        self.end_factor = timestamp.minute / 60
        self.end_timestamp = timestamp
        self.value = ""

    def set_partial(self, start_timestamp, end_timestamp):
        self.state = self.PARTIAL
        self.start_factor = start_timestamp.minute / 60
        self.end_factor = end_timestamp.minute / 60
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.value = ""

    def set_reverse_partial(self, start_timestamp, end_timestamp):
        self.state = self.REVERSE_PARTIAL
        self.start_factor = start_timestamp.minute / 60
        self.end_factor = end_timestamp.minute / 60
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.value = ""

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
                "background-image: linear-gradient(to right, {self.BACKGROUND_COLOR} 0%, {self.BACKGROUND_COLOR} 100%);".format(
                    self=self),
                "background-repeat: no-repeat;",
                "background-position: {}% 100%;".format(int(self.start_factor * 100)),
                "background-size: {}% 100%".format(int(fill * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)

        return '<td title="{}" class="day_cell" {}>{}</td>'.format(self.title, attributes, self.value)
