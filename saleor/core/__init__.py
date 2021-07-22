class JobStatus:
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DELETED = "deleted"

    CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
        (DELETED, "Deleted"),
    ]


class TimePeriodType:
    DAY = "day"
    MONTH = "month"
    YEAR = "year"

    CHOICES = [(DAY, "day"), (MONTH, "Month"), (YEAR, "Year")]
