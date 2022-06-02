"""
-----------------------------------------------------------
A library describing a digital pool model with temperature sensors. 
Simulates the output of real data from physical sensors. 

(C) 2022 Olga Pershina, PetrSU, Petrozavodsk, Russia
email catola2001@gmail.com
-----------------------------------------------------------
"""

import math
import numpy

# класс бассейна    
class Pool:
    # функция инициализации бассейна
    def __init__(self, 
                 height, 
                 width, 
                 length, 
                 water_temperature, 
                 ambient_temperature, 
                 mixing_speed):
        # параметры бассейна: высота, ширина и длина
        self.height = height
        self.width = width
        self.length = length
        # начальная температура воды в бассейне
        self.water_temperature = water_temperature
        # температура окружающей среды
        self.ambient_temperature = ambient_temperature
        # скорость перемешивания
        self.mixing_speed = mixing_speed
        # значение предыдущей температуры бассейна
        self.__old_temp = self.water_temperature
        self.__time = 1
    
    # функция полного опустошения и наполнения бассейна
    def reset_pool(self, water_temperature):
        """ Function for complete replacement of water in the pool """
        if water_temperature > 100 or water_temperature < 1:
            raise ValueError("Wrong value of temperature")
        self.water_temperature = water_temperature
        self.__time = 1
    
    # функция добавления воды 
    def open_pipe(self, volume, water_temperature):
        """ Pipe opening function to add water to the pool """
        pool_volume = self.height*self.length*self.width
        if volume > pool_volume:
            raise ValueError("Wrong volume of water")
        if water_temperature > 100 or water_temperature < 1:
            raise ValueError("Wrong value of temperature")
        self.__old_temp = self.water_temperature
        self.water_temperature = (water_temperature*volume 
                                  + self.get_in_sensor_temp(self.__time)
                                  * (pool_volume - volume)) / pool_volume
        
    # функция получения данных с входного датчика
    def get_in_sensor_temp(self, time):
        """ The function of receiving data from the input sensor """
        if time <= 0:
            raise ValueError("Time cannot be negative")
        full_mixing_speed = self.height*self.length*self.width/self.mixing_speed
        ans = 0
        self.__time += time
        if time <= full_mixing_speed:
            ans = self.water_temperature 
        if time > full_mixing_speed:
            if self.water_temperature - self.ambient_temperature > 1:
                ans = self.water_temperature - ((self.water_temperature-self.ambient_temperature) / math.log(self.water_temperature-self.ambient_temperature)) * math.log(time/60)
            elif self.water_temperature - self.ambient_temperature < 1:
                ans = self.water_temperature + ((self.ambient_temperature-self.water_temperature) / math.log(abs(self.water_temperature-self.ambient_temperature)))/2 * math.log(time/60)
                if ans > self.ambient_temperature:
                    ans = self.ambient_temperature
            else: 
                ans = self.water_temperature
        return self.__noise(ans, time <= full_mixing_speed)               
            
    # функция получения данных с выходного датчика
    def get_out_sensor_temp(self, time):
        """ The function of receiving data from the output sensor """
        if time <= 0:
            raise ValueError("Time cannot be negative")
        full_mixing_speed = self.height*self.length*self.width/self.mixing_speed
        ans = 0
        if time <= full_mixing_speed:
            if time >= self.length/self.mixing_speed:
                ans = self.water_temperature
            else: 
                ans = self.__old_temp
        if time > full_mixing_speed:
            if self.water_temperature - self.ambient_temperature > 1:
                ans = self.water_temperature - ((self.water_temperature-self.ambient_temperature) / math.log(self.water_temperature-self.ambient_temperature)) * math.log(time/60)
            elif self.water_temperature - self.ambient_temperature < 1:
                ans = self.water_temperature + ((self.ambient_temperature-self.water_temperature) / math.log(abs(self.water_temperature-self.ambient_temperature)))/2 * math.log(time/60)
                if ans > self.ambient_temperature:
                    ans = self.ambient_temperature
            else: 
                ans = self.water_temperature
        return self.__noise(ans, time <= full_mixing_speed) 
    
    # функция наложения шума
    def __noise(self, ans, not_mixed):
        if numpy.random.randint(1, 1000) == 73:
            return numpy.random.randint(1, 100) + numpy.random.randint(1, 100)/100
        if not_mixed and self.water_temperature-self.__old_temp != 0:
            scl = math.log(abs(self.water_temperature-self.__old_temp))
        else: scl = 1
        return round(numpy.random.normal(loc = ans, scale=scl), 2)