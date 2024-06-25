def test_metadata(siffreader):
    assert (
        siffreader.get_experiment_timestamps()
    )

    assert (
        siffreader.get_epoch_timestamps_laser()
    )

    assert (
        siffreader.get_epoch_timestamps_system()
    )

    assert (
        siffreader.get_epoch_both()
    )
