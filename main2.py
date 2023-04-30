import pyautogui as pag
import time

# media pipe dependencies
import cv2
import mediapipe as mp
from scipy.spatial import distance as dist
from datetime import datetime

# audio file dependencies
import speech_recognition as sr
import pyttsx3
import pyperclip

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

CAMERA = 1 # Usually 0, depends on input device(s)

# Optionally record the video feed to a timestamped AVI in the current directory
RECORDING = False
FPS = 10
RECORDING_FILENAME = str(datetime.now()).replace('.','').replace(':','') + '.avi'

EYE_BLINK_HEIGHT = .15
EYE_OPEN_HEIGHT = .25
MOUTH_OPEN_HEIGHT = .2
MIN_OPEN_DURATION = 2

winkedR = False
winkedL = False

mouth_open = False
mouth_log = []

def get_aspect_ratio(top, bottom, right, left):
  height = dist.euclidean([top.x, top.y], [bottom.x, bottom.y])
  width = dist.euclidean([right.x, right.y], [left.x, left.y])
  return height / width

def draw_frame(image, face_landmarks):
  mp_drawing.draw_landmarks(
      image=image,
      landmark_list=face_landmarks,
      connections=mp_face_mesh.FACEMESH_TESSELATION,
      landmark_drawing_spec=None,
      connection_drawing_spec=mp_drawing_styles
      .get_default_face_mesh_tesselation_style())
  mp_drawing.draw_landmarks(
      image=image,
      landmark_list=face_landmarks,
      connections=mp_face_mesh.FACEMESH_CONTOURS,
      landmark_drawing_spec=None,
      connection_drawing_spec=mp_drawing_styles
      .get_default_face_mesh_contours_style())
  mp_drawing.draw_landmarks(
      image=image,
      landmark_list=face_landmarks,
      connections=mp_face_mesh.FACEMESH_IRISES,
      landmark_drawing_spec=None,
      connection_drawing_spec=mp_drawing_styles
      .get_default_face_mesh_iris_connections_style())
  frame = cv2.flip(image, 1) # Flip image horizontally
  
  cv2.imshow('face', frame)

r = sr.Recognizer()

def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()
    
