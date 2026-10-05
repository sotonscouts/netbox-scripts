import re

from dcim.models import Device
from extras.scripts import Script


class HostnameValidationScript(Script):
    name = "Validate Device Hostnames"
    description = "Checks if all hostnames match our format."

    def test_hostname_format(self):
        devices = Device.objects.select_related("site", "role").all()

        for device in devices:
            site = device.site
            role = device.role

            if not site or not role:
                self.log_warning(
                    f"Device '{device.name}' is missing a Site or Role assignment.",
                    obj=device,
                )
                continue

            site_slug = site.custom_field_data.get("hostname_slug")
            role_slug = role.custom_field_data.get("hostname_slug")

            if not site_slug or not role_slug:
                self.log_warning(
                    f"Skipped '{device.name}': Missing 'hostname_slug' on "
                    f"Site ({site.name}) or Role ({role.name}).",
                    obj=device,
                )
                continue

            # Construct the expected prefix and build a dynamic regex pattern
            expected_prefix = f"{role_slug}-{site_slug}"
            pattern = re.compile(rf"^{re.escape(expected_prefix)}(?:-[a-z0-9\-]+)?$")

            hostname = device.name

            if not pattern.match(hostname):
                self.log_failure(
                    f"Device '{hostname}' is invalid. "
                    f"Expected format starting with '{expected_prefix}'.",
                    obj=device,
                )
            else:
                self.log_success(f"Device '{hostname}' is valid.", obj=device)
