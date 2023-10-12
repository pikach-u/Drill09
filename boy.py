# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def time_out(e):
    return e[0] == 'TIME_OUT'

def time_out_5(e):
    return e[0] == 'TIME_OUT' and e[1] == 5.0


class Idle:

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.start_time = get_time() #게임을 시작했을 때를 0초로, get time이 호출될 때까지의 경과시간을 가져오는 함수
        print('Idle Enter')

    @staticmethod
    def exit(boy,e):
        print('Idle Exit')

    @staticmethod
    def do(boy): #frame value change
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100, boy.action*100, 100, 100, boy.x, boy.y)

class Sleep:

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('눕다')

    @staticmethod
    def exit(boy, e):
        print('일어서기')

    @staticmethod
    def do(boy):  # frame value change
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                      -math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                                          math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)

class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e) : # right running
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e): # left running
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):  # frame value change
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.table = { #상태 테이블
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep},
            Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run,space_down: Idle},
            Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def handle_event(self, e):
        for check_event, next_state in self.table[self.cur_state].items(): #current state: Sleep / check event: space down / next state: Idle
            if check_event(e):
                self.cur_state.exit(self.boy, e)   #상태를 바꾸기 전에 현재 상태의 exit() 수행
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)  #바뀐 상태의 entry action 수행
                return True #상태변화 완료

        return False #들어온 이벤트가 처리되지 않았음


    def draw(self):
        self.cur_state.draw(self.boy)





class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
