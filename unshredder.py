# This script just unshreds an image that is 640 x 359 and has 20 slices.
from PIL import Image
import math
image = Image.open("shredded.jpg")
data = image.getdata()

slice_width = 32
width,height  = image.size
slice_count = 20
slices,ordered = [],[]

class Comparison:
	def __init__(self, num = 0):
		self.i = num
		self.l,self.r = 100,100
		
class Slice:
	def __init__(self, num = 0):
		self.i = num
		self.comparisons = []
		self.lowest_on_left,self.lowest_on_right = None,None

def get_gray_pixel(x, y):
	width, height = image.size
	pixel = data[y * width + x]
	return 1 - (((pixel[0] / 255.0) * 0.2989) + ((pixel[1] / 255.0) * 0.587) + ((pixel[2] / 255.0) * 0.114))

count = 0
while count < slice_count:
	slices.append(Slice(count))
	count += 1

for cur in slices:
	for against in slices:
		comp = Comparison(against.i)
		cur.comparisons.append(comp)
		comp.r = comp.l = 0
		y = 0
		while y < height:
			comp.r += math.fabs(get_gray_pixel(cur.i * slice_width + slice_width -1, y) - get_gray_pixel(against.i * slice_width, y))
			comp.l += math.fabs(get_gray_pixel(cur.i * slice_width, y) - get_gray_pixel(against.i * slice_width + slice_width - 1, y))
			y += 1

for cur in slices:	
	cur.lowest_on_left = cur.lowest_on_right = cur.comparisons[0]
	for edge in cur.comparisons:
		if edge != cur:
			if edge.l < cur.lowest_on_left.l:
				cur.lowest_on_left = edge
			if edge.r < cur.lowest_on_right.r:
				cur.lowest_on_right = edge
	
#for each_item in slices:
#	print(each_item.i, each_item.lowest_on_left.i, each_item.lowest_on_right.i)
	
for first in slices:
	for second in slices:
		if first.i != second.i and first.lowest_on_left.i == second.lowest_on_left.i:
			left_candidate = second if first.lowest_on_left.l < second.lowest_on_left.l else first
			
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

unshredded = Image.new("RGBA", image.size)
count = 0
for s in ordered:
	x1, y1 = s.i * slice_width, 0
	x2, y2 = x1 + slice_width, height
	
	source_region = image.crop([x1, y1, x2, y2])
	destination_point = (count * slice_width, 0)
	unshredded.paste(source_region, destination_point)
	count = count + 1

unshredded.save("unshredded.jpg", "JPEG")