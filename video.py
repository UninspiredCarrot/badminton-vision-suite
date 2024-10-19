import json
import cv2
import numpy as np
import time



class Score:
    def __init__(self, sets=None):
        if sets is None:
            self.sets = [[0,0], [0,0], [0,0]]
        else:
            self.sets = [set.copy() for set in sets]

    def get_current_set(self):
        for i, set in enumerate(self.sets):
            if (set[0] < 21 and set[1] < 21) or (abs(set[0] - set[1]) < 2 and (30 not in set)):
                return i, set
        return False, False
    
    def get_score(self):
        return self.sets
    
    def increment(self, points_given):
        index, set = self.get_current_set()
        self.sets[index] = [x+points_given[i] for i,x in enumerate(set)]

class Rally:
    def __init__(self, start_frame, end_frame, start_score):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.start_score = start_score

    def frame_in_rally(self, frame_number):
        return frame_number in range(self.start_frame, self.end_frame)

class Rallies:
    def __init__(self, total_frames, path):
        self.path = path
        self.total_frames = total_frames
        if open(path).read() == '':
            self.rallies = [Rally(0, self.total_frames, Score())]
        else:
            rally_dict = {}
            with open(path) as f_in:
                rally_dict = json.load(f_in)
            self.rallies = []
            for key, value in rally_dict.items():
                start, end = key.split('-')
                self.rallies.append(Rally(int(start), int(end), Score(value)))

    def get_rally_index(self, index):
        return self.rallies[index]
    
    def get_rally(self, frame_number):
        for i,rally in enumerate(self.rallies):
            if rally.frame_in_rally(frame_number):
                return i,rally
        return False,False
    
    def get_rally_before_break(self, frame_number):
        for i, rally in enumerate(self.rallies[:-1]):
            if frame_number in range(rally.end_frame, self.rallies[i+1].start_frame):
                return i, rally
        return False,False
    
    def append(self, frame_number, total_frames):
        self.rallies.append(Rally(frame_number, total_frames, Score(self.rallies[-1].start_score.get_score())))
    
    def pop(self, index):
        self.rallies.pop(index)

    def save(self):
        rallies = {}
        for rally in controls.rallies.rallies:
            rallies[f"{rally.start_frame}-{rally.end_frame}"] = rally.start_score.get_score()
        print(rallies)
        with open(self.path, 'w') as fp:
            json.dump(rallies, fp)



class Video:
    def __init__(self, path, players, start_score):
        self.path = path
        self.cap = cv2.VideoCapture(path)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.players = players
        self.start_score = start_score
        
        



        cv2.namedWindow("Info", cv2.WINDOW_NORMAL)

        
    def get_frame(self, frame_number, rallies):
        if frame_number != self.cap.get(cv2.CAP_PROP_POS_FRAMES):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = self.cap.read()
        if not ret:
            return None
        
        ri, rally = rallies.get_rally(frame_number)
        if rally:
            score_info = f"{rally.start_score.get_score()}; live"
        else:
            i, rally = rallies.get_rally_before_break(frame_number)
            score_info = f"{rallies.rallies[i+1].start_score.get_score()}; break"

        score_image = np.zeros((100, 600, 3), dtype=np.uint8)  # Adjust size as needed
        cv2.putText(score_image, score_info, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Info", score_image)
        return frame

    def release(self):
        self.cap.release()

class Controls:
    def __init__(self, total_frames, fps, path):
        self.playing = True
        self.quit = False
        self.frame_number = 0
        self.total_frames = total_frames
        self.fps = fps
        self.path = path
        self.rallies = Rallies(self.total_frames, path=path)
    
    def act(self, key):
        # print(key)
        key_actions = {
            27: self.quit_video, 
            ord(' '): self.toggle_play,
            2: self.rewind,
            3: self.fast_forward,
            ord('c'): self.toggle_cut,
            ord('u'): self.uncut,
            0: self.increment_1,
            1: self.increment_2,
            ord('z'): self.undo
        }
        
        for i in range(10):
            key_actions[ord(str(i))] = lambda i=i: self.goto_number(i)
        
        if key in key_actions:
            key_actions[key]()
        # elif key != 255:
        #     print(f"Unmapped key pressed: {key}")

    def quit_video(self):
        self.quit = True

    def toggle_play(self):
        self.playing = not self.playing

    def goto_number(self, number):
        self.frame_number = (self.total_frames // 10) * number

    def rewind(self):
        self.frame_number -= self.fps*2

    def fast_forward(self):
        self.frame_number += self.fps*2

    def isFinished(self):
        return self.frame_number >= self.total_frames
    
    def toggle_cut(self):
        ir, rally = self.rallies.get_rally(self.frame_number)
        if rally:
            rally.end_frame = self.frame_number
            self.rallies.append(self.total_frames, self.total_frames)
            return
        
        self.rallies.rallies[-1].start_frame = self.frame_number

    def uncut(self):
        if self.rallies.get_rally(self.frame_number):
            return 
        index, rally = self.rallies.get_rally_before_break(self.frame_number)
        self.rallies.get_rally_index(index+1).start_frame = rally.start_frame
        self.rallies.pop(index)

    def increment_1(self):
        ir, rally = self.rallies.get_rally(self.frame_number)
        if rally:
            rally.start_score.increment([1,0])
        else:
            i, rally = self.rallies.get_rally_before_break(self.frame_number)
            self.rallies.rallies[i+1].start_score.increment([1,0])

    
    def increment_2(self):
        ir, rally = self.rallies.get_rally(self.frame_number)
        if rally:
            rally.start_score.increment([0,1])
        else:
            i, rally = self.rallies.get_rally_before_break(self.frame_number)
            self.rallies.rallies[i+1].start_score.increment([0,1])

    def undo(self):
        ir, rally = self.rallies.get_rally(self.frame_number)
        if rally:
            if ir == 0:
                rally.start_score = Score()
            else:
                rally.start_score = Score(self.rallies.rallies[ir - 1].start_score.get_score())
           
        else:
            i, rally = self.rallies.get_rally_before_break(self.frame_number)
            self.rallies.rallies[i+1].start_score = Score(rally.start_score.get_score())


        
        
if __name__ == "__main__":
    video = Video(path="media/abbie.mp4", players=[], start_score=[])
    controls = Controls(video.total_frames, video.fps, "rallies.json")
    delta = 1 / video.fps
    last_time = time.time()
    

    while True:
        new_time = time.time()
        if new_time - last_time < delta and controls.playing:
            continue
        last_time += delta
        if controls.quit:
            break

        
        frame = video.get_frame(controls.frame_number, controls.rallies)
        if frame is None:
            break
        cv2.imshow("Frame", frame)
        if controls.playing:
            controls.frame_number += 1
            if controls.isFinished():
                controls.frame_number = 0

        key = cv2.waitKey(1) & 0xFF
        controls.act(key)

    video.release()
    cv2.destroyAllWindows()
    controls.rallies.save()

    
