CURRENCY_UNITS = (
    ('Dollar', 'Dollar'),
    ('INR', 'INR'),
)

REPORT_STATUS_CHOICES = (
    ('1', 'Complete'),
    ('2', 'Incomplete'),
    ('3', 'Error'),
)

report_status_choices_dict = {
    "1": "Complete",
    "2": "Incomplete",
    "3": "Error"
}

target_classes = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
