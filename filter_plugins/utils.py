from re import sub as regex_replace

MIKROTIK_MAC_PREFIX = 'C4:AD:34:00'


class FilterModule(object):
    def filters(self):
        return {
            "generate_mikrotik_mac_address": self.generate_mikrotik_mac_address,
            "filter_ap_by_name": self.filter_ap_by_name,
            "any_package_missing": self.any_package_missing,
        }

    @staticmethod
    def generate_mikrotik_mac_address(ap_name: str) -> str:
        # append the ap nr (should be fixed) to a mikrotik mac-prefix
        ap_nr = regex_replace(r'[^0-9]+', '', ap_name)
        if len(ap_nr) == 1:
            ap_nr = f'000{ap_nr}'

        elif len(ap_nr) == 2:
            ap_nr = f'00{ap_nr}'

        elif len(ap_nr) == 3:
            ap_nr = f'0{ap_nr}'

        elif len(ap_nr) > 4:
            ap_nr = ap_nr[-4:]

        return f"{MIKROTIK_MAC_PREFIX}:{ap_nr[0:2]}:{ap_nr[2:]}"

    @staticmethod
    def filter_ap_by_name(ap_name: str, filter_names: list) -> bool:
        for filter_name in filter_names:
            if ap_name.find(filter_name) != -1:
                return True

        return False

    @staticmethod
    def any_package_missing(existing: str, wanted: list) -> bool:
        for pkg in wanted:
            if existing.find(pkg) == -1:
                return True

        return False
