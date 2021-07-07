# crop_scanned_photos

Script that crops scanned photos

## Requirements

Needs the libraries `getopt` and `PIL`


## Usage

```
python extract.py -i <input image>
```


## Example

This is an example of multiple scanned images 

<img src="example/sample.jpg" width=30% height=30%>

The output of the following command is
```
python extract.py -i example/sample.jpg
```

<img src="example/sample_0.jpg" width=15% height=15%>
<img src="example/sample_1.jpg" width=15% height=15%>
<img src="example/sample_2.jpg" width=15% height=15%>
<img src="example/sample_3.jpg" width=15% height=15%>
<img src="example/sample_4.jpg" width=15% height=15%>


## Options:

* `-i`  Name of the input image
* `-f, --freq` Percentage of the pixels scanned. Default 0.05
* `--min_len` Subimages have a minimum length on each axis. Default 100
* `--min_area` Subimages have a fraction of the original area . Default 0.1
* `--min_entropy` Subimages have a fraction of the original entropy . Default 0.8
* `--pos_x` Position in the x axis to find the height of the picture. Default 0.5
* `--pos_y` Position in the y axis to find the width of the picture. Default 0.5
* `--conf_lvl` Confidence level to distinguish an image from the background. Default 0.6
* `--thld_bg` Threshold to distinguish a photo's  pixel from the background. Default 6


## Notes

The script assumes that the photos are rectangles aligned with the edges (thus, the photos aren't rotated). In the example I aligned the photos with the edge of the scanner.

The script scans a fraction of the pixels (defined by `-freq`) to identify pixels that don't match the background. When this happens, the script first traverses the image horizontally to estimate the width of a photo. Then it traverses the image vertically to estimate it's height. With these values the script traverses the image again to make sure that it detects the borders and then crops the final image.

The parameter `--posx` determines the position in the x-axis to traverse vertically. With `--posx` closer to zero it traverses the photo closer to the right side, while a value closer to 1 instructs a traverse close to the left side. The parameter `--posy` is analogous on the y-axis. One can use these parameters to avoid traversing an image on regions with white color, which may be interpreted as the background.

A pixel is considered part of the background if its average RGB value (computed using adjacent nodes) is lower than 255 - `--thld_bg`. 

`--conf_lvl` is used to distinguish the photos from the background. This is used to find the borders of an image.

The parameters `--min_len`, `--min_area`, and `--min_entropy` are useful to discard images that are too small or that do not resemble the original image.


