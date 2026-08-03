from .devices import TrackingDevices
from .captures import IndividualCaptures, IndividualsCaptureObservations, CorRoleCapture
from .deployments import IndividualDeployments
from .individuals import register_individual_extensions

IndividualDeployments.register_individual_backref()
register_individual_extensions()

# __all__ = [
#     "TrackingDevices",
#     "IndividualDeployments",
# ]
