# Ansible Role - OpenWRT Access Points

**WARNING**: Make sure to test the role on single Access Points before mass-managing them! There might be hardware-specific special-cases.

This role utilizes the [OpenWRT UCI command-line interface](https://openwrt.org/docs/guide-user/base-system/uci) to interact with the configuration. This provides a basic validation.

Feel free to point out problems and possible issues in the [Repository issues](https://github.com/NiceRath/ansible-openwrt-ap/issues/new).

----

## Prerequisites

If you want to configure a factory-default AP - you will have to set its hostname before managing it:

```bash
uci set system.system=system
uci set system.system.hostname=<HOSTNAME>
uci set system.@system[0].hostname=<HOSTNAME>
uci commit system
```

----

## Config

See [the defaults](https://github.com/NiceRath/ansible-openwrt-ap/blob/main/defaults/main.yml) for all options.

This config assumes:

* The untagged network is the management interface
* The management interface has only DHCP (IPv4) enabled
* You will not change the WLAN-ID `wid`

```yaml
PREFIX_NET: 'lan_'
PREFIX_BR: 'br-'

openwrt:
  ssh_port: 9822

  pkg:
    install:
      - 'openwisp-monitoring'

    uninstall:
      - 'zabbix-extra-wifi'

  system_settings:  # see: https://openwrt.org/docs/guide-user/base-system/system_configuration
    log_ip: '192.168.0.1'  # syslog server
    zonename: 'Europe/Vienna'
    timezone: 'CET-1CEST,M3.5.0,M10.5.0/3'  # see: https://github.com/openwrt/luci/blob/master/modules/luci-lua-runtime/luasrc/sys/zoneinfo/tzdata.lua

  radio_settings:
    all:
      country: 'AT'

  vlans:
    - vid: 59
      name: 'intern'
      device: 'vlan59'
      interface: "{{ PREFIX_NET }}intern"
      bridge: "{{ PREFIX_BR }}intern"

    - vid: 61
      name: 'iot'
      device: 'vlan61'
      interface: "{{ PREFIX_NET }}iot"
      bridge: "{{ PREFIX_BR }}iot"

    - vid: 65
      name: 'guest'
      device: 'vlan65'
      interface: "{{ PREFIX_NET }}guest"
      bridge: "{{ PREFIX_BR }}guest"

  wlans:
    - network: "{{ PREFIX_NET }}intern"
      wid: 'intern'
      ssid: 'SuperWIFI'
      key: !vault |
        ...
      filter_by_name: [ # only add wlan to aps matching one of these sub-strings
        'office',
      ]

      fast_roaming: true

    - network: "{{ PREFIX_NET }}iot"
      wid: 'iot'
      state_5g: 'absent'
      ssid: 'IOT'
      key: !vault |
        ...

      # special config - all options are supported: https://openwrt.org/docs/guide-user/network/wifi/basic
      encryption: 'psk2+tkip+ccmp'
      hidden: '0'

    - network: "{{ PREFIX_NET }}guest"
      wid: 'guest'
      filter_by_not_name: [ # only add wlan to aps NOT matching one of these sub-strings
        'wh',
      ]
      ssid: 'GuestWIFI'
      key: !vault |
        ...

    # remove legacy wlan
    - network: 'some-legacy'
      ssid: 'Legacy'
      wid: 'some-legacy'
      filter_by_name: ['NONE']  # remove on all aps - legacy
```

You might want to use 'ansible-vault' to encrypt the secrets: `ansible-vault encrypt_string 'YOUR-SECRET'`

----

## Result

These are prettified outputs.

```bash
AP# uci show network
## mgmt interface
> network.device1=device
> network.device1.bridge_empty='1'
> network.device1.ipv6='0'
> network.device1.multicast='0'
> network.device1.name='br-lan'
> network.device1.ports='eth0'
> network.device1.rpfilter='loose'
> network.device1.sendredirects='0'
> network.device1.type='bridge'
> network.lan=interface
> network.lan.device='br-lan'
> network.lan.proto='dhcp'
> network.lan.delegate='0'
> network.lan.force_link='1'
> ## vlan bridges
> network.lan_intern=interface
> network.lan_intern.proto='none'
> network.lan_intern.device='br-intern'
> network.lan_intern.defaultroute='0'
> network.lan_intern.peerdns='0'
> network.lan_intern.delegate='0'
> network.lan_iot=interface
> network.lan_iot.proto='none'
> network.lan_iot.device='br-iot'
> network.lan_iot.defaultroute='0'
> network.lan_iot.peerdns='0'
> network.lan_iot.delegate='0'
> network.lan_guest=interface
> network.lan_guest.proto='none'
> network.lan_guest.device='br-guest'
> network.lan_guest.defaultroute='0'
> network.lan_guest.peerdns='0'
> network.lan_guest.delegate='0'
> ## vlans
> network.vlan59=device
> network.vlan59.name='br-intern'
> network.vlan59.ports='eth0.59'
> network.vlan59.ipv6='0'
> network.vlan59.multicast='0'
> network.vlan59.sendredirects='0'
> network.vlan59.bridge_empty='1'
> network.vlan59.type='bridge'
> network.vlan61=device
> network.vlan61.name='br-iot'
> network.vlan61.ports='eth0.61'
> network.vlan61.ipv6='0'
> network.vlan61.multicast='0'
> network.vlan61.sendredirects='0'
> network.vlan61.bridge_empty='1'
> network.vlan61.type='bridge'
> network.vlan65=device
> network.vlan65.name='br-guest'
> network.vlan65.ports='eth0.65'
> network.vlan65.ipv6='0'
> network.vlan65.multicast='0'
> network.vlan65.sendredirects='0'
> network.vlan65.bridge_empty='1'
> network.vlan65.type='bridge'

AP# uci show wireless
> ## radio 5GHz
> wireless.radio0=wifi-device
> wireless.radio0.type='mac80211'
> wireless.radio0.path='pci0000:00/0000:00:00.0'
> wireless.radio0.band='5g'
> wireless.radio0.country='AT'
> wireless.radio0.country_ie='1'
> wireless.radio0.channel='auto'
> wireless.radio0.disabled='0'
> wireless.radio0.htmode='VHT40'
> wireless.radio0.cell_density='1'
> wireless.radio0.beacon_int='100'
> wireless.radio0.log_level='2'
> wireless.radio0.channels='100-140'
> ## radio 2.4GHz
> wireless.radio1=wifi-device
> wireless.radio1.type='mac80211'
> wireless.radio1.path='platform/ahb/18100000.wmac'
> wireless.radio1.band='2g'
> wireless.radio1.country='AT'
> wireless.radio1.country_ie='1'
> wireless.radio1.channel='auto'
> wireless.radio1.disabled='0'
> wireless.radio1.htmode='HT20'
> wireless.radio1.cell_density='1'
> wireless.radio1.beacon_int='200'
> wireless.radio1.log_level='2'
> wireless.radio1.channels='1 6 11 13'
> ## wlans
> ### intern 5GHz
> wireless.intern5=wifi-iface
> wireless.intern5.device='radio0'
> wireless.intern5.mode='ap'
> wireless.intern5.ssid='SuperWIFI'
> wireless.intern5.isolate='1'
> wireless.intern5.key='<SECRET>'
> wireless.intern5.ieee80211r='1'
> wireless.intern5.ft_psk_generate_local='1'
> wireless.intern5.network='lan_intern'
> wireless.intern5.encryption='psk2+aes'
> wireless.intern5.mobility_domain='1111'
> wireless.intern5.reassociation_deadline='20000'
> wireless.intern5.ieee80211w='0'
> wireless.intern5.wmm='0'
> wireless.intern5.disabled='0'
> wireless.intern5.wpa_group_rekey='3600'
> wireless.intern5.pmk_r1_push='1'
> wireless.intern5.max_inactivity='3600'
> wireless.intern5.disassoc_low_ack='0'
> wireless.intern5.bss_transition='1'
> wireless.intern5.ieee80211k='1'
> wireless.intern5.time_advertisement='2'
> wireless.intern5.wpa_disable_eapol_key_retries='1'
> wireless.intern5.rrm_neighbor_report='1'
> wireless.intern5.rrm_beacon_report='1'
> wireless.intern5.ieee80211v='1'
> wireless.intern5.wnm_sleep_mode='0'
> ### intern 2.4GHz
> wireless.intern2=wifi-iface
> wireless.intern2.device='radio1'
> wireless.intern2.mode='ap'
> wireless.intern2.ssid='SuperWIFI'
> wireless.intern2.isolate='1'
> wireless.intern2.key='<SECRET>'
> wireless.intern2.ieee80211r='1'
> wireless.intern2.ft_psk_generate_local='1'
> wireless.intern2.network='lan_intern'
> wireless.intern2.encryption='psk2+aes'
> wireless.intern2.mobility_domain='1111'
> wireless.intern2.reassociation_deadline='20000'
> wireless.intern2.ieee80211w='0'
> wireless.intern2.wmm='0'
> wireless.intern2.disabled='0'
> wireless.intern2.wpa_group_rekey='3600'
> wireless.intern2.pmk_r1_push='1'
> wireless.intern2.max_inactivity='3600'
> wireless.intern2.disassoc_low_ack='0'
> wireless.intern2.bss_transition='1'
> wireless.intern2.ieee80211k='1'
> wireless.intern2.time_advertisement='2'
> wireless.intern2.wpa_disable_eapol_key_retries='1'
> wireless.intern2.rrm_neighbor_report='1'
> wireless.intern2.rrm_beacon_report='1'
> wireless.intern2.ieee80211v='1'
> wireless.intern2.wnm_sleep_mode='0'
> ### iot 2.4GHz
> wireless.iot2=wifi-iface
> wireless.iot2.device='radio1'
> wireless.iot2.mode='ap'
> wireless.iot2.ssid='IOT'
> wireless.iot2.isolate='1'
> wireless.iot2.key='<SECRET>'
> wireless.iot2.ft_psk_generate_local='1'
> wireless.iot2.network='lan_iot'
> wireless.iot2.encryption='psk2+tkip+ccmp'
> wireless.iot2.ieee80211w='0'
> wireless.iot2.wmm='0'
> wireless.iot2.disabled='0'
> wireless.iot2.wpa_group_rekey='3600'
> wireless.iot2.max_inactivity='3600'
> wireless.iot2.disassoc_low_ack='0'
> wireless.iot2.bss_transition='1'
> wireless.iot2.ieee80211k='1'
> wireless.iot2.time_advertisement='2'
> wireless.iot2.wpa_disable_eapol_key_retries='1'
> wireless.iot2.rrm_neighbor_report='1'
> wireless.iot2.rrm_beacon_report='1'
> wireless.iot2.ieee80211v='1'
> wireless.iot2.wnm_sleep_mode='0'
> ### guest 5GHz
> wireless.guest5=wifi-iface
> wireless.guest5.device='radio0'
> wireless.guest5.mode='ap'
> wireless.guest5.ssid='GuestWIFI'
> wireless.guest5.isolate='1'
> wireless.guest5.key='<SECRET>'
> wireless.guest5.ft_psk_generate_local='1'
> wireless.guest5.network='lan_guest'
> wireless.guest5.encryption='psk2+aes'
> wireless.guest5.ieee80211w='0'
> wireless.guest5.wmm='0'
> wireless.guest5.disabled='0'
> wireless.guest5.wpa_group_rekey='3600'
> wireless.guest5.max_inactivity='3600'
> wireless.guest5.disassoc_low_ack='0'
> wireless.guest5.bss_transition='1'
> wireless.guest5.ieee80211k='1'
> wireless.guest5.time_advertisement='2'
> wireless.guest5.wpa_disable_eapol_key_retries='1'
> wireless.guest5.rrm_neighbor_report='1'
> wireless.guest5.rrm_beacon_report='1'
> wireless.guest5.ieee80211v='1'
> wireless.guest5.wnm_sleep_mode='0'
> ### guest 2.4GHz
> wireless.guest2=wifi-iface
> wireless.guest2.device='radio1'
> wireless.guest2.mode='ap'
> wireless.guest2.ssid='GuestWIFI'
> wireless.guest2.isolate='1'
> wireless.guest2.key='<SECRET>'
> wireless.guest2.ft_psk_generate_local='1'
> wireless.guest2.network='lan_guest'
> wireless.guest2.encryption='psk2+aes'
> wireless.guest2.ieee80211w='0'
> wireless.guest2.wmm='0'
> wireless.guest2.disabled='0'
> wireless.guest2.wpa_group_rekey='3600'
> wireless.guest2.max_inactivity='3600'
> wireless.guest2.disassoc_low_ack='0'
> wireless.guest2.bss_transition='1'
> wireless.guest2.ieee80211k='1'
> wireless.guest2.time_advertisement='2'
> wireless.guest2.wpa_disable_eapol_key_retries='1'
> wireless.guest2.rrm_neighbor_report='1'
> wireless.guest2.rrm_beacon_report='1'
> wireless.guest2.ieee80211v='1'
> wireless.guest2.wnm_sleep_mode='0'
```

----

## Troubleshooting

### Mac-Address randomized on reboot

This is [a known issue](https://forum.openwrt.org/t/mac-address-changing-automatically-why/122037) with some hardware.

It seems OpenWRT is not able to pull the hardware's mac-address config.

In this case you will have to set the mac-addresses manually.

Per example - use the unique hostname digits in it: [filter-plugin](https://github.com/NiceRath/ansible-openwrt-ap/blob/main/filter_plugins/utils.py#L15) & [filter-plugin](https://github.com/NiceRath/ansible-openwrt-ap/blob/main/tasks/hw_mikrotik_wap.yml) 

### Failed with `Unreachable` on some Task

This might happen if the existing configuration is not compatible with the one set by this command.

To debug this behavior you can manually execute the `uci` command or manually remove legacy config.
