# Image Unshredder
# Author: Derrick Pelletier

# This script takes an image that is shredded into uniform pieces and
# rearranged randomly. It will detect how wide the slices are and
# attempt to arrange them in proper order.

# This is my first Python script. It was done as quickly as possible
# for an Instagram Developer Challange. I'm likely missing some 
# Python best practices, or something.


from PIL import Image
import math
import sys

image = Image.open(sys.argv[1])
data = image.getdata()

width,height  = image.size
slice_count = 2
slice_width = width/slice_count
slices,ordered = [],[]
dif,max_dif = 100,20
last_slice = 2
left_candidate = None

# Comparison object used to define a comparison value to the left and right of another slice
class Comparison:
	def __init__(self, num = 0):
		self.i = num
		self.l,self.r = 100,100

# Slice object that defines the slice's index, and its comparisons to other Slices
class Slice:
	def __init__(self, num = 0):
		self.i = num
		self.comparisons = []
		self.lowest_on_left,self.lowest_on_right = None,None

# Get the gray pixel value at a specific location
def get_gray_pixel(x, y):
	width, height = image.size
	pixel = data[y * width + x]
	return 1 - (((pixel[0] / 255.0) * 0.2989) + ((pixel[1] / 255.0) * 0.587) + ((pixel[2] / 255.0) * 0.114))

# Compares two columns of pixels to see how similar they are.
# Each pixel is compared to its partner in the other column.
# The difference values are totalled and returned as a column-match-value
def get_col_difference(x1,x2):
	total,y = 0,0
	while y < height:
		total += math.fabs(get_gray_pixel(x1, y) - get_gray_pixel(x2,y))
		y += 1
	return total

def get_average_over_area(x1,x2):
	total = 0
	count = x2 - x1
	while x1 < x2:
		total += get_col_difference(x1,x1+1)
		x1 += 1
	return total / count

# END definitions

# BEGIN SCRIPT
# Scans the image, first testing for 2 slices, and then increasing the 
# slice count on each iteration until it finds a difference value that exceeds max_dif.
# This would presumably be an indication that it is a suitable slice.
check_slice = 2
while slice_width > 5:
	if width % check_slice == 0:
		avg = get_average_over_area(slice_width - 5, slice_width - 1)
		next = get_col_difference(slice_width - 1, slice_width)
		dif =  next - avg
		print(check_slice, next, avg)
		if dif > max_dif:
			slice_count = check_slice
	check_slice += 1
	slice_width = width / check_slice

print("slice_count", slice_count)
print("processing...")
if(slice_count <= 2 ):
	print("I'm sorry--I'm afraid I can't do that.")
	quit()

slice_width = width / slice_count

# Slice width found, now divides the image into Slices
count = 0
while count < slice_count:
	slices.append(Slice(count))
	count += 1

# Compare each slice to all other slices, both the left and the right sides.
for cur in slices:
	for against in slices:
		comp = Comparison(against.i)
		cur.comparisons.append(comp)
		comp.r += get_col_difference(cur.i*slice_width + slice_width -1, against.i * slice_width)
		comp.l += get_col_difference(cur.i*slice_width, against.i * slice_width + slice_width -1)

# Find the best matches for left and right sides of each slice
for cur in slices:	
	cur.lowest_on_left = cur.lowest_on_right = cur.comparisons[0]
	for edge in cur.comparisons:
		if edge != cur:
			if edge.l < cur.lowest_on_left.l:
				cur.lowest_on_left = edge
			if edge.r < cur.lowest_on_right.r:
				cur.lowest_on_right = edge

# This will loop through and find an instance where two objects have the same lowest_on_left
# Because there is a duplicate, one is presumably incorrect and would be the left-most-slice.
for first in slices:
	for second in slices:
		if first.i != second.i and first.lowest_on_left.i == second.lowest_on_left.i:
			left_candidate = second if first.lowest_on_left.l < second.lowest_on_left.l else first

# Begin a new array with the left-most-candidate first
# Place the lowest_on_right slice of each subsequent addition
ordered.append(left_candidate)
while len(ordered) < slice_count:
	last = ordered[len(ordered) - 1]
	wants = slices[last.lowest_on_right.i]	
	found = None
	if wants.lowest_on_left.i != last.i:
		for s in slices:
			if s.lowest_on_left.i == last.i:
				found = s
	ordered.append(found if found != None else wants)

# Generate a new image based on newly ordered slices.
# Cross fingers. Hold breath. Open 'unshredded.jpg'. Exhale.
unshredded = Image.new("RGBA", image.size)
count = 0
for s in ordered:
	x1, y1 = s.i * slice_width, 0
	x2, y2 = x1 + slice_width, height
	source_region = image.crop([x1, y1, x2, y2])
	destination_point = (count * slice_width, 0)
	unshredded.paste(source_region, destination_point)
	count = count + 1

unshredded.save("unshredded.png", "PNG")
print("Cross fingers. Hold breath. Open 'unshredded.png'")
print("Exhale.")