def test_metadata(siffreaders):
    for siffreader in siffreaders:
        siffreader.get_experiment_timestamps()
        siffreader.get_epoch_timestamps_laser()
        siffreader.get_epoch_timestamps_system()
        siffreader.get_epoch_both()