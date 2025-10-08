import sys
import os
import time

import numpy as np
from matplotlib.pyplot import imshow, plot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import brimfile as brim

sync = brim.file_abstraction.sync
import asyncio
async def test():
    await asyncio.sleep(1)
    return 42
async def g():
    return await asyncio.gather(test(), test())
a, b = sync(asyncio.gather(test(), test()))

filename = r'/Users/bevilacq/Downloads/oil_beads_FTBM.brim.zip'
f = brim.File(filename)

# get the first data group in the file
d = f.get_data()

all_spectra, _, _, _ = d.get_PSD_as_spatial_map()

coord = (0, 3, 4)
spectrum, _, _, _ = d.get_spectrum_in_image(coord)
assert np.all(spectrum == all_spectra[coord])

# get the metadata 
md = d.get_metadata()
all_metadata = md.all_to_dict()


ar = d.get_analysis_results()

# get the image of the shift quantity for the average of the Stokes and anti-Stokes peaks
img, px_size = ar.get_image(brim.Data.AnalysisResults.Quantity.Shift, brim.Data.AnalysisResults.PeakType.average)

imshow(np.squeeze(img[0,...]))

#ar.save_image_to_OMETiff(brim.Data.AnalysisResults.Quantity.Shift, brim.Data.AnalysisResults.PeakType.average)

# get the spectrum in the image at a specific pixel (coord)
coord = (0, 3, 4)
start = time.perf_counter()
PSD, frequency, PSD_units, frequency_units = d.get_spectrum_in_image(coord)    
end = time.perf_counter()
print(f"Time to get spectrum in image: {(end - start)*1000:.2f} ms")

coord = (0, 3, 4)
start = time.perf_counter()
PSD, frequency, PSD_units, frequency_units = d.get_spectrum_in_image(coord)    
end = time.perf_counter()
print(f"Time to get spectrum in image: {(end - start)*1000:.2f} ms")

f.close()