from pydantic import BaseModel

class Activity(BaseModel):
    """Base schema for any activity.

    Attributes:
        activity_type (str): The type of activity being performed.
    """
    activity_type: str
