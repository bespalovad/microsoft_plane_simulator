import math as m
import sys
from abc import ABCMeta, abstractmethod, ABC
from functools import singledispatch
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from Window import Ui_MainWindow as W
from Start import Ui_MainWindow as S
from PyQt5.QtCore import pyqtSignal
import threading

class Start(QtWidgets.QMainWindow, S):
	def __init__(self, planes_dict):
		super().__init__()
		self.setupUi(self)
		elements = []
		self.planes_dict = planes_dict
		keys = planes_dict.keys()
		for i in keys:
			elements.append(i)
		self.key = "Choose plane"
		self.comboBox.addItems(elements)
		self.connectButtons()
		self.show()
        
	def connectButtons(self):
		self.pushButton.pressed.connect(lambda: self.openWindow())
		self.comboBox.activated[str].connect(self.onActivated)
	
	def onActivated (self, key):
		self.key = key
		try:
			self.label.setText("Max speed: %.2f km/h" % (self.planes_dict.get(key)[0] * 72000.0))
			self.label_2.setText("Pitch speed: %.2f deg/s" % (self.planes_dict.get(key)[1][0] * 10000.0))
			self.label_3.setText("Roll speed: %.2f deg/s" % (self.planes_dict.get(key)[1][1] * 1000.0))
		except Exception:
			self.label.setText("Max speed: -")
			self.label_2.setText("Pitch speed: -")
			self.label_3.setText("Roll speed: -")
	
	def openWindow(self):
		if (self.key == "Choose plane"):
			pass
		else:
			type_of_plane = Intercaptor(self.planes_dict[self.key])
			plane_vektor = PologSamoleta()
			plane_status = PlaneControl(type_of_plane)
			phys_model = PhysModule(type_of_plane, plane_status, plane_vektor)
			quantity_of_ammo = 10
			gun_connector = GunConnector('Gun')
			type_x = 'ammo'
			name_of_gun = []
			for i in range(quantity_of_ammo):
				name_of_connecting_object = ("Ammo #" + str(i))
				name_of_gun.append(name_of_connecting_object)
			gun_connector.create_command(name_of_gun, quantity_of_ammo)
			kasset_of_ammo = gun_connector.return_ammo()
			type_of_plane.load_ammo(kasset_of_ammo)
			win = Window(type_of_plane, self, quantity_of_ammo)
			self.hide()
	
	def finish (self):
		self.show()

