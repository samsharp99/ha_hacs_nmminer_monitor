# NMMiner Swarm

Home Assistant custom integration for polling an NMMiner/NerdMiner-style `/swarm` REST endpoint.

## HACS install from your GitHub repo

1. In Home Assistant, open HACS.
2. Open the three-dot menu and choose **Custom repositories**.
3. Paste your repository URL, for example:

   ```text
   https://github.com/samsharp99/ha_hacs_nmminer_monitor
   ```

4. Select **Integration** as the repository type.
5. Add it, then install **NMMiner Swarm** from HACS.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration → NMMiner Swarm**.

## Endpoint

Use either a full swarm URL:

```text
http://192.168.1.100/swarm
```

or a host/base URL:

```text
192.168.1.100
```

The integration appends `/swarm` automatically when needed.

A custom Home Assistant integration that polls an NMMiner/NerdMiner-style `swarm` REST endpoint and creates sensors for:

- Swarm summary:
  - total workers
  - total hash rate
  - best difficulty
- Each device:
  - hash rate
  - RSSI
  - free heap
  - valid shares
  - temperature, if available
  - best/pool/last/network difficulty

## Notes

- Hash rates like `993.22KH/s` and `1.9715M` are normalized to `H/s`.
- Difficulty values like `139.0T` and `480.5K` are normalized to plain numeric values.
- Device sensors are added dynamically when new IPs appear in the swarm response.
- If a device disappears from the response, its sensors remain but show unavailable values until it returns.
