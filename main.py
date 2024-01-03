from openai import OpenAI
from dotenv import load_dotenv
import os, playsound, threading, time, datetime

#-MAKE UI

load_dotenv()

apikey = os.getenv("OPENAI_KEY")
assistant_id = os.getenv("ASSISTANT_ID")    
client = OpenAI(api_key=apikey)
audio_folder = "audio"
generated_story_folder = "generated_story"
assistants_dict = {}

# create thread
thread = client.beta.threads.create()

def create_storyteller(name):
    client.beta.assistants.create(
        model="gpt-3.5",
        instructions="Tell an interesting story",
        name=name
    )

def get_assistant_id(assistant_name):
    f = open("storyteller_list\\list.txt","w")
    assistants_data = client.beta.assistants.list().data
    
    for i in range(len(assistants_data)):
        assistants_dict[assistants_data[i].name] = assistants_data[i].id
        f.write(assistants_data[i].name+"\n")

    f = open("storyteller_list\\list.txt","r")
    name = f.read()
    try:
        if assistant_name in name:
            assistant_id = assistants_dict[assistant_name]
            return assistant_id

    except KeyError:
        return "Assistant ID not available"

def system_message():
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="continue the story. Make sure that the story progresses and keep it interesting! with character dialogg, keep it 25-50 words long (LANGUAGE: INDONESIAN)"
    )

def assistant_message():
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=get_assistant_id("Sakura")
        )
    
    while True:
        # answering the message   
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == "completed":
            break
        else:
            pass

def storyteller(file_name):
    story_history = []
    i = 0
    while True:
        system_message()
        assistant_message()

        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        story_history.clear()
        for message in reversed(messages.data):
            story_history.append(message.content[0].text.value)

        f = open(f"{generated_story_folder}\\story_{file_name}","a")
        f.write(f"{story_history[-1]}\n")
        #text to speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            speed=1,
            input=story_history[-1]
        )
        response.stream_to_file(f"audio\\currtts{i}.mp3")
        i+=1

def start():
    curr_time = datetime.datetime.now()
    curr_story_name = f"{curr_time.date()}_{curr_time.hour}{curr_time.minute}{curr_time.second}"
    open(f"{generated_story_folder}\\story_{curr_story_name}", "x")

    # run assistant
    t1 = threading.Thread(target=storyteller, args=(curr_story_name,))
    t1.start()
    i=0
    while True:
        try:
            if os.path.exists(f"audio\\currtts{i}.mp3") == False:
                print("Loading")
                time.sleep(1)
                os.system("cls")
            else:
                playsound.playsound(f"audio\\currtts{i}.mp3")
                os.system("cls")
                i+=1
        except KeyboardInterrupt:
            print("Exiting program")
            t1.join(timeout=0)
            for files in os.listdir(audio_folder):
                os.remove(f"{audio_folder}\\{files}")
            break

start()