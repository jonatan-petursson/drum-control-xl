from builtins import range
from future.moves.itertools import zip_longest
import Live

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ButtonElement import ON_VALUE, OFF_VALUE, Color
from _Framework.Util import find_if

from .Skin import Colors

import logging
logger = logging.getLogger(__name__)

# represent a single drum pad, assuming a single chain,
# allowing control of the chains volume, mute and solo
# as well as the chains first device's parameters
class DrumChainStripComponent(ControlSurfaceComponent):
    _chain = None
    _device = None
    _device_controls = []
    _device_component = None
    _volume_control = None

    _select_button = None
    _mute_button = None

    def __init__(self, *a, **k):
        super(DrumChainStripComponent, self).__init__(*a, **k)

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, "_%s_value" % name), "value")

        self._select_button_slot = make_button_slot("select")
        self._mute_button_slot = make_button_slot("mute")

        self._chain = None

    def set_chain(self, chain):
        self._chain = chain
        self._chain.add_devices_listener(self._on_devices_changed)
        self._chain.add_mute_listener(self._on_mute_changed)
        self._chain.canonical_parent.view.add_selected_drum_pad_listener(self._on_selected_drum_pad_changed)
        self._device = self._chain.devices[0] if self._chain else None

    def _on_devices_changed(self):
        self._device = self._chain.devices[0] if self._chain else None
        self._update_device_component()

    def _on_mute_changed(self):
        self.update_mute_lights()

    def update_mute_lights(self):
        if not self._mute_button:
            return

        if not self._chain:
            self._mute_button.send_value(Colors.DrumGroup.NoChain)
            return

        self._mute_button.send_value(Color(15) if self._chain.mute else Color(29))

    def _on_selected_drum_pad_changed(self):
        self.update_selected_lights()

    def update_selected_lights(self):
        if not self._select_button:
            return

        if not self._chain:
            self._select_button.send_value(Colors.DrumGroup.NoChain)
            return

        selected_drum_pad = self._chain.canonical_parent.view.selected_drum_pad
        selected_chain = None
        if selected_drum_pad.chains and len(selected_drum_pad.chains) > 0:
            selected_chain = selected_drum_pad.chains[0]

        if selected_chain and selected_chain == self._chain:
            self._select_button.send_value(Colors.DrumGroup.PadSelected)
        else:
            self._select_button.send_value(Colors.DrumGroup.PadUnselected)

    def set_volume_control(self, control):
        if self._volume_control:
            self._volume_control.release_parameter()
        self._volume_control = control
        self.update()

    def set_device_controls(self, controls):
        self._device_controls = controls
        self._create_device_component()

    def update(self):
        if self._chain:
            if self._volume_control:
                self._volume_control.release_parameter()
                self._volume_control.connect_to(self._chain.mixer_device.volume)
            self._update_device_component()

    def _create_device_component(self):
        if self._device:
            self._device_component = DeviceComponent(
                device_selection_follows_track_selection=False
            )
            self._update_device_component()
        else:
            self._device_component = None

    def _update_device_component(self):
        if self._device_component:
            self._device_component.set_lock_to_device(True, self._device)
            self._device_component.set_parameter_controls(self._device_controls)
            self._device_component.set_enabled(True)

    def _select_value(self, value):
        if self._chain != None and self._device:
            app = Live.Application.get_application()
            app.view.show_view('Detail')
            app.view.show_view('Detail/DeviceChain')

            drum_rack = self._chain.canonical_parent
            track = self._get_track_of_device(drum_rack)
            if track and self._select_button:
                self.song().view.selected_track = track
                drum_rack.view.selected_chain = self._chain

    def _mute_value(self, value):
        if self._chain and value:
            self._chain.mute = not self._chain.mute

    def _get_track_of_device(self, device):
        parent = device.canonical_parent
        while parent:
            if isinstance(parent, Live.Track.Track):
                return parent
            parent = parent.canonical_parent
        return None

    def set_select_button(self, button):
        if button != None:
            button.reset()

        self._select_button = button
        self._select_button_slot.subject = button

    def set_mute_button(self, button):
        if button != None:
            button.reset()

        self._mute_button = button
        self._mute_button_slot.subject = button

    def _get_all_controls(self):
        return self._volume_controls + self._pan_controls + self._send_controls

    def disconnect(self):
        if self._volume_control:
            self._volume_control.release_parameter()
        if self._device_component:
            self._device_component.disconnect()
        if self._chain:
            self._chain.remove_devices_listener(self._on_devices_changed)
            if hasattr(self._chain, 'canonical_parent') and self._chain.canonical_parent:
                self._chain.canonical_parent.view.remove_selected_drum_pad_listener(self._on_selected_drum_pad_changed)
        self._chain = None
        self._device = None
        self._device_controls = None
        self._device_component = None
        self._volume_control = None

        if self._select_button:
            self._select_button.send_value(0)
        self._select_button = None
        super(DrumChainStripComponent, self).disconnect()

