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

def auto_run_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == 97

def auto_run_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == 97

def time_out(e):
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
        boy.start_time = get_time()
        print('Idle Enter')

    @staticmethod
    def exit(boy,e):
        print('Idle Exit')

    @staticmethod
    def do(boy): #frame value change
        boy.frame = (boy.frame + 1) % 8
        print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame*100, boy.action*100, 100, 100, boy.x, boy.y)


class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e): # right running
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

        if boy.x >= 780:
            boy.x = 780
        elif boy.x <= 20:
            boy.x = 20
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class AutoRun:

    @staticmethod
    def enter(boy, e):
        if auto_run_down(e) or auto_run_up(e):  # right running
            if boy.dir == 0 or boy.dir == 1:
                boy.dir, boy.action = 1, 1
            elif boy.dir == -1:
                boy.dir, boy.action = -1, 0

        print('AutoRun Enter')

    @staticmethod
    def exit(boy, e):
        print('AutoRun Exit')
        pass

    @staticmethod
    def do(boy):  # frame value change
        print('AutoRun Do')

        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 20

        if boy.x >= 700:
            boy.x = 700
            boy.dir, boy.action = -1, 0
        elif boy.x <= 0:
            boy.x = 0
            boy.dir, boy.action = 1, 1

        if get_time() - boy.start_time > 5: #Idle
            boy.state_machine.handle_event(('TIME_OUT', 5))
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x + 60, boy.y + 60, 300, 300)
        print('AutoRun Draw')



class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.table = { #상태 테이블
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, auto_run_down: AutoRun, auto_run_up: AutoRun},
            Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle},
            AutoRun: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Idle}
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