class Loop(threading.Thread):
	def __init__(self, b, c, a, p, w):
		super().__init__(group=None, daemon=True)
		self.f = 1
		self.a = a
		self.b = b
		self.c = c
		self.p = p
		self.w = w

	def run(self):
		while (self.f):
			self.b.set_coord(self.c)
			self.b.set_pologSama(self.c)
			self.b.set_vectorSkorosti(self.c)
			self.b.set_eng_procent(self.p)
			coord_x = "X: " + str("%.2f" % self.b.get_coord()[0]) + " km"
			coord_y = "Y: " + str("%.2f" % self.b.get_coord()[1]) + " km"
			coord_z = "Z: " + str("%.2f" % self.b.get_coord()[2]) + " km"
			direct_x = self.azimut(self.b.get_plogSama()[0])
			direct_y = self.horizont(self.b.get_plogSama()[0])
			direct_z = self.list_angle(self.b.get_plogSama()[2], self.b.get_plogSama()[1])
			speed = str("%.2f" % (self.b.get_eng_procent() * self.a.get_tech_char[0] * 72000)) + " km/h"
			engine = str("%.2f" % float(self.b.get_eng_procent()*100.0)) + "%"
			self.w.setcoord_X(coord_x)
			self.w.setcoord_Y(coord_y)
			self.w.setcoord_Z(coord_z)
			self.w.setdirect_X(direct_x)
			self.w.setdirect_Y(direct_y)
			self.w.setdirect_Z(direct_z)
			self.w.setspeed(speed)
			self.w.setengine(engine)
			self.c = PhysModule(self.a, self.p, self.b)
			if (float(self.b.get_coord()[2]) < 0.0):
				self.w.addStatusText("Plane crashed\n")
				time.sleep(2)
				self.stop()
				self.w.exit()
			if ((float(self.b.get_plogSama()[2][2]) != 1.0) & (float(self.b.get_coord()[2]) == 0.0)):
				self.w.addStatusText("Plane crashed\n")
				time.sleep(2)
				self.stop()
				self.w.exit()
			time.sleep(0.02)

	def stop(self):
		self.f = 0
        
	def azimut (self, vector):
		try:
			sin = (-1)*vector[1]/m.sqrt(vector[0]**2 + vector[1]**2)
			cos = vector[0]
		except ZeroDivisionError:
			return ("-")
		if ((sin > 0) & (cos > 0)):
			return ("NE: " + str("%.2f" % float(m.acos(cos)*180.0/m.pi)) + "°")
		if ((sin > 0) & (cos < 0)):
			return ("SE: " + str("%.2f" % float(m.acos(cos)*180.0/m.pi)) + "°")
		if ((sin < 0) & (cos < 0)):
			return ("SW: " + str("%.2f" % float(360.0 - m.acos(cos)*180.0/m.pi)) + "°")
		if ((sin < 0) & (cos > 0)):
			return ("NW: " + str("%.2f" % float(360.0 - m.acos(cos)*180.0/m.pi)) + "°")
		if ((sin == 0) & (cos > 0)):
			return ("N: " + str("%.2f" % 0.0) + "°")
		if ((sin == 0) & (cos < 0)):
			return ("S: " + str("%.2f" % 180.0) + "°")
		if ((sin > 0) & (cos == 0)):
			return ("E: " + str("%.2f" % 90.0) + "°")
		if ((sin < 0) & (cos == 0)):
			return ("W: " + str("%.2f" % 270.0) + "°")
		
	def horizont (self, vector):
		sin = vector[2]
		if (sin > 0):
			return("UP: " + str("%.2f" % float(m.asin(sin)*180.0/m.pi)) + "°")
		if (sin < 0):
			return("DOWN: " + str("%.2f" % float(m.asin(sin)*180.0/m.pi)) + "°")
		if (sin == 0):
			return("STRAIGHT: " + str("%.2f" % 0.0) + "°")
		
	def list_angle (self, vectorZ, vectorY):
		cos = float(vectorZ[2])
		if ((vectorY[2] == 0) & (cos > 0)):
			return("UP: " + str("%.2f" % 0) + "°")
		if ((vectorY[2] > 0) & (cos > 0)):
			return("UPRIGHT: " + str("%.2f" % float(m.acos(cos)*180.0/m.pi)) + "°")
		if ((vectorY[2] > 0) & (cos == 0)):
			return("RIGHT: " + str("%.2f" % (90.0)) + "°")
		if ((vectorY[2] > 0) & (cos < 0)):
			return("DOWNRIGHT: " + str("%.2f" % float(m.acos(cos)*180.0/m.pi)) + "°")
		if ((vectorY[2] == 0) & (cos < 0)):
			return("DOWN: " + str("%.2f" % 180.0) + "°")
		if ((vectorY[2] < 0) & (cos < 0)):
			return("DOWNLEFT: " + str("%.2f" % float((-1)*m.acos(cos)*180.0/m.pi)) + "°")
		if ((vectorY[2] < 0) & (cos == 0)):
			return("LEFT: " + str("%.2f" % (-90.0)) + "°")
		if ((vectorY[2] < 0) & (cos > 0)):
			return("UPLEFT: " + str("%.2f" % float((-1)*m.acos(cos)*180.0/m.pi)) + "°")
		if ((vectorY[2] == 0) & (cos == 0)):
			return("-")


