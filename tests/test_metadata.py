import corrosiffpy

def test_metadata(siffreaders):
    for siffreader in siffreaders:
        siffreader.get_experiment_timestamps()
        siffreader.get_epoch_timestamps_laser()
        siffreader.get_epoch_timestamps_system()
        siffreader.get_epoch_both()

        assert (
            corrosiffpy.get_start_timestamp(siffreader.filename)
            ==
            corrosiffpy.get_start_and_end_timestamps(siffreader.filename)[0]
        )