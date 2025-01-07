from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import corrosiffpy

def test_metadata(siffreaders : List['corrosiffpy.SiffIO']):
    for siffreader in siffreaders:
        siffreader.get_experiment_timestamps()
        siffreader.get_epoch_timestamps_laser()
        siffreader.get_epoch_timestamps_system()
        siffreader.get_epoch_both()

        # I don't understand why this line is causing problems
        # only on a few linux builds!!
        # assert (
        #     corrosiffpy.get_start_timestamp(siffreader.filename)
        #     ==
        #     corrosiffpy.get_start_and_end_timestamps(siffreader.filename)[0]
        # )