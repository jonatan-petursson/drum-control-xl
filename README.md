# drum-control-xl
Ableton drum rack control surface script for the Launch Control XL mk2

## Features

A control script that turns the Launch Control XL mk2 into a drum rack mixer, allowing you to control the volumes and first 3 parameters of 8 pads in a drum rack. Great fun for live performances, turns Ableton into something much closer to a groovebox. Can be moved from track to track as needed using the track selection buttons.

- Control volume for each pad
- Control top 3 parameters for each pad
- Select focused drum pad
- Mute/Unmute drum pads

## State

I'd say this is beta, it's pretty stable and works well for me as long as you don't change the drum rack around a lot. In case of device mappings not updating correctly when changing the devices, you should try selecting the next track and then the previous track to refresh all the mappings.

## Todo

- [ ] Add support for the mode switches
- [ ] Add configuration
- [ ] Add drum pad offset, so you can extend using multiple Launch Controls
- [ ] Improve handling of drum rack changes, decrease need for manual refresh

## Quick Install

macOS:

Copy and paste the following command into your terminal:

```
curl -fsSL https://raw.githubusercontent.com/jonatan-petursson/drum-control-xl/main/installer/fetch-and-install.sh | bash
```

## Manual installation

### Step 1: Download the Latest Release

1. Go to the [Releases page](https://github.com/jonatan-petursson/drum-control-xl/releases) of this repository
2. Download the latest `Drum_Control_XL.zip` file from the most recent release

### Step 2: Install the Script

Extract the downloaded zip file and copy the `Drum_Control_XL` folder to your Ableton Live MIDI Remote Scripts directory:

#### Windows
```
C:\ProgramData\Ableton\Live [version]\Resources\MIDI Remote Scripts\
```

#### macOS
```
/Applications/Ableton Live [version].app/Contents/App-Resources/MIDI Remote Scripts/
```

**Note:** Replace `[version]` with your Ableton Live version (e.g., "12 Suite", "11 Standard", etc.)

### Step 3: Enable the Script in Ableton Live

1. Open Ableton Live
2. Go to **Live > Preferences** (macOS) or **Options > Preferences** (Windows/Linux)
3. Select the **Link/Tempo/MIDI** tab
4. In the **Control Surface** section, select "Drum Control XL" from the dropdown
5. Set the appropriate Input and Output ports for your Launch Control XL
6. Close the Preferences window

Your Launch Control XL should now be configured to control Ableton's drum racks!
