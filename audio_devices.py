import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    list_devices = []

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            # print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            device = str(i) + " - " + p.get_device_info_by_host_api_device_index(0, i).get('name')
            device = {
                "id": i,
                "name": p.get_device_info_by_host_api_device_index(0, i).get('name')
            }
            list_devices.append(device)
    return list_devices