def get_audio(): 
    spoken_text = []
    #SpeakText("Voice enabled")

    while True:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration = 0.5)
            audio2 = r.listen(source2)
            try:
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
                if MyText.endswith('terminate'):
                    #SpeakText("Voice disabled")
                    words = MyText.lower().split()
                    words.pop()
                    new_text = " ".join(words)
                    print("parrot says : ", new_text)
                    spoken_text.append(new_text)
                    pyperclip.copy(new_text)
                    time.sleep(3)
                    pag.hotkey('command', 'v')
                    break
                print("parrot says : ", MyText)
                spoken_text.append(MyText)
                pyperclip.copy(MyText)
                time.sleep(3)
                pag.hotkey('command', 'v')

            except sr.UnknownValueError:
                print("Could not understand audio, please try again.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

cap = cv2.VideoCapture(CAMERA)
screen_w, screen_h = pag.size() #Getting screen height and width
pag.moveTo(screen_w/2, screen_h/2) #Initializing cursor to centre of screen
pag.FAILSAFE = False 

# to get output video, set RECORDING to true
if RECORDING:
  frame_size = (int(cap.get(3)), int(cap.get(4)))
  recording = cv2.VideoWriter(
    RECORDING_FILENAME, cv2.VideoWriter_fourcc(*'MJPG'), FPS, frame_size)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
  while cap.isOpened():
    success, image = cap.read()
    #image = cv2.flip(image,1)
    if not success: 
      break

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks and len(results.multi_face_landmarks) > 0:
      face_landmarks = results.multi_face_landmarks[0]
      face = face_landmarks.landmark
      face_w = face[454].x - face[227].x 
      face_h = face[10].y - face[152].y
      image_h, image_w, _ = image.shape
      nose_x, nose_y = 0,0
      
      for id, landmark in enumerate(face): #Looping through the coordinates of mesh
            #Denormalizing to get actual coordinates of landmarks of the face
            x = int(landmark.x * image_w) 
            y = int(landmark.y * image_h)
            if id==1:
                nose_x, nose_y = x,y #Getting x and y nose coordinates 
            cv2.circle(image, (x,y), 3, (0,255,0)) #the points, centre of circle is x and y, 3 channels, which color the cirlce should be


      sensitivity_factor = 2.5

      if nose_x > 0 and nose_y > 0: 
        # map nose position to screen coordinates
        screen_x = int(((nose_x / image_w) * screen_w - (screen_w / 2)) * sensitivity_factor + screen_w / 2) 
        screen_y = int(((nose_y / image_h) * screen_h - (screen_h / 2)) * sensitivity_factor + screen_h / 2)

        #(nose_x / image_w) * screen_w gives a range of the screen width and height- (nose_x / image_w) * screen_w
        #Subtracting it so that we can adjust the range to the 2 halves of the screen 
        #We multiply the sensitivity factor to increase sensitvity and add the centre of the screen to ensure that the cursor is still ath centre in the beginning of execution
          
        # clamp screen coordinates to screen edges to ensure that cursor does not go beyond screen 
        screen_x = max(0, min(screen_x, screen_w))          
        screen_y = max(0, min(screen_y, screen_h))

        #Horizontal inversion
        screen_x = screen_w - screen_x
          
        pag.moveTo(screen_x, screen_y)

      eyeR_top = face[159]
      eyeR_bottom = face[145]
      eyeR_inner = face[133]
      eyeR_outer = face[33]
      eyeR_ar = get_aspect_ratio(eyeR_top, eyeR_bottom, eyeR_outer, eyeR_inner)

      eyeL_top = face[386]
      eyeL_bottom = face[374]
      eyeL_inner = face[362]
      eyeL_outer = face[263]
      eyeL_ar = get_aspect_ratio(eyeL_top, eyeL_bottom, eyeL_outer, eyeL_inner)
      eyeA_ar = (eyeR_ar + eyeL_ar) / 2
  
      if eyeR_ar < EYE_BLINK_HEIGHT:
        if eyeL_ar > EYE_OPEN_HEIGHT:
          print("R wink", eyeR_ar)
          winkedR = True
          pag.rightClick()
          pag.sleep(1)
      elif eyeL_ar < EYE_BLINK_HEIGHT and eyeR_ar > EYE_OPEN_HEIGHT:
        print("L wink", eyeL_ar)
        winkedL = True
        pag.click()
        pag.sleep(1)
        
      mouth_inner_top = face[13]
      mouth_inner_bottom = face[14]
      mouth_inner_right = face[78]
      mouth_inner_left = face[308]
      mouth_inner_ar = get_aspect_ratio(
        mouth_inner_top, mouth_inner_bottom, mouth_inner_right, mouth_inner_left)

      mouth_open = mouth_inner_ar > MOUTH_OPEN_HEIGHT
      mouth_log.append([mouth_open, datetime.now()])
        # print("mouth open", mouth_inner_ar)
        # get_audio()
        
      # Initialize variables for tracking mouth open duration
      open_start_time = None
      last_open_time = None

      # Iterate over the mouth_log list
      for i in range(len(mouth_log)):
          # Check if mouth is closed
          if not mouth_log[i][0]:
              print("Mouth closed")
              open_start_time = None
              mouth_log = []
              break
          # Check if mouth is open
          else:
              print("Mouth open")
              # Check if this is the start of a new mouth open period
              if open_start_time is None:
                  open_start_time = mouth_log[i][1]
              # Check if the current open period is longer than MIN_OPEN_DURATION
              elif (mouth_log[i][1] - open_start_time).total_seconds() >= MIN_OPEN_DURATION:
                  print(f"Mouth has been continuously open for at least {MIN_OPEN_DURATION} seconds")
                  get_audio()
                  time.sleep(1)
                  pag.keyDown('command')
                  pag.keyDown('option')
                  pag.keyDown('9')
                  pag.keyUp('9')
                  pag.keyUp('option')
                  pag.keyUp('command')
                  time.sleep(1)
                  mouth_log = []

      draw_frame(image, face_landmarks)
      if RECORDING:
        recording.write(image)

    # Type 'q' on the video frame to quit
    if cv2.waitKey(5) & 0xFF == ord('q'):
      break

if RECORDING:
  recording.release()

cap.release()
cv2.destroyAllWindows()