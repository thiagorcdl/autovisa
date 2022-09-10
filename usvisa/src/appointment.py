import datetime


class Appointment:
    """Class to represent an appointment date, time and location."""
    city = None
    date = None
    time = None

    def __init__(self, day, month, year, time, city):
        self.city = city
        self.date = datetime.date(year, month, day)
        self.time = time

    def __repr__(self):
        return f"{self.date_repr} {self.time} in {self.city}"

    @property
    def date_repr(self):
        """Return formatted date."""
        return self.date.strftime("%Y-%m-%d") if self.date else "<No date>"
