## WeChat Command-Line Tool

#### Configuration

You need to get Tuling Chatbot API key and Face++ API key if you want to use Tuling.py and FaceAnalysis.py

After you've acquired these keys, create the "\_\_secrets__.py" file in modules folder and add your API keys
```python
facepp_keys = ["Key1", "Key2", "..."]
facepp_secrets = ["Secret1", "Secret2", "..."]
tuling_keys = ["Key1", "Key2", "..."]
```
If you want to write your own command-line module, please refer to "\_\_templates__.py" for details.

If you want to get better parallel performance (i.e. when many users are requesting simultaneously), set multi_process=True in \_\_config__.py, in folder "modules".

#### Running

Execute main.py using python 3

#### Dependencies:
##### python 3 (required, tested on 3.5)
##### itchat (required)
##### numpy (required)
##### Pillow (required)
##### numba (optional)
##### primesieve or pyprimes (recommend the former)

Opitonal modules are recommended to be installed because they can significantly the improve performance.

### Demo

![demo-pic](demo/1.jpg)
![demo-pic](demo/2.jpg)

