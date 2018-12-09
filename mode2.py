#Zhengzhi Wang
import logging
import sys
import time

import pygame
from pygame.locals import *
import os
import time
import RPi.GPIO as GPIO
from numpy import *
import RPi.GPIO as GPIO


from Adafruit_BNO055 import BNO055

bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')

#set matrix function
def set_matrix(s,g,z,nx,ny):
    for i in range(nx):
        for j in range(ny):
            if z[i,j]==1:
                red=255
            else:
                red=0
            if s[i,j]==1:
                green=255
            else:
                green=0
            if g[i,j]==1:
                blue=255
            else:
                blue=0
            color=red,green,blue
            pygame.draw.rect(screen,color,(i,j,1,1),0)

def sandFalling(i,sand,gnd,z,sandNew,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary

    if p==0:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1
    elif p==1:
        xind1 = 1-p
        xind2 = nx-3+p
        yind1 = 1-p
        yind2 = nx-3+p

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1+1:xind2+1:2,yind1:yind2:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s01=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s11=sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1+1:xind2+1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1+1:yind2+1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1:xind2:2,yind1+1:yind2+1:2]
    sN10=sandNew[xind1+1:xind2+1:2,yind1:yind2:2]
    sN11=sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    temp1 = sN01*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN11*vary1[xind1:xind2:2,yind1+1:yind2+1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN01*vary1[xind1:xind2:2,yind1+1:yind2+1:2]

    sandNew[xind1:xind2:2,yind1+1:yind2+1:2] = copy(temp1)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2] = copy(temp2)

    #sand=copy(sandNew)
    #screen.fill(BLACK)
    #set_matrix(sand,gnd,z,320,240)
    #pygame.display.flip()

def sandFalling180(i,sand,gnd,z,sandNew,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1-1:xind2-1:2,yind1:yind2:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1-1:xind2-1:2,yind1:yind2:2]
    s01=sand[xind1:xind2:2,yind1-1:yind2-1:2]
    s11=sand[xind1-1:xind2-1:2,yind1-1:yind2-1:2]


    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1-1:xind2-1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1:xind2:2,yind1-1:yind2-1:2]
    sN10=sandNew[xind1-1:xind2-1:2,yind1:yind2:2]
    sN11=sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2]

    temp1 = sN01*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN11*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN01*vary1[xind1:xind2:2,yind1-1:yind2-1:2]

    sandNew[xind1:xind2:2,yind1-1:yind2-1:2] = copy(temp1)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2] = copy(temp2)