class Window(QtWidgets.QMainWindow, W):
	def __init__(self, type_of_plane, start, q):
		super().__init__()
		self.setupUi(self)
		self.start = start
		self.a = type_of_plane
		self.statustext = []
		b = PologSamoleta()
		self.p = PlaneControl(self.a)
		c = PhysModule(self.a, self.p, b)
		self.connectButtons()
		loop = Loop(b, c, self.a, self.p, self)
		loop.start()
		self.addStatusText("Plane is ready\n")
		self.addStatusText(str(q) + " ammo are ready\n")
		self.show()

	def addStatusText (self, text):
		self.statustext.append(text)
		if (len(self.statustext) == 6):
			for i in range(len(self.statustext)-1):
				self.statustext[i] = self.statustext[i+1]
			self.statustext.pop(5)
		self.Status_label.clear()
		for i in range(len(self.statustext)):
			self.Status_label.setText(self.Status_label.text() + self.statustext[i])
			
	
	def setcoord_X(self, s):
		self.Coord_X.setText(s)

	def setcoord_Y(self, s):
		self.Coord_Y.setText(s)

	def setcoord_Z(self, s):
		self.Coord_Z.setText(s)

	def setdirect_X(self, s):
		self.Direct_X.setText(s)

	def setdirect_Y(self, s):
		self.Direct_Y.setText(s)

	def setdirect_Z(self, s):
		self.Direct_Z.setText(s)

	def setspeed(self, s):
		self.Speed_value.setText(s)

	def setengine(self, s):
		self.Engine_value.setText(s)

	def connectButtons(self):
		self.Gas.pressed.connect(lambda: self.p.forward_press())
		self.Stop.pressed.connect(lambda: self.p.backward_press())
		self.Fire_Bombs.clicked.connect(lambda: self.fire())
		self.Left.pressed.connect(lambda: self.p.right_press())
		self.Up.pressed.connect(lambda: self.p.down_press())
		self.Down.pressed.connect(lambda: self.p.up_press())
		self.Right.pressed.connect(lambda: self.p.left_press())
		self.Gas.released.connect(lambda: self.p.forward_release())
		self.Stop.released.connect(lambda: self.p.backward_release())
		self.Left.released.connect(lambda: self.p.right_release())
		self.Up.released.connect(lambda: self.p.down_release())
		self.Down.released.connect(lambda: self.p.up_release())
		self.Right.released.connect(lambda: self.p.left_release())
        
	def fire (self):
		self.addStatusText(str(self.p.fier_press(self.a)) + "\n")
	
	def exit (self):
		self.start.finish()
		self.hide()


### FACTORY METOD
# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#
class GunConnector():
    def __init__(self, type_of_gun):
        self.__type_of_gun = type_of_gun

    def create_command(self, name_of_gun: list, kol_vo_ammo):
        i = 0
        self.__ammo = self.create()
        for i in range(kol_vo_ammo):
            self.__ammo.name_of_gun(name_of_gun[i])

    def return_ammo(self):
        return self.__ammo

    def create(self):
        if self.__type_of_gun == 'Bomb':
            return KassetaBomba()
        elif self.__type_of_gun == 'Gun':
            return LentaPulya()


class AbstractTypeOrug(ABC):

    @abstractmethod
    def name_of_gun(self, name_of_gun):
        pass

    @abstractmethod
    def return_ammo(self):
        pass


class KassetaBomba(AbstractTypeOrug):
    def __init__(self):
        self.__bomb_list = []

    def name_of_gun(self, name_of_gun):
        self.__bomb_list.append(name_of_gun)

    def return_ammo(self):
        return self.__bomb_list


class LentaPulya(AbstractTypeOrug):
    def __init__(self):
        self.__ammo_list = []

    def name_of_gun(self, name_of_gun):
        self.__ammo_list.append(name_of_gun)

    def return_ammo(self):
        return self.__ammo_list


# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#
# & plane_mark брать из файла


###<<interaface  GUN + BOMB>>
# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#
class Bomb():
    @abstractmethod
    def gun_fier(self):
        if self.__bomb_count != 0:
            self.__bomb_count = self.__bomb_count - 1
            a = self.__bomb_list.pop(0)
            print(f'bomba {str(a)} poshla')
        else:
            print('sorry, no bombs - no fier')

    # & доделать
    @property
    @abstractmethod
    def get_bomb_count(self):
        return self.__bomb_count


class Gun():
    @abstractmethod
    def gun_fier(self):
        if self.__ammo_count != 0:
            self.__ammo_count = self.__ammo_count - 1
            a = self.__ammo_list.pop(0)
            print(f'pulka {str(a)} poshla')
        else:
            print('sorry, no ammo - no fier')

    # & доделать
    @property
    def get_ammo_count(self):
        return self.__ammo_count


# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#


# TechChar -> Intercaptor Bomber Plane
# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#
class TechChar():
    # & plane_mark брать из файла
    def __init__(self, plane_mark):
        self.engine = plane_mark[0]
        self.wing = plane_mark[1]
        self.Stabilizator = plane_mark[2]

    def set_tech_char(self):
        self.max_speed = float(self.engine)
        self.max_rotateX_speed = float(self.wing[1])
        self.max_rotateY_speed = float(self.wing[1])
#0.2 * float(self.wing[0]) + 0.8 * float(self.Stabilizator)
    @property
    def get_tech_char(self):
        return [self.max_speed, self.max_rotateX_speed, self.max_rotateY_speed]


class Bomber(TechChar, Bomb):
    def __init__(self, plane_mark):
        super().__init__(plane_mark)
        self.set_tech_char()

    # установить кассету бомб
    def load_ammo(self, kasseta_bomb):
        self.__bomb_count = len(kasseta_bomb.return_ammo())
        self.__bomb_list = kasseta_bomb.return_ammo()

    '''#установить кассету бомб
    def set_casseta_bombs(self, kasseta_bomb: KassetaBomba):
        self.__bomb_count = len(kasseta_bomb)
        self.__bomb_list = kasseta_bomb'''

    def gun_fier(self):
        if self.__ammo_count != 0:
            self.__ammo_count = self.__ammo_count - 1
            a = self.__ammo_list.pop(0)
            print(f'bomba {str(a)} poshla')
        else:
            print('sorry, no ammo - no fier')


class Intercaptor(TechChar, Gun):
    def __init__(self, plane_mark):
        super().__init__(plane_mark)
        self.set_tech_char()

    def load_ammo(self, lenta_pulya):
        self.__ammo_count = len(lenta_pulya.return_ammo())
        self.__ammo_list = lenta_pulya.return_ammo()

    '''def set_lenta_pulya(self, lenta_pulya: LentaPulya):
        self.__ammo_count = len(lenta_pulya)
        self.__ammo_list = lenta_pulya'''

    def gun_fier(self):
        if self.__ammo_count != 0:
            self.__ammo_count = self.__ammo_count - 1
            a = self.__ammo_list.pop(0)
            return (f'pulka {str(a)} poshla')
        else:
            return ('sorry, no ammo - no fier')


class Plane(TechChar):
    def __init__(self, plane_mark):
        super().__init__(plane_mark)
        self.set_tech_char()


# =====================================================================================================#
# =====================================================================================================#
# =====================================================================================================#


