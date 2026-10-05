from dcim.models import Device
from django.db import models
from extras.scripts import Script


class RouterValidationScript(Script):
    name = "Check Router Config"

    def _get_routers(self) -> models.QuerySet[Device]:
        return Device.objects.filter(role__name__icontains="router")

    def _assert(self, condition: bool, message: str, obj: models.Model) -> None:
        if not condition:
            self.log_failure(message, obj=obj)

    def test_has_loopback_interface(self):
        routers = self._get_routers()

        for router in routers:
            try:
                loopback_interface = router.interfaces.get(name="lo")
            except Device.interfaces.RelatedObjectDoesNotExist:
                self.log_failure(
                    "Missing loopback interface.",
                    obj=router,
                )
            else:
                self._assert(
                    loopback_interface.enabled,
                    "Loopback interface is not enabled.",
                    obj=router,
                )
                self._assert(
                    loopback_interface.ip_addresses.exists(),
                    "Loopback interface has no IP address assigned.",
                    obj=router,
                )
                self._assert(
                    loopback_interface.type == "virtual",
                    "Loopback interface is not of type 'virtual'.",
                    obj=router,
                )
                self._assert(
                    not loopback_interface.untagged_vlan.exists(),
                    "Loopback interface has VLANs assigned.",
                    obj=router,
                )
                self._assert(
                    not loopback_interface.tagged_vlans.exists(),
                    "Loopback interface has VLANs assigned.",
                    obj=router,
                )
