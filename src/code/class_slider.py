import numpy as np
import pygame as py
import pygame.gfxdraw


class Slider:

    def __init__(self, surface, bottom, length, width):
        self.screen = surface
        self.ref = np.array(surface.get_size(), dtype=np.float64) * [.5, 1] - [length / 2, bottom]
        self.length = length
        self.width = width
        self.color = (192, 192, 192)
        self.points = np.array([self.ref, self.ref + [0, -width], self.ref + [length, -width], self.ref + [length, 0]])
        self.angle = 0
        self.rotating = False

        # Masses
        self.masses = []
        self.mw = 50
        self.W = 15
        self.moving_mass = [False, 0]
        self.moving_sensor = [False, 0]

        self.play = False
        self.rule = self.rule_points(220) + self.points[1]

        # Sensors
        self.sensors = []
        self.h = 75
        self.sl = 16
        self.sw = 30
        self.s = np.array([[0, self.h], [-self.mw, self.h]], dtype=np.float64)
        self.ref_s = self.ref + [[0, -self.h - 2*self.W], [self.length, -self.h - 2*self.W]]

        # Timers
        self.timers = []
        self.t_id = 0

    def draw(self):
        # Draw the slider
        py.gfxdraw.aapolygon(self.screen, self.points, self.color)
        py.gfxdraw.filled_polygon(self.screen, self.points, self.color)
        if not self.play:
            py.gfxdraw.aacircle(self.screen, int(self.points[-1, 0]), int(self.points[-1, 1]),  int(self.width/3), (255, 0, 0))
            py.gfxdraw.filled_circle(self.screen, int(self.points[-1, 0]), int(self.points[-1, 1]),  int(self.width/3), (255, 0, 0))
            py.gfxdraw.aacircle(self.screen, int(self.points[0, 0]), int(self.points[0, 1]), int(self.width/5), (0, 0, 0))
            py.gfxdraw.filled_circle(self.screen, int(self.points[0, 0]), int(self.points[0, 1]), int(self.width/5), (0, 0, 0))

        # Draw all the masses
        for mass in self.masses:
            py.gfxdraw.aapolygon(self.screen, mass['points'], mass['color'])
            py.gfxdraw.filled_polygon(self.screen, mass['points'], mass['color'])

        # Draw the rule
        for i in range(self.rule.shape[0]):
            py.draw.aaline(self.screen, (0, 0, 0), self.rule[i, 0], self.rule[i, 1])

        # Draw all the sensors
        for sensor in self.sensors:
            py.gfxdraw.aapolygon(self.screen, sensor['points'][:4], sensor['color'])
            py.gfxdraw.filled_polygon(self.screen, sensor['points'][:4], sensor['color'])
            py.draw.aaline(self.screen, sensor['color'], sensor['points'][4], sensor['points'][5])

        py.draw.aaline(self.screen, (0, 0, 0), self.ref_s[0], self.ref_s[1])

    def hover(self):
        hover = self.hover_check()
        if hover['type'] != 'none' or self.moving_mass[0] or self.moving_sensor[0]:
            py.mouse.set_cursor(py.SYSTEM_CURSOR_HAND)
        else:
            py.mouse.set_cursor(py.SYSTEM_CURSOR_ARROW)

    def hover_check(self):
        pos = np.array(py.mouse.get_pos(), dtype=np.float64)
        d = pos - self.points[-1]
        if np.dot(d, d) <= (self.width/3)**2:
            return {'type': 'rotate'}
        else:
            R = self.rotation_matrix2d(self.angle)
            pos -= self.ref
            pos = R @ pos
            pos += self.ref
            for i in range(len(self.masses)):
                points = []
                for j in range(4):
                    p = self.masses[i]['points'][j] - self.ref
                    p = R @ p
                    points.append(p + self.ref)
                if points[0][0] <= pos[0] <= points[3][0] and points[1][1] <= pos[1] <= points[0][1]:
                    return {'type': 'mass', 'mass': 'Mass = '+str(self.masses[i]['mass'])+' gr', 'n': i}
        return {'type': 'none'}

    @staticmethod
    def rotation_matrix2d(angle):
        cos = np.cos(angle)
        sin = np.sin(angle)
        R = np.array([[cos, -sin], [sin, cos]], dtype=np.float64)
        return R

    def rotate(self, v, a):
        r = self.rotation_matrix2d(a)  # Rotation matrix
        return (r @ v.reshape((v.shape[-2], v.shape[-1], 1))).reshape((v.shape[-2], v.shape[-1]))

    def rotate_all(self, angle):

        r = self.rotation_matrix2d(angle)  # Rotation matrix
        def rotate(v): return (r @ v.reshape((v.shape[-2], v.shape[-1], 1))).reshape((v.shape[-2], v.shape[-1]))

        # Rotate the slider
        self.points -= self.ref
        self.points = rotate(self.points)
        self.points += self.ref

        # Rotate the rule
        for i in range(2):
            size = self.rule.shape[0]
            self.rule[:, i] -= self.ref
            self.rule[:, i] = rotate(self.rule[:, i])
            self.rule[:, i] += self.ref

        # Rotate all masses
        for i in range(len(self.masses)):
            self.masses[i]['points'] -= self.ref
            self.masses[i]['points'] = rotate(self.masses[i]['points'])
            self.masses[i]['points'] += self.ref
            self.masses[i]['vel'] = 0

        # Rotate all the sensors
        for i in range(len(self.sensors)):
            self.sensors[i]['points'] -= self.ref
            self.sensors[i]['points'] = rotate(self.sensors[i]['points'])
            self.sensors[i]['points'] += self.ref

        self.ref_s -= self.ref
        self.ref_s = rotate(self.ref_s)
        self.ref_s += self.ref

        # Rotate s vector
        self.s = rotate(self.s)

    def rotate_mouse(self):

        if self.rotating and not (self.moving_mass[0] or self.moving_sensor[0]):  # Check this
            pos = np.array(py.mouse.get_pos())
            y = self.ref[1] - pos[1]
            a = np.arctan(y / (pos[0] - self.ref[0]))
            b = a - self.angle

            if y >= 0 and a <= 30*np.pi/180:
                self.angle = a
                self.rotate_all(-b)

    def add_mass(self, mass):
        color = np.random.randint(20, 230, 3)
        mass = {'mass': mass, 'vel': 0, 'points': np.zeros(8, dtype=np.float64).reshape(4, 2), 'color': color}
        self.masses.append(mass)
        self.moving_mass = [True, -1]

    def move_object(self):
        if self.moving_mass[0]:
            R = self.rotation_matrix2d(-self.angle)
            pos = np.array(py.mouse.get_pos())
            x = (pos[0] - self.points[1, 0])
            v1 = np.array([self.mw/2, self.width + self.W], dtype=np.float64)
            v2 = np.array([-self.mw/2, self.width + self.W], dtype=np.float64)
            R1 = self.rotation_matrix2d(self.angle)
            v1 = R1 @ v1
            v2 = R1 @ v2
            if v1[0] + self.points[0, 0] <= pos[0] <= v2[0] + self.points[3, 0]:
                points = np.array([[0, 0], [0, -2*self.W], [self.mw, -2*self.W], [self.mw, 0]], dtype=np.float64)
                points = self.rotate(points, -self.angle)
                points += self.points[1] + [x, - x * np.tan(self.angle)] + (self.mw/2 - self.W*np.tan(self.angle))*np.array([-np.cos(self.angle), np.sin(self.angle)])
                self.masses[self.moving_mass[1]]['points'] = points
        if self.moving_sensor[0]:
            R = self.rotation_matrix2d(-self.angle)
            pos = np.array(py.mouse.get_pos())
            x = (pos[0] - self.ref_s[0, 0])
            if self.ref_s[0, 0] <= pos[0] <= self.ref_s[1, 0]:
                points = np.array([[0, 0], [0, -self.sw], [self.sl, -self.sw], [self.sl, 0], [self.sl/2, 0], [self.sl/2, 15]], dtype=np.float64)
                points = self.rotate(points, -self.angle)
                points += self.ref_s[0] + [x, - x * np.tan(self.angle)]
                self.sensors[self.moving_sensor[1]]['points'] = points

    def evol(self, dt, mu):
        if self.play:
            g = 981*3  # 9.81
            sin = np.sin(self.angle)
            cos = np.cos(self.angle)
            def u(x): return x*np.tan(self.angle)
            for mass in self.masses:
                m = mass['mass']
                v0 = mass['vel']
                n = 1 if v0 <= 0 else -1
                d = v0*dt - .5*g*sin*dt**2 + n*.5*u(mu)*g*cos*dt**2
                vel = v0 - g*sin*dt + n*u(mu)*g*cos*dt
                r = d*np.array([cos, -sin])
                mass['vel'] = vel
                for i in range(4):
                    mass['points'][i] += r
                if mass['points'][0, 0] < self.points[1, 0] or mass['points'][3, 0] > self.points[2, 0]:
                    mass['vel'] *= -1

            for i in range(len(self.masses) - 1):

                for j in range(i + 1, len(self.masses)):

                    d = self.masses[i]['points'][0] - self.masses[j]['points'][0]

                    if np.dot(d, d) < self.mw**2:

                        v1 = self.masses[i]['vel']
                        v2 = self.masses[j]['vel']
                        m1 = self.masses[i]['mass']
                        m2 = self.masses[j]['mass']

                        self.masses[i]['vel'] = (2*m2*v2 + (m1 - m2)*v1)/(m1+m2)
                        self.masses[j]['vel'] = (2*m1*v1 + (m2 - m1)*v2)/(m1+m2)

    def rule_points(self, n):

        points = np.zeros((n - 1) * 2 * 2, dtype=np.float64).reshape((n - 1, 2, 2))

        step = self.length / n
        for i in range(1, n):
            s = 30 if i % 100 == 0 else 22 if i % 50 == 0 else 15 if i % 10 == 0 else 10 if i % 5 == 0 else 5

            points[i - 1, :, 0] = step * i
            points[i - 1, 1, 1] = s

        return points

    def add_timer(self):
        color = np.random.randint(20, 230, 3)
        timer = {'s': 0, 'type': 'pulse', 'id': self.t_id, 'play': False, 'time': 0., 'color': color, 'precision_mode': 1}
        self.timers.append(timer)
        self.t_id += 1

    def add_sensor(self, timer):
        sensor = {'h': False, 'color': timer['color'], 'timer': timer['id'], 'points': np.zeros((4+2)*2, dtype=np.float64).reshape((4+2, 2))}
        self.sensors.append(sensor)
        self.moving_sensor = [True, -1]

    def rem_sensor(self, timer, one):
        for i in range(len(self.sensors)):
            if self.sensors[i]['timer'] == timer['id']:
                self.sensors.pop(i)
                if one:
                    break
        if not one:
            self.timers.remove(timer)

    def timer_pulse(self, timer, pulse):
        ind = self.index_timer(timer)
        if self.timers[ind]['type'] == 'pulse':
            if pulse and self.timers[ind]['s'] == 0:
                self.timers[ind]['s'] += 1
                self.timers[ind]['play'] = True
            elif pulse and self.timers[ind]['s'] == 1:
                self.timers[ind]['s'] += 1
                self.timers[ind]['play'] = False
        elif self.timers[ind]['type'] == 'gate':
            if pulse and self.timers[ind]['s'] == 0:
                self.timers[ind]['s'] += 1
                self.timers[ind]['play'] = True
            elif not pulse and self.timers[ind]['s'] == 1:
                self.timers[ind]['s'] += 1
                self.timers[ind]['play'] = False

    def sensor_check(self):
        R = self.rotation_matrix2d(self.angle)
        R1 = self.rotation_matrix2d(-self.angle)

        def rotate(r, v):
            return (r @ v.reshape((v.shape[-2], v.shape[-1], 1))).reshape((v.shape[-2], v.shape[-1]))

        for sensor in self.sensors:
            for mass in self.masses:
                mass['points'] -= self.ref
                mass['points'] = rotate(R, mass['points'])
                mass['points'] += self.ref
                sensor['points'] -= self.ref
                sensor['points'] = rotate(R, sensor['points'])
                sensor['points'] += self.ref

                if mass['points'][0, 0] <= sensor['points'][4, 0] <= mass['points'][3, 0]:
                    if not sensor['h']:
                        self.timer_pulse(sensor['timer'], True)
                        sensor['h'] = True
                else:
                    if sensor['h']:
                        self.timer_pulse(sensor['timer'], False)
                        sensor['h'] = False

                mass['points'] -= self.ref
                mass['points'] = rotate(R1, mass['points'])
                mass['points'] += self.ref
                sensor['points'] -= self.ref
                sensor['points'] = rotate(R1, sensor['points'])
                sensor['points'] += self.ref

    def index_timer(self, di):
        for i in range(len(self.timers)):
            if self.timers[i]['id'] == di:
                return i

    def reset_timer(self, n):
        self.timers[n]['s'] = 0
        self.timers[n]['time'] = 0
