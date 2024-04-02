# importing libraries
import cv2 
import imutils
import numpy as np 


NMS_THRESHOLD = 0.3
MIN_CONFIDENCE = 0.2

# function to detect people
def pedestrian_detection(image, model, layer_name, personidz=0):
	
	# getting image size
	height_, weight_ = image.shape[:2]
	
	results = []

	# preparing model
	blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
	
	model.setInput(blob)
	
	layerOutputs = model.forward(layer_name)

	boxes = []
	centroids = []
	confidences = []

	for output in layerOutputs:
		
		for detection in output:

			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			# checking if the class detected is a Person-Class number 0
			if classID == personidz and confidence > MIN_CONFIDENCE:

				box = detection[0:4] * np.array([weight_, height_, weight_, height_])
				(centerX, centerY, width, height) = box.astype("int")

				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))

				boxes.append([x, y, int(width), int(height)])
				centroids.append((centerX, centerY))
				confidences.append(float(confidence))
	
	# bounding boxes
	idzs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONFIDENCE, NMS_THRESHOLD)
	
	# ensuring at least one detection exists
	if len(idzs) > 0:
	
		# loop over the indexes we are keeping
		for i in idzs.flatten():
	
			# extracting the bounding box coordinates
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])
	
			# update our results list to consist of the person
			# prediction probability, bounding box coordinates,
			# and the centroid
			res = (confidences[i], (x, y, x + w, y + h), centroids[i])
			results.append(res)
	
	# return the list of results
	return results

# openning all classes in Yolo
labelsPath = "coco.names"
LABELS = open(labelsPath).read().strip().split("\n")

weights_path = "yolov4-tiny.weights"
config_path = "yolov4-tiny.cfg"

model = cv2.dnn.readNetFromDarknet(config_path, weights_path)

layer_name = model.getLayerNames()
layer_name = [layer_name[i - 1] for i in model.getUnconnectedOutLayers()]

# openning the default camera
camera = cv2.VideoCapture(0)

# loopingh through camera frames
while camera.isOpened():
	
	success, frame = camera.read()

	# checking if camera did open
	if not success:

		print("Error! Camera could not be opened.")
		break
	
	image = imutils.resize(frame, width=700)
	
	# classifying only person class
	results = pedestrian_detection(frame, model, layer_name, personidz=LABELS.index("person"))
	
	# displaying the count of detected people
	cv2.putText(frame, f"People Detected: {len(results)}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
	
	# detecting people
	for res in results:
		
		cv2.rectangle(frame, (res[1][0],res[1][1]), (res[1][2],res[1][3]), (255, 0, 255), 2)

	# displaying frame
	cv2.imshow("People Detection", frame)

	# terminating frame by pressing "q":quit
	if cv2.waitKey(1) & 0xFF == ord("q"):
		
		break

# closing all opened frames
camera.release()
cv2.destroyAllWindows()