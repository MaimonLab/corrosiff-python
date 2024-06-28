import numpy as np
import corrosiffpy

def test_read_frames(siffreaders):

    for siffreader in siffreaders:
        corrosiffpy.siff_to_tiff(
            siffreader.filename,
        ) 
        
        tiffreader = corrosiffpy.open_file(siffreader.filename.replace('.siff', '.tiff'))

        assert (
            tiffreader.get_frames()
            == siffreader.get_frames()
        ).all()