class DrumGroupMixerComponent(ControlSurfaceComponent):
    _session = None
    _drum_group_device = None

    _volume_controls = []
    _device_controls = []
    _drum_strips = []

    _arm_button_slot = None
    _arm_button = None

    def __init__(self, *a, **k):
        super(DrumGroupMixerComponent, self).__init__(*a, **k)

        def make_button_slot(name):
            return self.register_slot(None, getattr(self, "_%s_value" % name), "value")

        self._arm_button_slot = make_button_slot("arm")

    def set_volume_controls(self, controls):
        self._release_controls(self._volume_controls)
        self._volume_controls = controls
        self.update()

    def set_device_controls(self, controls):
        self._release_controls(self._device_controls)

        if not self._drum_group_device:
            return

        controls_by_device = [[None, None, None] for _ in range(8)]

        for index, control in enumerate(controls):
            controls_by_device[index%8][index//8] = controls[index]

        drum_pads = self._drum_group_device.drum_pads
        drum_pads = sorted(drum_pads, key=lambda pad: pad.note)

        chains_in_note_order = []

        for pad in drum_pads:
            if pad.chains and len(pad.chains) > 0:
                chains_in_note_order.append(pad.chains[0])

        self._drum_strips = []
        for drum_chain in chains_in_note_order[:8]:
            drum_strip = DrumChainStripComponent()
            drum_strip.set_chain(drum_chain)
            self._drum_strips.append(drum_strip)

        for device_controls, volume_control, device in zip(controls_by_device, self._volume_controls, self._drum_strips):
            device.set_device_controls(device_controls)
            device.set_volume_control(volume_control)

        self.update()

    def set_session(self, session):
        self._session = session
        first_track = session.current_tracks[0]
        self._drum_group_device = self._find_drum_group_device(first_track)

        if self._drum_group_device:
            self._drum_group_device.canonical_parent.add_arm_listener(self._on_arm_changed)

    def _on_arm_changed(self):
        if not self._drum_group_device or not self._arm_button:
            return

        if not self._session:
            return

        if self._drum_group_device.canonical_parent.arm:
            self._arm_button.send_value(Color(127))
        else:
            self._arm_button.send_value(Color(0))

    def update(self):
        super(DrumGroupMixerComponent, self).update()

    def _find_drum_group_device(self, track_or_chain):
        instrument = find_if((lambda d: d.type == Live.Device.DeviceType.instrument), track_or_chain.devices)
        if instrument:
            if instrument.can_have_drum_pads:
                return instrument
            if instrument.can_have_chains:
                return find_if(bool, map(_find_drum_group_device, instrument.chains))

    def set_pad_select_buttons(self, buttons):
        if not self._drum_group_device:
            return

        for strip, button in zip_longest(self._drum_strips, buttons or []):
            if button:
                button.set_on_off_values("DrumGroup.PadSelected", "DrumGroup.PadUnselected")
            strip.set_select_button(button)

    def set_mute_buttons(self, buttons):
        if not self._drum_group_device:
            return

        for strip, button in zip_longest(self._drum_strips, buttons or []):
            if button:
                button.set_on_off_values("DrumGroup.MuteOn", "DrumGroup.MuteOff")
            strip.set_mute_button(button)

    def _release_controls(self, controls ):
         for control in controls:
            if control:
                control.release_parameter()

    def _get_all_controls(self):
        controls = self._device_controls
        if self._volume_controls:
            controls.extend(self._volume_controls)
        return controls

    def update_selected_lights(self):
        if not self._drum_group_device or not self._drum_strips:
            return

        for drum_strip in self._drum_strips:
            drum_strip.update_selected_lights()

    def update_mute_lights(self):
        if not self._drum_group_device or not self._drum_strips:
            return

        for drum_strip in self._drum_strips:
            drum_strip.update_mute_lights()

    def set_arm_button(self, button):
        if not self._drum_group_device or not self._arm_button_slot:
            return

        self._arm_button = button
        self._arm_button_slot.subject = button
        self._arm_button.set_on_off_values("DrumGroup.ArmSelected", "DrumGroup.ArmUnselected")

    def _arm_value(self, value):
        if not self._drum_group_device or not self._arm_button:
            return

        if value != 0:
            self._drum_group_device.canonical_parent.arm = not self._drum_group_device.canonical_parent.arm

    def disconnect(self):
        self._release_controls(self._get_all_controls())
        if self._drum_strips:
            for strip in self._drum_strips:
                strip.disconnect()
        self._drum_group_device = None
        self._drum_strips = None
        self._volume_controls = None
        self._pan_controls = None
        self._send_controls = None
        self._session = None
