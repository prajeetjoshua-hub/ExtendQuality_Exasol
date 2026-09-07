# EXtendQuality connected phone camera

The primary event workflow exposes an Android phone to Windows 11 as a webcam.
The inspector controls capture and inspection entirely from the laptop dashboard.

## Requirements

- Windows 11 laptop
- Android 10 or later
- Link to Windows app on the phone
- Laptop and phone connected to Wi-Fi

Microsoft's current setup reference:
<https://support.microsoft.com/en-US/Windows/Apps/PhoneLink/manage-mobile-devices-in-windows>

## One-time Windows pairing

1. On the laptop open **Settings**.
2. Select **Bluetooth & devices**.
3. Select **Mobile devices**, then **Manage devices**.
4. Enable **Allow this PC to access your mobile devices**.
5. Select **Add device** and scan the displayed QR code with the Android phone.
6. Complete the Link to Windows permission prompts on the phone.
7. Under the linked phone, enable **Use as a connected camera**.
8. Keep the phone awake and near the laptop.

## EXtendQuality workflow

1. Start EXtendQuality on the laptop.
2. Open `http://localhost:3000/` on the laptop only.
3. Under **Camera source**, select the entry representing the connected phone.
   Camera names appear after the browser has received camera permission once.
4. Select a **Capture zoom** between 1x and 3x. This is a centre crop applied
   during capture; it is not optical zoom or additional sensor resolution.
5. Click **Start selected camera** on the laptop.
6. Accept the phone/Windows connected-camera notification if requested.
7. Position the phone above the bearing.
8. Click **Capture phone frame** on the laptop.
9. Confirm that the captured frame appears on the laptop.
10. Click **Run inspection** on the laptop.

The phone does not display the EXtendQuality dashboard. It acts only as the
connected camera device.

## Capture conditions

- Mount the phone with the rear camera facing directly downward.
- Use a plain, non-reflective surface.
- Fill roughly 65-80% of the captured frame with the complete bearing.
- Use diffuse lighting from both sides; avoid flash glare.
- Clean the camera lens.
- Keep distance, zoom, lighting, background and bearing orientation consistent.

## Safety behavior

Connected-camera images remain outside the validated prepared-image set. The
classifier exposes its three probabilities, but every usable camera capture is
forced to `REVIEW`. The class is evidence; the inspector is responsible for the
final accept/reject confirmation.

The internal model label `rust` is displayed as **surface condition (rust /
grease)** because the present dataset cannot separate corrosion from grease or
staining.

## Troubleshooting

- **Phone is missing in Camera source:** confirm **Use as a connected camera**
  is enabled, unlock the phone, click **Start selected camera** once to grant
  browser permission, then reselect the camera.
- **Browser camera permission is blocked:** Windows Settings > Privacy &
  security > Camera; enable camera access and desktop-app access.
- **Wrong camera starts:** stop it, select the phone under Camera source, and
  start again.
- **Phone disconnects:** keep both devices on Wi-Fi, keep Link to Windows active,
  unlock the phone, and reconnect before presenting.
- **Connected-camera feature is unavailable:** use the prepared real photographs
  for the primary demo. Do not install a new virtual-camera driver on event day.