###Plane_control
# =====================================================================================================#
class PlaneControl():
    def __init__(self, plane_type):
        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0
        self.forward = 0
        self.backward = 0
        self.__plane_type = plane_type

    def up_press(self):
        self.up = 1

    def down_press(self):
        self.down = 1

    def left_press(self):
        self.left = 1

    def right_press(self):
        self.right = 1

    def forward_press(self):
        self.forward = 1

    def backward_press(self):
        self.backward = 1

    def up_release(self):
        self.up = 0

    def down_release(self):
        self.down = 0

    def left_release(self):
        self.left = 0

    def right_release(self):
        self.right = 0

    def forward_release(self):
        self.forward = 0

    def backward_release(self):
        self.backward = 0

    def return_data_plane(self):
        self.__mov_list_plane = [self.up, self.down, self.left, self.right]
        return self.__mov_list_plane

    def return_data_eng(self):
        self.__mov_list_eng = [self.forward, self.backward]
        return self.__mov_list_eng

    def fier_press(self, plane_type):
        return plane_type.gun_fier()

    ##def knopka_ognya(self, plane_type):
    ##   plane_type.gun_fier()

    '''@knopka_ognya.register(Intercaptor)
    def _(self, plane_type):
        plane_type.gun_fier()
        plane_type.get_ammo_count

    @knopka_ognya.register(Bomber)
    def _(self, plane_type):
        plane_type.bomb_fier()
        plane_type.get_bomb_count'''


###pologenie_samoleta
# =====================================================================================================#
class PologSamoleta():
	def __init__(self):
		self.__x = 0
		self.__y = 0
		self.__z = 0
		self.__e1 = [1, 0, 0]
		self.__e2 = [0, 1, 0]
		self.__e3 = [0, 0, 1]
		self.__vx = 0
		self.__vy = 0
		self.__vz = 0
		self.__eng_procent = 0.0

    # setter_coordinat_samoleta
	def set_coord(self, physik):
		self.__x = self.__x + physik.getter_vektorSkorosti()[0]
		self.__y = self.__y + physik.getter_vektorSkorosti()[1]
		self.__z = self.__z + physik.getter_vektorSkorosti()[2]

    # getter_coordinat_samoleta
	def get_coord(self):
		return [self.__x, self.__y, self.__z]

    # setter_polog_samoleta
	def set_pologSama(self, physik):
		self.__e1 = physik.getter_pologSama()[0]
		self.__e2 = physik.getter_pologSama()[1]
		self.__e3 = physik.getter_pologSama()[2]

	# getter_polog_sama
	def get_plogSama(self):
		return [self.__e1, self.__e2, self.__e3]

	#setter_vector_skorosti
	def set_vectorSkorosti(self, physik):
		self.__vx = physik.getter_vektorSkorosti()[0]
		self.__vy = physik.getter_vektorSkorosti()[1]
		self.__vz = physik.getter_vektorSkorosti()[2]

    # setter_eng_procent
	def set_eng_procent(self, p: PlaneControl):
		self.__eng_procent = self.__eng_procent + p.return_data_eng()[0] * 0.005 - p.return_data_eng()[1] * 0.005
		if (self.__eng_procent < 0.0):
			self.__eng_procent = 0.0
		if (self.__eng_procent > 1.0):
			self.__eng_procent = 1.0

    # getter_eng_procent
	def get_eng_procent(self):
		return self.__eng_procent


