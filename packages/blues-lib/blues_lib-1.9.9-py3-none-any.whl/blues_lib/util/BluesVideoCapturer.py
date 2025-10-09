from blues_lib.util.BluesFiler import BluesFiler

class BluesVideoCapturer():

  capturer = None

  @classmethod
  def start(cls,file_path=''):
    if file_path:
      dl_path = file_path
    else:
      filename = BluesFiler.get_filename(extension='swf')
      dl_path = BluesFiler.get_file('video',filename)
    cls.capturer = Castro(filename=dl_path)
    cls.capturer.start()

  @classmethod
  def stop(cls):
    if cls.capturer:
      cls.capturer.stop()
      cls.capturer=None