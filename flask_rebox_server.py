from flask import Flask, Response, request, send_file, jsonify, json
import os
import natsort
import subprocess
import cv2
import time

running_time = 0
app = Flask(__name__)

@app.route("/get-time", methods=["GET"])
def get_time():
    now = time.time()
    time_elapsed = now - running_time
    return json.dumps(round(time_elapsed))

@app.route("/check-running", methods=["GET"])
def check_running():
    try:
        # One-liner command to check if screen session exists
        result = subprocess.run(f"screen -ls | grep -q 'rebox'", shell=True)
        return json.dumps(result.returncode == 0)
    except subprocess.CalledProcessError:
        return json.dumps(False)

@app.route("/start-script",methods=["GET"])
def start_script():
    global running_time
    running_time = time.time()
    session_name = "rebox"

    script_command = "python /home/rebox/main.py"
    
    subprocess.Popen(f"screen -dmS {session_name} -L bash -c '{script_command}'", shell=True)

    return jsonify({"message": "Script started in screen session."})

@app.route("/get-output", methods=["GET"])
def get_output():
    
    def generate():
        process = subprocess.Popen(["stdbuf","-i0", "-o0","-e0","tail", "-f","---disable-inotify", "--sleep-interval=0.1","screenlog.0"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
 
        for line in iter(process.stdout.readline, ''):
            if line == "ENDED\n":
                break
            yield f"{line}"
            
    
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/event-stream')

    # command = "screen -dmS test_script bash -c 'python test_script.py; exec bash'"
    # # command = "screen -S test1 -X quit"
    # subprocess.run(command, shell=True, check=True)
    # return "yo"

@app.route("/stop-running", methods=["GET"])
def stop_running():
    try:
        subprocess.run(["screen","-S","rebox","-X","quit"], check=True)
    except subprocess.CalledProcessError:
        pass
    subprocess.run(["rm","screenlog.0"])
    return jsonify({"message": "Script finished running and log deleted"})

@app.route("/listdir/<path:folder>", methods=["GET"])
def get_listdir(folder):
    # current_dir = os.getcwd()
    folders = natsort.os_sorted(os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),folder)))
    return folders


@app.route("/store-config", methods=["PUT"])
def store_config():
    data = request.json
    print(type(data))
    print(data)
    with open("/home/rebox/config.txt", "w") as f:
        for i in data:
            f.write(str(i)+"\n")

    return "done", 200

@app.route("/get-config", methods=["GET"])
def get_config():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"config.txt"), "r") as f:
        data = f.readlines()
    
    return data
# @app.route('/run-script')
# def run_script():
#     def generate():
#         process = subprocess.Popen(["python", "/home/rebox/test_script.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

#         # while True:
#         #     output = process.stdout.readline()
#         #     error = process.stderr.readline()
#         #     if error == "" and process.poll() is not None:
#         #         break
#         #     if output:
#         #         yield f"{output}"
#         #     if error:
#         #         yield f"{error}"

#         # process.stdout.close()
#         # process.stderr.close()
#         # process.wait()
#         for line in iter(process.stdout.readline, ''):
#             yield f"{line}"
        
#         for line in iter(process.stderr.readline, ''):
#             yield f"{line}"
        
#         process.stdout.close()
#         process.stderr.close()
#         process.wait()
#     return Response(generate(), mimetype='text/event-stream')

@app.route("/get-image/<path:image_path>",methods=["GET"])
def get_image(image_path):
    return send_file(os.path.join(os.path.dirname(os.path.realpath(__file__)),image_path), mimetype="image/jpg")

@app.route("/get-image-preview",methods=["GET"])
def get_image_preview():
    with open("/home/rebox/config.txt", "r") as f:
        data = [i.replace("\n","") for i in f.readlines()]
        name = data[-1]
        img_path = os.path.join("/home/rebox/boxed", name)
        img_list = natsort.os_sorted(os.listdir(img_path))


    if img_list:
        latest_img_path = img_list[-1]
        return send_file(os.path.join(img_path,latest_img_path), mimetype="image/jpg")
    return json.dumps(None)


# BAD PRACTICE TO ALSO PASS THE VIDEOS DIR IN THE ARUGMENT, FIX LATER
@app.route("/get-video/<path:video_path>", methods=["GET"])
def get_video(video_path):
    print(os.path.join(os.path.dirname(os.path.realpath(__file__)),video_path))
    return send_file(os.path.join(os.path.dirname(os.path.realpath(__file__)),video_path), mimetype="video/mp4")


@app.route("/check",methods=["GET"])
def check():
    return "status checked"

# TESTING
if __name__ == "__main__":

    app.run(host='0.0.0.0', port=40030, debug=True, threaded=True)   # deploy