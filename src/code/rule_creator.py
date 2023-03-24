from PIL import Image, ImageDraw
import numpy as np


size = (660, 30)
rule = Image.new('RGBA', size, (255, 255, 255, 0))
ruleD = ImageDraw.Draw(rule, 'RGBA')

N = 110
step = size[0]/N
for i in range(1, N):
    s = 30 if i % 100 == 0 else 22 if i % 50 == 0 else 15 if i % 10 == 0 else 10 if i % 5 == 0 else 5

    ruleD.line([step*i, 0, step*i, s], width=2, fill=(0, 0, 0, 255))

rule.save('../images/rule.png')
rule.show()


def rule_points(length, N):

    points = np.zeros((N-1)*2*2, dtype=np.float64).reshape((N-1, 2, 2))

    step = length / N
    for i in range(1, N):
        s = 30 if i % 100 == 0 else 22 if i % 50 == 0 else 15 if i % 10 == 0 else 10 if i % 5 == 0 else 5

        points[i, :, 0] = step*i
        points[i, 1, 1] = s

    return points