def sandFalling90cw(i,sand,gnd,z,sandNew,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1


    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1-1:yind2-1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1-1:yind2-1:2]
    s01=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s11=sand[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1+1:xind2+1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1+1:xind2+1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1+1:xind2+1:2,yind1:yind2:2]
    sN10=sandNew[xind1:xind2:2,yind1-1:yind2-1:2]
    sN11=sandNew[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    temp1 = sN01*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN11*vary1[xind1+1:xind2+1:2,yind1:yind2:2]
    temp2 = sN11*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN01*vary1[xind1+1:xind2+1:2,yind1:yind2:2]

    sandNew[xind1+1:xind2+1:2,yind1:yind2:2] = copy(temp1)
    sandNew[xind1+1:xind2+1:2,yind1-1:yind2-1:2] = copy(temp2)


def sandFalling90ccw(i,sand,gnd,z,sandNew,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1+1:yind2+1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s01=sand[xind1-1:xind2-1:2,yind1:yind2:2]
    s11=sand[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1:xind2:2,yind1+1:yind2+1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1-1:xind2-1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1-1:xind2-1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1-1:xind2-1:2,yind1:yind2:2]
    sN10=sandNew[xind1:xind2:2,yind1+1:yind2+1:2]
    sN11=sandNew[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    temp1 = sN01*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN11*vary1[xind1-1:xind2-1:2,yind1:yind2:2]
    temp2 = sN11*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN01*vary1[xind1-1:xind2-1:2,yind1:yind2:2]

    sandNew[xind1-1:xind2-1:2,yind1:yind2:2] = copy(temp1)
    sandNew[xind1-1:xind2-1:2,yind1+1:yind2+1:2] = copy(temp2)

def sandFalling45ur(i,sand,gnd,z,sandNew,sandNew2,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1


    g00=copy(gnd[xind1:xind2:2,yind1:yind2:2])
    g10=copy(gnd[xind1-1:xind2-1:2,yind1:yind2:2])
    g01=copy(gnd[xind1:xind2:2,yind1-1:yind2-1:2])
    g11=copy(gnd[xind1-1:xind2-1:2,yind1-1:yind2-1:2])
    s00=copy(sand[xind1:xind2:2,yind1:yind2:2])
    s10=copy(sand[xind1-1:xind2-1:2,yind1:yind2:2])
    s01=copy(sand[xind1:xind2:2,yind1-1:yind2-1:2])
    s11=copy(sand[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    #sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s10*s01*s11
    sandNew[xind1-1:xind2-1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)
    #sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=g11*s11+(1-g11)*(1-s11)*sor+(1-g11)*s11

    sN00=copy(sandNew[xind1:xind2:2,yind1:yind2:2])
    sN01=copy(sandNew[xind1:xind2:2,yind1-1:yind2-1:2])
    sN10=copy(sandNew[xind1-1:xind2-1:2,yind1:yind2:2])
    sN11=copy(sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    temp1 = sN01*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN11*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN01*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2] = copy(temp1)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2] = copy(temp2)

    sand=copy(sandNew)
    #screen.fill(BLACK)
    #set_matrix(sand,gnd,z,320,240)
    #pygame.surfarray.blit_array(screen,(sand)*65280+gnd*16777215)
    #set_matrix(gnd,320,240)
    #pygame.display.flip()

    '''if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1


    g00=copy(gnd[xind1:xind2:2,yind1:yind2:2])
    g10=copy(gnd[xind1-1:xind2-1:2,yind1:yind2:2])
    g01=copy(gnd[xind1:xind2:2,yind1-1:yind2-1:2])
    g11=copy(gnd[xind1-1:xind2-1:2,yind1-1:yind2-1:2])
    s00=copy(sand[xind1:xind2:2,yind1:yind2:2])
    s10=copy(sand[xind1-1:xind2-1:2,yind1:yind2:2])
    s01=copy(sand[xind1:xind2:2,yind1-1:yind2-1:2])
    s11=copy(sand[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    #sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s10*s01*s11
    sandNew[xind1-1:xind2-1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)
    #sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=g11*s11+(1-g11)*(1-s11)*sor+(1-g11)*s11

    sN00=copy(sandNew[xind1:xind2:2,yind1:yind2:2])
    sN01=copy(sandNew[xind1:xind2:2,yind1-1:yind2-1:2])
    sN10=copy(sandNew[xind1-1:xind2-1:2,yind1:yind2:2])
    sN11=copy(sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    temp1 = sN01*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN11*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN01*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2] = copy(temp1)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2] = copy(temp2)

    sand=copy(sandNew)'''
    if p==0:
        p=1
    elif p==1:
        p=0


    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1-1:yind2-1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1-1:yind2-1:2]
    s01=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s11=sand[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    sandNew2[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew2[xind1:xind2:2,yind1-1:yind2-1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew2[xind1+1:xind2+1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew2[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew2[xind1+1:xind2+1:2,yind1:yind2:2]
    sN10=sandNew2[xind1:xind2:2,yind1-1:yind2-1:2]
    sN11=sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    temp3 = sN01*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN11*vary1[xind1+1:xind2+1:2,yind1:yind2:2]
    temp4 = sN11*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN01*vary1[xind1+1:xind2+1:2,yind1:yind2:2]

    sandNew2[xind1+1:xind2+1:2,yind1:yind2:2] = copy(temp3)
    sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2] = copy(temp4)

def sandFalling45ul(i,sand,gnd,z,sandNew,sandNew2,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1


    g00=copy(gnd[xind1:xind2:2,yind1:yind2:2])
    g10=copy(gnd[xind1-1:xind2-1:2,yind1:yind2:2])
    g01=copy(gnd[xind1:xind2:2,yind1-1:yind2-1:2])
    g11=copy(gnd[xind1-1:xind2-1:2,yind1-1:yind2-1:2])
    s00=copy(sand[xind1:xind2:2,yind1:yind2:2])
    s10=copy(sand[xind1-1:xind2-1:2,yind1:yind2:2])
    s01=copy(sand[xind1:xind2:2,yind1-1:yind2-1:2])
    s11=copy(sand[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    #sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s10*s01*s11
    sandNew[xind1-1:xind2-1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)
    #sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=g11*s11+(1-g11)*(1-s11)*sor+(1-g11)*s11

    sN00=copy(sandNew[xind1:xind2:2,yind1:yind2:2])
    sN01=copy(sandNew[xind1:xind2:2,yind1-1:yind2-1:2])
    sN10=copy(sandNew[xind1-1:xind2-1:2,yind1:yind2:2])
    sN11=copy(sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2])

    temp1 = sN01*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN11*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1-1:yind2-1:2]+sN01*vary1[xind1:xind2:2,yind1-1:yind2-1:2]
    sandNew[xind1:xind2:2,yind1-1:yind2-1:2] = copy(temp1)
    sandNew[xind1-1:xind2-1:2,yind1-1:yind2-1:2] = copy(temp2)

    sand=copy(sandNew)

    

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1+1:yind2+1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s01=sand[xind1-1:xind2-1:2,yind1:yind2:2]
    s11=sand[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    sandNew2[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew2[xind1:xind2:2,yind1+1:yind2+1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew2[xind1-1:xind2-1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew2[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew2[xind1-1:xind2-1:2,yind1:yind2:2]
    sN10=sandNew2[xind1:xind2:2,yind1+1:yind2+1:2]
    sN11=sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    temp3 = sN01*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN11*vary1[xind1-1:xind2-1:2,yind1:yind2:2]
    temp4 = sN11*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN01*vary1[xind1-1:xind2-1:2,yind1:yind2:2]

    sandNew2[xind1-1:xind2-1:2,yind1:yind2:2] = copy(temp3)
    sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2] = copy(temp4)

def sandFalling45ll(i,sand,gnd,z,sandNew,sandNew2,nx,ny):
    time.sleep(0.00002)
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1


    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1+1:xind2+1:2,yind1:yind2:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s01=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s11=sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    #sandNew[xind1:xind2:2,yind1:yind2:2]=gnd[xind1:xind2:2,yind1:yind2:2]*sand[xind1:xind2:2,yind1:yind2:2]+(1-gnd[xind1:xind2:2,yind1:yind2:2])*sand[xind1:xind2:2,yind1:yind2:2]*sand[xind1:xind2:2,yind1+1:yind2+1:2]*(sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]+(1-sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]))*sand[xind1+1:xind2+1:2,yind1:yind2:2]
    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1+1:xind2+1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1+1:yind2+1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1:xind2:2,yind1+1:yind2+1:2]
    sN10=sandNew[xind1+1:xind2+1:2,yind1:yind2:2]
    sN11=sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    temp1 = sN01*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN11*vary1[xind1:xind2:2,yind1+1:yind2+1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN01*vary1[xind1:xind2:2,yind1+1:yind2+1:2]

    sandNew[xind1:xind2:2,yind1+1:yind2+1:2] = copy(temp1)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2] = copy(temp2)
    sand=copy(sandNew)
    if p==0:
        p=1
    else:
        p=0

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1+1:yind2+1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s01=sand[xind1-1:xind2-1:2,yind1:yind2:2]
    s11=sand[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    sandNew2[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew2[xind1:xind2:2,yind1+1:yind2+1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew2[xind1-1:xind2-1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew2[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew2[xind1-1:xind2-1:2,yind1:yind2:2]
    sN10=sandNew2[xind1:xind2:2,yind1+1:yind2+1:2]
    sN11=sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2]

    temp3 = sN01*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN11*vary1[xind1-1:xind2-1:2,yind1:yind2:2]
    temp4 = sN11*vary[xind1-1:xind2-1:2,yind1:yind2:2]+sN01*vary1[xind1-1:xind2-1:2,yind1:yind2:2]

    sandNew2[xind1-1:xind2-1:2,yind1:yind2:2] = copy(temp3)
    sandNew2[xind1-1:xind2-1:2,yind1+1:yind2+1:2] = copy(temp4)

def sandFalling45lr(i,sand,gnd,z,sandNew,sandNew2,nx,ny):
    p=i%2
    vary = random.randint(2,size=(nx,ny))
    vary = vary.astype(float)
    vary1 = 1-vary
    print vary1
    #print vary

    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1 = 1+p
        xind2 = nx-2+p+1
        yind1 = 1+p
        yind2 = ny-2+p+1


    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1+1:xind2+1:2,yind1:yind2:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s01=sand[xind1:xind2:2,yind1+1:yind2+1:2]
    s11=sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    #sandNew[xind1:xind2:2,yind1:yind2:2]=gnd[xind1:xind2:2,yind1:yind2:2]*sand[xind1:xind2:2,yind1:yind2:2]+(1-gnd[xind1:xind2:2,yind1:yind2:2])*sand[xind1:xind2:2,yind1:yind2:2]*sand[xind1:xind2:2,yind1+1:yind2+1:2]*(sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]+(1-sand[xind1+1:xind2+1:2,yind1+1:yind2+1:2]))*sand[xind1+1:xind2+1:2,yind1:yind2:2]
    sandNew[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew[xind1+1:xind2+1:2,yind1:yind2:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew[xind1:xind2:2,yind1+1:yind2+1:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew[xind1:xind2:2,yind1+1:yind2+1:2]
    sN10=sandNew[xind1+1:xind2+1:2,yind1:yind2:2]
    sN11=sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2]

    temp1 = sN01*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN11*vary1[xind1:xind2:2,yind1+1:yind2+1:2]
    temp2 = sN11*vary[xind1:xind2:2,yind1+1:yind2+1:2]+sN01*vary1[xind1:xind2:2,yind1+1:yind2+1:2]

    sandNew[xind1:xind2:2,yind1+1:yind2+1:2] = copy(temp1)
    sandNew[xind1+1:xind2+1:2,yind1+1:yind2+1:2] = copy(temp2)
    sand=copy(sandNew)

    
    if p==0:
        xind1=1-p
        xind2=nx-3+p
        yind1=1-p
        yind2=ny-3+p
    elif p==1:
        xind1=1+p
        xind2=nx-2+p+1
        yind1=1+p
        yind2=ny-2+p+1

    g00=gnd[xind1:xind2:2,yind1:yind2:2]
    g10=gnd[xind1:xind2:2,yind1-1:yind2-1:2]
    s00=sand[xind1:xind2:2,yind1:yind2:2]
    s10=sand[xind1:xind2:2,yind1-1:yind2-1:2]
    s01=sand[xind1+1:xind2+1:2,yind1:yind2:2]
    s11=sand[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    sandNew2[xind1:xind2:2,yind1:yind2:2]=g00*s00+(1-g00)*s00*s01*(s11+(1-s11)*s10)
    sandNew2[xind1:xind2:2,yind1-1:yind2-1:2]=g10*s10+(1-g10)*s10*s11*(s01+(1-s01)*s00)
    sandNew2[xind1+1:xind2+1:2,yind1:yind2:2]=s01+(1-s01)*(s00*(1-g00)+(1-s00)*s10*(1-g10)*s11)
    sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2]=s11+(1-s11)*(s10*(1-g10)+(1-s10)*s00*(1-g00)*s01)

    sN00=sandNew2[xind1:xind2:2,yind1:yind2:2]
    sN01=sandNew2[xind1+1:xind2+1:2,yind1:yind2:2]
    sN10=sandNew2[xind1:xind2:2,yind1-1:yind2-1:2]
    sN11=sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2]

    temp3 = sN01*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN11*vary1[xind1+1:xind2+1:2,yind1:yind2:2]
    temp4 = sN11*vary[xind1+1:xind2+1:2,yind1:yind2:2]+sN01*vary1[xind1+1:xind2+1:2,yind1:yind2:2]

    sandNew2[xind1+1:xind2+1:2,yind1:yind2:2] = copy(temp3)
    sandNew2[xind1+1:xind2+1:2,yind1-1:yind2-1:2] = copy(temp4)



os.putenv('SDL_VIDEODRIVER','fbcon')
os.putenv('SDL_FBDEV','/dev/fb1')
os.putenv('SDL_MOUSEDRV','TSLIB')
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')
nx=320
ny=240

z=zeros((nx,ny))
z1=zeros((nx,ny))
z2=zeros((nx,ny))
z3=zeros((nx,ny))
z4=zeros((nx,ny))
o=ones((nx,ny))

sand=z1
sandNew=z2
sandNew2=z4
gnd=z3
#mode 1 ground
#gnd[0:nx,0]=1
#gnd[0:nx,ny-1]=1
#gnd[0,0:ny]=1
#gnd[nx-1,0:ny]=1

#fill the certain part of the screen with sand
#sand[int(nx/8):int(7*nx/8-1),0:31]=1

#pygame setting
pygame.init()
pygame.mouse.set_visible(False)
WHITE=255,255,255
BLACK=0,0,0
screen = pygame.display.set_mode((320,240))

my_font=pygame.font.Font(None,25)
my_buttons={'Quit':(290,210),'Mode One':(160,50),'Mode Two':(160,110),'Mode Three':(160,170)}
back_buttons={'Back':(290,210),'Reset':(30,210)}


screen.fill(BLACK)
for my_text, text_pos in my_buttons.items():
    text_surface=my_font.render(my_text, True, WHITE)
    rect=text_surface.get_rect(center=text_pos)
    screen.blit(text_surface,rect)
#set_matrix(sand,gnd,z,320,240)
pygame.display.flip()

GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

color1=65280

i=0
game_running=True
backToMenu=False
stop_game=False
Ha=-3
Hb=3
H180a=-3
H180b=3
H90cwa=7.5
H90cwb=15
H90ccwa=-15
H90ccwb=-7.5
Ra=7.5
Rb=15
R90cwa=-3
R90cwb=3
R180a=-15
R180b=-7.5
R90ccwa=-3
R90ccwb=3

Hlra=2.8
Hlrb=9.5
Hlla=-9.5
Hllb=-3.2
Hura=2.8
Hurb=9.5
Hula=-9.5
Hulb=-3.2

Rlra=2.8
Rlrb=9.5
Rlla=2.8
Rllb=9.5
Rura=-9.5
Rurb=-3.2
Rula=-9.5
Rulb=-3.2


while game_running:
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    '''heading, roll, pitch = bno.read_euler()'''
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    '''sys, gyro, accel, mag = bno.get_calibration_status()'''
    # Print everything out.
    '''print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))'''
    # Other values you can optionally read:
    # Orientation as a quaternion:
    #x,y,z,w = bno.read_quaterion()
    # Sensor temperature in degrees Celsius:
    #temp_c = bno.read_temp()
    # Magnetometer data (in micro-Teslas):
    #x,y,z = bno.read_magnetometer()
    # Gyroscope data (in degrees per second):
    #x,y,z = bno.read_gyroscope()
    # Accelerometer data (in meters per second squared):
    #x,y,z = bno.read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    #x,y,z = bno.read_linear_acceleration()
    # Gravity acceleration data (i.e. acceleration just from gravity--returned
    # in meters per second squared):
    #x,y,z = bno.read_gravity()
    # Sleep for a second until the next reading.


    time.sleep(0.02)
    #sandFalling(i,sand,gnd,z,sandNew,nx,ny)
    #sand=copy(sandNew)
    screen.fill(BLACK)
    for my_text, text_pos in my_buttons.items():
        text_surface=my_font.render(my_text, True, WHITE)
        rect=text_surface.get_rect(center=text_pos)
        screen.blit(text_surface,rect)
    #set_matrix(sand,gnd,z,320,240)
    pygame.display.flip()

    for event in pygame.event.get():
        if (event.type is MOUSEBUTTONDOWN):
            pos=pygame.mouse.get_pos()
        elif (event.type is MOUSEBUTTONUP):
            pos=pygame.mouse.get_pos()
            x,y=pos
            print x,y
            if x>115 and x<205:
                if y>43 and y<57:
                    #time.sleep(0.02)
                    print "Mode One!!"
                    screen.fill(BLACK)
                    gnd=zeros((320,240))
                    gnd[119:125,99:140]=1
                    gnd[199:204,99:140]=1
                    gnd[125:155,85:90]=1
                    gnd[125:155,145:150]=1
                    gnd[165:199,85:90]=1
                    gnd[165:199,145:150]=1
                    gnd[315:320,0:240]=1
                    gnd[0:3,0:240]=1
                    gnd[0:320,0:4]=1
                    gnd[0:320,235:240]=1
                    sand=z1
                    sand[int(nx/8):int(7*nx/8-1),4:31]=1
                    sand[int(nx/8):int(7*nx/8-1),210:235]=1
                    #set_matrix(sand,gnd,z,320,240)
                    pygame.surfarray.blit_array(screen,sand*65280+gnd*65535)
                    pygame.display.flip()
                    '''j=0
                    while True:
                        sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                        sand=copy(sandNew2)
                        screen.fill(BLACK)
                        pygame.surfarray.blit_array(screen,sand*65280+gnd*16777215)
                        j+=1
                        pygame.display.flip()'''
                    while backToMenu==False:
                        time.sleep(0.25)
                        Heading,Roll,Pitch = bno.read_accelerometer()
                        #Heading, Roll, Pitch = bno.read_euler()
                        print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(Heading, Roll, Pitch, sys, gyro, accel, mag))
                        if Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Yellow")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Purple")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Green")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762
                                sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()


                        elif Heading>Hlra and Heading<Hlrb and Roll>Rlra and Roll<Rlrb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Yellow")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Purple")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Green")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlra  and Heading<Hlrb and  Roll>Rlra and Roll<Rlrb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()



                        elif Heading>H90cwa and Heading<H90cwb and Roll>R90cwa and Roll<R90cwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling90cw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                #sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                #sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90cwa and  Heading<H90cwb and Roll>R90cwa and Roll<R90cwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()


                           #counter clockwise 90 degree
                        elif Heading>H90ccwa and Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling90ccw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90ccwa and  Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True 
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()



                        elif Heading>H180a and Heading<H180b and Roll>R180a and Roll<R180b:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling180(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H180a and  Heading<H180b and Roll>R180a and Roll<R180b):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()



                        elif Heading>Hlla and Heading<Hllb and Roll>Rlla and Roll<Rllb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ll(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlla  and Heading<Hllb and  Roll>Rlla and Roll<Rllb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True

                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()


                        elif Heading>Hura and Heading<Hurb and Roll>Rura and Roll<Rurb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ur(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hura  and Heading<Hurb and  Roll>Rura and Roll<Rurb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()



                        elif Heading>Hula and Heading<Hulb and Roll>Rula and Roll<Rulb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ul(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hula  and Heading<Hulb and  Roll>Rula and Roll<Rulb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()


                        #sand=copy(sandNew)
                        #screen.fill(BLACK)
                        #pygame.surfarray.blit_array(screen,sand*65280+gnd*65535)
                        #j+=1
                        #Back button
                        for my_text, text_pos in back_buttons.items():
                            text_surface=my_font.render(my_text, True, WHITE)
                            rect=text_surface.get_rect(center=text_pos)
                            screen.blit(text_surface,rect)
                        pygame.display.flip()
                        for event in pygame.event.get():
                            if (event.type is MOUSEBUTTONDOWN):
                                pos=pygame.mouse.get_pos()
                            elif (event.type is MOUSEBUTTONUP):
                                pos=pygame.mouse.get_pos()
                                x,y=pos
                                if x>275 and x<305:
                                    if y>200 and y<216:
                                        backToMenu=True
                                if x>10 and x<50:
                                    if y>200 and y<216:
                                        sand=copy(z1)
                                        sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                        sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                        screen.fill(BLACK)
                                        pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                        pygame.display.flip()


                    backToMenu=False
                    stop_game=False
                    break

                elif y>100 and y<118:
                    print "Mode Two!!"
                    '''screen.fill(BLACK)
                    pygame.surfarray.blit_array(screen,sand*65535+gnd*16777215)
                    pygame.display.flip()
                    
                    while True:
                        for event in pygame.event.get():
                            if (event.type is MOUSEBUTTONDOWN):
                                pos=pygame.mouse.get_pos()
                                x,y=pos
                                
                            elif (event.type is MOUSEBUTTONUP):
                                pos=pygame.mouse.get_pos()
                                x,y=pos
                                sand[x-2:x+2,y-2:y+2]=1
                                j=0
                                while True:
                                    sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                                    sand=copy(sandNew)
                                    pygame.surfarray.blit_array(screen,sand*65535+gnd*16777215)
                                    pygame.display.flip()
                                    for event in pygame.event.get():
                                        if (event.type is MOUSEBUTTONDOWN):
        
                                            pos=pygame.mouse.get_pos()
                                        elif (event.type is MOUSEBUTTONUP):
                                            pos=pygame.mouse.get_pos()
                                            x,y=pos
                                            sand[x-2:x+2,y-2:y+2]=1
                                            sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                                            sand=copy(sandNew)
                                            pygame.surfarray.blit_array(screen,sand*65535+gnd*16777215)
                                            pygame.display.flip()
                                    j+=1'''
                    screen.fill(BLACK)
                    gnd=zeros((320,240))
                    #gnd[119:125,99:140]=1
                    #gnd[199:204,99:140]=1
                    #gnd[125:155,85:90]=1
                    #gnd[125:155,145:150]=1
                    #gnd[165:199,85:90]=1
                    #gnd[165:199,145:150]=1
                    gnd[150:170,0:20]=1
                    gnd[0:20,110:130]=1
                    gnd[300:320,110:130]=1
                    gnd[315:320,0:240]=1
                    gnd[0:3,0:240]=1
                    gnd[0:320,0:4]=1
                    gnd[0:320,235:240]=1
                    sand
                    #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                    #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                    #set_matrix(sand,gnd,z,320,240)
                    pygame.surfarray.blit_array(screen,sand*65280+gnd*65535)
                    pygame.display.flip()
                    pressed=True
                    pressed2=True
                    pressed3=True
                    button=0
                    button2=0
                    button3=0
                    while backToMenu==False:
                        time.sleep(0.25)
                        #Heading, Roll, Pitch = bno.read_euler()
                        Heading,Roll,Pitch = bno.read_accelerometer()
                        print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(Heading, Roll, Pitch, sys, gyro, accel, mag))
                        if Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hlra and Heading<Hlrb and Roll>Rlra and Roll<Rlrb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''

                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1

                            

                                print "454545"
                                sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlra  and Heading<Hlrb and  Roll>Rlra and Roll<Rlrb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>H90cwa and Heading<H90cwb and Roll>R90cwa and Roll<R90cwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                sandFalling90cw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                #sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                #sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90cwa and  Heading<H90cwb and Roll>R90cwa and Roll<R90cwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                           #counter clockwise 90 degree
                        elif Heading>H90ccwa and Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=65535
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16711680'''
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                sandFalling90ccw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90ccwa and  Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>H180a and Heading<H180b and Roll>R180a and Roll<R180b:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                


                                sandFalling180(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H180a and  Heading<H180b and Roll>R180a and Roll<R180b):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hlla and Heading<Hllb and Roll>Rlla and Roll<Rllb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                print "454545"
                                sandFalling45ll(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlla  and Heading<Hllb and  Roll>Rlla and Roll<Rllb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hura and Heading<Hurb and Roll>Rura and Roll<Rurb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                print "454545"
                                sandFalling45ur(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hura  and Heading<Hurb and  Roll>Rura and Roll<Rurb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hula and Heading<Hulb and Roll>Rula and Roll<Rulb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                '''if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed=False
                                    button=23
                                elif (not GPIO.input(23)) and pressed==False:
                                    sand[20:30,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(22)) and pressed==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed=False
                                    button=22
                                elif (not GPIO.input(22)) and pressed==False:
                                    sand[290:300,110:130]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed==False and button==23:
                                    sand[20:30,110:130]=1
                                if pressed==False and button==22:
                                    sand[290:300,110:130]=1'''
                                if (not GPIO.input(27)) and pressed==True:
                                    print ("top")
                                    sand[150:170,20:30]=1
                                    pressed=False
                                    button=27
                                elif (not GPIO.input(27)) and pressed==False:
                                    sand[150:170,20:30]=0
                                    pressed=True
                                    button=0
                                elif (not GPIO.input(23)) and pressed2==True:
                                    print ("left")
                                    sand[20:30,110:130]=1
                                    pressed2=False
                                    button2=23
                                elif (not GPIO.input(23)) and pressed2==False:
                                    sand[20:30,110:130]=0
                                    pressed2=True
                                    button2=0
                                elif (not GPIO.input(22)) and pressed3==True:
                                    print ("Blue")
                                    sand[290:300,110:130]=1
                                    pressed3=False
                                    button3=22
                                elif (not GPIO.input(22)) and pressed3==False:
                                    sand[290:300,110:130]=0
                                    pressed3=True
                                    button3=0
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=255

                                if pressed==False and button==27:
                                    sand[150:170,20:30]=1
                                if pressed2==False and button2==23:
                                    sand[20:30,110:130]=1
                                if pressed3==False and button3==22:
                                    sand[290:300,110:130]=1


                                print "454545"
                                sandFalling45ul(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hula  and Heading<Hulb and  Roll>Rula and Roll<Rulb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                backToMenu=True
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=copy(z1)
                                                sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                        #sand=copy(sandNew)
                        #screen.fill(BLACK)
                        #pygame.surfarray.blit_array(screen,sand*65280+gnd*65535)
                        #j+=1
                        #Back button
                        for my_text, text_pos in back_buttons.items():
                            text_surface=my_font.render(my_text, True, WHITE)
                            rect=text_surface.get_rect(center=text_pos)
                            screen.blit(text_surface,rect)
                        pygame.display.flip()
                        for event in pygame.event.get():
                            if (event.type is MOUSEBUTTONDOWN):
                                pos=pygame.mouse.get_pos()
                            elif (event.type is MOUSEBUTTONUP):
                                pos=pygame.mouse.get_pos()
                                x,y=pos
                                if x>275 and x<305:
                                    if y>200 and y<216:
                                        backToMenu=True
                                if x>10 and x<50:
                                    if y>200 and y<216:
                                        sand=copy(z1)
                                        #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                        #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                        screen.fill(BLACK)
                                        pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                        pygame.display.flip()
                    backToMenu=False
                    stop_game=False
                    break
                                
                elif y>162 and y<175:
                    print "Mode Three!!"
                    screen.fill(BLACK)
                    pygame.surfarray.blit_array(screen,sand*65535+gnd*16777215)
                    pygame.display.flip()
                    Running=True
                    gnd=zeros((320,240))
                    gnd[315:320,0:240]=1
                    gnd[0:3,0:240]=1
                    gnd[0:320,0:4]=1
                    gnd[0:320,235:240]=1
                    sand=zeros((320,240))
                    j=0
                    while Running:
                        '''if pygame.mouse.get_pressed():
                            pos=pygame.mouse.get_pos()
                            x,y=pos
                            sand[x-5:x+5,y-5:y+5]=1
                        time.sleep(0.02)
                        sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                        sand=copy(sandNew)
                        pygame.surfarray.blit_array(screen,sand*65525+gnd*16777215)
                        pygame.display.flip()
                        j+=1
                        print "xxxxx"'''
                        Heading,Roll,Pitch = bno.read_accelerometer()
                        #Heading, Roll, Pitch = bno.read_euler()
                        print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(Heading, Roll, Pitch, sys, gyro, accel, mag))
                        if Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762
                                sandFalling(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Ha and Heading<Hb and Roll>Ra and Roll<Rb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                        elif Heading>Hlra and Heading<Hlrb and Roll>Rlra and Roll<Rlrb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlra  and Heading<Hlrb and  Roll>Rlra and Roll<Rlrb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                        elif Heading>H90cwa and Heading<H90cwb and Roll>R90cwa and Roll<R90cwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling90cw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                #sandFalling45lr(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                #sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90cwa and  Heading<H90cwb and Roll>R90cwa and Roll<R90cwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                           #counter clockwise 90 degree
                        elif Heading>H90ccwa and Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling90ccw(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>H90ccwa and  Heading<H90ccwb and Roll>R90ccwa and Roll<R90ccwb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>H180a and Heading<H180b and Roll>R180a and Roll<R180b:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1

                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                sandFalling180(j,sand,gnd,z,sandNew,nx,ny)
                                sand=copy(sandNew)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                print 'xxx'
                                #Heading, Roll, Pitch = bno.read_euler()
                                '''while pygame.mouse.get_pressed():
                                    time.sleep(0.02)
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                    #sand=copy(sandNew)
                                    #pygame.surfarray.blit_array(screen,sand*65525+gnd*16777215)
                                    #pygame.display.flip()
                                    pygame.event.get()
                                    print "yyyy"
                                    if event.type is MOUSEBUTTONUP:
                                        break'''

                                Heading,Roll,Pitch = bno.read_accelerometer()

                                if not (Heading>H180a and  Heading<H180b and Roll>R180a and Roll<R180b):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()
                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()
                            
 
                        elif Heading>Hlla and Heading<Hllb and Roll>Rlla and Roll<Rllb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ll(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hlla  and Heading<Hllb and  Roll>Rlla and Roll<Rllb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hura and Heading<Hurb and Roll>Rura and Roll<Rurb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ur(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hura  and Heading<Hurb and  Roll>Rura and Roll<Rurb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        elif Heading>Hula and Heading<Hulb and Roll>Rula and Roll<Rulb:
                            j=0
                            while not stop_game:
                                time.sleep(0.02)
                                if pygame.mouse.get_pressed():
                                    pos=pygame.mouse.get_pos()
                                    x,y=pos
                                    sand[x-5:x+5,y-5:y+5]=1
                                if (not GPIO.input(27)):
                                    print ("Green")
                                    color1=65280
                                elif (not GPIO.input(23)):
                                    print ("Yellow")
                                    color1=11823615
                                elif (not GPIO.input(22)):
                                    print ("Blue")
                                    color1=16758465
                                elif (not GPIO.input(17)):
                                    print ("Red")
                                    color1=16752762

                                print "454545"
                                sandFalling45ul(j,sand,gnd,z,sandNew,sandNew2,nx,ny)
                                sand=copy(sandNew2)
                                screen.fill(BLACK)
                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                j+=1
                                pygame.display.flip()
                                #Heading, Roll, Pitch = bno.read_euler()
                                Heading,Roll,Pitch = bno.read_accelerometer()
                                if not (Heading>Hula  and Heading<Hulb and  Roll>Rula and Roll<Rulb):
                                    break
                                for my_text, text_pos in back_buttons.items():
                                    text_surface=my_font.render(my_text, True, WHITE)
                                    rect=text_surface.get_rect(center=text_pos)
                                    screen.blit(text_surface,rect)
                                    pygame.display.flip()

                                for event in pygame.event.get():
                                    if (event.type is MOUSEBUTTONDOWN):
                                        pos=pygame.mouse.get_pos()
                                    elif (event.type is MOUSEBUTTONUP):
                                        pos=pygame.mouse.get_pos()
                                        x,y=pos
                                        if x>275 and x<305:
                                            if y>200 and y<216:
                                                stop_game=True
                                                Running=False
                                        if x>10 and x<50:
                                            if y>200 and y<216:
                                                sand=zeros((320,240))
                                                #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                                #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                                screen.fill(BLACK)
                                                pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                                pygame.display.flip()

                        for my_text, text_pos in back_buttons.items():
                            text_surface=my_font.render(my_text, True, WHITE)
                            rect=text_surface.get_rect(center=text_pos)
                            screen.blit(text_surface,rect)
                            pygame.display.flip()
                        for event in pygame.event.get():
                            if (event.type is MOUSEBUTTONDOWN):
                                pos=pygame.mouse.get_pos()
                            elif (event.type is MOUSEBUTTONUP):
                                pos=pygame.mouse.get_pos()
                                x,y=pos
                                if x>275 and x<305:
                                    if y>200 and y<216:
                                        Running=False
                                if x>10 and x<50:
                                    if y>200 and y<216:
                                        sand=copy(z1)
                                        #sand[int(nx/8):int(7*nx/8-1),4:31]=1
                                        #sand[int(nx/8):int(7*nx/8-1),210:235]=1
                                        screen.fill(BLACK)
                                        pygame.surfarray.blit_array(screen,sand*color1+gnd*16777215)
                                        pygame.display.flip()

                    Running=True
                    stop_game=False
                    break
                
                                                   
                                

            if x>275 and x<305:
                if y>200 and y<216:
                    game_running=False

       
    i+=1    

