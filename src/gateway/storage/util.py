import pika, json

def upload(f, fs, channel, access):
    try:
        file_id = fs.put(f)
        
    except Exception as err:
        return "internal server error", 500
    
    message = {
        "video_id": str(file_id),
        "mp3_id": None,
        "username": access["username"]
    }

    try:
        channel.basic_publish(
            exchange="", 
            routing_key="video", #this is the name of the queue
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
            
        )
    except Exception as err:
        print(err)
        fs.delete(file_id)
        return "internal server error", 500    