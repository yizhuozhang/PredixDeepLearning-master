# Python Flask application for TensorFlow demo

# Import Flask for building web app
from flask import Flask, request ,render_template,Markup,send_from_directory

# Other standard imports in Python
import os
import ssl
import six.moves.urllib as urllib
import cv2
import random
import numpy as np
# Import our method for running model
from predict import run_model, load_image_into_numpy_array,numpy_array_to_PIL

# Get the port for starting web server
port = int(os.getenv('PORT', '5000'))


# Create the Flask app
app = Flask(__name__, static_url_path='')

# Initialize SSL context to read URLs with HTTPS
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#### DEFINE Flask Routes ####

@app.route('/create/<summary>/<change>')
def createcm(summary=None, change=None):
    print(summary)
    print(change)
    return summary + change
    
@app.route("/")
def index():
    return render_template("upload.html",env_vars=os.environ, req_headers=request.headers, req_params=request.args)

# Handle the request when URL is passed
@app.route('/upload', methods=['POST', 'GET'])
def upload():
                                            
    target = os.path.join(APP_ROOT, 'images/')
    #target2 = os.path.join(APP_ROOT, 'images/')
    # target = os.path.join(APP_ROOT, 'static/')
    if not os.path.isdir(target):
            os.mkdir(target)
    #if not os.path.isdir(target2):
    #       os.mkdir(target2)            
    else:
        print("Couldn't create upload directory: {}".format(target))
        
    mytag = str(random.random())
    
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        filename = 'im' + '0' + mytag +'.jpg'
        destination = "/".join([target, filename])
        upload.save(destination)

    # read the image using PIL
    image_np = cv2.imread(destination)

    image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    # Call method to run Caffe model on the image        
    result,idxs,idxe,label = run_model(image_np)
    
    width, height,dim = image_np.shape
    
    resultold = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)	
    for res in idxs:
        resultold = cv2.rectangle(resultold,idxs[res],idxe[res],(0,0,255))
        resultold=	cv2.putText(resultold,label[res],idxs[res],cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

    cv2.imwrite('images/'+ filename , resultold)
    
    ret_str = ""
    i = 1
    for res in result:
        # Create temp image for each image detected
        tempimage = numpy_array_to_PIL(result[res],(width,height,dim))
        resname = res.split(":")[0]
        tempimage.save("images/" + 'im' + str(i) + mytag + ".jpg")	
        i += 1 
        print("res path:" + res)
        ret_str = ret_str + "<b>Object = %s</b><br>"%(res)
    
    #ret_str = ret_str + "<br><hr><b>Analyzed Image</b><br><img src='%s'><br>"%(filename)
    image_names = os.listdir('./images')
    tag = mytag
    im = []
    for name in image_names:
        if name.find(tag) >-1:
            im.append(name)
            

    return render_template("complete_display_image.html", image_names=im, tag = tag ,numberofdetected=len(result),objective= Markup(ret_str))



@app.route('/upload/<filename>/<tag>')
def send_image(filename=None,tag=None):
    return send_from_directory('images', filename)
      
        
# Run the application and start server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
