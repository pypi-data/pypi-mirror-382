from norman_core.services.persist.accounts import Accounts
from norman_core.services.persist.invocation_flags import InvocationFlags
from norman_core.services.persist.invocations import Invocations
from norman_core.services.persist.model_bases import ModelBases
from norman_core.services.persist.model_flags import ModelFlags
from norman_core.services.persist.models import Models
from norman_core.services.persist.notifications import Notifications


class Persist:
    accounts = Accounts
    invocation_flags = InvocationFlags
    invocations = Invocations
    model_bases = ModelBases
    model_flags = ModelFlags
    models = Models
    notifications = Notifications


__all__ = ["Persist"]