###Physick
# =====================================================================================================#
class PhysModule():
    def __init__(self, techChar, planeControl: PlaneControl, pologSamoleta: PologSamoleta):
        self.__a = techChar
        self.__b = planeControl
        self.__c = pologSamoleta
        self.setter_pologSama(self.__a, self.__b, self.__c)
        self.setter_vektorSkorosti()

    # setter_polog_sama
    def setter_pologSama(self, __a: TechChar, __b: PlaneControl, __c: PologSamoleta):
        list_old = __c.get_plogSama()
        '''print(__b.return_data_plane(), '\n')
        print(list_old, '\n')
        print(__b.return_data_plane()[1])'''
        e1 = [0, 0, 0]
        e2 = [0, 0, 0]
        e3 = [0, 0, 0]
        if sum(__b.return_data_plane()) == 1:
            e1[0] = __b.return_data_plane()[3] * list_old[0][0] + __b.return_data_plane()[2] * list_old[0][0] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[0][0] + __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[2][0] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[0][0] - __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[2][0]
            e1[1] = __b.return_data_plane()[3] * list_old[0][1] + __b.return_data_plane()[2] * list_old[0][1] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[0][1] + __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[2][1] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[0][1] - __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[2][1]
            e1[2] = __b.return_data_plane()[3] * list_old[0][2] + __b.return_data_plane()[2] * list_old[0][2] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[0][2] + __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[2][2] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[0][2] - __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[2][2]

            e2[0] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[1][0] - __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[2][0] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[1][0] + __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[2][0] + __b.return_data_plane()[1] * list_old[1][0] + __b.return_data_plane()[0] * list_old[1][0]
            e2[1] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[1][1] - __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[2][1] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[1][1] + __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[2][1] + __b.return_data_plane()[1] * list_old[1][1] + __b.return_data_plane()[0] * list_old[1][1]
            e2[2] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[1][2] - __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[2][2] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[1][2] + __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[2][2] + __b.return_data_plane()[1] * list_old[1][2] + __b.return_data_plane()[0] * list_old[1][2]

            e3[0] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[2][0] + __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[1][0] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[2][0] - __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[1][0] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[2][0] - __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[0][0] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[2][0] + __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[0][0]
            e3[1] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[2][1] + __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[1][1] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[2][1] - __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[1][1] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[2][1] - __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[0][1] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[2][1] + __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[0][1]
            e3[2] = __b.return_data_plane()[3] * m.cos(__a.get_tech_char[1]) * list_old[2][2] + __b.return_data_plane()[3] * m.sin(__a.get_tech_char[1]) * list_old[1][2] + __b.return_data_plane()[2] * m.cos(__a.get_tech_char[1]) * list_old[2][2] - __b.return_data_plane()[2] * m.sin(__a.get_tech_char[1]) * list_old[1][2] + __b.return_data_plane()[1] * m.cos(__a.get_tech_char[2]) * list_old[2][2] - __b.return_data_plane()[1] * m.sin(__a.get_tech_char[2]) * list_old[0][2] + __b.return_data_plane()[0] * m.cos(__a.get_tech_char[2]) * list_old[2][2] + __b.return_data_plane()[0] * m.sin(__a.get_tech_char[2]) * list_old[0][2]

            self.__e1 = e1
            self.__e2 = e2
            self.__e3 = e3
        else:
            e1 = list_old[0]
            e2 = list_old[1]
            e3 = list_old[2]

            self.__e1 = e1
            self.__e2 = e2
            self.__e3 = e3

    # getter_polog_samoleta
    def getter_pologSama(self):
        return [self.__e1, self.__e2, self.__e3]

    # setter_vektor_skorosti
    def setter_vektorSkorosti(self):
        list = self.getter_pologSama()
        self.__vx = self.__c.get_eng_procent() * self.__a.get_tech_char[0] * list[0][0]
        self.__vy = self.__c.get_eng_procent() * self.__a.get_tech_char[0] * list[0][1]
        self.__vz = self.__c.get_eng_procent() * self.__a.get_tech_char[0] * list[0][2]

    # getter_vektor_skorosti
    def getter_vektorSkorosti(self):
        return [self.__vx, self.__vy, self.__vz]


def readFile():
    f = open("Char.txt", "r")
    planes_dict = {}
    for line in f:
        newline = line.replace("\n", "")
        tech_list = newline.split(":")
        new_tech_list = [float(tech_list[1])/72000, [float(tech_list[2])/10000.0, float(tech_list[3])/1000.0], tech_list[4]]
        name = tech_list[0]
        planes_dict[name] = new_tech_list
    return planes_dict


# Main
def main():
    planes_dict = readFile()
    
    app = QtWidgets.QApplication([])
    start = Start(planes_dict)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
