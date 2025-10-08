from typing import List, Dict

from pydantic import BaseModel


class AttributeNames(BaseModel):
    """Attribute names used inside case details."""

    context: List[str] = []
    query: List[str] = []
    response: List[str] = []


class SessionConfig(BaseModel):
    """Evaluation session configuration.

    `show_responses` - if `False` the `response` case detail
    won't be shown during the evaluation.

    `allow_user_evaluations` - if `True` the evaluator will
    be able to add evaluations to the cases during the evaluation.

    `submitters_disabled_fields` - case details with included
    attribute names won't be displayed to the evaluator during the
    evaluation. Session submitters configuration type. Attribute
    names used by submitters' cases. First level dictionary keys
    are submitter names and second level dictionary keys are
    submitter versions.

    `allow_reevaluations` - if `True` case workers are permitted
    to reevaluate cases in this session. If `False`, case workers
    are blocked from evaluating cases that are finised across any
    instance of the session.
    """

    show_responses: bool = True
    allow_user_evaluations: bool = True
    submitters_disabled_fields: Dict[str, Dict[str, AttributeNames]] = {}
    allow_reevalutations: bool = True
