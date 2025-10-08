from dataclasses import dataclass


@dataclass(frozen=True)
class ToucanConfig:
    """
    Class to define the mandatory fields in the config.yml files.

    :param alice: The emulator for Alice
    :param bob: The emulator for Bob
    :param use_snapshots: If True, saves snapshots after starting the emulators
    :param debug_snapshot_name: The name of the snapshots of the emulators
    :param wait_time: The maximum number of seconds to wait for booting of the emulators
    """

    alice: str
    bob: str
    use_snapshots: bool
    debug_snapshot_name: str
    wait_time: int

    def __post_init__(self):
        if not self.alice:
            raise ValueError('alice should be present and filled in the config file.')
        if not self.bob:
            raise ValueError('bob should be present and filled in the config file.')
        if self.use_snapshots is None:
            raise ValueError('use_snapshots should be present and filled in the config file.')
        if not self.debug_snapshot_name:
            raise ValueError('debug_snapshot_name should be present and filled in the config file.')
        if self.wait_time is None:
            raise ValueError('wait_time should be present and filled in the config file.')
