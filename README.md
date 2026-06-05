# NMMiner Swarm

Home Assistant custom integration for polling an NMMiner/NerdMiner-style `/swarm` REST endpoint.

## HACS install from your GitHub repo

1. Push this repository to GitHub.
2. In Home Assistant, open HACS.
3. Open the three-dot menu and choose **Custom repositories**.
4. Paste your repository URL, for example:

   ```text
   https://github.com/YOUR_USERNAME/nmminer_swarm
   ```

5. Select **Integration** as the repository type.
6. Add it, then install **NMMiner Swarm** from HACS.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add integration → NMMiner Swarm**.

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

## Install

Copy this folder:

```text
custom_components/nmminer_swarm
```

into your Home Assistant config directory:

```text
/config/custom_components/nmminer_swarm
```

Restart Home Assistant.

Then go to:

```text
Settings → Devices & services → Add integration → NMMiner Swarm
```

Use either a full swarm URL:

```text
http://192.168.1.100/swarm
```

or a host/base URL:

```text
192.168.1.100
```

The integration appends `/swarm` automatically when needed.

## Notes

- Hash rates like `993.22KH/s` and `1.9715M` are normalized to `H/s`.
- Difficulty values like `139.0T` and `480.5K` are normalized to plain numeric values.
- Device sensors are added dynamically when new IPs appear in the swarm response.
- If a device disappears from the response, its sensors remain but show unavailable values until it returns.
