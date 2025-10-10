from dataclasses import dataclass

@dataclass(frozen=True)
class BSDate:
    year: int
    month: int
    day: int
    def __str__(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
